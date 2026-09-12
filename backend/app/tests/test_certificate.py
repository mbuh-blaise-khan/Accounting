"""Certificate + course-completion tests (Session 11 Part B1).

Covers:
1. Auth required for /learning/completion and /learning/certificate.
2. Not-eligible user: completed=False, certificate=None, POST -> 403.
3. Eligible user: certificate issued with the EXACT fixed wording; issuing
   twice is idempotent (same certificate id, no duplicate row).
4. A user who completes every lesson but has ONE wrong answer is NOT
   eligible (completion requires 100% correct, not merely attempted).
"""

from app.models.certificate import Certificate
from app.models.learning import Answer, Question


def _register(client, email="cert@example.com", name="Cert User"):
    r = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "supersecret123",
            "display_name": name,
            "language_preference": "en",
        },
    )
    assert r.status_code == 200, r.text
    login = client.post(
        "/auth/login", json={"email": email, "password": "supersecret123"}
    )
    assert login.status_code == 200, login.text


def _lessons(client):
    r = client.get("/learning/lessons")
    assert r.status_code == 200, r.text
    return r.json()


def _lesson(client, lesson_id):
    r = client.get(f"/learning/lessons/{lesson_id}")
    assert r.status_code == 200, r.text
    return r.json()


def _answer_map(db, lesson_id):
    """question_id -> correct payload, straight from the DB (test only)."""
    out = {}
    questions = db.query(Question).filter(Question.lesson_id == lesson_id).all()
    for q in questions:
        if q.kind == "mcq":
            correct = next(a for a in q.answers if a.is_correct)
            out[q.id] = {"option_key": correct.option_key}
        else:
            out[q.id] = {"text": q.short_answer_en or q.short_answer_fr}
    return out


def _complete_all_lessons(client, db):
    """Answer EVERY question in EVERY lesson with the correct answer."""
    for lesson in _lessons(client):
        detail = _lesson(client, lesson["id"])
        answers = _answer_map(db, detail["id"])
        for q in detail["questions"]:
            payload = {"lesson_id": detail["id"], "question_id": q["id"]}
            payload.update(answers[q["id"]])
            r = client.post("/learning/attempts", json=payload)
            assert r.status_code == 200, r.text
            assert r.json()["is_correct"] is True, (q["id"], r.text)


# --- 1) Authentication --------------------------------------------------------
def test_completion_and_certificate_require_auth(client):
    assert client.get("/learning/completion").status_code == 401
    assert client.post("/learning/certificate").status_code == 401


# --- 2) Not eligible ---------------------------------------------------------
def test_not_completed_user_cannot_issue_certificate(client, test_db_session):
    _register(client)
    r = client.get("/learning/completion")
    assert r.status_code == 200
    body = r.json()
    assert body["completed"] is False
    assert body["certificate"] is None

    r = client.post("/learning/certificate")
    assert r.status_code == 403, r.text


# --- 3) Eligible + idempotent ------------------------------------------------
def test_full_completion_issues_certificate_idempotently(client, test_db_session):
    _register(client)
    _complete_all_lessons(client, test_db_session)

    r = client.get("/learning/completion")
    assert r.status_code == 200
    body = r.json()
    assert body["completed"] is True
    assert body["certificate"] is None  # not issued yet

    first = client.post("/learning/certificate")
    assert first.status_code == 200, first.text
    cert = first.json()
    assert cert["wording"] == "Kinxta Docu Certificate of Completion"
    assert cert["course_slug"] == "accounting-basics"

    # GET now shows the certificate.
    r = client.get("/learning/completion")
    assert r.json()["certificate"]["id"] == cert["id"]

    # Idempotency: issuing again returns the SAME certificate (same id).
    second = client.post("/learning/certificate")
    assert second.status_code == 200
    assert second.json()["id"] == cert["id"]

    from app.models.certificate import Certificate

    count = test_db_session.query(Certificate).count()
    assert count == 1  # never a duplicate row


# --- 4) One wrong answer blocks the certificate ------------------------------
def test_one_wrong_answer_blocks_certificate(client, test_db_session):
    _register(client)
    lessons = _lessons(client)

    # Complete every lesson correctly EXCEPT one question in lesson 1.
    first_lesson = lessons[0]
    for lesson in lessons:
        detail = _lesson(client, lesson["id"])
        answers = _answer_map(test_db_session, detail["id"])
        questions = detail["questions"]
        if lesson["id"] == first_lesson["id"]:
            # Skip the LAST question here (we answer it wrongly below).
            questions = questions[:-1]
        for q in questions:
            payload = {"lesson_id": detail["id"], "question_id": q["id"]}
            payload.update(answers[q["id"]])
            r = client.post("/learning/attempts", json=payload)
            assert r.json()["is_correct"] is True, r.text

    detail = _lesson(client, first_lesson["id"])
    last = detail["questions"][-1]
    answers = _answer_map(test_db_session, detail["id"])
    wrong_payload = {"lesson_id": detail["id"], "question_id": last["id"]}
    if last["kind"] == "mcq":
        correct_key = answers[last["id"]]["option_key"]
        all_keys = [a["option_key"] for a in last["answers"]]
        wrong_payload["option_key"] = next(
            k for k in all_keys if k != correct_key
        )
    else:
        wrong_payload["text"] = "definitely-not-the-answer"
    r = client.post("/learning/attempts", json=wrong_payload)
    assert r.status_code == 200
    assert r.json()["is_correct"] is False

    # The whole course is otherwise done, but 100% is required.
    assert client.post("/learning/certificate").status_code == 403


# --- 5) B2 summary fields drive the certificate UI --------------------------
def test_completion_summary_fields_drive_the_certificate_ui(client, test_db_session):
    _register(client)
    total = len(_lessons(client))

    # Not started: 0/N, locked, no certificate.
    r = client.get("/learning/completion")
    assert r.status_code == 200
    body = r.json()
    assert body["total_lessons"] == total
    assert body["completed_lessons"] == 0
    assert body["completion_percentage"] == 0
    assert body["completed"] is False
    assert body["certificate"] is None
    assert body["certificate_status"] == "locked"

    # Fully correct everywhere: 100%, available but not yet issued.
    _complete_all_lessons(client, test_db_session)
    r = client.get("/learning/completion")
    body = r.json()
    assert body["completed_lessons"] == total
    assert body["completion_percentage"] == 100
    assert body["completed"] is True
    assert body["certificate"] is None
    assert body["certificate_status"] == "available"

    # After issuing: status flips to issued, certificate present.
    cert = client.post("/learning/certificate")
    assert cert.status_code == 200, cert.text
    body = client.get("/learning/completion").json()
    assert body["certificate_status"] == "issued"
    assert body["certificate"]["id"] == cert.json()["id"]


# --- Session 11 Part B3: public certificate verification ---------------------
# These tests pin the read-only public endpoint: no auth, privacy-safe output,
# valid/revoked/not-found behavior, secure credential-id lookup, and the
# hard rule that the sequential PK is NEVER a credential.


def _issue_certificate_for_public_tests(client, db):
    """Register + complete all lessons + issue; return the credential_id."""
    _register(client, email="pubcert@example.com", name="Pub Cert")
    _complete_all_lessons(client, db)
    r = client.post("/learning/certificate")
    assert r.status_code == 200, r.text
    return r.json()["credential_id"]


# 1) Public verification does NOT require authentication.
def test_public_verification_is_unauthenticated(client, test_db_session):
    cred_id = _issue_certificate_for_public_tests(client, test_db_session)
    # Fresh client = no cookies, no Authorization header.
    from starlette.testclient import TestClient
    from app.main import app
    anon = TestClient(app)
    r = anon.get(f"/learning/certificates/verify/{cred_id}")
    assert r.status_code == 200, r.text


# 2) Valid credential id returns the expected privacy-safe fields.
def test_public_verification_returns_privacy_safe_fields(client, test_db_session):
    cred_id = _issue_certificate_for_public_tests(client, test_db_session)
    r = client.get(f"/learning/certificates/verify/{cred_id}")
    assert r.status_code == 200
    body = r.json()
    assert body["credential_id"] == cred_id
    assert body["status"] == "valid"
    assert body["issuer"] == "Kinxta Docu"
    assert body["wording"] == "Kinxta Docu Certificate of Completion"
    assert body["course_title"] == "Accounting Basics"
    assert body["course_slug"] == "accounting-basics"
    assert body["recipient_name"] == "Pub Cert"
    assert body["issued_at"] is not None
    assert body["completed_at"] is not None
    assert body["verification_url"] is not None
    assert cred_id in body["verification_url"]


# 3) Invalid credential id returns the safe not-found response.
def test_public_verification_invalid_id_returns_404(client):
    r = client.get("/learning/certificates/verify/kinxta-doesnotexist999")
    assert r.status_code == 404
    # The 404 detail must not leak whether a related private user/workspace exists.
    assert "not found" in r.json()["detail"].lower()


# 4-7) Public response EXCLUDES email, internal id/user_id, workspace,
#       transaction, and lesson-answer data.
def test_public_verification_excludes_private_data(client, test_db_session):
    cred_id = _issue_certificate_for_public_tests(client, test_db_session)
    r = client.get(f"/learning/certificates/verify/{cred_id}")
    body = r.json()
    # The response carries NO private fields at all.
    forbidden = {"id", "user_id", "email", "password", "hashed_password",
                 "workspace_id", "organization_id", "transaction", "transactions",
                 "journal", "answers", "answer_key", "is_correct", "option_key",
                 "workspace_name", "transactions", "ledger", "account_id"}
    for key in forbidden:
        assert key not in body, f"private field '{key}' must not be public"


# 8) Valid status is represented correctly.
def test_public_verification_valid_status(client, test_db_session):
    cred_id = _issue_certificate_for_public_tests(client, test_db_session)
    r = client.get(f"/learning/certificates/verify/{cred_id}")
    assert r.json()["status"] == "valid"


# 9-10) Revoked status is represented correctly AND a revoked credential never
#         looks valid just because its id still exists.
def test_public_verification_revoked_status(client, test_db_session):
    cred_id = _issue_certificate_for_public_tests(client, test_db_session)
    # Revoke directly in the DB (no admin UI in this session).
    cert = test_db_session.query(Certificate).filter(
        Certificate.credential_id == cred_id).first()
    cert.status = "revoked"
    test_db_session.commit()

    r = client.get(f"/learning/certificates/verify/{cred_id}")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "revoked"
    # The word "revoked" must never appear as "valid".
    assert body["status"] != "valid"
    assert body["credential_id"] == cred_id  # still resolves
    assert body["recipient_name"] == "Pub Cert"  # snapshot retained


# 11-12) Credential lookup uses the SECURE public credential id; the sequential
#          integer PK is NEVER accepted as a credential (numeric-only input
#          cannot be a real credential since ours always start with 'kinxta-').
def test_public_verification_rejects_sequential_pk(client, test_db_session):
    cred_id = _issue_certificate_for_public_tests(client, test_db_session)
    # The real certificate's PK is a small integer; it must NOT verify.
    cert = test_db_session.query(Certificate).filter(
        Certificate.credential_id == cred_id).first()
    numeric_id = str(cert.id)
    r = client.get(f"/learning/certificates/verify/{numeric_id}")
    assert r.status_code == 404


# 13) Private authenticated certificate endpoints REMAIN protected.
def test_private_certificate_endpoints_still_require_auth(client):
    from starlette.testclient import TestClient
    from app.main import app
    anon = TestClient(app)
    assert anon.get("/learning/completion").status_code == 401
    assert anon.post("/learning/certificate").status_code == 401


# 14) The verification endpoint is read-only (GET only; no mutation).
def test_public_verification_is_read_only(client, test_db_session):
    cred_id = _issue_certificate_for_public_tests(client, test_db_session)
    # POST/PUT/PATCH/DELETE must not be allowed on the verify path.
    for method in ("post", "put", "patch", "delete"):
        r = getattr(client, method)(f"/learning/certificates/verify/{cred_id}")
        assert r.status_code in (405, 404), f"{method.upper()} should be disallowed"
