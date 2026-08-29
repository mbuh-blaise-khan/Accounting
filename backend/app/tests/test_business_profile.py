"""Business Profile + fiscal-year period-math tests (Post-S9 session).

Covers the acceptance points:
1. A workspace can be created and used (posted to) with ALL Business Profile
   fields unset — no regression; fiscal_year_start_month defaults to 1.
2. The Business Profile fields are updated via the org PATCH endpoint, and
   blank input clears them back to None.
3. An invalid fiscal_year_start_month is rejected (422).
4. Trial-balance period math shifts the "opening" point when a non-January
   fiscal_year_start_month is set, and equals the calendar year when unset.
5. The pure fiscal-year-start helper is correct.
"""
from datetime import date

from app.services.trial_balance_service import _fiscal_year_start


def _register(client, email="biz@example.com", name="Biz"):
    return client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "supersecret123",
            "display_name": name,
            "language_preference": "en",
        },
    )


def _create_org(client, framework="OHADA", name="Biz Co"):
    r = client.post(
        "/organizations",
        json={"name": name, "framework": framework, "currency": "XAF", "is_demo": True},
    )
    assert r.status_code == 201, r.text
    return r.json()


def _get(client, org_id):
    r = client.get(f"/organizations/{org_id}")
    assert r.status_code == 200, r.text
    return r.json()


def _patch(client, org_id, **data):
    return client.patch(f"/organizations/{org_id}", json=data)


def _accounts_by_code(client, org_id):
    return {a["code"]: a for a in client.get(f"/accounts?organization_id={org_id}").json()}


def _post_txn(client, org_id, acc_d, acc_c, amount, description="entry"):
    r = client.post(
        "/transactions",
        json={
            "organization_id": org_id,
            "description": description,
            "lines": [
                {"account_id": acc_d["id"], "debit": amount, "credit": 0},
                {"account_id": acc_c["id"], "debit": 0, "credit": amount},
            ],
        },
    )
    assert r.status_code in (200, 201), r.text
    txn = r.json()
    p = client.post(f"/transactions/{txn['id']}/post?organization_id={org_id}")
    assert p.status_code == 200, p.text
    return txn


def _tb(client, org_id, **params):
    qs = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
    r = client.get(f"/trial-balance?organization_id={org_id}" + (f"&{qs}" if qs else ""))
    assert r.status_code == 200, r.text
    return r.json()


def _backdate_posted_at(test_db_session, txn_id, d: date):
    from app.models.transaction import Transaction

    row = test_db_session.get(Transaction, txn_id)
    row.posted_at = row.posted_at.replace(year=d.year, month=d.month, day=d.day)
    test_db_session.commit()


# --- 1) Created & usable with all profile fields unset ------------------------
def test_org_created_and_usable_with_all_profile_fields_unset(client):
    _register(client)
    org = _create_org(client)
    # New fields default: fiscal-year month = 1 (calendar year), others NULL.
    got = _get(client, org["id"])
    assert got["fiscal_year_start_month"] == 1
    assert got["registered_address"] is None
    assert got["rccm_number"] is None
    assert got["tax_id"] is None

    # Still fully usable: posting works exactly as before.
    acc = _accounts_by_code(client, org["id"])
    _post_txn(client, org["id"], acc["57"], acc["70"], 5000, "sale")
    tb = _tb(client, org["id"])
    assert tb["balanced"] is True
    assert float(tb["totals"]["closing_debit"]) == 5000.0


# --- 2) Business Profile fields can be updated via PATCH ----------------------
def test_business_profile_fields_can_be_updated_and_cleared(client):
    _register(client)
    org = _create_org(client)

    r = _patch(
        client,
        org["id"],
        registered_address="Yaoundé, Cameroon",
        tax_id="P12345678901N",
        rccm_number="RC/YA/2026/000123",
        fiscal_year_start_month=6,
    )
    assert r.status_code == 200, r.text
    got = r.json()
    assert got["registered_address"] == "Yaoundé, Cameroon"
    assert got["rccm_number"] == "RC/YA/2026/000123"
    assert got["tax_id"] == "P12345678901N"
    assert got["fiscal_year_start_month"] == 6

    # PATCH is partial: sending only one key must NOT clobber the others.
    r2 = _patch(client, org["id"], tax_id="")
    assert r2.status_code == 200, r2.text
    got2 = r2.json()
    assert got2["tax_id"] is None  # blank clears back to NULL
    assert got2["rccm_number"] == "RC/YA/2026/000123"  # untouched
    assert got2["fiscal_year_start_month"] == 6  # untouched


def test_invalid_fiscal_year_start_month_rejected(client):
    _register(client)
    org = _create_org(client)
    assert _patch(client, org["id"], fiscal_year_start_month=0).status_code == 422
    assert _patch(client, org["id"], fiscal_year_start_month=13).status_code == 422


# --- 5) Mandatory-step flag (profile_completed) --------------------------------
def test_new_org_is_not_profile_completed(client):
    """A brand-new workspace starts hard-gated (profile_completed=False)."""
    _register(client, email="gate@example.com", name="Gate")
    org = _create_org(client, name="GateCo")
    got = _get(client, org["id"])
    assert got["profile_completed"] is False


def test_saving_full_profile_completes_the_mandatory_step(client):
    _register(client, email="done@example.com", name="Done")
    org = _create_org(client, name="DoneCo")
    r = _patch(
        client,
        org["id"],
        registered_address="Bonanjo, Douala, Cameroon",
        rccm_number="RC/DLA/2024/B/1234",
        tax_id="M012345678901X",
        fiscal_year_start_month=1,
    )
    assert r.status_code == 200, r.text
    assert r.json()["profile_completed"] is True


def test_learner_save_without_registration_still_completes(client):
    """Learner exemption server-side: address + fiscal year are enough."""
    _register(client, email="learn@example.com", name="Learn")
    org = _create_org(client, name="LearnCo")
    r = _patch(
        client,
        org["id"],
        registered_address="Nkolbisson, Yaoundé, Cameroon",
        rccm_number="",  # learner: cleared
        tax_id="",  # learner: cleared
        fiscal_year_start_month=7,
    )
    assert r.status_code == 200, r.text
    got = r.json()
    assert got["profile_completed"] is True
    assert got["rccm_number"] is None
    assert got["tax_id"] is None


def test_partial_save_without_blocking_fields_does_not_complete(client):
    _register(client, email="part@example.com", name="Part")
    org = _create_org(client, name="PartCo")
    # Only a tax id — no registered_address, so the step is NOT complete.
    r = _patch(client, org["id"], tax_id="P123")
    assert r.status_code == 200, r.text
    assert r.json()["profile_completed"] is False

    # Adding the address completes it (fiscal month defaults to 1).
    r2 = _patch(client, org["id"], registered_address="Bafoussam, Cameroon")
    assert r2.status_code == 200, r2.text
    assert r2.json()["profile_completed"] is True


# --- 3) Fiscal-year start helper ----------------------------------------------
def test_fiscal_year_start_helper():
    assert _fiscal_year_start(date(2026, 3, 15), 6) == date(2025, 6, 1)
    assert _fiscal_year_start(date(2026, 7, 1), 6) == date(2026, 6, 1)
    assert _fiscal_year_start(date(2026, 3, 15), 1) == date(2026, 1, 1)
    assert _fiscal_year_start(date(2026, 1, 5), 6) == date(2025, 6, 1)
    assert _fiscal_year_start(date(2027, 1, 5), 6) == date(2026, 6, 1)


# --- 4) Trial Balance opening point shifts with fiscal-year start -------------
def test_trial_balance_opening_shifts_with_non_january_fiscal_year(client, test_db_session):
    """Deterministic scenario. A posting on 2025-12-01, an as-of of 2026-03-15.

    With default fiscal-year start (January): the fiscal year begins 2026-01-01,
    so the 2025-12-01 posting lands in OPENING.
    With fiscal_year_start_month=6: the fiscal year runs 2025-06-01 →
    2026-05-31, so the same posting is MOVEMENT (current fiscal year-to-date).
    """
    _register(client, email="fisc@example.com", name="Fisc")

    default_org = _create_org(client, name="CalendarOrg")
    acc = _accounts_by_code(client, default_org["id"])
    txn = _post_txn(client, default_org["id"], acc["57"], acc["70"], 1000, "dec sale")
    _backdate_posted_at(test_db_session, txn["id"], date(2025, 12, 1))

    shifted_org = _create_org(client, name="FiscalOrg")
    _patch(client, shifted_org["id"], fiscal_year_start_month=6)
    acc_s = _accounts_by_code(client, shifted_org["id"])
    txn_s = _post_txn(client, shifted_org["id"], acc_s["57"], acc_s["70"], 1000, "dec sale")
    _backdate_posted_at(test_db_session, txn_s["id"], date(2025, 12, 1))

    jan_tb = _tb(client, default_org["id"], **{"as_of": "2026-03-15"})
    jun_tb = _tb(client, shifted_org["id"], **{"as_of": "2026-03-15"})

    jan_cash = next(r for r in jan_tb["rows"] if r["code"] == "57")
    jun_cash = next(r for r in jun_tb["rows"] if r["code"] == "57")

    # Calendar year (unset): the pre-January posting is OPENING, no movement.
    assert float(jan_cash["opening_debit"]) == 1000.0
    assert float(jan_cash["movement_debit"]) == 0.0

    # June-start fiscal year: same posting is current-year MOVEMENT.
    assert float(jun_cash["opening_debit"]) == 0.0
    assert float(jun_cash["movement_debit"]) == 1000.0

    # Both still balance (closing Dr == Cr), and closing totals AGREE — only
    # the opening/movement split differs.
    assert jan_tb["balanced"] is True
    assert jun_tb["balanced"] is True
    assert float(jan_tb["totals"]["closing_debit"]) == float(jun_tb["totals"]["closing_debit"])


# --- 5) Business Profile Part 2: identity type, country, legal form ----------
# Acceptance points: OHADA country restricted to the 17 real member states
# (anything else rejected); IFRS accepts any valid ISO country; legal-form
# options differ correctly by framework; identity_type=learner skips RCCM/tax
# and may use the explicit NOT_APPLICABLE legal form; identity_type=
# registered_business requires RCCM + tax ID; framework is immutable after
# creation via ANY code path; existing pre-change orgs stay valid unset.

# The 17 OHADA member states (ISO 3166-1 alpha-2) — see identity_reference.py.
OHADA_CODES = {
    "BJ", "BF", "CM", "CF", "TD", "KM", "CG", "CI", "CD",
    "GA", "GN", "GW", "GQ", "ML", "NE", "SN", "TG",
}


def _org(client, email, name, framework="OHADA"):
    _register(client, email=email, name=name)
    return _create_org(client, framework=framework, name=name)


def test_identity_options_differ_by_framework(client):
    """GET /organizations/identity-options is the single source of truth."""
    _register(client, email="opts@example.com", name="Opts")
    ohada = client.get("/organizations/identity-options?framework=OHADA")
    assert ohada.status_code == 200, ohada.text
    ohada_ok = ohada.json()
    # ONLY the 17 member states.
    assert {c["code"] for c in ohada_ok["countries"]} == OHADA_CODES
    ohada_forms = {f["code"] for f in ohada_ok["legal_forms"]}
    expected_ohada = {"SARL", "SARLU", "SA", "SA_UNI", "SAS", "SASU", "SNC", "SCS", "GIE", "EI"}
    assert expected_ohada <= ohada_forms
    assert "LLC" not in ohada_forms

    ifrs = client.get("/organizations/identity-options?framework=IFRS")
    assert ifrs.status_code == 200, ifrs.text
    ifrs_ok = ifrs.json()
    assert len(ifrs_ok["countries"]) > 100  # full international list
    ifrs_forms = {f["code"] for f in ifrs_ok["legal_forms"]}
    assert ifrs_forms == {
        "SOLE_PROP", "PARTNERSHIP", "LLC", "LTD", "PLC", "CORPORATION", "NONPROFIT", "COOPERATIVE",
    }
    assert "SARL" not in ifrs_forms


def test_ohada_country_must_be_a_member_state(client):
    org = _org(client, "oh@example.com", "OhadaCo")
    # France / Nigeria are NOT OHADA member states -> rejected.
    for bad in ("FR", "NG"):
        r = _patch(client, org["id"], identity_type="unregistered_business", country=bad, legal_form="SARL")
        assert r.status_code == 422, (bad, r.text)
    # Case-insensitive: "cm" normalizes to the valid member code "CM".
    r = _patch(client, org["id"], identity_type="unregistered_business", country="cm", legal_form="SARL")
    assert r.status_code == 200, r.text
    assert r.json()["country"] == "CM"


def test_ifrs_accepts_any_valid_country_rejects_garbage(client):
    org = _org(client, "if@example.com", "IfrsCo", framework="IFRS")
    r = _patch(client, org["id"], identity_type="unregistered_business", country="FR", legal_form="SOLE_PROP")
    assert r.status_code == 200, r.text
    assert r.json()["country"] == "FR"
    # GB + LLC all work together; providing RCCM/tax keeps the
    # registered_business identity valid (that identity REQUIRES them).
    r2 = _patch(
        client, org["id"],
        identity_type="registered_business", country="GB", legal_form="LLC",
        rccm_number="RC/LON/12345", tax_id="GB123456789",
    )
    assert r2.status_code == 200, r2.text
    assert r2.json()["country"] == "GB"
    # "ZZ" is not a real ISO 3166-1 alpha-2 code.
    r3 = _patch(client, org["id"], country="ZZ")
    assert r3.status_code == 422, r3.text


def test_legal_form_valid_per_framework_and_not_applicable_learner_only(client):
    org = _org(client, "lf@example.com", "LegalCo")
    # LLC is not an OHADA form -> rejected.
    r = _patch(client, org["id"], identity_type="unregistered_business", country="CM", legal_form="LLC")
    assert r.status_code == 422, r.text
    # NOT_APPLICABLE is allowed ONLY for identity_type=learner.
    r2 = _patch(client, org["id"], identity_type="unregistered_business", country="CM", legal_form="NOT_APPLICABLE")
    assert r2.status_code == 422, r2.text
    r3 = _patch(
        client, org["id"],
        identity_type="learner", country="CM", legal_form="NOT_APPLICABLE",
        registered_address="Yaoundé, Cameroon",
    )
    assert r3.status_code == 200, r3.text
    assert r3.json()["profile_completed"] is True


def test_registered_business_requires_rccm_and_tax_id(client):
    org = _org(client, "reg@example.com", "RegCo")
    # Missing RCCM + tax ID -> 422 even though country + legal form are set.
    r = _patch(client, org["id"], identity_type="registered_business", country="CM", legal_form="SARL")
    assert r.status_code == 422, r.text
    r2 = _patch(
        client, org["id"],
        identity_type="registered_business", country="CM", legal_form="SARL",
        rccm_number="RC/DLA/2024/B/1234", tax_id="NIU:M012345678901X",
        registered_address="Bonanjo, Douala, Cameroon",
    )
    assert r2.status_code == 200, r2.text
    got = r2.json()
    assert got["identity_type"] == "registered_business"
    assert got["rccm_number"] == "RC/DLA/2024/B/1234"
    assert got["profile_completed"] is True


def test_unregistered_business_requires_legal_form_only(client):
    org = _org(client, "und@example.com", "UndCo")
    # Missing legal form -> 422.
    r = _patch(client, org["id"], identity_type="unregistered_business", country="CM")
    assert r.status_code == 422, r.text
    r2 = _patch(client, org["id"], identity_type="unregistered_business", country="CM", legal_form="SCS")
    assert r2.status_code == 200, r2.text
    got = r2.json()
    assert got["identity_type"] == "unregistered_business"
    assert got["rccm_number"] is None  # optional for this identity
    assert got["tax_id"] is None


def test_learner_skips_rccm_tax_and_allows_na_legal_form(client):
    org = _org(client, "learn2@example.com", "Learn2Co")
    # The backend does NOT hard-require country for a learner (that requirement
    # is enforced in the frontend form + frontend/src/utils/profile.js
    # missingIdentityFields, which demands country for EVERY identity) — so a
    # bare learner PATCH succeeds but does NOT complete the profile step.
    r = _patch(client, org["id"], identity_type="learner")
    assert r.status_code == 200, r.text
    assert r.json()["identity_type"] == "learner"
    assert r.json()["profile_completed"] is False
    # Full learner save: country + address + fiscal-month(+N/A legal form) —
    # no RCCM/tax needed.
    r2 = _patch(
        client, org["id"],
        identity_type="learner", country="CM", legal_form="NOT_APPLICABLE",
        registered_address="Nkolbisson, Yaoundé, Cameroon",
    )
    assert r2.status_code == 200, r2.text
    got = r2.json()
    assert got["identity_type"] == "learner"
    assert got["legal_form"] == "NOT_APPLICABLE"
    assert got["rccm_number"] is None and got["tax_id"] is None
    assert got["profile_completed"] is True


def test_framework_cannot_be_changed_via_api(client):
    org = _org(client, "fw@example.com", "FwCo")
    # OrganizationUpdate has NO framework field (deliberate), so a PATCH body
    # attempting to change it is simply not exposed: it is ignored and the org
    # keeps its framework.
    r = client.patch(f"/organizations/{org['id']}", json={"framework": "IFRS"})
    assert r.status_code == 200, r.text
    assert r.json()["framework"] == "OHADA"


def test_framework_immutability_guard_at_service_layer(client, test_db_session):
    """The belt-and-braces service guard rejects a framework change directly."""
    from fastapi import HTTPException

    from app.models.user import User
    from app.services import organization_service

    org = _org(client, "fwsvc@example.com", "FwSvcCo")
    user = test_db_session.query(User).filter(User.email == "fwsvc@example.com").one()
    raised = None
    try:
        organization_service.update_business_profile(
            db=test_db_session, user=user, org_id=org["id"], framework="IFRS"
        )
    except HTTPException as exc:
        raised = exc
    assert raised is not None
    assert raised.status_code == 422