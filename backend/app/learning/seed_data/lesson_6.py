"""Lesson 6 — The trial balance."""
LESSON = {
    "slug": "the-trial-balance",
    "position": 6,
    "title_en": "The trial balance",
    "title_fr": "La balance de vérification",
    "summary_en": "A single report listing every account's closing balance, with debits and credits that must always match.",
    "summary_fr": "Un rapport unique listant le solde de clôture de chaque compte, avec des débits et des crédits qui doivent toujours correspondre.",
    "sections": [
        {
            "position": 1,
            "body_en": "The trial balance takes every ledger account's balance and lists it in one table: debit balances in the debit column, credit balances in the credit column. Because every journal entry was balanced, the two totals must be equal.",
            "body_fr": "La balance de vérification reprend le solde de chaque compte du grand livre et le liste dans un tableau unique : les soldes débiteurs dans la colonne débit, les soldes créditeurs dans la colonne crédit. Comme chaque écriture de journal était équilibrée, les deux totaux doivent être égaux.",
        },
        {
            "position": 2,
            "heading_en": "Why it matters",
            "heading_fr": "Pourquoi c'est important",
            "body_en": "An unbalanced trial balance (debits ≠ credits) signals an error somewhere. A balanced one does not prove everything is perfect — an entry could have been posted to the wrong account — but it catches many mistakes. This app checks this for you automatically.",
            "body_fr": "Une balance déséquilibrée (débits ≠ crédits) signale une erreur quelque part. Une balance équilibrée ne prouve pas que tout est parfait — une écriture peut avoir été portée au mauvais compte — mais elle détecte beaucoup d'erreurs. Cette application le vérifie automatiquement pour vous.",
        },
    ],
    "questions": [
        {
            "position": 1,
            "kind": "mcq",
            "question_en": "If total debits do NOT equal total credits in the trial balance, it means…",
            "question_fr": "Si le total des débits n'est PAS égal au total des crédits dans la balance, cela signifie…",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "There is likely an error somewhere in the books", "text_fr": "Il y a probablement une erreur quelque part dans les livres", "is_correct": True},
                {"option_key": "B", "position": 2, "text_en": "The business is bankrupt", "text_fr": "L'entreprise est en faillite", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "It is normal and can be ignored", "text_fr": "C'est normal et on peut l'ignorer", "is_correct": False},
            ],
            "explanation_en": "The trial balance totals only match when every posted entry was balanced, so an inequality points to an error.",
            "explanation_fr": "Les totaux de la balance ne correspondent que si chaque écriture publiée était équilibrée ; une inégalité pointe donc vers une erreur.",
        },
        {
            "position": 2,
            "kind": "short_answer",
            "question_en": "In a correct trial balance, total ______ equal total credits.",
            "question_fr": "Dans une balance correcte, le total des ______ égale le total des crédits.",
            "short_answer_en": "debits",
            "short_answer_fr": "débits",
            "explanation_en": "Total debits must equal total credits in a balanced trial balance.",
            "explanation_fr": "Le total des débits doit être égal au total des crédits dans une balance équilibrée.",
        },
    ],
}