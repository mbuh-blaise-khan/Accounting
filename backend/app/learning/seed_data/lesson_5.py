"""Lesson 5 - From journal to ledger (grand livre), and how posting works.

Expanded IN PLACE (same slug "journal-to-ledger", same curriculum position 5,
same EN/FR titles). The two ORIGINAL questions keep their positions (1, 2),
their question ids, answer ids, option keys, correct answers, accepted
short-answer texts, explanations and corrections, so historical attempts,
progress rows, review cards, current mastery and certificate eligibility are
untouched. The seed only INSERTs and UPDATEs - it never deletes - so nothing a
historical row points at can vanish. `attempts.selected_answer_id` is a foreign
key to `answers.id`, so a historic attempt records WHICH ANSWER ROW was picked,
never a display index: stored rows may never be reordered or removed.

SCOPE - this lesson is DISTINCT from its neighbours:
  Lesson 4 = HOW a business event becomes a dated, narrated, BALANCED journal
             entry (documents, dates, narrations, Dr/Cr columns);
  Lesson 5 = WHAT HAPPENS NEXT: each balanced journal line is POSTED into its
             own ledger account (one page per account), where running balances
             build up - the T-account, debit vs credit balances, reading one
             account, and fixing a posting with a new correcting entry;
  Lesson 6 = the trial balance (all closing balances in one table);
  Lesson 7 = reading the income statement and the balance sheet.
Lesson 5 never teaches the trial-balance totals test as its own topic and never
teaches statements - those stay reserved for Lessons 6 and 7.

SCENARIO: "Manka'a Provisions" - the same neighbourhood food shop in Bamenda,
Cameroon used in Lessons 1-4, so the whole course follows one continuous
business (XAF/FCFA, zero decimals, per project convention).

ANSWER-POSITION INTEGRITY: the new closed-ended questions deliberately place the
correct option at DIFFERENT authored positions so the answer is never revealed
by layout alone, and this lesson is registered in the engine's deterministic
display-order gate (`_OPTION_ORDER_LESSON_SLUGS` in app/learning/service.py),
which permutes the SERVED option order from the immutable question/answer ids.
The gate is safe here because no question in this lesson asks the learner to
read options IN a meaningful order: every option list is a set of alternative
candidate balances, statements or postings. The order that matters (debit side
vs credit side, journal vs ledger) lives INSIDE each option's text, which the
permutation never touches. Grading is unaffected: the server resolves the
submitted `option_key` to its Answer row by id.

NO PRACTICE CONNECTOR: this lesson carries no `posts_demo_transaction`
question. The Learn->Practice connector lives ONLY on Lesson 4 position 1 and
is untouched by this expansion.

REFERENCES: (a) globally recognised, freely-verifiable authoritative accounting
bodies - cited by name, standard title and URL, with NO copyrighted text
reproduced; (b) clearly-labelled OPTIONAL academic reading. UBa and FEMS are
named only as the institutions of the cited authors - NO endorsement by any
institution is claimed or implied. Nothing here states or implies that
completing this lesson or the course makes anyone a professional or regulated
accountant.
"""
LESSON = {
    "slug": "journal-to-ledger",
    "position": 5,
    "title_en": "From journal to ledger",
    "title_fr": "Du journal au grand livre",
    "summary_en": "Once a balanced journal entry exists, each line is posted into its own ledger account.",
    "summary_fr": "Une fois qu'une ecriture equilibree existe, chaque ligne est reportee dans son propre compte.",
    "sections": [
        {
            "position": 1,
            "heading_en": "What you will learn",
            "heading_fr": "Ce que vous allez apprendre",
            "body_en": "By the end of this lesson you will be able to: explain journal vs ledger; post each balanced journal line to the right account; read a T-account balance; say which accounts carry debit or credit balances; follow Friday at Manka'a Provisions; post Saturday yourself; fix a posting error with a new entry.\n\nBEFORE YOU START: finish Lesson 4 first - you can read a source document and a balanced journal entry (debit + credit). Simple adding and subtracting is enough. Nothing to install - works on a phone.\n\nTHE SHOP: Manka'a Provisions, the same food shop in Bamenda as Lessons 1-4. Amounts in XAF/FCFA, zero decimals.\n\nAN HONEST PROMISE: this course teaches accounting. It does NOT make you an accountant - see the last section.",
            "body_fr": "A la fin de cette lecon, vous saurez : expliquer journal contre grand livre ; reporter chaque ligne equilibree dans le bon compte ; lire le solde d'un compte en T ; dire quels comptes portent un solde debiteur ou crediteur ; suivre vendredi chez Manka'a Provisions ; reporter samedi vous-meme ; corriger une erreur par une nouvelle ecriture.\n\nAVANT DE COMMENCER : terminez d'abord la Lecon 4 - vous savez lire une piece justificative et une ecriture equilibree (debit + credit). De simples additions suffisent. Rien a installer - fonctionne sur un telephone.\n\nLA BOUTIQUE : Manka'a Provisions, la meme boutique a Bamenda que dans les Lecons 1 a 4. Montants en XAF/FCFA, sans decimales.\n\nUNE PROMESSE HONNETE : ce cours enseigne la comptabilite. Il ne fait PAS de vous un comptable - voir la derniere section.",
        },
        {
            "position": 2,
            "heading_en": "Two views of the same truth",
            "heading_fr": "Deux vues de la meme verite",
            "body_en": "The JOURNAL is the diary: every balanced entry in date order. Ask WHEN something happened and it answers. Ask HOW MUCH cash we hold now, or HOW MUCH we still owe the rice supplier, and the journal is painful: cash movements are scattered across dozens of dated entries. The LEDGER is the second view: ONE PAGE PER ACCOUNT. All Cash movements on the Cash page, all Supplier movements on the Supplier page. Same events, organised by account. In this app the ledger builds itself from your posted journal.",
            "body_fr": "Le JOURNAL est le journal intime : chaque ecriture equilibree dans l'ordre des dates. Demandez QUAND un evenement est arrive et il repond. Demandez COMBIEN de tresorerie nous detenons, et le journal devient penible : les mouvements sont disperses. Le GRAND LIVRE est la seconde vue : UNE PAGE PAR COMPTE. Tous les mouvements de Tresorerie sur la page Tresorerie. Memes operations, regroupees par compte. Dans cette application, le grand livre se construit seul depuis votre journal.",
        },
        {
            "position": 3,
            "heading_en": "Posting: debit to debit, credit to credit",
            "heading_fr": "Le report : debit au debit, credit au credit",
            "body_en": "POSTING carries each journal line to its matching ledger account. A DEBIT line becomes a DEBIT movement; a CREDIT line becomes a CREDIT movement. Date, narration and amount travel with it. Example: Debit Cash 25,000 / Credit Sales 25,000 (receipt 0110). Posting adds 25,000 on the DEBIT side of Cash and 25,000 on the CREDIT side of Sales. The entry stays balanced in transit: 25,000 posted debit = 25,000 posted credit. Posting never invents a side.",
            "body_fr": "Le REPORT porte chaque ligne du journal dans le compte correspondant. Une ligne au DEBIT devient un mouvement au DEBIT ; une ligne au CREDIT devient un mouvement au CREDIT. Date, libelle et montant voyagent avec. Exemple : Debit Tresorerie 25 000 / Credit Ventes 25 000 (recu 0110). Le report ajoute 25 000 au DEBIT de Tresorerie et 25 000 au CREDIT de Ventes. L'ecriture reste equilibree : 25 000 debit = 25 000 credit. Le report n'invente jamais un cote.",
        },
        {
            "position": 4,
            "heading_en": "The T-account and its balance",
            "heading_fr": "Le compte en T et son solde",
            "body_en": "Each ledger page is a T: name on top, DEBITS down the LEFT arm, CREDITS down the RIGHT arm. The BALANCE is the difference: add each arm, subtract the smaller from the larger. Debits larger = DEBIT balance; credits larger = CREDIT balance; equal = ZERO. Example: Cash debits 60,000, credits 15,000. Balance = 45,000 debit. The shop holds 45,000.",
            "body_fr": "Chaque page du grand livre est un T : nom en haut, DEBITS le long du bras GAUCHE, CREDITS le long du bras DROIT. Le SOLDE est la difference : additionnez chaque bras, soustrayez le plus petit du plus grand. Debits plus grands = SOLDE DEBITEUR ; credits plus grands = SOLDE CREDITEUR ; egaux = ZERO. Exemple : Tresorerie debits 60 000, credits 15 000. Solde = 45 000 debiteur. La boutique detient 45 000.",
        },
        {
            "position": 5,
            "heading_en": "Which side is normal?",
            "heading_fr": "Quel cote est normal ?",
            "body_en": "Each account normally lives on the side it grows on (Lesson 3): ASSETS and EXPENSES carry DEBIT balances (Cash, Stock, Electricity expense). LIABILITIES, EQUITY and INCOME carry CREDIT balances (Supplier, Capital, Sales). The SIDE is a check: Cash with a credit balance is a warning - you cannot hold minus cash. A Supplier credit balance is money still OWED. Paid in full, debits catch up and the balance falls to zero.",
            "body_fr": "Chaque compte vit normalement du cote ou il grandit (Lecon 3) : ACTIFS et CHARGES portent des SOLDES DEBITEURS (Tresorerie, Stocks, Electricite). PASSIFS, CAPITAUX PROPRES et PRODUITS portent des SOLDES CREDITEURS (Fournisseur, Capital, Ventes). Le COTE est un controle : une Tresorerie creditrice est une alerte - on ne detient pas de la tresorerie negative. Un Fournisseur crediteur est de l'argent encore DU. Paye en totalite, le solde tombe a zero.",
        },
        {
            "position": 6,
            "heading_en": "Worked example: Friday postings",
            "heading_fr": "Exemple : les reports de vendredi",
            "body_en": "Opening balances: Cash 50,000 Dr; Stock 120,000 Dr; Supplier 40,000 Cr; Sales 0; Capital 130,000 Cr. Debits 170,000 = credits 170,000. Friday entries: (1) 9:00 cash sale receipt 0110: Debit Cash 25,000 / Credit Sales 25,000. (2) 11:30 buy rice on credit invoice F-221: Debit Stock 45,000 / Credit Supplier 45,000. (3) 17:00 pay ENEO bill receipt E-77: Debit Electricity 8,000 / Credit Cash 8,000. Posted: Cash debits 75,000 credits 8,000 = 67,000 Dr. Sales = 25,000 Cr. Stock = 165,000 Dr. Supplier = 85,000 Cr. Electricity = 8,000 Dr. Capital 130,000 Cr. Every line reached one page; every entry stayed balanced.",
            "body_fr": "Soldes d'ouverture : Tresorerie 50 000 Dr ; Stocks 120 000 Dr ; Fournisseur 40 000 Cr ; Ventes 0 ; Capital 130 000 Cr. Debits 170 000 = credits 170 000. Ecritures de vendredi : (1) 9h00 vente recu 0110 : Debit Tresorerie 25 000 / Credit Ventes 25 000. (2) 11h30 achat riz a credit facture F-221 : Debit Stocks 45 000 / Credit Fournisseur 45 000. (3) 17h00 facture ENEO recu E-77 : Debit Electricite 8 000 / Credit Tresorerie 8 000. Reporte : Tresorerie debits 75 000 credits 8 000 = 67 000 Dr. Ventes = 25 000 Cr. Stocks = 165 000 Dr. Fournisseur = 85 000 Cr. Electricite = 8 000 Dr. Capital 130 000 Cr. Chaque ligne a atteint une page ; chaque ecriture est restee equilibree.",
        },
        {
            "position": 7,
            "heading_en": "Your turn: Saturday (guided)",
            "heading_fr": "A vous : samedi (guide)",
            "body_en": "From Friday close: Cash 67,000 Dr; Stock 165,000 Dr; Supplier 85,000 Cr; Sales 25,000 Cr; Electricity 8,000 Dr; Capital 130,000 Cr. Saturday: (A) 10:00 cash sale receipt 0111: Debit Cash 30,000 / Credit Sales 30,000. (B) 16:00 pay Mama Rice 35,000 slip BS-12: Debit Supplier 35,000 / Credit Cash 35,000. Guided: Cash debits 75,000 + 30,000 = 105,000; credits 8,000 + 35,000 = 43,000; balance 62,000 Dr. Sales credits 25,000 + 30,000 = 55,000 Cr. Supplier debits 35,000 vs credits 85,000; balance 50,000 Cr still owed. The questions test these three figures.",
            "body_fr": "Depuis vendredi : Tresorerie 67 000 Dr ; Stocks 165 000 Dr ; Fournisseur 85 000 Cr ; Ventes 25 000 Cr ; Electricite 8 000 Dr ; Capital 130 000 Cr. Samedi : (A) 10h00 vente recu 0111 : Debit Tresorerie 30 000 / Credit Ventes 30 000. (B) 16h00 paiement Mama Rice 35 000 bordereau BS-12 : Debit Fournisseur 35 000 / Credit Tresorerie 35 000. Guide : Tresorerie debits 75 000 + 30 000 = 105 000 ; credits 8 000 + 35 000 = 43 000 ; solde 62 000 Dr. Ventes credits 25 000 + 30 000 = 55 000 Cr. Fournisseur debits 35 000 contre credits 85 000 ; solde 50 000 Cr encore du. Les questions portent sur ces trois chiffres.",
        },
        {
            "position": 8,
            "heading_en": "Reading one account",
            "heading_fr": "Lire un compte",
            "body_en": "A balance is a one-line story. Cash 62,000 Dr: the shop HOLDS 62,000. Supplier 50,000 Cr: the shop still OWES 50,000. Sales 55,000 Cr: the shop has EARNED 55,000. Electricity 8,000 Dr: 8,000 USED UP. Two rules: (1) the SIDE tells the story - debit asset is held, credit supplier is owed; (2) the ledger never changes the journal - a wrong balance means a wrong ENTRY or POSTING, so check the journal line it came from. Documents here: receipts 0110/0111, invoice F-221, ENEO receipt E-77, slip BS-12.",
            "body_fr": "Un solde est une histoire en une ligne. Tresorerie 62 000 Dr : la boutique DETIENT 62 000. Fournisseur 50 000 Cr : la boutique DOIT encore 50 000. Ventes 55 000 Cr : la boutique a GAGNE 55 000. Electricite 8 000 Dr : 8 000 CONSOMMES. Deux regles : (1) le COTE raconte l'histoire - actif debiteur detenu, fournisseur crediteur du ; (2) le grand livre ne change jamais le journal - un solde faux vient d'une ECRITURE ou d'un REPORT faux, verifiez la ligne d'origine. Pieces ici : recus 0110/0111, facture F-221, recu ENEO E-77, bordereau BS-12.",
        },
        {
            "position": 9,
            "heading_en": "Fixing a posting error",
            "heading_fr": "Corriger une erreur de report",
            "body_en": "Posted records are never erased (Lesson 4 rule). Suppose Saturday's 35,000 payment was wrongly posted as Debit Stock / Credit Cash instead of Debit Supplier / Credit Cash. Stock wrongly grew; Supplier never shrank. Fix with a NEW entry, dated today: Debit Supplier 35,000 / Credit Stock 35,000, narration 'Correction of BS-12 posting - wrong account debited'. It carries the amount OUT of the wrong account INTO the right one. The wrong line stays visible; the new line explains it. Same in this app: posted rows are immutable or corrected by reversal.",
            "body_fr": "On n'efface jamais un enregistrement publie (regle de la Lecon 4). Supposez que le paiement de 35 000 de samedi a ete reporte a tort en Debit Stocks / Credit Tresorerie au lieu de Debit Fournisseur / Credit Tresorerie. Stocks a grossi a tort ; Fournisseur n'a jamais diminue. Corrigez par une NOUVELLE ecriture datee d'aujourd'hui : Debit Fournisseur 35 000 / Credit Stocks 35 000, libelle 'Correction du report BS-12 - mauvais compte debite'. Elle sort le montant du MAUVAIS compte vers le BON. La ligne fausse reste visible ; la nouvelle l'explique. Pareil dans cette application : les lignes publiees sont immuables ou corrigees par extourne.",
        },
        {
            "position": 10,
            "heading_en": "Where to learn more",
            "heading_fr": "Ou en apprendre davantage",
            "body_en": "SOURCES (by title, nothing reproduced): OHADA Uniform Act on Accounting Law and Financial Information (SYSCOHADA, 26 Jan 2017) - ohada.org - the accounting law of Cameroon and OHADA states; a signpost only, and this platform's charts are a demo subset, NOT an official chart. IFRS Foundation / IASB, IFRS Accounting Standards and Conceptual Framework - ifrs.org. IFAC / IAESB, International Education Standards - ifac.org - competence grows through study plus SUPERVISED practice. ACCA, Foundations in Accountancy syllabus overview - accaglobal.com. OPTIONAL: Neba, Akoso Wilfred (UBa) and Kueda Wamba, Berthelo (FEMS) - public listable work only, find via Google Scholar or AJOL; NO endorsement claimed; nothing reproduced. A perfect score does NOT make you an accountant: designation needs recognised study, supervised experience and a body such as ONECCA Cameroon. NEXT: Lesson 6 gathers every closing balance into one table, the trial balance.",
            "body_fr": "SOURCES (par titre, rien reproduit) : OHADA Acte uniforme droit comptable et information financiere (SYSCOHADA, 26 janv. 2017) - ohada.org - droit comptable du Cameroun et des Etats OHADA ; simple panneau, et les plans de cette plateforme sont une demo, PAS un plan officiel. IFRS Foundation / IASB, IFRS Accounting Standards et Conceptual Framework - ifrs.org. IFAC / IAESB, International Education Standards - ifac.org - la competence vient de l'etude plus la pratique ENCADREE. ACCA, Foundations in Accountancy apercu - accaglobal.com. OPTIONNEL : Neba, Akoso Wilfred (UBa) et Kueda Wamba, Berthelo (FEMS) - travaux publics listables uniquement, via Google Scholar ou AJOL ; AUCUNE caution revendiquee ; rien reproduit. Un score parfait ne fait PAS de vous un comptable : il faut etudes reconnues, experience encadree et un ordre comme l'ONECCA Cameroun. SUITE : la Lecon 6 rassemble tous les soldes dans un tableau, la balance.",
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
            "correction_en": "Both hold the same transactions, just organised differently: the journal is in date order, while the ledger groups the movements account by account.",
            "correction_fr": "Les deux contiennent les mêmes opérations, simplement organisées autrement : le journal suit l'ordre des dates, le grand livre regroupe les mouvements compte par compte.",
            "remediation_section_position": 2,
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
            "correction_en": "Posting means carrying each journal line into its matching individual ledger account, where the account's balance builds up.",
            "correction_fr": "Le report consiste à porter chaque ligne du journal dans le compte individuel correspondant du grand livre, où le solde du compte se construit.",
            "remediation_section_position": 3,
        },
        {
            "position": 3,
            "kind": "mcq",
            "question_en": "A journal entry says: Debit Cash 25,000 / Credit Sales 25,000. How is it posted?",
            "question_fr": "Une ecriture dit : Debit Tresorerie 25 000 / Credit Ventes 25 000. Comment est-elle reportee ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "25,000 on the credit side of Cash and 25,000 on the debit side of Sales", "text_fr": "25 000 au credit de Tresorerie et 25 000 au debit de Ventes", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "25,000 twice on the Cash page, nothing on Sales", "text_fr": "25 000 deux fois sur la page Tresorerie, rien sur Ventes", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "25,000 on the debit side of Cash and 25,000 on the credit side of Sales", "text_fr": "25 000 au debit de Tresorerie et 25 000 au credit de Ventes", "is_correct": True},
            ],
            "explanation_en": "Debit to debit, credit to credit: Cash debit 25,000 and Sales credit 25,000.",
            "explanation_fr": "Debit au debit, credit au credit : Tresorerie debit 25 000 et Ventes credit 25 000.",
            "correction_en": "Carry each line to its own page on the SAME side: the debit line to the debit arm of Cash, the credit line to the credit arm of Sales.",
            "correction_fr": "Portez chaque ligne sur sa page du MEME cote : la ligne debit au bras debit de Tresorerie, la ligne credit au bras credit de Ventes.",
            "remediation_section_position": 3,
        },
        {
            "position": 4,
            "kind": "mcq",
            "question_en": "A Cash T-account shows debits 60,000 and credits 15,000. What is its balance?",
            "question_fr": "Un compte en T Tresorerie montre debits 60 000 et credits 15 000. Quel est son solde ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "75,000 debit balance", "text_fr": "75 000 solde debiteur", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "45,000 debit balance", "text_fr": "45 000 solde debiteur", "is_correct": True},
                {"option_key": "C", "position": 3, "text_en": "45,000 credit balance", "text_fr": "45 000 solde crediteur", "is_correct": False},
            ],
            "explanation_en": "60,000 - 15,000 = 45,000, and debits are larger, so a debit balance.",
            "explanation_fr": "60 000 - 15 000 = 45 000, et les debits sont plus grands, donc un solde debiteur.",
            "correction_en": "Add each arm, subtract the smaller from the larger, and keep the side of the larger arm: 60,000 debit minus 15,000 credit = 45,000 debit.",
            "correction_fr": "Additionnez chaque bras, soustrayez le plus petit du plus grand, et gardez le cote du plus grand bras : 60 000 debit moins 15 000 credit = 45 000 debiteur.",
            "remediation_section_position": 4,
        },
        {
            "position": 5,
            "kind": "short_answer",
            "question_en": "Assets and expenses normally carry a ______ balance (debit/credit).",
            "question_fr": "Les actifs et les charges portent normalement un solde ______ (debiteur/crediteur).",
            "short_answer_en": "debit",
            "short_answer_fr": "debiteur",
            "explanation_en": "Assets and expenses grow on the debit side, so their normal balance is a debit.",
            "explanation_fr": "Les actifs et les charges grandissent au debit, donc leur solde normal est un debit.",
            "correction_en": "The word names the side assets grow on: Cash, Stock and Electricity all live on the debit side.",
            "correction_fr": "Le mot designe le cote ou les actifs grandissent : Tresorerie, Stocks et Electricite vivent tous au debit.",
            "remediation_section_position": 5,
        },
        {
            "position": 6,
            "kind": "mcq",
            "question_en": "Which account normally carries a CREDIT balance?",
            "question_fr": "Quel compte porte normalement un solde CREDITEUR ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "Supplier (money the shop owes)", "text_fr": "Fournisseur (argent que la boutique doit)", "is_correct": True},
                {"option_key": "B", "position": 2, "text_en": "Cash (money the shop holds)", "text_fr": "Tresorerie (argent que la boutique detient)", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "Stock (goods on the shelves)", "text_fr": "Stocks (marchandises en rayon)", "is_correct": False},
            ],
            "explanation_en": "A liability grows on the credit side, so the Supplier account is normally in credit.",
            "explanation_fr": "Un passif grandit au credit, donc le compte Fournisseur est normalement crediteur.",
            "correction_en": "Liabilities, equity and income live on the credit side; assets and expenses live on the debit side.",
            "correction_fr": "Passifs, capitaux propres et produits vivent au credit ; actifs et charges vivent au debit.",
            "remediation_section_position": 5,
        },
        {
            "position": 7,
            "kind": "mcq",
            "question_en": "After Friday's postings, what is the Cash balance?",
            "question_fr": "Apres les reports de vendredi, quel est le solde de Tresorerie ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "75,000 debit - forgetting the ENEO payment", "text_fr": "75 000 debiteur - en oubliant le paiement ENEO", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "67,000 debit (debits 75,000 minus credits 8,000)", "text_fr": "67 000 debiteur (debits 75 000 moins credits 8 000)", "is_correct": True},
                {"option_key": "C", "position": 3, "text_en": "67,000 credit", "text_fr": "67 000 crediteur", "is_correct": False},
            ],
            "explanation_en": "Cash debits 50,000 + 25,000 = 75,000; credits 8,000; 75,000 - 8,000 = 67,000 debit.",
            "explanation_fr": "Tresorerie debits 50 000 + 25 000 = 75 000 ; credits 8 000 ; 75 000 - 8 000 = 67 000 debiteur.",
            "correction_en": "Post first, then balance: add the debit arm (50,000 + 25,000), add the credit arm (8,000), subtract.",
            "correction_fr": "Reportez d'abord, soldez ensuite : additionnez le bras debit (50 000 + 25 000), additionnez le bras credit (8 000), soustrayez.",
            "remediation_section_position": 6,
        },
        {
            "position": 8,
            "kind": "mcq",
            "question_en": "After Friday's postings, what is the Supplier balance?",
            "question_fr": "Apres les reports de vendredi, quel est le solde Fournisseur ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "85,000 credit", "text_fr": "85 000 crediteur", "is_correct": True},
                {"option_key": "B", "position": 2, "text_en": "45,000 credit", "text_fr": "45 000 crediteur", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "85,000 debit", "text_fr": "85 000 debiteur", "is_correct": False},
            ],
            "explanation_en": "Supplier credits 40,000 + 45,000 = 85,000 credit: still owed to Mama Rice.",
            "explanation_fr": "Fournisseur credits 40 000 + 45 000 = 85 000 crediteur : toujours du a Mama Rice.",
            "correction_en": "The opening 40,000 credit plus the new 45,000 credit invoice stay on the credit arm: 85,000 credit.",
            "correction_fr": "Les 40 000 d'ouverture au credit plus la nouvelle facture de 45 000 restent au bras credit : 85 000 crediteur.",
            "remediation_section_position": 6,
        },
        {
            "position": 9,
            "kind": "mcq",
            "question_en": "After Saturday's two entries, what is the Cash balance?",
            "question_fr": "Apres les deux ecritures de samedi, quel est le solde de Tresorerie ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "32,000 debit", "text_fr": "32 000 debiteur", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "62,000 debit (debits 105,000 minus credits 43,000)", "text_fr": "62 000 debiteur (debits 105 000 moins credits 43 000)", "is_correct": True},
                {"option_key": "C", "position": 3, "text_en": "97,000 debit", "text_fr": "97 000 debiteur", "is_correct": False},
            ],
            "explanation_en": "Cash debits 75,000 + 30,000 = 105,000; credits 8,000 + 35,000 = 43,000; 105,000 - 43,000 = 62,000 debit.",
            "explanation_fr": "Tresorerie debits 75 000 + 30 000 = 105 000 ; credits 8 000 + 35 000 = 43 000 ; 105 000 - 43 000 = 62 000 debiteur.",
            "correction_en": "Carry both Saturday lines first: the sale adds to the debit arm, the supplier payment adds to the credit arm, then balance.",
            "correction_fr": "Reportez d'abord les deux lignes de samedi : la vente ajoute au bras debit, le paiement ajoute au bras credit, puis soldez.",
            "remediation_section_position": 7,
        },
        {
            "position": 10,
            "kind": "mcq",
            "question_en": "After Saturday, what is the Supplier balance?",
            "question_fr": "Apres samedi, quel est le solde Fournisseur ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "50,000 debit - the payment wipes the debt out", "text_fr": "50 000 debiteur - le paiement efface la dette", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "120,000 credit", "text_fr": "120 000 crediteur", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "50,000 credit (credits 85,000 minus debits 35,000)", "text_fr": "50 000 crediteur (credits 85 000 moins debits 35 000)", "is_correct": True},
            ],
            "explanation_en": "Supplier credits 85,000 against debits 35,000: 50,000 credit still owed.",
            "explanation_fr": "Fournisseur credits 85 000 contre debits 35 000 : 50 000 crediteur encore du.",
            "correction_en": "The payment is a debit on the Supplier page: 85,000 credit minus 35,000 debit = 50,000 credit.",
            "correction_fr": "Le paiement est un debit sur la page Fournisseur : 85 000 credit moins 35 000 debit = 50 000 crediteur.",
            "remediation_section_position": 7,
        },
        {
            "position": 11,
            "kind": "mcq",
            "question_en": "After Saturday's sale, what is the Sales balance?",
            "question_fr": "Apres la vente de samedi, quel est le solde des Ventes ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "30,000 credit", "text_fr": "30 000 crediteur", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "55,000 credit (credits 25,000 + 30,000)", "text_fr": "55 000 crediteur (credits 25 000 + 30 000)", "is_correct": True},
                {"option_key": "C", "position": 3, "text_en": "55,000 debit", "text_fr": "55 000 debiteur", "is_correct": False},
            ],
            "explanation_en": "Sales credits 25,000 + 30,000 = 55,000 credit: income grows on the credit side.",
            "explanation_fr": "Ventes credits 25 000 + 30 000 = 55 000 crediteur : les produits grandissent au credit.",
            "correction_en": "Add both credit postings on the Sales page: Friday 25,000 plus Saturday 30,000 = 55,000 credit.",
            "correction_fr": "Additionnez les deux reports au credit sur la page Ventes : 25 000 de vendredi plus 30 000 de samedi = 55 000 crediteur.",
            "remediation_section_position": 7,
        },
        {
            "position": 12,
            "kind": "mcq",
            "question_en": "The ledger shows Supplier 50,000 credit after Saturday. What does it mean?",
            "question_fr": "Le grand livre montre Fournisseur 50 000 crediteur apres samedi. Qu'est-ce que cela signifie ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "The shop still owes Mama Rice 50,000", "text_fr": "La boutique doit encore 50 000 a Mama Rice", "is_correct": True},
                {"option_key": "B", "position": 2, "text_en": "The shop has earned 50,000", "text_fr": "La boutique a gagne 50 000", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "The shop holds 50,000 of goods", "text_fr": "La boutique detient 50 000 de marchandises", "is_correct": False},
            ],
            "explanation_en": "A credit balance on a supplier account is money still owed.",
            "explanation_fr": "Un solde crediteur sur un compte fournisseur est de l'argent encore du.",
            "correction_en": "Read the SIDE plus the ACCOUNT: a supplier credit balance is a liability - money owed BY the shop, not held or earned.",
            "correction_fr": "Lisez le COTE plus le COMPTE : un solde crediteur fournisseur est un passif - de l'argent du PAR la boutique, ni detenu ni gagne.",
            "remediation_section_position": 8,
        },
        {
            "position": 13,
            "kind": "mcq",
            "question_en": "Saturday's 35,000 payment was wrongly posted as Debit Stock / Credit Cash instead of Debit Supplier / Credit Cash. How is it fixed?",
            "question_fr": "Le paiement de 35 000 de samedi a ete reporte a tort en Debit Stocks / Credit Tresorerie au lieu de Debit Fournisseur / Credit Tresorerie. Comment le corriger ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "Erase the wrong line and write over it", "text_fr": "Effacer la ligne fausse et ecrire par-dessus", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "Delete the whole Supplier page and start again", "text_fr": "Supprimer toute la page Fournisseur et recommencer", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "Post a new entry: Debit Supplier 35,000 / Credit Stock 35,000", "text_fr": "Reporter une nouvelle ecriture : Debit Fournisseur 35 000 / Credit Stocks 35 000", "is_correct": True},
            ],
            "explanation_en": "Posted lines are never erased: a new entry carries the amount out of the wrong account into the right one.",
            "explanation_fr": "On n'efface jamais les lignes publiees : une nouvelle ecriture porte le montant du mauvais compte vers le bon.",
            "correction_en": "Keep the trail: leave the wrong line visible and add a dated correcting entry that debits Supplier and credits Stock for 35,000.",
            "correction_fr": "Gardez la trace : laissez la ligne fausse visible et ajoutez une ecriture de correction datee qui debite Fournisseur et credite Stocks de 35 000.",
            "remediation_section_position": 9,
        },
        {
            "position": 14,
            "kind": "mcq",
            "question_en": "You finish this lesson with a perfect score. What does that make you?",
            "question_fr": "Vous terminez cette lecon avec un score parfait. Qu'est-ce que cela fait de vous ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "A professional accountant who may sign statements", "text_fr": "Un comptable professionnel qui peut signer des etats", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "Someone with real posting skill - but not a regulated accountant", "text_fr": "Quelqu'un avec un vrai savoir-faire - mais pas un comptable reglemente", "is_correct": True},
                {"option_key": "C", "position": 3, "text_en": "Automatically a member of ONECCA", "text_fr": "Automatiquement membre de l'ONECCA", "is_correct": False},
            ],
            "explanation_en": "Real skill, honest boundary: posting and reading balances is valuable but designation needs study, experience and a body.",
            "explanation_fr": "Vrai savoir-faire, limite honnete : reporter et lire des soldes est precieux mais le titre exige etudes, experience et un ordre.",
            "correction_en": "A perfect score proves you can post and read balances - it does not confer professional status, signing rights or membership.",
            "correction_fr": "Un score parfait prouve que vous savez reporter et lire des soldes - il ne confere ni statut professionnel, ni droit de signature, ni adhesion.",
            "remediation_section_position": 10,
        },
    ],
}