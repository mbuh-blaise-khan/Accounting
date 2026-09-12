"""Certificate + course-completion tests (Session 11 Part B1).

Covers:
1. Auth required for /learning/completion and /learning/certificate.
2. Not-eligible user: completed=False, certificate=None, POST -> 403.
3. Eligible user: certificate issued with the EXACT fixed wording; issuing
   twice is idempotent (same certificate id, no duplicate row).
4. A user who completes every lesson but has ONE wrong answer is NOT
   eligible (completion requires 100% correct, not merely attempted).
"""

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
