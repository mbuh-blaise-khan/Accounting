"""Learner-facing feedback copy for the answer-submission response (Session 11 Part C1).

This module holds ONLY the platform's own generic UI phrasing, localized in
English and French, so the answer-submission endpoint can reply in the
learner's language without shipping duplicated UI strings:

- ``encouragement``  — optional next-step encouragement after a CORRECT answer.
- ``action_label``   — the label of the optional remediation action
  ("Review this concept" / "Revoir ce concept").

Accounting substance is deliberately NOT here. The concept explanation and the
plain-language correction are authored per question in the illustrative seed
content (app/learning/seed_data/*.py) and stored on the question row, so they
stay reviewable, bilingual and versioned with the lesson they belong to.

Nothing in this module is a professional, legal or accreditation claim: it is
platform copy ("keep going", "review this concept"), never accounting advice.
"""

#: The languages the learning engine can answer in (mirrors the user model's
#: LanguagePreference enum; 'pidgin' and others are future scope).
SUPPORTED_LANGUAGES = ("en", "fr")

#: Generic, non-accounting platform copy, keyed by language.
COPY: dict[str, dict[str, str]] = {
    "en": {
        "encouragement": "Well done — keep going: the next lesson builds on this idea.",
        "action_label": "Review this concept",
    },
    "fr": {
        "encouragement": (
            "Bien joué — continuez : la leçon suivante s'appuie sur cette idée."
        ),
        "action_label": "Revoir ce concept",
    },
}

DEFAULT_LANGUAGE = "en"


def resolve_language(preference: str | None) -> str:
    """Normalise a language preference/parameter to a supported code.

    Accepts either the user's stored ``language_preference`` or an explicit
    ``lang`` request value. Anything unknown (None, 'pidgin', '', 'EN', ...)
    falls back to the default so the endpoint never fails on language.
    """
    if isinstance(preference, str):
        code = preference.strip().lower()[:2]
        if code in SUPPORTED_LANGUAGES:
            return code
    return DEFAULT_LANGUAGE


def encouragement(lang: str) -> str:
    """Next-step encouragement (shown only after a correct answer)."""
    return COPY[resolve_language(lang)]["encouragement"]


def action_label(lang: str) -> str:
    """Localized label for the remediation action, e.g. 'Review this concept'."""
    return COPY[resolve_language(lang)]["action_label"]
