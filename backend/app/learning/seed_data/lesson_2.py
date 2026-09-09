"""Lesson 2 — The accounting equation."""
LESSON = {
    "slug": "the-accounting-equation",
    "position": 2,
    "title_en": "The accounting equation",
    "title_fr": "L'équation comptable",
    "summary_en": "Assets = Liabilities + Equity. This simple equation is the foundation of every balance sheet you will ever see.",
    "summary_fr": "Actif = Passif + Capitaux propres. Cette équation simple est le fondement de tout bilan que vous verrez.",
    "sections": [
        {
            "position": 1,
            "body_en": "Everything a business owns is called an ASSET: cash, stock, equipment, money owed by customers. Everything the business owes to others is a LIABILITY: loans, unpaid supplier bills. What is left for the owners is EQUITY.",
            "body_fr": "Tout ce qu'une entreprise possède s'appelle un ACTIF : la trésorerie, les stocks, le matériel, l'argent dû par les clients. Tout ce que l'entreprise doit à d'autres est un PASSIF : emprunts, factures fournisseurs impayées. Ce qui reste pour les propriétaires, ce sont les CAPITAUX PROPRES.",
        },
        {
            "position": 2,
            "heading_en": "The equation",
            "heading_fr": "L'équation",
            "body_en": "The equation is always: Assets = Liabilities + Equity. If a business has 100,000 FCFA of assets and owes 30,000 FCFA, the owners' share is 70,000 FCFA. The two sides must always balance.",
            "body_fr": "L'équation est toujours : Actif = Passif + Capitaux propres. Si une entreprise a 100 000 FCFA d'actif et doit 30 000 FCFA, la part des propriétaires est de 70 000 FCFA. Les deux côtés doivent toujours être équilibrés.",
        },
        {
            "position": 3,
            "heading_en": "Why it never breaks",
            "heading_fr": "Pourquoi elle ne se casse jamais",
            "body_en": "Every double-entry transaction keeps this equation in balance. Buy stock with cash? Cash goes down, stock goes up — assets stay balanced. Borrow money? Cash goes up and liabilities go up by the same amount.",
            "body_fr": "Chaque transaction en partie double maintient cette équation en équilibre. Acheter des stocks en espèces ? La trésorerie baisse, les stocks montent — l'actif reste équilibré. Emprunter de l'argent ? La trésorerie monte et le passif monte du même montant.",
        },
    ],
    "questions": [
        {
            "position": 1,
            "kind": "mcq",
            "question_en": "A business owns 200,000 FCFA of assets and owes 50,000 FCFA. What is the equity?",
            "question_fr": "Une entreprise possède 200 000 FCFA d'actif et doit 50 000 FCFA. Quel est le montant des capitaux propres ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "150,000 FCFA", "text_fr": "150 000 FCFA", "is_correct": True},
                {"option_key": "B", "position": 2, "text_en": "250,000 FCFA", "text_fr": "250 000 FCFA", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "50,000 FCFA", "text_fr": "50 000 FCFA", "is_correct": False},
            ],
            "explanation_en": "Assets = Liabilities + Equity, so Equity = 200,000 - 50,000 = 150,000 FCFA.",
            "explanation_fr": "Actif = Passif + Capitaux propres, donc Capitaux propres = 200 000 - 50 000 = 150 000 FCFA.",
        },
        {
            "position": 2,
            "kind": "short_answer",
            "question_en": "Complete the equation: Assets = Liabilities + ______",
            "question_fr": "Complétez l'équation : Actif = Passif + ______",
            "short_answer_en": "equity",
            "short_answer_fr": "capitaux propres",
            "explanation_en": "The full equation is Assets = Liabilities + Equity.",
            "explanation_fr": "L'équation complète est : Actif = Passif + Capitaux propres.",
        },
        {
            "position": 3,
            "kind": "mcq",
            "question_en": "A business borrows 10,000 FCFA from the bank in cash. What happens?",
            "question_fr": "Une entreprise emprunte 10 000 FCFA à la banque en espèces. Que se passe-t-il ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "Cash (asset) goes up by 10,000 and the loan (liability) goes up by 10,000", "text_fr": "La trésorerie (actif) augmente de 10 000 et l'emprunt (passif) augmente de 10 000", "is_correct": True},
                {"option_key": "B", "position": 2, "text_en": "Cash goes up and equity goes down", "text_fr": "La trésorerie augmente et les capitaux propres baissent", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "Nothing changes in the books", "text_fr": "Rien ne change dans les livres", "is_correct": False},
            ],
            "explanation_en": "Both sides of the equation grow by the same amount: assets (cash) +10,000 and liabilities (loan) +10,000 — still balanced.",
            "explanation_fr": "Les deux côtés de l'équation augmentent du même montant : actif (trésorerie) +10 000 et passif (emprunt) +10 000 — toujours équilibré.",
        },
    ],
}