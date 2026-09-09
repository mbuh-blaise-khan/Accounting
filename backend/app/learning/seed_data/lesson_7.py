"""Lesson 7 — Reading a basic financial statement."""
LESSON = {
    "slug": "reading-financial-statements",
    "position": 7,
    "title_en": "Reading a basic financial statement",
    "title_fr": "Lire un état financier de base",
    "summary_en": "The final stop: a basic income statement and balance sheet that summarize everything you have learned.",
    "summary_fr": "La dernière étape : un compte de résultat et un bilan de base qui résument tout ce que vous avez appris.",
    "sections": [
        {
            "position": 1,
            "body_en": "At the end of a period, the business summarizes everything into two key statements. The INCOME STATEMENT shows revenue minus expenses, giving the profit or loss. The BALANCE SHEET (Statement of Financial Position) shows the accounting equation in real life: assets on one side, liabilities plus equity on the other.",
            "body_fr": "À la fin d'une période, l'entreprise résume tout dans deux états clés. Le COMPTE DE RÉSULTAT présente les produits moins les charges, donnant le bénéfice ou la perte. Le BILAN (état de la situation financière) montre l'équation comptable en vrai : l'actif d'un côté, le passif plus les capitaux propres de l'autre.",
        },
        {
            "position": 2,
            "heading_en": "How to read them",
            "heading_fr": "Comment les lire",
            "body_en": "For the income statement: a positive net result is a profit, a negative one is a loss. For the balance sheet: check that assets equal liabilities plus equity. If they do, the statements are consistent with the double entry you learned.",
            "body_fr": "Pour le compte de résultat : un résultat net positif est un bénéfice, un résultat négatif est une perte. Pour le bilan : vérifiez que l'actif est égal au passif plus les capitaux propres. Si c'est le cas, les états sont cohérents avec la partie double que vous avez apprise.",
        },
        {
            "position": 3,
            "heading_en": "You built all of this",
            "heading_fr": "Vous avez construit tout cela",
            "body_en": "In this app, every statement is generated FROM your posted transactions — nothing is entered by hand. Post a sale in the journal and it appears in the ledger, the trial balance, and the statements. That is the whole accounting cycle you just learned.",
            "body_fr": "Dans cette application, chaque état est généré À PARTIR de vos transactions publiées — rien n'est saisi à la main. Publiez une vente au journal et elle apparaît dans le grand livre, la balance et les états financiers. C'est tout le cycle comptable que vous venez d'apprendre.",
        },
    ],
    "questions": [
        {
            "position": 1,
            "kind": "mcq",
            "question_en": "A business has revenue of 500,000 FCFA and expenses of 350,000 FCFA. What is its net result?",
            "question_fr": "Une entreprise a des produits de 500 000 FCFA et des charges de 350 000 FCFA. Quel est son résultat net ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "A profit of 150,000 FCFA", "text_fr": "Un bénéfice de 150 000 FCFA", "is_correct": True},
                {"option_key": "B", "position": 2, "text_en": "A loss of 350,000 FCFA", "text_fr": "Une perte de 350 000 FCFA", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "A profit of 500,000 FCFA", "text_fr": "Un bénéfice de 500 000 FCFA", "is_correct": False},
            ],
            "explanation_en": "Revenue 500,000 - Expenses 350,000 = Profit 150,000 FCFA.",
            "explanation_fr": "Produits 500 000 - Charges 350 000 = Bénéfice 150 000 FCFA.",
        },
        {
            "position": 2,
            "kind": "mcq",
            "question_en": "A balance sheet is only consistent if…",
            "question_fr": "Un bilan n'est cohérent que si…",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "Assets equal liabilities plus equity", "text_fr": "L'actif est égal au passif plus les capitaux propres", "is_correct": True},
                {"option_key": "B", "position": 2, "text_en": "Revenue is higher than last year", "text_fr": "Les produits sont supérieurs à l'année dernière", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "Assets minus equity is zero", "text_fr": "L'actif moins les capitaux propres est nul", "is_correct": False},
            ],
            "explanation_en": "The balance sheet is the accounting equation in real life: Assets = Liabilities + Equity.",
            "explanation_fr": "Le bilan est l'équation comptable en vrai : Actif = Passif + Capitaux propres.",
        },
    ],
}