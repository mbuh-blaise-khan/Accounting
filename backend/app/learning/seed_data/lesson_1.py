"""Lesson 1 — What is accounting and why it matters."""
LESSON = {
    "slug": "what-is-accounting",
    "position": 1,
    "title_en": "What is accounting and why it matters",
    "title_fr": "Qu'est-ce que la comptabilité et pourquoi est-elle importante",
    "summary_en": "Accounting is the way a business keeps track of its money. Learn why every business — big or small — needs it.",
    "summary_fr": "La comptabilité est la façon dont une entreprise suit son argent. Découvrez pourquoi toute entreprise, grande ou petite, en a besoin.",
    "sections": [
        {
            "position": 1,
            "body_en": "Accounting is the language of business. It records what a business owns, what it owes, and what happens to its money over time. When you write down every sale and every purchase, you can look back and see clearly how the business is doing.",
            "body_fr": "La comptabilité est le langage des affaires. Elle enregistre ce qu'une entreprise possède, ce qu'elle doit et ce qu'il advient de son argent au fil du temps. Lorsque vous notez chaque vente et chaque achat, vous pouvez revenir en arrière et voir clairement comment va l'entreprise.",
        },
        {
            "position": 2,
            "heading_en": "Why it matters",
            "heading_fr": "Pourquoi c'est important",
            "body_en": "Without records, you cannot know if your business makes money or loses it. Good accounting helps you make better decisions, pay the right taxes, and show banks or investors exactly how the business is doing.",
            "body_fr": "Sans registres, vous ne pouvez pas savoir si votre entreprise gagne de l'argent ou en perd. Une bonne comptabilité vous aide à prendre de meilleures décisions, à payer les bons impôts et à montrer aux banques ou aux investisseurs exactement comment va l'entreprise.",
        },
        {
            "position": 3,
            "heading_en": "One golden rule",
            "heading_fr": "Une règle d'or",
            "body_en": "In accounting, every single recorded operation is called a transaction. This app posts each transaction as a double entry — which you will learn in the next lessons. For now, remember: accounting turns real events into numbers you can trust.",
            "body_fr": "En comptabilité, chaque opération enregistrée s'appelle une transaction. Cette application enregistre chaque transaction en partie double — vous l'apprendrez dans les prochaines leçons. Pour l'instant, retenez ceci : la comptabilité transforme des événements réels en chiffres fiables.",
        },
    ],
    "questions": [
        {
            "position": 1,
            "kind": "mcq",
            "question_en": "What is the main purpose of accounting for a business?",
            "question_fr": "Quel est le principal rôle de la comptabilité pour une entreprise ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "To keep track of the business's money and performance", "text_fr": "Suivre l'argent et la performance de l'entreprise", "is_correct": True},
                {"option_key": "B", "position": 2, "text_en": "To decorate the office with numbers", "text_fr": "Décorer le bureau avec des chiffres", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "To replace the need for a bank account", "text_fr": "Remplacer le besoin d'un compte bancaire", "is_correct": False},
            ],
            "explanation_en": "Accounting records what the business owns, owes, and earns so its owners see the real picture and make good decisions.",
            "explanation_fr": "La comptabilité enregistre ce que l'entreprise possède, doit et gagne, afin que ses dirigeants voient la réalité et prennent de bonnes décisions.",
            # Session 11 Part C1 — learner-safe correction (returned ONLY after a
            # submitted answer) + the section of THIS lesson to review. It states
            # what is right without echoing the correct option or its text.
            "correction_en": "Accounting exists to record what the business owns, owes and earns, so it can be measured and managed.",
            "correction_fr": "La comptabilité sert à enregistrer ce que l'entreprise possède, doit et gagne, afin de pouvoir le mesurer et le piloter.",
            "remediation_section_position": 2,
        },
        {
            "position": 2,
            "kind": "mcq",
            "question_en": "A 'transaction' in accounting is…",
            "question_fr": "Une « transaction » en comptabilité est…",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "A real event that is recorded in the books", "text_fr": "Un événement réel enregistré dans les livres", "is_correct": True},
                {"option_key": "B", "position": 2, "text_en": "A bank employee's job title", "text_fr": "Le titre d'un employé de banque", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "A type of tax", "text_fr": "Un type d'impôt", "is_correct": False},
            ],
            "explanation_en": "A transaction is a real business event — a sale, a purchase, a payment — that gets recorded in the accounting books.",
            "explanation_fr": "Une transaction est un événement réel de l'entreprise — une vente, un achat, un paiement — qui est enregistré dans les livres comptables.",
            "correction_en": "A transaction is a real business event — a sale, a purchase, a payment — written into the books.",
            "correction_fr": "Une transaction est un événement réel de l'entreprise — une vente, un achat, un paiement — inscrit dans les livres.",
            "remediation_section_position": 3,
        },
    ],
}