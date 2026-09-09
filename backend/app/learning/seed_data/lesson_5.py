"""Lesson 5 — From journal to ledger."""
LESSON = {
    "slug": "journal-to-ledger",
    "position": 5,
    "title_en": "From journal to ledger",
    "title_fr": "Du journal au grand livre",
    "summary_en": "Once a transaction is in the journal, its amounts are 'posted' into individual ledger accounts — one page per account.",
    "summary_fr": "Une fois une transaction au journal, ses montants sont « reportés » dans les comptes individuels du grand livre — une page par compte.",
    "sections": [
        {
            "position": 1,
            "body_en": "The journal is in date order, but when you need to know the balance of ONE account — say, Cash — you do not want to scan the whole journal. The ledger solves this: each account has its own page, and every journal line is POSTED there.",
            "body_fr": "Le journal est dans l'ordre des dates, mais lorsque vous avez besoin de connaître le solde d'UN seul compte — disons la Trésorerie — vous ne voulez pas parcourir tout le journal. Le grand livre résout cela : chaque compte a sa propre page, et chaque ligne de journal y est REPORTÉE.",
        },
        {
            "position": 2,
            "heading_en": "How posting works",
            "heading_fr": "Comment fonctionne le report",
            "body_en": "Each debit in the journal becomes a debit movement in the ledger account; each credit becomes a credit movement. After all postings, each account shows its balance. This app does this automatically — open any account's ledger from the Trial Balance and you see its full history.",
            "body_fr": "Chaque débit du journal devient un mouvement au débit dans le compte du grand livre ; chaque crédit devient un mouvement au crédit. Après tous les reports, chaque compte affiche son solde. Cette application le fait automatiquement — ouvrez le grand livre de n'importe quel compte depuis la Balance et vous verrez tout son historique.",
        },
    ],
    "questions": [
        {
            "position": 1,
            "kind": "mcq",
            "question_en": "What is the main difference between the journal and the ledger?",
            "question_fr": "Quelle est la principale différence entre le journal et le grand livre ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "The journal is chronological; the ledger groups movements by account", "text_fr": "Le journal est chronologique ; le grand livre regroupe les mouvements par compte", "is_correct": True},
                {"option_key": "B", "position": 2, "text_en": "The journal is only for cash, the ledger only for sales", "text_fr": "Le journal est réservé à la trésorerie, le grand livre aux ventes", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "There is no difference", "text_fr": "Il n'y a aucune différence", "is_correct": False},
            ],
            "explanation_en": "Same transactions, two views: the journal tells you WHEN things happened; the ledger tells you the balance of each account.",
            "explanation_fr": "Mêmes transactions, deux vues : le journal dit QUAND les choses sont arrivées ; le grand livre dit le solde de chaque compte.",
        },
        {
            "position": 2,
            "kind": "short_answer",
            "question_en": "Each journal line is 'posted' to an individual ledger ______(page/account/section).",
            "question_fr": "Chaque ligne de journal est « reportée » dans un ______ individuel du grand livre (compte/page/section).",
            "short_answer_en": "account",
            "short_answer_fr": "compte",
            "explanation_en": "The ledger keeps one account per page, and each journal line is posted to its matching account.",
            "explanation_fr": "Le grand livre conserve un compte par page, et chaque ligne de journal est reportée dans le compte correspondant.",
        },
    ],
}