"""Lesson 4 — Recording a transaction (journal entries), with the PRACTICE
connector: a correct answer posts a real balanced transaction into the
user's demo workspace (Learn Mode -> Practice Mode)."""
LESSON = {
    "slug": "journal-entries",
    "position": 4,
    "title_en": "Recording a transaction (journal entries)",
    "title_fr": "Enregistrer une opération (écritures de journal)",
    "summary_en": "The journal is the diary of the business: every transaction, written in the correct double-entry form, in date order.",
    "summary_fr": "Le journal est le journal intime de l'entreprise : chaque transaction, écrite sous la forme correcte de la partie double, dans l'ordre des dates.",
    "sections": [
        {
            "position": 1,
            "body_en": "The journal is where every transaction is first written down. Each journal entry shows the date, a short description, the account(s) to debit, the account(s) to credit, and the amounts. It is the first stop on a transaction's journey through the books.",
            "body_fr": "Le journal est l'endroit où chaque transaction est d'abord écrite. Chaque écriture de journal indique la date, une courte description, le ou les comptes à débiter, le ou les comptes à créditer, et les montants. C'est la première étape du voyage d'une transaction dans les livres.",
        },
        {
            "position": 2,
            "heading_en": "How to write one",
            "heading_fr": "Comment en écrire une",
            "body_en": "Example: you sell goods for 25,000 FCFA and receive cash immediately. Debit Cash 25,000 (the asset increases) and credit Sales 25,000 (the revenue increases). Left side = debits, right side = credits. Total debits must equal total credits.",
            "body_fr": "Exemple : vous vendez des marchandises pour 25 000 FCFA et recevez l'argent immédiatement. Débit de la Trésorerie 25 000 (l'actif augmente) et crédit des Ventes 25 000 (le produit augmente). Côté gauche = débits, côté droit = crédits. Le total des débits doit être égal au total des crédits.",
        },
        {
            "position": 3,
            "heading_en": "Try it for real",
            "heading_fr": "Essayez pour de vrai",
            "body_en": "The question below is special: answer it correctly and this app will actually POST the transaction into your demo workspace. Then open your Journal, Ledger, and Trial Balance to see it flow through the whole accounting cycle.",
            "body_fr": "La question ci-dessous est spéciale : répondez-y correctement et cette application va réellement PUBLIER la transaction dans votre espace de démonstration. Ouvrez ensuite votre Journal, votre Grand livre et votre Balance pour la voir circuler dans tout le cycle comptable.",
        },
    ],
    "questions": [
        {
            "position": 1,
            "kind": "mcq",
            "question_en": "You sell goods for 25,000 FCFA and the customer pays you immediately in cash. Which journal entry is correct?",
            "question_fr": "Vous vendez des marchandises pour 25 000 FCFA et le client vous paie immédiatement en espèces. Quelle écriture de journal est correcte ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "Debit Cash 25,000 / Credit Sales 25,000", "text_fr": "Débit Trésorerie 25 000 / Crédit Ventes 25 000", "is_correct": True},
                {"option_key": "B", "position": 2, "text_en": "Debit Sales 25,000 / Credit Cash 25,000", "text_fr": "Débit Ventes 25 000 / Crédit Trésorerie 25 000", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "Debit Cash 25,000 / Credit Capital 25,000", "text_fr": "Débit Trésorerie 25 000 / Crédit Capital 25 000", "is_correct": False},
                {"option_key": "D", "position": 4, "text_en": "Credit Cash 25,000 / Credit Sales 25,000", "text_fr": "Crédit Trésorerie 25 000 / Crédit Ventes 25 000", "is_correct": False},
            ],
            "explanation_en": "Cash increases (an asset, debited) and Sales revenue increases (credited). The entry is balanced: 25,000 debited = 25,000 credited.",
            "explanation_fr": "La trésorerie augmente (un actif, débitée) et les Ventes augmentent (un produit, créditées). L'écriture est équilibrée : 25 000 de débit = 25 000 de crédit.",
            "correction_en": "Write the entry from the movement: the cash received is debited and the sales revenue is credited, for the same 25,000 — debits equal credits.",
            "correction_fr": "Écrivez l'écriture à partir du mouvement : la trésorerie reçue est débitée et le produit des ventes est crédité, pour le même montant de 25 000 — débits égaux aux crédits.",
            "remediation_section_position": 2,
            # PRACTICE CONNECTOR: a correct answer posts this exact cash sale
            # into the user's demo workspace (Learn -> Practice).
            "posts_demo_transaction": True,
            "practice_amount": 25000,
        },
        {
            "position": 2,
            "kind": "mcq",
            "question_en": "What is the purpose of the journal?",
            "question_fr": "Quel est le rôle du journal ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "It is where every transaction is first recorded in date order", "text_fr": "C'est là que chaque transaction est enregistrée pour la première fois, dans l'ordre des dates", "is_correct": True},
                {"option_key": "B", "position": 2, "text_en": "It replaces the bank statement", "text_fr": "Il remplace le relevé bancaire", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "It is only used at the end of the year", "text_fr": "Il n'est utilisé qu'en fin d'année", "is_correct": False},
            ],
            "explanation_en": "The journal is the chronological first record of every transaction, before the amounts are posted to ledger accounts.",
            "explanation_fr": "Le journal est la première trace chronologique de chaque transaction, avant que les montants ne soient reportés dans les comptes du grand livre.",
            "correction_en": "The journal is the first, chronological record of every transaction, in date order.",
            "correction_fr": "Le journal est la première trace de chaque opération, dans l'ordre chronologique des dates.",
            "remediation_section_position": 1,
        },
    ],
}