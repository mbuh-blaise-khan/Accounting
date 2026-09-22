"""Tests for workspace archive / restore / conditional permanent delete.

Rules under test (archive-first product policy):
- `archived_at` is NULL for every existing/new workspace (active by default).
- Archive is the PRIMARY action: hides the workspace from the active list,
  makes it read-only at the SERVICE layer, deletes NOTHING — profile,
  accounts, drafts, posted transactions, reports and memberships all stay,
  and every read/report endpoint keeps working.
- Restore returns the workspace to the active list (owner-only).
- Permanent delete is owner-only and eligible ONLY with zero posted AND zero
  reversed transactions; any protected history is rejected with a clear
  "archive it instead" error. Typed confirmation is REQUIRED and validated
  SERVER-SIDE. Deletion removes only the workspace's own dependent data and
  never touches users, other orgs, learner progress, attempts, review
  records, certificates, or public verification data.
"""
from datetime import datetime, timezone

from app.models.account import Account
from app.models.certificate import Certificate
from app.models.learning import Attempt, LessonProgress, ReviewItem
from app.models.organization import Organization, OrganizationMember
from app.models.transaction import TransactionLine


def _register(client, email="alice@example.com"):
    resp = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "supersecret123",
            "display_name": "Alice",
            "language_preference": "en",
        },
    )
    assert resp.status_code == 200, resp.text
    login = client.post(
        "/auth/login", json={"email": email, "password": "supersecret123"}
    )
    assert login.status_code == 200, login.text
    return resp


def _create_org(client, name="Acme", framework="OHADA", is_demo=True):
    resp = client.post(
        "/organizations",
        json={"name": name, "framework": framework, "currency": "XAF", "is_demo": is_demo},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _accounts_by_code(client, org_id):
    resp = client.get(f"/accounts?organization_id={org_id}")
    assert resp.status_code == 200, resp.text
    return {a["code"]: a for a in resp.json()}


def _make_txn(client, org_id, lines, description="Sold goods for cash"):
    resp = client.post(
        "/transactions",
        json={"organization_id": org_id, "description": description, "lines": lines},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _balanced_lines(acc):
    return [
        {"account_id": acc["57"]["id"], "debit": 50000, "credit": 0},
        {"account_id": acc["70"]["id"], "debit": 0, "credit": 50000},
    ]


def _post_txn(client, org_id, txn_id):
    resp = client.post(f"/transactions/{txn_id}/post?organization_id={org_id}")
    assert resp.status_code == 200, resp.text
    return resp.json()


def _custom_account(client, org_id, code="9980", name_en="My Special Account"):
    resp = client.post(
        "/accounts",
        json={
            "organization_id": org_id,
            "framework": "OHADA",
            "code": code,
            "name_en": name_en,
            "name_fr": "Mon compte",
            "account_class": "expense",
            "normal_balance": "debit",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _delete_org(client, org_id, confirm_name):
    # client.request (NOT client.delete): the installed httpx does not accept
    # a `json` body on the convenience .delete() verb, but the REAL endpoint
    # requires a JSON body — browsers send DELETE with a body via fetch.
    return client.request(
        "DELETE", f"/organizations/{org_id}", json={"confirm_name": confirm_name}
    )


# --- 1. Existing workspaces default to active/non-archived -------------------

def test_existing_workspaces_default_to_active(client, test_db_session):
    _register(client)
    org = _create_org(client)
    detail = client.get(f"/organizations/{org['id']}").json()
    assert detail["archived_at"] is None
    assert detail["has_protected_history"] is False
    row = test_db_session.get(Organization, org["id"])
    assert row is not None and row.archived_at is None


# --- 2. Archive hides the workspace from the active list ---------------------

def test_archive_hides_from_active_list(client):
    _register(client)
    a = _create_org(client, name="Archive Me")
    b = _create_org(client, name="Stay Active")
    resp = client.post(f"/organizations/{a['id']}/archive")
    assert resp.status_code == 200, resp.text
    archived = resp.json()
    assert archived["archived_at"] is not None

    active_ids = [o["id"] for o in client.get("/organizations").json()]
    assert a["id"] not in active_ids
    assert b["id"] in active_ids


# --- 3. Archived list retrieves only authorized archived workspaces ----------

def test_archived_list_returns_only_authorized_archived(client):
    _register(client, "alice@example.com")
    a = _create_org(client, name="Alice Archived")
    b = _create_org(client, name="Alice Active")
    client.post(f"/organizations/{a['id']}/archive")

    # Alice: archived list = only the archived one.
    resp = client.get("/organizations?archived=true")
    assert resp.status_code == 200
    archived_ids = [o["id"] for o in resp.json()]
    assert a["id"] in archived_ids
    assert b["id"] not in archived_ids

    # Bob (different user): never sees Alice's archived workspace.
    _register(client, "bob@example.com")
    resp = client.get("/organizations?archived=true")
    assert resp.status_code == 200
    assert a["id"] not in [o["id"] for o in resp.json()]
    resp = client.get("/organizations")
    assert a["id"] not in [o["id"] for o in resp.json()]


# --- 4. Restore returns the workspace to the active list ---------------------

def test_restore_returns_to_active_list(client):
    _register(client)
    org = _create_org(client, name="Come Back")
    client.post(f"/organizations/{org['id']}/archive")
    assert org["id"] not in [o["id"] for o in client.get("/organizations").json()]

    resp = client.post(f"/organizations/{org['id']}/restore")
    assert resp.status_code == 200, resp.text
    restored = resp.json()
    assert restored["archived_at"] is None

    active_ids = [o["id"] for o in client.get("/organizations").json()]
    assert org["id"] in active_ids
    assert org["id"] not in [
        o["id"] for o in client.get("/organizations?archived=true").json()
    ]


# --- 5. Non-owner/member access follows the safe 404/authorization rules -----

def test_non_member_gets_404_and_member_non_owner_403(client, test_db_session):
    _register(client, "alice@example.com")
    org = _create_org(client, name="Alices Org")

    # Bob (non-member): 404 on all three actions, never 403 (no existence leak).
    _register(client, "bob@example.com")
    assert client.post(f"/organizations/{org['id']}/archive").status_code == 404
    assert client.post(f"/organizations/{org['id']}/restore").status_code == 404
    assert _delete_org(client, org["id"], org["name"]).status_code == 404

    # Carol is a MEMBER but not the owner: 403 (she already knows the org).
    _register(client, "carol@example.com")
    carol_id = client.get("/me").json()["id"]
    test_db_session.add(
        OrganizationMember(org_id=org["id"], user_id=carol_id, role="member")
    )
    test_db_session.commit()
    assert client.post(f"/organizations/{org['id']}/archive").status_code == 403
    assert client.post(f"/organizations/{org['id']}/restore").status_code == 403
    assert _delete_org(client, org["id"], org["name"]).status_code == 403

    # Unauthenticated requests are rejected outright.
    client.post("/auth/logout")
    assert client.post(f"/organizations/{org['id']}/archive").status_code == 401
    assert _delete_org(client, org["id"], org["name"]).status_code == 401


# --- 6. Archive preserves profile, accounts, drafts, posted data, reports ----

def test_archive_preserves_profile_accounts_drafts_posted_reports(client):
    _register(client)
    org = _create_org(client, name="Full History")
    acc = _accounts_by_code(client, org["id"])
    custom = _custom_account(client, org["id"])
    draft = _make_txn(client, org["id"], _balanced_lines(acc))
    posted = _post_txn(client, org["id"], draft["id"])
    resp = client.patch(
        f"/organizations/{org['id']}",
        json={"registered_address": "123 Test Street"},
    )
    assert resp.status_code == 200, resp.text

    assert client.post(f"/organizations/{org['id']}/archive").status_code == 200

    # Profile readable, accounts (seeded + custom) intact, transactions intact.
    detail = client.get(f"/organizations/{org['id']}").json()
    assert detail["registered_address"] == "123 Test Street"
    assert detail["archived_at"] is not None
    assert detail["has_protected_history"] is True

    accounts = client.get(f"/accounts?organization_id={org['id']}").json()
    assert custom["id"] in [a["id"] for a in accounts]

    txns = client.get(f"/transactions?organization_id={org['id']}").json()
    assert len(txns) == 1  # the draft WAS posted before archiving
    assert txns[0]["id"] == posted["id"]
    assert txns[0]["status"] == "posted"


# --- 7. Archived workspace rejects every relevant mutation -------------------

def test_archived_rejects_every_relevant_mutation(client):
    _register(client)
    org = _create_org(client, name="Read Only")
    acc = _accounts_by_code(client, org["id"])
    posted = _post_txn(
        client, org["id"], _make_txn(client, org["id"], _balanced_lines(acc))["id"]
    )
    custom = _custom_account(client, org["id"])
    kept_draft = _make_txn(
        client, org["id"], _balanced_lines(acc), description="Draft kept"
    )

    assert client.post(f"/organizations/{org['id']}/archive").status_code == 200

    # create draft transaction
    resp = client.post(
        "/transactions",
        json={
            "organization_id": org["id"],
            "description": "new draft",
            "lines": _balanced_lines(acc),
        },
    )
    assert resp.status_code == 409
    assert "archived" in resp.json()["detail"].lower()

    # post a (pre-existing) draft
    resp = client.post(
        f"/transactions/{kept_draft['id']}/post?organization_id={org['id']}"
    )
    assert resp.status_code == 409
    assert "archived" in resp.json()["detail"].lower()

    # reverse a posted transaction
    resp = client.post(
        f"/transactions/{posted['id']}/reverse?organization_id={org['id']}"
    )
    assert resp.status_code == 409
    assert "archived" in resp.json()["detail"].lower()

    # create account
    resp = client.post(
        "/accounts",
        json={
            "organization_id": org["id"],
            "framework": "OHADA",
            "code": "9970",
            "name_en": "Blocked Account",
            "name_fr": "Compte bloqué",
            "account_class": "expense",
            "normal_balance": "debit",
        },
    )
    assert resp.status_code == 409
    assert "archived" in resp.json()["detail"].lower()

    # update account
    resp = client.patch(
        f"/accounts/{custom['id']}?organization_id={org['id']}",
        json={"name_en": "Renamed"},
    )
    assert resp.status_code == 409
    assert "archived" in resp.json()["detail"].lower()

    # update business profile
    resp = client.patch(
        f"/organizations/{org['id']}",
        json={"registered_address": "Should Not Work"},
    )
    assert resp.status_code == 409
    assert "archived" in resp.json()["detail"].lower()


# --- 8. Archived workspace still permits reads and reports -------------------

def test_archived_permits_reads_and_reports(client):
    _register(client)
    org = _create_org(client, name="Still Readable")
    acc = _accounts_by_code(client, org["id"])
    posted = _post_txn(
        client, org["id"], _make_txn(client, org["id"], _balanced_lines(acc))["id"]
    )
    assert client.post(f"/organizations/{org['id']}/archive").status_code == 200

    reads = (
        f"/organizations/{org['id']}",
        f"/accounts?organization_id={org['id']}",
        f"/accounts/suggested?organization_id={org['id']}",
        # There is deliberately NO GET /transactions/{id} endpoint: the
        # frontend reads historical transactions through the org-scoped LIST
        # (fetchTransactions) and finds the row client-side. The list must
        # keep working while archived AND still contain the posted txn.
        f"/transactions?organization_id={org['id']}",
        f"/journal-entries?organization_id={org['id']}",
        f"/cashbook?organization_id={org['id']}",
        f"/ledger/{acc['57']['id']}?organization_id={org['id']}",
        f"/trial-balance?organization_id={org['id']}",
        f"/reports/income-statement?organization_id={org['id']}",
        f"/reports/financial-position?organization_id={org['id']}",
    )
    for path in reads:
        resp = client.get(path)
        assert resp.status_code == 200, f"{path} -> {resp.status_code}"

    # The posted transaction itself remains readable through the list.
    listed = client.get(f"/transactions?organization_id={org['id']}").json()
    assert any(t["id"] == posted["id"] for t in listed)


# --- 9. Delete rejects any workspace with posted or reversed history ---------

def test_delete_rejected_with_posted_or_reversed_history(client):
    _register(client)

    org_posted = _create_org(client, name="Has Posted")
    acc = _accounts_by_code(client, org_posted["id"])
    txn = _make_txn(client, org_posted["id"], _balanced_lines(acc))
    _post_txn(client, org_posted["id"], txn["id"])
    resp = _delete_org(client, org_posted["id"], org_posted["name"])
    assert resp.status_code == 409, resp.text
    assert "archive" in resp.json()["detail"].lower()

    org_reversed = _create_org(client, name="Has Reversed")
    acc = _accounts_by_code(client, org_reversed["id"])
    txn = _make_txn(client, org_reversed["id"], _balanced_lines(acc))
    posted = _post_txn(client, org_reversed["id"], txn["id"])
    resp = client.post(
        f"/transactions/{posted['id']}/reverse?organization_id={org_reversed['id']}"
    )
    assert resp.status_code == 200, resp.text
    resp = _delete_org(client, org_reversed["id"], org_reversed["name"])
    assert resp.status_code == 409, resp.text
    assert "archive" in resp.json()["detail"].lower()


# --- 10. Delete succeeds for an owner with an eligible workspace -------------

def test_delete_succeeds_for_owner_eligible_workspace(client, test_db_session):
    _register(client)
    org = _create_org(client, name="Only Drafts")
    acc = _accounts_by_code(client, org["id"])
    _make_txn(client, org["id"], _balanced_lines(acc))  # draft only
    _custom_account(client, org["id"])

    resp = _delete_org(client, org["id"], "Only Drafts")
    assert resp.status_code == 204, resp.text

    assert test_db_session.get(Organization, org["id"]) is None
    assert org["id"] not in [o["id"] for o in client.get("/organizations").json()]
    assert org["id"] not in [
        o["id"] for o in client.get("/organizations?archived=true").json()
    ]


# --- 10b. REGRESSION: the DELETE endpoint must never 500 ---------------------
#
# Production symptom: DELETE /organizations/33 -> HTTP 500 (the browser
# blamed CORS, but the CORS error was SECONDARY — the 500 was produced by
# Starlette's outermost ServerErrorMiddleware, whose plain-text response
# bypasses CORSMiddleware and therefore carries no CORS headers).
#
# Real root cause: delete_organization() built its draft-transaction-line
# cleanup as a JOINED bulk query
#     db.query(TransactionLine).join(Transaction, ...).delete(...)
# which SQLAlchemy rejects at statement-compile time with
#     InvalidRequestError: Can't call Query.update() or Query.delete()
#     when join(), outerjoin(), select_from(), or from_self() has been called
# — BEFORE any SQL ran, so EVERY eligible delete 500'd (even with zero
# drafts), on SQLite AND PostgreSQL. The fix uses an IN-(subquery) filter.
# This test reproduces the failing shape: an eligible workspace WITH draft
# transaction lines must delete successfully with an EMPTY 204 body.

def test_delete_regression_no_500_with_draft_lines(client, test_db_session):
    _register(client)
    org = _create_org(client, name="Delete Regression")
    acc = _accounts_by_code(client, org["id"])
    draft = _make_txn(client, org["id"], _balanced_lines(acc))  # draft WITH lines

    resp = _delete_org(client, org["id"], "Delete Regression")
    # The endpoint must succeed with 204 + empty body — never 500.
    assert resp.status_code == 204, resp.text
    assert resp.text == ""

    # The workspace and its workspace-scoped data are gone; the draft's lines
    # went with it (no orphans left behind).
    assert test_db_session.get(Organization, org["id"]) is None
    assert client.get(f"/organizations/{org['id']}").status_code == 404
    assert (
        test_db_session.query(Account)
        .filter(Account.organization_id == org["id"])
        .count()
        == 0
    )
    assert (
        test_db_session.query(TransactionLine)
        .filter(TransactionLine.transaction_id == draft["id"])
        .count()
        == 0
    )


# --- 11. Typed confirmation is required and validated server-side ------------

def test_typed_confirmation_required_and_validated_server_side(
    client, test_db_session
):
    _register(client)
    org = _create_org(client, name="Exact Name")
    acc = _accounts_by_code(client, org["id"])
    _make_txn(client, org["id"], _balanced_lines(acc))  # draft, still eligible

    # Missing confirmation -> 422 (pydantic), nothing deleted.
    resp = client.delete(f"/organizations/{org['id']}")
    assert resp.status_code == 422
    # Wrong name / wrong case -> 422 (whitespace padding is tolerated by the
    # service's strip(); the NAME itself must match exactly, case included).
    for bad in ("Wrong Name", "exact name"):
        resp = _delete_org(client, org["id"], bad)
        assert resp.status_code == 422, f"confirmation {bad!r} -> {resp.status_code}"
    assert test_db_session.get(Organization, org["id"]) is not None

    # Exact match works (see also test 10).
    resp = _delete_org(client, org["id"], "Exact Name")
    assert resp.status_code == 204, resp.text


# --- 12 + 13. Delete removes only own data and leaves no orphan rows ---------

def test_delete_removes_only_own_data_and_leaves_no_orphans(
    client, test_db_session
):
    from app.models.account import Account
    from app.models.transaction import Transaction, TransactionLine
    from app.models.user import User

    _register(client, "alice@example.com")
    a = _create_org(client, name="Deleted Org")
    b = _create_org(client, name="Survivor Org")

    # Org A: draft transaction + lines + a custom account (all deletable).
    acc_a = _accounts_by_code(client, a["id"])
    _make_txn(client, a["id"], _balanced_lines(acc_a))
    _custom_account(client, a["id"], code="9961")

    # Org B: posted history (protected, untouched by A's deletion).
    acc_b = _accounts_by_code(client, b["id"])
    _post_txn(client, b["id"], _make_txn(client, b["id"], _balanced_lines(acc_b))["id"])

    users_before = test_db_session.query(User).count()
    b_accounts_before = (
        test_db_session.query(Account)
        .filter(Account.organization_id == b["id"])
        .count()
    )

    assert _delete_org(client, a["id"], "Deleted Org").status_code == 204

    # A's dependent data is fully gone.
    assert test_db_session.get(Organization, a["id"]) is None
    assert (
        test_db_session.query(Account)
        .filter(Account.organization_id == a["id"])
        .count()
        == 0
    )
    assert (
        test_db_session.query(Transaction)
        .filter(Transaction.organization_id == a["id"])
        .count()
        == 0
    )
    assert (
        test_db_session.query(TransactionLine)
        .join(Transaction, Transaction.id == TransactionLine.transaction_id)
        .filter(Transaction.organization_id == a["id"])
        .count()
        == 0
    )
    assert (
        test_db_session.query(OrganizationMember)
        .filter(OrganizationMember.org_id == a["id"])
        .count()
        == 0
    )

    # No orphan rows: every remaining line's transaction exists, every
    # remaining transaction's org exists.
    orphan_lines = (
        test_db_session.query(TransactionLine)
        .outerjoin(Transaction, Transaction.id == TransactionLine.transaction_id)
        .filter(Transaction.id.is_(None))
        .count()
    )
    assert orphan_lines == 0
    orphan_txns = (
        test_db_session.query(Transaction)
        .outerjoin(Organization, Organization.id == Transaction.organization_id)
        .filter(Organization.id.is_(None))
        .count()
    )
    assert orphan_txns == 0

    # Org B and the user are untouched.
    assert test_db_session.get(Organization, b["id"]) is not None
    assert (
        test_db_session.query(Account)
        .filter(Account.organization_id == b["id"])
        .count()
        == b_accounts_before
    )
    assert test_db_session.query(User).count() == users_before
    assert b["id"] in [o["id"] for o in client.get("/organizations").json()]


# --- 14. Delete never touches user/learning/review/certificate data ----------

def test_delete_preserves_learning_review_certificate_data(client, test_db_session):
    from app.models.learning import Lesson

    _register(client, "alice@example.com")
    org = _create_org(client, name="Demo Org")
    acc = _accounts_by_code(client, org["id"])
    _make_txn(client, org["id"], _balanced_lines(acc))  # draft-only: eligible

    alice_id = test_db_session.get(Organization, org["id"]).owner_user_id
    lesson = test_db_session.query(Lesson).order_by(Lesson.position).first()
    question = lesson.questions[0]

    progress = LessonProgress(
        user_id=alice_id, lesson_id=lesson.id, status="in_progress"
    )
    attempt = Attempt(user_id=alice_id, lesson_id=lesson.id, question_id=question.id)
    attempt.organization_id = org["id"]  # the connector-style org reference
    review = ReviewItem(
        user_id=alice_id,
        question_id=question.id,
        due_at=datetime.now(timezone.utc),
    )
    certificate = Certificate(
        user_id=alice_id,
        course_slug="accounting-basics",
        credential_id="cred-test-0001",
        wording="completion",
        recipient_name="Alice",
    )
    test_db_session.add_all([progress, attempt, review, certificate])
    test_db_session.commit()
    progress_id, attempt_id = progress.id, attempt.id
    review_id, cert_id = review.id, certificate.id

    assert _delete_org(client, org["id"], "Demo Org").status_code == 204

    # The delete endpoint runs in its OWN session and clears the attempt's org
    # reference with a bulk update (synchronize_session=False), so this test
    # session's cached identity map is stale — expire everything to force a
    # fresh read of the actual DB state before asserting.
    test_db_session.expire_all()

    # Learner data survives; the attempt's nullable org reference is cleared.
    assert test_db_session.get(LessonProgress, progress_id) is not None
    kept_attempt = test_db_session.get(Attempt, attempt_id)
    assert kept_attempt is not None
    assert kept_attempt.organization_id is None
    assert test_db_session.get(ReviewItem, review_id) is not None
    kept_cert = test_db_session.get(Certificate, cert_id)
    assert kept_cert is not None
    assert kept_cert.credential_id == "cred-test-0001"

    # The user account itself is untouched.
    resp = client.get("/me")
    assert resp.status_code == 200
    assert resp.json()["email"] == "alice@example.com"


# --- 15. Existing org behavior unchanged (create/list/profile update) --------

def test_org_create_list_and_profile_update_unchanged(client):
    _register(client)
    org = _create_org(client, name="Normal Flow", is_demo=False)
    resp = client.get("/organizations")
    assert [o["id"] for o in resp.json()] == [org["id"]]
    resp = client.patch(
        f"/organizations/{org['id']}",
        json={"registered_address": "1 Main St", "fiscal_year_start_month": 4},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["registered_address"] == "1 Main St"
    assert body["fiscal_year_start_month"] == 4
    assert body["profile_completed"] is True





