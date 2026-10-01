"""Lesson 3 — Debits and credits.

Expanded in place (same slug "debits-and-credits", same curriculum position 3).
The three ORIGINAL questions keep their positions (1, 2, 3), question ids,
answer ids, option keys, correct answers and accepted short-answer texts, so
historical attempts, progress rows, review cards, current mastery and
certificate eligibility are all untouched. The seed still only INSERTs and
UPDATEs — it never deletes — so nothing a historical row points at can vanish.
`attempts.selected_answer_id` is a foreign key to `answers.id`, so a historic
attempt records WHICH ANSWER ROW was picked, never a display index: nothing
about the stored rows may be reordered.

SCENARIO: "Manka'a Provisions" — the same small neighbourhood food shop in
Bamenda, Cameroon used in Lessons 1 and 2, so the whole course follows one
continuous business (amounts in XAF/FCFA, zero decimals, per project
convention).

ANSWER-POSITION INTEGRITY: the new closed-ended questions deliberately place the
correct option at DIFFERENT authored positions (A/B/C spread across the lesson)
so the answer is never revealed by layout alone. Lesson 3 is also registered in
the engine's deterministic display-order gate
(`_OPTION_ORDER_LESSON_SLUGS` in app/learning/service.py), which permutes the
SERVED option order from the immutable question/answer ids. That gate is safe
here because no question in this lesson asks the learner to read options IN a
meaningful order: there is no "list these steps in order", no chronological
sequence and no ordering whose sequence IS the answer. All options are
alternative candidate entries or statements. Grading is unaffected: the server
resolves the submitted `option_key` to its Answer row by id.

REFERENCES: (a) globally recognized, freely-verifiable authoritative accounting
bodies — cited by name, standard title and URL, with NO copyrighted text
reproduced; (b) clearly-labelled OPTIONAL academic reading. UBa and FEMS are
named only as the institutions of the cited authors — NO endorsement by any
institution is claimed or implied. Nothing here states or implies that
completing this lesson or the course makes anyone a professional or regulated
accountant (see Section 10, and the final exam question that pins it).
"""
LESSON = {
    "slug": "debits-and-credits",
    "position": 3,
    "title_en": "Debits and credits",
    "title_fr": "Le débit et le crédit",
    "summary_en": "Every transaction has two sides — a debit and a credit. Learn which side each account moves on, using a real neighbourhood shop, and write your first balanced entries without memorizing tables.",
    "summary_fr": "Chaque transaction a deux côtés : un débit et un crédit. Apprenez de quel côté chaque compte bouge, avec une vraie boutique de quartier, et écrivez vos premières écritures équilibrées sans mémoriser de tableaux.",
    "sections": [
        # --- Section 1: learning objectives + prerequisite note ---------------
        {
            "position": 1,
            "heading_en": "What you will learn",
            "heading_fr": "Ce que vous allez apprendre",
            "body_en": (
                "By the end of this lesson you will be able to:\n"
                "• explain what debit and credit really mean (and what they do NOT mean);\n"
                "• say which side an asset, a liability, an income and an expense moves on;\n"
                "• check that an entry balances before it is posted;\n"
                "• name the parts of a journal entry and the source document behind it;\n"
                "• write the correct two-sided entry for a cash sale, a cash purchase, an expense and a loan;\n"
                "• follow a full day of a shop's entries and prove the debits equal the credits.\n\n"
                "BEFORE YOU START (prerequisite): you should have finished Lessons 1 and 2 — you already sort assets, liabilities and equity, and you know the accounting equation. That is exactly the knowledge this lesson turns into entries. Nothing to install — the whole lesson works on a phone.\n\n"
                "HOW THIS LESSON WORKS: read the sections in order — Section 8 is a worked example you follow line by line, then Section 9 is your turn at the same skill. Questions 1–6 are quick checks; Questions 7–12 consolidate what you learned; Questions 13–18 are the final check of the whole lesson. Every answer gets instant feedback with an explanation, and anything you miss (or answer on a guess) can come back to you later as a short scheduled review, so finishing with a perfect score is the goal.\n\n"
                "One promise about honesty: this course teaches you accounting. It does not make you an accountant — see the last section."
            ),
            "body_fr": (
                "À la fin de cette leçon, vous serez capable de :\n"
                "• expliquer ce que débit et crédit signifient vraiment (et ce qu'ils ne signifient PAS) ;\n"
                "• dire de quel côté bouge un actif, un passif, un produit et une charge ;\n"
                "• vérifier qu'une écriture est équilibrée avant de la publier ;\n"
                "• nommer les parties d'une écriture de journal et la pièce justificative qui l'appuie ;\n"
                "• écrire la bonne écriture à deux côtés pour une vente au comptant, un achat au comptant, une charge et un emprunt ;\n"
                "• suivre une journée entière d'écritures et prouver que les débits égalent les crédits.\n\n"
                "AVANT DE COMMENCER (prérequis) : vous devriez avoir terminé les Leçons 1 et 2 — vous savez déjà classer actif, passif et capitaux propres, et vous connaissez l'équation comptable. C'est exactement ce savoir que cette leçon transforme en écritures. Rien à installer — toute la leçon fonctionne sur un téléphone.\n\n"
                "COMMENT FONCTIONNE CETTE LEÇON : lisez les sections dans l'ordre — la Section 8 est un exemple corrigé que vous suivez ligne par ligne, puis la Section 9 est votre tour sur la même compétence. Les Questions 1–6 sont des vérifications rapides ; les Questions 7–12 consolident ce que vous avez appris ; les Questions 13–18 sont la vérification finale de toute la leçon. Chaque réponse reçoit une correction immédiate, et tout ce que vous manquez (ou répondez au hasard) peut revenir plus tard sous forme de courte révision planifiée : visez donc le score parfait.\n\n"
                "Une promesse d'honnêteté : ce cours vous enseigne la comptabilité. Il ne fait pas de vous un comptable — voir la dernière section."
            ),
        },
        # --- Section 2 (ORIGINAL position): what Dr/Cr actually mean ---------
        {
            "position": 2,
            "heading_en": "Debit and credit: the two sides of one entry",
            "heading_fr": "Débit et crédit : les deux côtés d'une écriture",
            "body_en": (
                "In double-entry accounting, every transaction is recorded in at least two accounts: one side is a DEBIT (Dr) and the other is a CREDIT (Cr).\n\n"
                "Start by throwing away two myths. A debit is NOT money coming in, and a credit is NOT money going out — that only happens to be true for one account, cash. A debit is also not 'bad' and a credit is not 'good'. Debit and credit are simply the two columns of every account: the left-hand column is the debit side, the right-hand column is the credit side. A transaction moves value from one account's column to another's.\n\n"
                "So the real question is never 'which side is good?'. It is: which side does THIS account's balance live on? For Manka'a Provisions, cash is an asset, and an asset balance lives on the DEBIT side. That is why the 30,000 FCFA cash a customer hands over is DEBIT Cash — not because money came in, but because the cash account's own balance grows on its debit side."
            ),
            "body_fr": (
                "En comptabilité en partie double, chaque transaction est enregistrée dans au moins deux comptes : un côté est un DÉBIT (Dr) et l'autre un CRÉDIT (Cr).\n\n"
                "Commencez par abandonner deux idées fausses. Un débit n'est PAS de l'argent qui rentre, et un crédit n'est PAS de l'argent qui sort — cela n'est vrai que pour un seul compte, la trésorerie. Un débit n'est pas non plus « mauvais » et un crédit n'est pas « bon ». Débit et crédit sont simplement les deux colonnes de chaque compte : la colonne de gauche est le côté débit, la colonne de droite le côté crédit. Une transaction déplace de la valeur d'une colonne de compte vers une autre.\n\n"
                "La vraie question n'est donc jamais « quel côté est bon ? ». C'est : de quel côté vit le solde de CE compte ? Pour Manka'a Provisions, la trésorerie est un actif, et le solde d'un actif vit du côté DÉBIT. C'est pourquoi les 30 000 FCFA en espèces que remet un client sont DÉBIT Trésorerie — non pas parce que l'argent rentre, mais parce que le solde du compte trésorerie grandit du côté débit."
            ),
        },
        # --- Section 3 (ORIGINAL position): the balance rule ------------------
        {
            "position": 3,
            "heading_en": "The golden rule: total debits = total credits",
            "heading_fr": "La règle d'or : total des débits = total des crédits",
            "body_en": (
                "The golden rule: total debits must always equal total credits — just like the accounting equation, it never breaks.\n\n"
                "Check an entry before anyone posts it: add up the debit column, add up the credit column, compare. A debit of 25,000 and a credit of 25,000 is balanced and can be posted. A debit of 25,000 against a credit of 24,000 is not balanced, and it is not 'nearly right' — it is wrong, and posting it would break the equation you learned in Lesson 2. This app refuses to post such an entry at all, at the service layer, not just in the screen.\n\n"
                "The arithmetic works out because the four account types in Section 4 and Section 5 push in opposite directions. An asset rising and an income rising are two debits and two credits of equal size; an asset falling and a liability falling are likewise. Nothing you can do to a transaction makes one side heavier than the other — unless you made a mistake."
            ),
            "body_fr": (
                "La règle d'or : le total des débits doit toujours être égal au total des crédits — comme l'équation comptable, cela ne se casse jamais.\n\n"
                "Vérifiez une écriture avant que quiconque ne la publie : additionnez la colonne débit, additionnez la colonne crédit, comparez. Un débit de 25 000 contre un crédit de 25 000 est équilibré et peut être publié. Un débit de 25 000 contre un crédit de 24 000 n'est pas équilibré, et ce n'est pas « presque juste » — c'est faux, et la publier casserait l'équation apprise en Leçon 2. Cette application refuse tout simplement de publier une telle écriture, au niveau du service, pas seulement à l'écran.\n\n"
                "Le calcul tombe juste parce que les quatre types de comptes des Sections 4 et 5 poussent en sens opposés. Un actif qui monte et un produit qui monte, ce sont deux débits et deux crédits de même montant ; un actif qui baisse et un passif qui baisse, également. Rien de ce que vous pouvez faire à une transaction ne rend un côté plus lourd que l'autre — à moins d'une erreur."
            ),
        },
        # --- NEW Section 4: assets and expenses move on the debit side -------
        {
            "position": 4,
            "heading_en": "Assets and expenses move on the debit side",
            "heading_fr": "Les actifs et les charges bougent du côté débit",
            "body_en": (
                "Two of the four account types behave the same way: ASSETS and EXPENSES.\n\n"
                "An ASSET account has a debit balance. Cash, stock, the freezer, the delivery bicycle, and the amount a customer owes the shop — all of them grow with a DEBIT and shrink with a CREDIT. So when Manka'a buys 10 bags of rice for 120,000 FCFA and pays cash, the stock account is DEBITED 120,000 (the asset grew) and the cash account is CREDITED 120,000 (that asset shrank).\n\n"
                "An EXPENSE account also grows with a DEBIT. When the shop pays 8,000 FCFA for electricity, the electricity expense is DEBITED 8,000 — the cost is recorded on the same side as the assets — and cash is CREDITED 8,000. An expense is simply the asset-side cost of running the business."
            ),
            "body_fr": (
                "Deux des quatre types de comptes se comportent pareil : les ACTIFS et les CHARGES.\n\n"
                "Un compte d'ACTIF a un solde débiteur. La trésorerie, les stocks, le congélateur, le vélo de livraison, et la somme qu'un client doit à la boutique — tous grandissent au DÉBIT et rétrécissent au CRÉDIT. Ainsi, quand Manka'a achète 10 sacs de riz pour 120 000 FCFA et paie en espèces, le compte de stocks est DÉBITÉ de 120 000 (l'actif a grandi) et le compte de trésorerie est CRÉDITÉ de 120 000 (cet actif a rétréci).\n\n"
                "Un compte de CHARGE grandit aussi au DÉBIT. Quand la boutique paie 8 000 FCFA d'électricité, la charge d'électricité est DÉBITÉE de 8 000 — le coût s'enregistre du même côté que les actifs — et la trésorerie est CRÉDITÉE de 8 000. Une charge est simplement le coût, côté actif, de faire tourner l'entreprise."
            ),
        },
        # --- NEW Section 5: liabilities/equity/income move on the credit side -
        {
            "position": 5,
            "heading_en": "Liabilities, equity and income move on the credit side",
            "heading_fr": "Les passifs, capitaux propres et produits bougent du côté crédit",
            "body_en": (
                "The other two account types behave the opposite way: LIABILITIES, EQUITY and INCOME.\n\n"
                "A LIABILITY account has a credit balance. The supplier Nkwen Market, the bank loan, the unpaid electricity bill — each grows with a CREDIT and shrinks with a DEBIT. So when the shop pays 30,000 FCFA on the Nkwen Market invoice, the supplier account is DEBITED 30,000 (the debt is smaller) and cash is CREDITED 30,000.\n\n"
                "INCOME (sales, fees earned) also grows with a CREDIT: selling 45,000 FCFA of goods for cash DEBITs cash 45,000 and CREDITs sales 45,000. EQUITY behaves the same way — the owner's capital is credited when it is brought in, and debited when the owner takes some back out as drawings.\n\n"
                "That is the whole rule, and it is short enough to say out loud: assets and expenses on the debit side; liabilities, equity and income on the credit side. Everything in the rest of this lesson is that sentence applied to a real shop."
            ),
            "body_fr": (
                "Les deux autres types de comptes se comportent à l'opposé : les PASSIFS, les CAPITAUX PROPRES et les PRODUITS.\n\n"
                "Un compte de PASSIF a un solde créditeur. Le fournisseur Nkwen Market, l'emprunt bancaire, la facture d'électricité impayée — chacun grandit au CRÉDIT et rétrécit au DÉBIT. Ainsi, quand la boutique paie 30 000 FCFA sur la facture de Nkwen Market, le compte fournisseur est DÉBITÉ de 30 000 (la dette diminue) et la trésorerie est CRÉDITÉE de 30 000.\n\n"
                "Les PRODUITS (ventes, frais gagnés) grandissent aussi au CRÉDIT : vendre 45 000 FCFA de marchandises en espèces débite la trésorerie de 45 000 et crédite les ventes de 45 000. Les CAPITAUX PROPRES se comportent de même — le capital du propriétaire est crédité quand il est apporté, et débité quand le propriétaire en reprend une partie sous forme de prélèvements.\n\n"
                "Voilà toute la règle, assez courte pour être dite à voix haute : les actifs et les charges du côté débit ; les passifs, capitaux propres et produits du côté crédit. Tout le reste de cette leçon est cette phrase appliquée à une vraie boutique."
            ),
        },
        # --- NEW Section 6: the parts of an entry + vocabulary ---------------
        {
            "position": 6,
            "heading_en": "The parts of an entry, and the words to know",
            "heading_fr": "Les parties d'une écriture, et le vocabulaire à connaître",
            "body_en": (
                "A journal entry has a fixed shape. For Manka'a's cash sale of 45,000 FCFA on 2 March:\n"
                "• DATE — when it happened (2 March).\n"
                "• ACCOUNTS — which accounts move (Cash, Sales).\n"
                "• Dr / Cr — which side of each account moves (Debit, Credit).\n"
                "• AMOUNT — how much, in XAF with no decimals (45,000).\n"
                "• NARRATION — one plain sentence a stranger could follow: 'Cash sale of goods, receipt 0118'.\n"
                "• SOURCE REFERENCE — which document proves it (receipt 0118).\n\n"
                "The words you now need: ACCOUNT (a named pot of value, e.g. Cash, Sales, Electricity expense); JOURNAL (the ordered list of entries before posting); LEDGER (the book of accounts, where each account collects its own debits and credits); POSTING (carrying an entry from the journal into the ledger); BALANCE (the running total of one side of one account); ENTRY (one complete debit-and-credit record). One thing that trips beginners up: Dr/Cr is written AFTER the account name — 'Cash Dr 45,000'. And a posted entry is never edited or deleted; a mistake is corrected with a reversing entry.\n\n"
                "In this platform's Practice workspace the same cash sale posts to the illustrative demo accounts 5711 (Cash) and 7011 (Sales of goods). Those codes come from a small ILLUSTRATIVE demo chart, not from any official chart of accounts — always confirm the real codes your own framework requires."
            ),
            "body_fr": (
                "Une écriture de journal a une forme fixe. Pour la vente au comptant de 45 000 FCFA de Manka'a du 2 mars :\n"
                "• DATE — quand cela s'est passé (2 mars).\n"
                "• COMPTES — quels comptes bougent (Trésorerie, Ventes).\n"
                "• Dr / Cr — de quel côté chaque compte bouge (Débit, Crédit).\n"
                "• MONTANT — combien, en FCFA sans décimales (45 000).\n"
                "• LIBELLÉ — une phrase simple qu'un inconnu pourrait suivre : « Vente au comptant de marchandises, reçu 0118 ».\n"
                "• RÉFÉRENCE PIÈCE — quel document le prouve (reçu 0118).\n\n"
                "Les mots dont vous avez maintenant besoin : COMPTE (un pot de valeur nommé, par ex. Trésorerie, Ventes, Charge d'électricité) ; JOURNAL (la liste ordonnée des écritures avant publication) ; GRAND LIVRE (le livre des comptes, où chaque compte rassemble ses propres débits et crédits) ; LETTURAGE (porter une écriture du journal au grand livre) ; SOLDE (le total cumulé d'un côté d'un compte) ; ÉCRITURE (un enregistrement complet débit et crédit). Une chose qui piège les débutants : on écrit Dr/Cr APRÈS le nom du compte — « Trésorerie Dr 45 000 ». Et une écriture portée au grand livre ne se modifie ni ne se supprime jamais ; une erreur se corrige par une contre-passation.\n\n"
                "Dans l'espace de pratique de cette plateforme, la même vente au comptant est portée sur les comptes de démonstration ILLUSTRATIFS 5711 (Trésorerie) et 7011 (Ventes de marchandises). Ces codes proviennent d'un petit plan comptable de DÉMONSTRATION illustratif, et non d'un plan de comptes officiel — vérifiez toujours les codes réels qu'exige votre propre référentiel."
            ),
        },
        # --- NEW Section 7: source documents behind an entry ------------------
        {
            "position": 7,
            "heading_en": "The paper behind every entry",
            "heading_fr": "Le papier derrière chaque écriture",
            "body_en": (
                "No entry is recorded from memory. Each one is backed by a source document — the Lesson 1 rule, now applied to the two-sided entry:\n"
                "• Owner's 150,000 FCFA start-up capital → the dated cash-receipt/virement note for the deposit.\n"
                "• Rice bought for 120,000 FCFA → Nkwen Market's supplier invoice plus the shop's cash-payment receipt.\n"
                "• Goods sold for 45,000 FCFA cash → the numbered sales receipt issued to the customer (0118).\n"
                "• Electricity paid for 8,000 FCFA → the ENEO bill and the Mobile Money/cash payment confirmation.\n"
                "• Mama Ndifor's 22,000 FCFA on credit → the signed delivery note showing the amount still owed.\n"
                "• 30,000 FCFA paid to Nkwen Market → the bank/Mobile Money transfer receipt against invoice 0117.\n\n"
                "The narration on the entry should always be readable from the document alone. If you cannot point at a paper that proves an entry, you do not have an entry yet — you have a guess."
            ),
            "body_fr": (
                "Aucune écriture n'est enregistrée de mémoire. Chacune est appuyée par une pièce justificative — la règle de la Leçon 1, appliquée à l'écriture à deux côtés :\n"
                "• Capital de démarrage de 150 000 FCFA → le reçu de caisse daté ou la note de virement du dépôt.\n"
                "• Riz acheté pour 120 000 FCFA → la facture fournisseur de Nkwen Market plus le reçu de paiement en espèces de la boutique.\n"
                "• Marchandises vendues pour 45 000 FCFA en espèces → le reçu de vente numéroté remis au client (0118).\n"
                "• Électricité payée 8 000 FCFA → la facture ENEO et la confirmation de paiement Mobile Money/espèces.\n"
                "• Les 22 000 FCFA de Mama Ndifor à crédit → le bon de livraison signé montrant la somme encore due.\n"
                "• 30 000 FCFA payés à Nkwen Market → le reçu de virement bancaire/Mobile Money contre la facture 0117.\n\n"
                "Le libellé de l'écriture doit toujours être compréhensible à partir du seul document. Si vous ne pouvez pas montrer un papier qui prouve une écriture, vous n'avez pas encore une écriture — vous avez une devinette."
            ),
        },
        # --- NEW Section 8: worked example ------------------------------------
        {
            "position": 8,
            "heading_en": "Worked example: one day at the shop",
            "heading_fr": "Exemple corrigé : une journée à la boutique",
            "body_en": (
                "Wednesday, 2 March at Manka'a Provisions. Four transactions, four entries. Decide the side from the rule first, then check that each entry balances:\n\n"
                "1) The owner deposits 150,000 FCFA of personal savings to start the shop. Cash (asset) grows → debit. Capital (equity) grows → credit.\n"
                "   Dr Cash 150,000 / Cr Owner's capital 150,000. Balanced.\n\n"
                "2) The shop buys 10 bags of rice for 120,000 FCFA and pays cash (invoice 0117). Stock (asset) grows → debit. Cash (asset) shrinks → credit.\n"
                "   Dr Stock 120,000 / Cr Cash 120,000. Balanced.\n\n"
                "3) The shop sells goods for 45,000 FCFA in cash (receipt 0118). Cash (asset) grows → debit. Sales (income) grows → credit.\n"
                "   Dr Cash 45,000 / Cr Sales 45,000. Balanced.\n\n"
                "4) The shop pays the 8,000 FCFA electricity bill in cash. Electricity expense grows → debit. Cash shrinks → credit.\n"
                "   Dr Electricity expense 8,000 / Cr Cash 8,000. Balanced.\n\n"
                "Day totals: debits 150,000 + 120,000 + 45,000 + 8,000 = 323,000. Credits 150,000 + 120,000 + 45,000 + 8,000 = 323,000. The whole day balances — and notice how many entries are simply 'one asset for another', with no effect on the owner's share at all."
            ),
            "body_fr": (
                "Mercredi 2 mars chez Manka'a Provisions. Quatre transactions, quatre écritures. Déterminez d'abord le côté grâce à la règle, puis vérifiez que chaque écriture s'équilibre :\n\n"
                "1) Le propriétaire dépose 150 000 FCFA d'économies personnelles pour démarrer la boutique. La trésorerie (actif) grandit → débit. Le capital (capitaux propres) grandit → crédit.\n"
                "   Dr Trésorerie 150 000 / Cr Capital du propriétaire 150 000. Équilibré.\n\n"
                "2) La boutique achète 10 sacs de riz pour 120 000 FCFA et paie en espèces (facture 0117). Les stocks (actif) grandissent → débit. La trésorerie (actif) rétrécit → crédit.\n"
                "   Dr Stocks 120 000 / Cr Trésorerie 120 000. Équilibré.\n\n"
                "3) La boutique vend des marchandises pour 45 000 FCFA en espèces (reçu 0118). La trésorerie (actif) grandit → débit. Les ventes (produit) grandissent → crédit.\n"
                "   Dr Trésorerie 45 000 / Cr Ventes 45 000. Équilibré.\n\n"
                "4) La boutique paie la facture d'électricité de 8 000 FCFA en espèces. La charge d'électricité grandit → débit. La trésorerie rétrécit → crédit.\n"
                "   Dr Charge d'électricité 8 000 / Cr Trésorerie 8 000. Équilibré.\n\n"
                "Totaux de la journée : débits 150 000 + 120 000 + 45 000 + 8 000 = 323 000. Crédits 150 000 + 120 000 + 45 000 + 8 000 = 323 000. La journée entière s'équilibre — et remarquez combien d'écritures sont simplement « un actif pour un autre », sans aucun effet sur la part du propriétaire."
            ),
        },
        # --- NEW Section 9: guided practice ------------------------------------
        {
            "position": 9,
            "heading_en": "Your turn: Thursday at the shop",
            "heading_fr": "À vous : jeudi à la boutique",
            "body_en": (
                "Work through this BEFORE answering Questions 13–15. Three more transactions at Manka'a Provisions:\n\n"
                "A) Mama Ndifor takes 22,000 FCFA of rice on credit and signs the delivery note. She now OWES the shop money.\n"
                "B) The shop pays Nkwen Market 30,000 FCFA on the rice invoice (transfer receipt kept).\n"
                "C) The owner takes 5,000 FCFA from the till for a family errand (dated note kept).\n\n"
                "Work them out, then check yourself:\n"
                "A) The customer account is an ASSET that grew → debit; the sale is INCOME that grew → credit. Dr Customer 22,000 / Cr Sales 22,000. Balanced.\n"
                "B) The supplier account is a LIABILITY that shrank → debit; cash is an ASSET that shrank → credit. Dr Supplier 30,000 / Cr Cash 30,000. Balanced.\n"
                "C) Drawings are a debit (the owner's share fell); cash fell → credit. Dr Drawings 5,000 / Cr Cash 5,000. Balanced.\n\n"
                "Three entries, three balanced. Notice the trap in B: paying money OUT does not mean 'credit everything' — you follow the account types, not the direction of the cash."
            ),
            "body_fr": (
                "Travaillez ceci AVANT de répondre aux Questions 13–15. Trois transactions de plus chez Manka'a Provisions :\n\n"
                "A) Mama Ndifor prend 22 000 FCFA de riz à crédit et signe le bon de livraison. Elle DOIT maintenant de l'argent à la boutique.\n"
                "B) La boutique paie 30 000 FCFA à Nkwen Market sur la facture de riz (reçu de virement conservé).\n"
                "C) Le propriétaire prend 5 000 FCFA dans la caisse pour une course familiale (note datée conservée).\n\n"
                "Calculez, puis vérifiez-vous :\n"
                "A) Le compte client est un ACTIF qui a grandi → débit ; la vente est un PRODUIT qui a grandi → crédit. Dr Client 22 000 / Cr Ventes 22 000. Équilibré.\n"
                "B) Le compte fournisseur est un PASSIF qui a diminué → débit ; la trésorerie est un ACTIF qui a diminué → crédit. Dr Fournisseur 30 000 / Cr Trésorerie 30 000. Équilibré.\n"
                "C) Les prélèvements sont un débit (la part du propriétaire a baissé) ; la trésorerie a baissé → crédit. Dr Prélèvements 5 000 / Cr Trésorerie 5 000. Équilibré.\n\n"
                "Trois écritures, trois équilibrées. Remarquez le piège de B : sortir de l'argent ne veut pas dire « tout créditer » — vous suivez les types de comptes, pas le sens de la trésorerie."
            ),
        },
        # --- NEW Section 10: references + honest note ------------------------
        {
            "position": 10,
            "heading_en": "Going further — and one honest note",
            "heading_fr": "Pour aller plus loin — et une note honnête",
            "body_en": (
                "AUTHORITATIVE SOURCES (freely verifiable; named by title — nothing reproduced):\n"
                "• OHADA, \"Uniform Act on Accounting Law and Financial Information\" (SYSCOHADA, adopted 26 January 2017, revised text) — ohada.org — the accounting law of Cameroon and the other OHADA member states. It is the source of the debit/credit convention taught here: a plan of accounts classifies accounts by nature, and that classification decides the normal side of each account. Mentioning SYSCOHADA is a signpost, not the law itself; this platform's charts are an illustrative demo subset, not an official chart.\n"
                "• IFRS Foundation / International Accounting Standards Board, \"IFRS Accounting Standards\" and the Conceptual Framework for Financial Reporting — ifrs.org — the global reference for financial reporting (the other framework this platform can practise in).\n"
                "• IFAC / IAESB, \"International Education Standards\" — ifac.org — how professional accounting competence is built through study and PRACTISED experience.\n"
                "• ACCA, \"Foundations in Accountancy (FIA)\" syllabus overview — accaglobal.com — a public, free-to-view syllabus whose early progression this course sequence mirrors.\n\n"
                "OPTIONAL ACADEMIC READING (clearly labelled; supplementary only):\n"
                "• Neba, Akoso Wilfred — public academic work in accounting and finance education, University of Bamenda (UBa), Cameroon. Listed for learners who want a local academic perspective. Public listable work only; NO teaching materials are reproduced here and NO UBa endorsement of this platform is claimed or implied.\n"
                "• Kueda Wamba, Berthelo — public academic work in accounting/finance, Cameroon (listed under FEMS — Faculty of Economics and Management Sciences). Same terms: citation of public work only, no reproduction, no endorsement claimed.\n"
                "To find their public work, search an academic index (e.g. Google Scholar or AJOL — African Journals Online) for the author name.\n\n"
                "AN HONEST NOTE ABOUT WHAT THIS LESSON IS NOT: being able to pick the correct side of an entry — even with a perfect score — does NOT make you an accountant, and it does not authorise you to practise as one. Accounting is a regulated profession: professional designation requires recognised study, supervised experience and, in most places, membership of a professional body (for example ONECCA, the Ordre National des Experts Comptables du Cameroun, for professional accountants in Cameroon). What this course gives you is real, practical understanding: you can read a set of entries and prove that they balance. That is worth having — and it is not the same as being one."
            ),
            "body_fr": (
                "SOURCES FAISANT AUTORITÉ (librement vérifiables ; citées par leur titre — rien n'est reproduit) :\n"
                "• OHADA, « Acte uniforme relatif au droit comptable et à l'information financière » (SYSCOHADA, adopté le 26 janvier 2017, texte révisé) — ohada.org — le droit comptable du Cameroun et des autres États parties OHADA. C'est la source de la convention débit/crédit enseignée ici : un plan de comptes classe les comptes par nature, et c'est cette classification qui décide du côté normal de chaque compte. La mention du SYSCOHADA dans cette leçon est un panneau indicateur, pas le droit lui-même ; les plans comptables de cette plateforme sont un sous-ensemble de démonstration illustratif, pas un plan officiel.\n"
                "• IFRS Foundation / International Accounting Standards Board, « IFRS Accounting Standards » et le Conceptual Framework for Financial Reporting — ifrs.org — la référence mondiale en information financière (l'autre cadre dans lequel cette plateforme permet de s'exercer).\n"
                "• IFAC / IAESB, « International Education Standards » — ifac.org — comment la compétence comptable professionnelle se construit par l'étude et l'expérience PRATIQUE encadrée.\n"
                "• ACCA, « Foundations in Accountancy (FIA) » aperçu du programme — accaglobal.com — un programme public consultable gratuitement dont la progression initiale inspire l'ordre de ce cours.\n\n"
                "LECTURES ACADÉMIQUES OPTIONNELLES :\n"
                "• Neba, Akoso Wilfred — travaux académiques publics en comptabilité et enseignement de la finance, Université de Bamenda (UBa), Cameroun. Listé pour les apprenants qui veulent une perspective académique locale. Travaux publics listables uniquement ; AUCUN support de cours n'est reproduit ici et AUCUNE caution de l'UBa n'est revendiquée ni suggérée.\n"
                "• Kueda Wamba, Berthelo — travaux académiques publics en comptabilité/finance, Cameroun (listés sous FEMS — Faculté des Sciences Économiques et de Gestion). Mêmes termes : citation de travaux publics uniquement, aucune reproduction, aucune caution revendiquée.\n"
                "Pour trouver leurs travaux publics, cherchez le nom de l'auteur dans un index académique (par ex. Google Scholar ou AJOL — African Journals Online).\n\n"
                "UNE NOTE HONNÊTE SUR CE QUE CETTE LEÇON N'EST PAS : savoir choisir le bon côté d'une écriture — même avec un score parfait — ne fait PAS de vous un comptable, et ne vous autorise pas à exercer comme tel. La comptabilité est une profession réglementée : le titre professionnel exige des études reconnues, une expérience encadrée et, dans la plupart des pays, l'appartenance à un ordre professionnel (par exemple l'ONECCA, l'Ordre National des Experts Comptables du Cameroun, pour les professionnels comptables au Cameroun). Ce que ce cours vous donne, c'est une compréhension réelle et pratique : vous savez lire un jeu d'écritures et prouver qu'il s'équilibre. Cela vaut la peine — et ce n'est pas la même chose que d'être comptable."
            ),
        },
    ],

    "questions": [
        # --- ORIGINAL Q1, Q2, Q3 — UNCHANGED (position, kind, option keys,
        # correct answers and accepted short-answer texts): these rows keep
        # their question ids and answer ids, so historical attempts, progress,
        # review cards, current mastery and certificate eligibility survive.
        {
            "position": 1,
            "kind": "mcq",
            "question_en": "A customer pays you 30,000 FCFA in cash for goods sold. Which two sides does this transaction have?",
            "question_fr": "Un client vous paie 30 000 FCFA en espèces pour des marchandises vendues. Quels sont les deux côtés de cette transaction ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "Debit Cash 30,000 / Credit Sales 30,000", "text_fr": "Débit Trésorerie 30 000 / Crédit Ventes 30 000", "is_correct": True},
                {"option_key": "B", "position": 2, "text_en": "Credit Cash 30,000 / Debit Sales 30,000", "text_fr": "Crédit Trésorerie 30 000 / Débit Ventes 30 000", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "Debit Cash 30,000 / Debit Sales 30,000", "text_fr": "Débit Trésorerie 30 000 / Débit Ventes 30 000", "is_correct": False},
            ],
            "explanation_en": "Cash (an asset) increases on the debit side; Sales revenue increases on the credit side. Debits equal credits: 30,000 = 30,000.",
            "explanation_fr": "La trésorerie (un actif) augmente au débit ; les Ventes (produits) augmentent au crédit. Les débits égalent les crédits : 30 000 = 30 000.",
            "correction_en": "The side follows the movement: the cash received is debited (the asset grows) and the sales revenue is credited (the income grows) for the same amount.",
            "correction_fr": "Le côté suit le mouvement : la trésorerie reçue est débitée (l'actif augmente) et le produit des ventes est crédité (le produit augmente) du même montant.",
            "remediation_section_position": 2,
        },
        {
            "position": 2,
            "kind": "mcq",
            "question_en": "Which statement about debits and credits is ALWAYS true?",
            "question_fr": "Quelle affirmation sur le débit et le crédit est TOUJOURS vraie ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "Total debits must equal total credits in every balanced entry", "text_fr": "Le total des débits doit être égal au total des crédits dans chaque écriture équilibrée", "is_correct": True},
                {"option_key": "B", "position": 2, "text_en": "Debits are always money coming in", "text_fr": "Les débits sont toujours de l'argent qui rentre", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "Credits are always bad for a business", "text_fr": "Les crédits sont toujours mauvais pour une entreprise", "is_correct": False},
            ],
            "explanation_en": "The only rule that never varies: a balanced double-entry transaction has equal total debits and total credits.",
            "explanation_fr": "La seule règle qui ne varie jamais : une transaction équilibrée en partie double a des totaux de débits et de crédits égaux.",
            "correction_en": "The only rule that never varies is the balance rule: total debits must equal total credits. Debit and credit are not 'good' or 'bad' sides, they are the two sides of one balanced entry.",
            "correction_fr": "La seule règle qui ne varie jamais est celle de l'équilibre : le total des débits égale le total des crédits. Débit et crédit ne sont pas des côtés « bons » ou « mauvais », mais les deux faces d'une même écriture équilibrée.",
            "remediation_section_position": 3,
        },
        {
            "position": 3,
            "kind": "short_answer",
            "question_en": "Money received in cash: cash is ______(debited or credited).",
            "question_fr": "De l'argent reçu en espèces : la trésorerie est ______(débitée ou créditée).",
            "short_answer_en": "debited",
            "short_answer_fr": "débitée",
            "explanation_en": "Cash in hand is an asset, and assets increase on the debit side — so cash is debited.",
            "explanation_fr": "La trésorerie en caisse est un actif, et les actifs augmentent au débit — la trésorerie est donc débitée.",
            "correction_en": "Money received increases cash, and cash is an asset: assets grow on the debit side, so the movement is recorded on the debit side.",
            "correction_fr": "L'argent reçu augmente la trésorerie, qui est un actif : les actifs augmentent au débit, donc le mouvement s'enregistre au débit.",
            "remediation_section_position": 2,
        },
        # --- NEW Q4 (formative): which side an asset lives on ------------------
        {
            "position": 4,
            "kind": "mcq",
            "question_en": "Which statement about an ASSET account is correct?",
            "question_fr": "Quelle affirmation sur un compte d'ACTIF est correcte ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "It grows on the debit side and shrinks on the credit side", "text_fr": "Il grandit du côté débit et rétrécit du côté crédit", "is_correct": True},
                {"option_key": "B", "position": 2, "text_en": "It grows on the credit side and shrinks on the debit side", "text_fr": "Il grandit du côté crédit et rétrécit du côté débit", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "It only ever grows — assets can never be reduced", "text_fr": "Il ne fait que grandir — un actif ne peut jamais être réduit", "is_correct": False},
            ],
            "explanation_en": "An asset account has a debit balance: it grows with a debit and shrinks with a credit. Cash, stock, the freezer and money owed to the shop all behave this way.",
            "explanation_fr": "Un compte d'actif a un solde débiteur : il grandit au débit et rétrécit au crédit. La trésorerie, les stocks, le congélateur et les sommes dues à la boutique se comportent ainsi.",
            "correction_en": "An asset account is like a bucket whose contents only ever rise on one side: increases are debits, decreases are credits. Compare with a liability, which is the mirror image.",
            "correction_fr": "Un compte d'actif ressemble à un seau dont le contenu ne monte que d'un côté : les augmentations sont des débits, les diminutions des crédits. Comparez avec un passif, qui en est l'image miroir.",
            "remediation_section_position": 4,
        },
        # --- NEW Q5 (formative): which side a liability lives on ----------------
        {
            "position": 5,
            "kind": "mcq",
            "question_en": "The shop still owes Nkwen Market money. Which side does that debt grow on?",
            "question_fr": "La boutique doit encore de l'argent à Nkwen Market. De quel côté grandit cette dette ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "The debit side, because a debt is something the business owns", "text_fr": "Du côté débit, car une dette est quelque chose que l'entreprise possède", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "The credit side — a liability grows with a credit", "text_fr": "Du côté crédit — un passif grandit au crédit", "is_correct": True},
                {"option_key": "C", "position": 3, "text_en": "Neither side — a debt is only recorded when it is paid", "text_fr": "Ni l'un ni l'autre — une dette n'est enregistrée que lorsqu'elle est payée", "is_correct": False},
            ],
            "explanation_en": "A liability account has a credit balance: it grows with a credit and shrinks with a debit. The moment the supplier's invoice arrives, the debt is on the books.",
            "explanation_fr": "Un compte de passif a un solde créditeur : il grandit au crédit et rétrécit au débit. Dès l'arrivée de la facture du fournisseur, la dette est dans les livres.",
            "correction_en": "A liability is the mirror image of an asset: increases are credits, decreases are debits. Remember the direction — money owed BY the shop is a liability.",
            "correction_fr": "Un passif est l'image miroir d'un actif : les augmentations sont des crédits, les diminutions des débits. Retenez le sens — l'argent dû PAR la boutique est un passif.",
            "remediation_section_position": 5,
        },
        # --- NEW Q6 (consolidate): writing a balanced purchase entry -----------
        {
            "position": 6,
            "kind": "mcq",
            "question_en": "The shop buys 10 bags of rice for 120,000 FCFA and pays cash. Which entry is correct?",
            "question_fr": "La boutique achète 10 sacs de riz pour 120 000 FCFA et paie en espèces. Quelle écriture est correcte ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "Debit Cash 120,000 / Credit Stock 120,000", "text_fr": "Débit Trésorerie 120 000 / Crédit Stocks 120 000", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "Debit Stock 120,000 / Credit Cash 120,000", "text_fr": "Débit Stocks 120 000 / Crédit Trésorerie 120 000", "is_correct": True},
                {"option_key": "C", "position": 3, "text_en": "Debit Stock 120,000 / Debit Cash 120,000", "text_fr": "Débit Stocks 120 000 / Débit Trésorerie 120 000", "is_correct": False},
            ],
            "explanation_en": "Stock is an asset that grows, so it is debited; cash is an asset that shrinks, so it is credited. Debits 120,000 = credits 120,000.",
            "explanation_fr": "Les stocks sont un actif qui grandit, donc ils sont débités ; la trésorerie est un actif qui rétrécit, donc elle est créditée. Débits 120 000 = crédits 120 000.",
            "correction_en": "Two assets move in opposite directions, so the entry is one debit and one credit: Dr Stock / Cr Cash. Two debits would not balance at all.",
            "correction_fr": "Deux actifs bougent en sens opposés, donc l'écriture est un débit et un crédit : Dr Stocks / Cr Trésorerie. Deux débits ne s'équilibreraient pas du tout.",
            "remediation_section_position": 4,
        },
        # --- NEW Q7 (consolidate): an expense entry ---------------------------
        {
            "position": 7,
            "kind": "mcq",
            "question_en": "The shop pays the 8,000 FCFA electricity bill in cash. Which entry is correct?",
            "question_fr": "La boutique paie la facture d'électricité de 8 000 FCFA en espèces. Quelle écriture est correcte ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "Debit Cash 8,000 / Credit Electricity expense 8,000", "text_fr": "Débit Trésorerie 8 000 / Crédit Charge d'électricité 8 000", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "Debit Electricity expense 8,000 / Credit Cash 8,000", "text_fr": "Débit Charge d'électricité 8 000 / Crédit Trésorerie 8 000", "is_correct": True},
                {"option_key": "C", "position": 3, "text_en": "Debit Electricity expense 8,000 / Debit Cash 8,000", "text_fr": "Débit Charge d'électricité 8 000 / Débit Trésorerie 8 000", "is_correct": False},
            ],
            "explanation_en": "An expense grows with a debit, and cash shrinks with a credit. Debits 8,000 = credits 8,000.",
            "explanation_fr": "Une charge grandit au débit, et la trésorerie rétrécit au crédit. Débits 8 000 = crédits 8 000.",
            "correction_en": "The cost of running the shop is recorded on the same side as the assets: Dr Electricity expense / Cr Cash.",
            "correction_fr": "Le coût de faire tourner la boutique s'enregistre du même côté que les actifs : Dr Charge d'électricité / Cr Trésorerie.",
            "remediation_section_position": 4,
        },
        # --- NEW Q8 (consolidate): unbalanced entry ---------------------------
        {
            "position": 8,
            "kind": "mcq",
            "question_en": "You spot an entry showing total debits of 25,000 and total credits of 24,000. What must you do?",
            "question_fr": "Vous repérez une écriture affichant 25 000 FCFA de débits et 24 000 FCFA de crédits. Que devez-vous faire ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "Post it — it is only 1,000 FCFA out", "text_fr": "La publier — ce n'est que 1 000 FCFA d'écart", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "Find the error before posting — every entry must balance", "text_fr": "Trouver l'erreur avant de publier — toute écriture doit s'équilibrer", "is_correct": True},
                {"option_key": "C", "position": 3, "text_en": "Add 1,000 FCFA to the credit side to make it balance", "text_fr": "Ajouter 1 000 FCFA au côté crédit pour l'équilibrer", "is_correct": False},
            ],
            "explanation_en": "An entry must balance exactly. An unbalanced entry is refused by this app at the service layer — it is never a matter of being 'close enough'.",
            "explanation_fr": "Une écriture doit s'équilibrer exactement. Cette application refuse au niveau du service toute écriture non équilibrée — il n'est jamais question d'être « presque juste ».",
            "correction_en": "Do not adjust a figure to force a balance — that hides the error. Trace which amount is missing or doubled; the 1,000 FCFA gap points straight at it.",
            "correction_fr": "N'ajustez pas un chiffre pour forcer l'équilibre — cela cache l'erreur. Retracez le montant qui manque ou qui est doublé ; l'écart de 1 000 FCFA y mène droit.",
            "remediation_section_position": 3,
        },
        # --- NEW Q9 (consolidate): income side ---------------------------------
        {
            "position": 9,
            "kind": "mcq",
            "question_en": "An INCOME account such as Sales behaves how?",
            "question_fr": "Un compte de PRODUIT comme les Ventes se comporte comment ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "It grows on the debit side, like an asset", "text_fr": "Il grandit du côté débit, comme un actif", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "It has no fixed side — it depends on the transaction", "text_fr": "Il n'a pas de côté fixe — cela dépend de la transaction", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "It grows on the credit side, like a liability", "text_fr": "Il grandit du côté crédit, comme un passif", "is_correct": True},
            ],
            "explanation_en": "Income shares the credit side with liabilities and equity: earning a sale grows Sales with a credit, which is exactly why a cash sale is Dr Cash / Cr Sales.",
            "explanation_fr": "Les produits partagent le côté crédit avec les passifs et les capitaux propres : encaisser une vente fait grandir les Ventes au crédit, ce qui explique qu'une vente au comptant soit Dr Trésorerie / Cr Ventes.",
            "correction_en": "Only assets and expenses live on the debit side. Everything else — liabilities, equity and income — grows on the credit side.",
            "correction_fr": "Seuls les actifs et les charges vivent du côté débit. Tout le reste — passifs, capitaux propres et produits — grandit du côté crédit.",
            "remediation_section_position": 5,
        },
        # --- NEW Q10 (consolidate): the parts of an entry ----------------------
        {
            "position": 10,
            "kind": "mcq",
            "question_en": "Which of these is part of a complete journal entry?",
            "question_fr": "Laquelle de ces éléments fait partie d'une écriture de journal complète ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "The date, the accounts, Dr/Cr, the amount, the narration and the source reference", "text_fr": "La date, les comptes, Dr/Cr, le montant, le libellé et la référence de la pièce", "is_correct": True},
                {"option_key": "B", "position": 2, "text_en": "Only the amount — everything else is optional", "text_fr": "Seulement le montant — tout le reste est facultatif", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "The owner's opinion of how the transaction went", "text_fr": "L'avis du propriétaire sur le déroulement de la transaction", "is_correct": False},
            ],
            "explanation_en": "A complete entry carries the date, the accounts moved, which side each moves, the amount, a narration a stranger could follow, and the source document that proves it.",
            "explanation_fr": "Une écriture complète porte la date, les comptes mouvementés, le côté de chacun, le montant, un libellé qu'un inconnu pourrait suivre, et la pièce justificative qui le prouve.",
            "correction_en": "The narration and the source reference are what make an entry checkable months later — without them you have numbers nobody can verify.",
            "correction_fr": "Le libellé et la référence de la pièce sont ce qui rend une écriture vérifiable des mois plus tard — sans eux, vous avez des chiffres que personne ne peut contrôler.",
            "remediation_section_position": 6,
        },
        # --- NEW Q11 (consolidate): owner capital -------------------------------
        {
            "position": 11,
            "kind": "mcq",
            "question_en": "The owner deposits 150,000 FCFA of personal savings to start the shop. Which entry is correct?",
            "question_fr": "Le propriétaire dépose 150 000 FCFA d'économies personnelles pour démarrer la boutique. Quelle écriture est correcte ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "Debit Owner's capital 150,000 / Credit Cash 150,000", "text_fr": "Débit Capital du propriétaire 150 000 / Crédit Trésorerie 150 000", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "Debit Cash 150,000 / Credit Owner's capital 150,000", "text_fr": "Débit Trésorerie 150 000 / Crédit Capital du propriétaire 150 000", "is_correct": True},
                {"option_key": "C", "position": 3, "text_en": "Debit Cash 150,000 / Credit Sales 150,000", "text_fr": "Débit Trésorerie 150 000 / Crédit Ventes 150 000", "is_correct": False},
            ],
            "explanation_en": "Cash is an asset that grows (debit); the owner's capital is equity that grows (credit). Money brought in is not income — it is the owner's own claim, which is why it is credited to capital and not to sales.",
            "explanation_fr": "La trésorerie est un actif qui grandit (débit) ; le capital du propriétaire est un capitau propre qui grandit (crédit). L'argent apporté n'est pas un produit — c'est la créance du propriétaire sur l'entreprise, d'où le crédit au capital et non aux ventes.",
            "correction_en": "Ask what the money IS: money the owner brings in grows equity, so it is credited to capital. Crediting Sales would wrongly report the shop as having earned it.",
            "correction_fr": "Demandez ce qu'est l'argent : l'argent apporté par le propriétaire grandit les capitaux propres, donc il est crédité au capital. Le créditer aux ventes ferait croire à tort que la boutique l'a gagné.",
            "remediation_section_position": 5,
        },
        # --- NEW Q12 (consolidate): the "money in / money out" myth ------------
        {
            "position": 12,
            "kind": "mcq",
            "question_en": "Why is the saying 'a debit is money coming in' not a safe rule?",
            "question_fr": "Pourquoi la phrase « un débit, c'est de l'argent qui rentre » n'est-elle pas une règle fiable ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "It is not true for cash, the only account where it happens to hold", "text_fr": "Elle n'est pas vraie pour la trésorerie, le seul compte où elle se trouve être vrai", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "It only works for large companies, not small shops", "text_fr": "Elle ne marche que pour les grandes entreprises, pas pour les petites boutiques", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "Debits and credits follow each account's own normal side, not the direction of the cash", "text_fr": "Débits et crédits suivent le côté normal de chaque compte, pas le sens de la trésorerie", "is_correct": True},
            ],
            "explanation_en": "The direction of cash is a coincidence for the cash account alone. The reliable rule is the account type: assets and expenses grow on the debit side; liabilities, equity and income grow on the credit side.",
            "explanation_fr": "Le sens de la trésorerie est une coïncidence pour le seul compte de trésorerie. La règle fiable est le type de compte : les actifs et les charges grandissent au débit ; les passifs, capitaux propres et produits grandissent au crédit.",
            "correction_en": "Paying a supplier sends money OUT but debits the supplier account — so following the cash instead of the account type would give you the wrong entry.",
            "correction_fr": "Payer un fournisseur fait sortir de l'argent mais débite le compte fournisseur — suivre la trésorerie plutôt que le type de compte vous donnerait donc la mauvaise écriture.",
            "remediation_section_position": 2,
        },
        # --- NEW Q13 (final): worked-example day totals -------------------------
        {
            "position": 13,
            "kind": "mcq",
            "question_en": "In the Wednesday worked example, what were the total DEBITS for the day?",
            "question_fr": "Dans l'exemple corrigé du mercredi, quel était le total des DÉBITS de la journée ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "150,000 FCFA", "text_fr": "150 000 FCFA", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "323,000 FCFA", "text_fr": "323 000 FCFA", "is_correct": True},
                {"option_key": "C", "position": 3, "text_en": "53,000 FCFA", "text_fr": "53 000 FCFA", "is_correct": False},
            ],
            "explanation_en": "Add the four debit amounts: 150,000 + 120,000 + 45,000 + 8,000 = 323,000 FCFA. The credit column adds up to exactly the same total.",
            "explanation_fr": "Additionnez les quatre montants au débit : 150 000 + 120 000 + 45 000 + 8 000 = 323 000 FCFA. La colonne crédit totalise exactement le même montant.",
            "correction_en": "Every entry contributes one debit and one credit of the same size, so the day totals match by construction. Add all four debit lines — not the running cash balance.",
            "correction_fr": "Chaque écriture apporte un débit et un crédit du même montant, donc les totaux de la journée correspondent par construction. Additionnez les quatre lignes au débit — pas le solde de trésorerie.",
            "remediation_section_position": 8,
        },
        # --- NEW Q14 (final): guided practice B, paying a supplier -------------
        {
            "position": 14,
            "kind": "mcq",
            "question_en": "The shop pays Nkwen Market 30,000 FCFA on the rice invoice. Which entry is correct?",
            "question_fr": "La boutique paie 30 000 FCFA à Nkwen Market sur la facture de riz. Quelle écriture est correcte ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "Debit Cash 30,000 / Credit Supplier 30,000", "text_fr": "Débit Trésorerie 30 000 / Crédit Fournisseur 30 000", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "Debit Supplier 30,000 / Credit Cash 30,000", "text_fr": "Débit Fournisseur 30 000 / Crédit Trésorerie 30 000", "is_correct": True},
                {"option_key": "C", "position": 3, "text_en": "Credit Supplier 30,000 / Credit Cash 30,000", "text_fr": "Crédit Fournisseur 30 000 / Crédit Trésorerie 30 000", "is_correct": False},
            ],
            "explanation_en": "The supplier account is a liability that SHRANK, so it is debited; cash is an asset that shrank, so it is credited. Debits 30,000 = credits 30,000.",
            "explanation_fr": "Le compte fournisseur est un passif qui a DIMINUÉ, donc il est débité ; la trésorerie est un actif qui a rétréci, donc elle est créditée. Débits 30 000 = crédits 30 000.",
            "correction_en": "This is the trap from Section 9: money going OUT does not mean 'credit everything'. The liability shrank, so it takes the debit.",
            "correction_fr": "C'est le piège de la Section 9 : faire sortir de l'argent ne veut pas dire « tout créditer ». Le passif a diminué, donc il prend le débit.",
            "remediation_section_position": 9,
        },
        # --- NEW Q15 (final): guided practice C, drawings ----------------------
        {
            "position": 15,
            "kind": "mcq",
            "question_en": "The owner takes 5,000 FCFA from the till for a family errand. Which entry is correct?",
            "question_fr": "Le propriétaire prend 5 000 FCFA dans la caisse pour une course familiale. Quelle écriture est correcte ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "Debit Cash 5,000 / Credit Drawings 5,000", "text_fr": "Débit Trésorerie 5 000 / Crédit Prélèvements 5 000", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "Debit Sales 5,000 / Credit Cash 5,000", "text_fr": "Débit Ventes 5 000 / Crédit Trésorerie 5 000", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "Debit Drawings 5,000 / Credit Cash 5,000", "text_fr": "Débit Prélèvements 5 000 / Crédit Trésorerie 5 000", "is_correct": True},
            ],
            "explanation_en": "Drawings reduce the owner's share, so they take a debit; cash shrank, so it is credited. This is NOT a shop expense — it is the owner taking back part of their own equity.",
            "explanation_fr": "Les prélèvements réduisent la part du propriétaire, donc ils prennent le débit ; la trésorerie a rétréci, donc elle est créditée. Ce n'est PAS une charge de la boutique — c'est le propriétaire qui reprend une partie de ses capitaux propres.",
            "correction_en": "Do not record a family withdrawal as a sale or an expense — neither happened. Drawings is the correct account, and it reduces equity rather than profit.",
            "correction_fr": "N'enregistrez pas un retrait familial comme une vente ou une charge — ni l'une ni l'autre n'a eu lieu. Le compte Prélèvements est le bon, et il réduit les capitaux propres et non le bénéfice.",
            "remediation_section_position": 9,
        },
        # --- NEW Q16 (final): the French term ----------------------------------
        {
            "position": 16,
            "kind": "short_answer",
            "question_en": "In French, which word names the right-hand side of an account where a liability grows? The answer is the same in English: ______",
            "question_fr": "En français, quel mot nomme le côté droit d'un compte où grandit un passif ? La réponse est identique en anglais : ______",
            "short_answer_en": "credit",
            "short_answer_fr": "crédit",
            "explanation_en": "It is the CREDIT (crédit) side: liabilities, equity and income all grow there.",
            "explanation_fr": "C'est le côté CRÉDIT : les passifs, les capitaux propres et les produits y grandissent tous.",
            "correction_en": "The credit side is the right-hand column of every account — the side where liabilities, equity and income grow.",
            "correction_fr": "Le côté crédit est la colonne de droite de chaque compte — le côté où grandissent les passifs, les capitaux propres et les produits.",
            "remediation_section_position": 2,
        },
        # --- NEW Q17 (final): what a posted entry may never do -----------------
        {
            "position": 17,
            "kind": "mcq",
            "question_en": "You discover a typo in an entry that has already been posted to the ledger. What is the correct response?",
            "question_fr": "Vous découvrez une faute de frappe dans une écriture déjà portée au grand livre. Quelle est la bonne réaction ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "Edit or delete the posted entry so the ledger looks clean", "text_fr": "Modifier ou supprimer l'écriture portée pour que le grand livre soit net", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "Leave it alone — a small typo never matters", "text_fr": "Ne rien faire — une petite faute de frappe n'a jamais d'importance", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "Correct it with a reversing entry, leaving the original visible", "text_fr": "La corriger par une contre-passation, en laissant l'original visible", "is_correct": True},
            ],
            "explanation_en": "A posted entry is never edited or deleted. The correcting practice is a reversing entry, so the audit trail shows both what was recorded and what corrected it.",
            "explanation_fr": "Une écriture portée au grand livre ne se modifie ni ne se supprime jamais. La pratique correctrice est la contre-passation, pour que la piste d'audit montre à la fois ce qui a été enregistré et ce qui l'a corrigé.",
            "correction_en": "Both wrong answers destroy evidence: one erases history, the other hides a real error. Reversing keeps the books honest and the trail intact.",
            "correction_fr": "Les deux mauvaises réponses détruisent des preuves : l'une efface l'histoire, l'autre cache une vraie erreur. La contre-passation garde les livres honnêtes et la piste intacte.",
            "remediation_section_position": 6,
        },
        # --- NEW Q18 (final): honest boundary ----------------------------------
        {
            "position": 18,
            "kind": "mcq",
            "question_en": "A learner finishes this lesson on debits and credits with a perfect score. Which statement is the honest one?",
            "question_fr": "Un apprenant termine cette leçon sur le débit et le crédit avec un score parfait. Quelle affirmation est honnête ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "They can now read and check a set of entries — but that does not make them an accountant", "text_fr": "Ils peuvent maintenant lire et vérifier un jeu d'écritures — mais cela n'en fait pas des comptables", "is_correct": True},
                {"option_key": "B", "position": 2, "text_en": "They are now qualified to prepare and sign a company's financial statements", "text_fr": "Ils sont désormais qualifiés pour préparer et signer les états financiers d'une entreprise", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "They may call themselves an accountant as soon as the certificate is issued", "text_fr": "Ils peuvent se dire comptables dès que le certificat est délivré", "is_correct": False},
            ],
            "explanation_en": "This lesson builds real, practical skill — choosing the correct side of an entry and proving a day's entries balance — but accounting is a regulated profession: recognised study, supervised experience and professional membership (e.g. ONECCA in Cameroon) are required to be called an accountant. Knowing that boundary IS part of financial literacy.",
            "explanation_fr": "Cette leçon construit une compétence réelle et pratique — choisir le bon côté d'une écriture et prouver l'équilibre d'une journée d'écritures — mais la comptabilité est une profession réglementée : des études reconnues, une expérience encadrée et une inscription professionnelle (p. ex. l'ONECCA au Cameroun) sont exigées pour s'appeler comptable. Connaître cette limite FAIT partie de la culture financière.",
            "correction_en": "The lesson gives practical ability, not a professional title: the title requires recognised study, supervised experience and registration with a professional body.",
            "correction_fr": "La leçon donne une capacité pratique, pas un titre professionnel : le titre exige des études reconnues, une expérience encadrée et une inscription à un ordre professionnel.",
            "remediation_section_position": 10,
        },
    ],
}