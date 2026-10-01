"""Lesson 2 — The accounting equation.

Expanded in place (same slug "the-accounting-equation", same curriculum
position 2). The three ORIGINAL questions keep their positions (1, 2, 3),
question ids, answer ids, option keys and accepted short-answer texts, so
historical attempts, progress rows, review cards, current mastery and
certificate eligibility are all untouched. The seed still only INSERTs and
UPDATEs by position — it never deletes — so nothing historical rows point at
can vanish.

SCENARIO: "Manka'a Provisions" — the same small neighbourhood food shop in
Bamenda, Cameroon used in Lesson 1, so every section, example and question
stays inside one continuous, concrete business (amounts in XAF/FCFA, zero
decimals, per project convention).

REFERENCES: (a) globally recognized, freely-verifiable authoritative accounting
bodies — cited by name, standard title and URL, with NO copyrighted text
reproduced; (b) clearly-labelled OPTIONAL academic reading. UBa and FEMS are
named only as the institutions of the cited authors — NO endorsement by any
institution is claimed or implied. Nothing here states or implies that
completing this lesson or course makes anyone a professional or regulated
accountant (see Section 10, and the final exam question that pins it).
"""
LESSON = {
    "slug": "the-accounting-equation",
    "position": 2,
    "title_en": "The accounting equation",
    "title_fr": "L'équation comptable",
    "summary_en": "Assets = Liabilities + Equity. Learn the one equation every balance sheet is built on, using a real neighbourhood shop — and check it yourself with worked numbers.",
    "summary_fr": "Actif = Passif + Capitaux propres. Apprenez l'unique équation sur laquelle repose tout bilan, avec une vraie boutique de quartier — et vérifiez-la vous-même avec des chiffres concrets.",
    "sections": [
        {
            "position": 1,
            "heading_en": "What you will learn",
            "heading_fr": "Ce que vous allez apprendre",
            "body_en": (
                "By the end of this lesson you will be able to:\n"
                "• state the accounting equation in one sentence and explain each of its three parts;\n"
                "• tell an asset apart from a liability apart from equity, for a small shop's real items;\n"
                "• work out equity from Assets minus Liabilities, in XAF with zero decimals;\n"
                "• show how borrowing, buying for cash, selling on credit and paying a supplier keep the equation balanced;\n"
                "• name the source documents that prove what a business owns and what it owes;\n"
                "• read a small completed balance check for Manka'a Provisions and explain how it stays balanced.\n\n"
                "BEFORE YOU START (prerequisite): you should have finished Lesson 1 — you know what a transaction is, what a source document is, and the five words asset, liability, income and expense. Simple addition and subtraction are enough. Nothing to install — the whole lesson works on a phone.\n\n"
                "HOW THIS LESSON WORKS: read the sections in order — Sections 8 and 9 are a worked example you follow line by line, then your own turn at the same skill. Questions 1–6 are quick checks; Questions 7–12 consolidate what you learned; Questions 13–18 are the final check of the whole lesson. Every answer gets instant feedback, and anything you miss (or answer on a guess) can come back to you later as a short scheduled review, so finishing with a perfect score is the goal.\n\n"
                "One promise about honesty: this course teaches you accounting. It does not make you an accountant — see the last section."
            ),
            "body_fr": (
                "À la fin de cette leçon, vous serez capable de :\n"
                "• énoncer l'équation comptable en une phrase et expliquer chacune de ses trois parties ;\n"
                "• distinguer un actif d'un passif et des capitaux propres, pour les éléments réels d'une petite boutique ;\n"
                "• calculer des capitaux propres à partir d'Actif moins Passif, en FCFA sans décimales ;\n"
                "• montrer comment l'emprunt, l'achat au comptant, la vente à crédit et le paiement d'un fournisseur maintiennent l'équation équilibrée ;\n"
                "• nommer les pièces justificatives qui prouvent ce que l'entreprise possède et ce qu'elle doit ;\n"
                "• lire une petite vérification d'équilibre bouclée pour Manka'a Provisions et expliquer comment elle reste équilibrée.\n\n"
                "AVANT DE COMMENCER (prérequis) : vous devriez avoir terminé la Leçon 1 — vous savez ce qu'est une transaction, ce qu'est une pièce justificative, et les cinq mots actif, passif, produit et charge. De simples additions et soustractions suffisent. Rien à installer — toute la leçon fonctionne sur un téléphone.\n\n"
                "COMMENT FONCTIONNE CETTE LEÇON : lisez les sections dans l'ordre — les Sections 8 et 9 sont un exemple corrigé que vous suivez ligne par ligne, puis votre tour sur la même compétence. Les Questions 1–6 sont des vérifications rapides ; les Questions 7–12 consolident ce que vous avez appris ; les Questions 13–18 sont la vérification finale de toute la leçon. Chaque réponse reçoit une correction immédiate, et tout ce que vous manquez (ou répondez au hasard) peut revenir plus tard sous forme de courte révision planifiée : visez donc le score parfait.\n\n"
                "Une promesse d'honnêteté : ce cours vous enseigne la comptabilité. Il ne fait pas de vous un comptable — voir la dernière section."
            ),
        },
        {
            "position": 2,
            "heading_en": "The equation",
            "heading_fr": "L'équation",
            "body_en": (
                "The equation is always: Assets = Liabilities + Equity. If a business has 100,000 FCFA of assets and owes 30,000 FCFA, the owners' share is 70,000 FCFA. The two sides must always be balanced.\n\n"
                "Meet the three words inside Manka'a Provisions. ASSETS are everything the shop owns: the cash in the till, the rice, oil, soap and sugar on the shelves, the freezer — and also money that customers still owe the shop, like Mama Ndifor's unpaid rice bill, because the right to collect it is itself valuable. LIABILITIES are everything the shop owes to others: the supplier who delivered rice on 30-day credit, the bank loan, the electricity bill not yet paid. EQUITY is what is left for the owner once the liabilities are taken away from the assets.\n\n"
                "You can also read the equation backwards to find a missing number: Equity = Assets − Liabilities, and Liabilities = Assets − Equity. If the shop's assets total 430,000 FCFA and what it owes totals 130,000 FCFA, its equity must be 300,000 FCFA. There is no guessing: the arithmetic decides."
            ),
            "body_fr": (
                "L'équation est toujours : Actif = Passif + Capitaux propres. Si une entreprise a 100 000 FCFA d'actif et doit 30 000 FCFA, la part des propriétaires est de 70 000 FCFA. Les deux côtés doivent toujours être équilibrés.\n\n"
                "Rencontrez les trois mots à l'intérieur de Manka'a Provisions. L'ACTIF, c'est tout ce que la boutique possède : l'argent en caisse, le riz, l'huile, le savon et le sucre sur les étagères, le congélateur — et aussi l'argent que les clients doivent encore à la boutique, comme la facture de riz impayée de Mama Ndifor, car le droit de l'encaisser a lui-même de la valeur. LE PASSIF, c'est tout ce que la boutique doit à d'autres : le fournisseur qui a livré le riz à crédit de 30 jours, l'emprunt bancaire, la facture d'électricité pas encore payée. LES CAPITAUX PROPRES, c'est ce qui reste au propriétaire une fois le passif retiré de l'actif.\n\n"
                "Vous pouvez aussi lire l'équation à l'envers pour retrouver un nombre manquant : Capitaux propres = Actif − Passif, et Passif = Actif − Capitaux propres. Si l'actif de la boutique totalise 430 000 FCFA et ce qu'elle doit totalise 130 000 FCFA, ses capitaux propres doivent être de 300 000 FCFA. Il n'y a aucune devinette : c'est l'arithmétique qui décide."
            ),
        },
        {
            "position": 3,
            "heading_en": "Why it never breaks",
            "heading_fr": "Pourquoi elle ne se casse jamais",
            "body_en": (
                "Every double-entry transaction keeps this equation in balance. Buy stock with cash? Cash goes down, stock goes up — assets stay balanced. Borrow money? Cash goes up and liabilities go up by the same amount.\n\n"
                "Notice the pattern: every transaction moves TWO places at the same time, and the moves always cancel out. More cash and more debt (borrowing); less cash and more stock (buying); less cash and less debt (paying the supplier); more cash and a bigger owners' share when a sale earns a profit. Like the two pans of a market scale — whatever you add to one pan, you add the same weight to the other, so the scale stays level.\n\n"
                "This is why a balance sheet is called a balance sheet: if the two sides ever disagree, the equation did not break — the bookkeeper made a recording mistake somewhere, and the difference is exactly the trail that leads to it. An unbalanced sheet is therefore never a mystery; it is an instruction to go and find the error."
            ),
            "body_fr": (
                "Chaque transaction en partie double maintient cette équation en équilibre. Acheter des stocks en espèces ? La trésorerie baisse, les stocks montent — l'actif reste équilibré. Emprunter de l'argent ? La trésorerie monte et le passif monte du même montant.\n\n"
                "Remarquez le schéma : chaque transaction déplace DEUX endroits en même temps, et les mouvements s'annulent toujours. Plus de trésorerie et plus de dette (emprunt) ; moins de trésorerie et plus de stocks (achat) ; moins de trésorerie et moins de dette (paiement du fournisseur) ; plus de trésorerie et une part du propriétaire plus grande quand une vente rapporte un bénéfice. Comme les deux plateaux d'une balance de marché — tout ce que vous ajoutez à un plateau, vous ajoutez le même poids à l'autre, pour que la balance reste à niveau.\n\n"
                "C'est pourquoi un bilan s'appelle un bilan : si les deux côtés diffèrent un jour, l'équation ne s'est pas brisée — le comptable a commis une erreur d'enregistrement quelque part, et l'écart est exactement la piste qui y mène. Un bilan déséquilibré n'est donc jamais un mystère ; c'est une consigne d'aller trouver l'erreur."
            ),
        },
        # --- NEW Section 4: assets, sorted item by item -----------------------
        {
            "position": 4,
            "heading_en": "Assets: what the shop owns",
            "heading_fr": "L'actif : ce que la boutique possède",
            "body_en": (
                "Walk through Manka'a Provisions and point at everything that belongs to the business. The cash in the till and the Mobile Money float are assets. The rice, oil, soap and sugar on the shelves — the stock — are assets. The freezer and the delivery bicycle are assets; they will serve for years. And the 22,000 FCFA Mama Ndifor still owes for last week's rice is an asset too: an amount owed TO the business is called a RECEIVABLE, and it is real value even though the cash has not arrived yet.\n\n"
                "The test for an asset is never 'where is it?' but 'whose is it, and can it bring future value to the business?' A rented freezer is not the shop's asset. The owner's personal phone is not the shop's asset. But everything the business owns and can use to earn — cash, stock, equipment, customer debts — sits on the left side of the equation."
            ),
            "body_fr": (
                "Faites le tour de Manka'a Provisions et montrez tout ce qui appartient à l'entreprise. L'argent en caisse et le flottant Mobile Money sont des actifs. Le riz, l'huile, le savon et le sucre sur les étagères — les stocks — sont des actifs. Le congélateur et le vélo de livraison sont des actifs ; ils serviront pendant des années. Et les 22 000 FCFA que Mama Ndifor doit encore pour le riz de la semaine dernière sont aussi un actif : une somme due À l'entreprise s'appelle une CRÉANCE, et c'est une vraie valeur même si l'argent n'est pas encore arrivé.\n\n"
                "Le test d'un actif n'est jamais « où est-il ? » mais « à qui est-il, et peut-il apporter une valeur future à l'entreprise ? » Un congélateur loué n'est pas un actif de la boutique. Le téléphone personnel du propriétaire n'est pas un actif de la boutique. Mais tout ce que l'entreprise possède et peut utiliser pour gagner — trésorerie, stocks, matériel, dettes des clients — se trouve du côté gauche de l'équation."
            ),
        },
        # --- NEW Section 5: liabilities --------------------------------------
        {
            "position": 5,
            "heading_en": "Liabilities: what the shop owes",
            "heading_fr": "Le passif : ce que la boutique doit",
            "body_en": (
                "Now turn the question around: who can walk into Manka'a Provisions and demand money? The Nkwen Market supplier delivered 10 bags of rice on 30-day credit — the supplier's invoice is a liability until cash or Mobile Money settles it. The bank loan that bought the freezer is a liability until the last instalment is paid. The 8,000 FCFA electricity bill sitting unpaid on the counter is a liability.\n\n"
                "An amount the business owes to anyone else is called a PAYABLE, and every liability sits on the right side of the equation, inside Liabilities + Equity. Notice the mirror image with Section 4: money owed TO the shop is an asset (receivable); money owed BY the shop is a liability (payable). Confusing the two directions is the single most common beginner mistake — and the questions below test it directly, so get the direction straight here: TO the shop = asset, BY the shop = liability."
            ),
            "body_fr": (
                "Retournez maintenant la question : qui peut entrer dans Manka'a Provisions et réclamer de l'argent ? Le fournisseur de Nkwen Market a livré 10 sacs de riz à crédit de 30 jours — la facture du fournisseur est un passif jusqu'à ce que les espèces ou le Mobile Money le règlent. L'emprunt bancaire qui a acheté le congélateur est un passif jusqu'au dernier versement. La facture d'électricité de 8 000 FCFA posée impayée sur le comptoir est un passif.\n\n"
                "Une somme que l'entreprise doit à quelqu'un d'autre s'appelle une DETTE, et tout passif se trouve du côté droit de l'équation, à l'intérieur de Passif + Capitaux propres. Remarquez le miroir avec la Section 4 : l'argent dû À la boutique est un actif (créance) ; l'argent dû PAR la boutique est un passif (dette). Confondre les deux sens est l'erreur de débutant la plus fréquente — et les questions ci-dessous la testent directement, alors fixez bien le sens ici : À la boutique = actif, PAR la boutique = passif."
            ),
        },
        # --- NEW Section 6: equity -------------------------------------------
        {
            "position": 6,
            "heading_en": "Equity: what is left for the owner",
            "heading_fr": "Les capitaux propres : ce qui reste au propriétaire",
            "body_en": (
                "Equity has three sources, and Manka'a Provisions shows all three.\n\n"
                "First, CAPITAL: the money the owner put into the business at the start — 200,000 FCFA from personal savings to stock the shelves. Second, PROFIT: when the shop sells for more than goods and running costs, the surplus stays inside the business and equity grows. Third — pulling the other way — DRAWINGS: when the owner takes 4,000 FCFA from the till for a family errand, equity falls by 4,000 FCFA. Drawings are not a shop expense; they are the owner taking back part of their own share.\n\n"
                "So equity is not a fixed number written in stone: it moves every day. Today's equity = capital put in + profits kept − drawings taken out. Watch it in the worked example of Section 8, where the shop's equity comes out at exactly 250,000 FCFA — and you will compute it yourself."
            ),
            "body_fr": (
                "Les capitaux propres ont trois sources, et Manka'a Provisions les montre toutes les trois.\n\n"
                "D'abord, le CAPITAL : l'argent que le propriétaire a mis dans l'entreprise au départ — 200 000 FCFA d'économies personnelles pour garnir les étagères. Ensuite, le BÉNÉFICE : quand la boutique vend pour plus que le coût des marchandises et des frais, le surplus reste dans l'entreprise et les capitaux propres grandissent. Troisième source — qui tire dans l'autre sens — les PRÉLÈVEMENTS : quand le propriétaire prend 4 000 FCFA dans la caisse pour une course familiale, les capitaux propres baissent de 4 000 FCFA. Un prélèvement n'est pas une charge de la boutique ; c'est le propriétaire qui reprend une partie de sa propre part.\n\n"
                "Les capitaux propres ne sont donc pas un nombre fixe gravé dans la pierre : ils bougent chaque jour. Capitaux propres d'aujourd'hui = capital apporté + bénéfices conservés − prélèvements effectués. Observez-le dans l'exemple corrigé de la Section 8, où les capitaux propres de la boutique ressortent à exactement 250 000 FCFA — et vous le calculerez vous-même."
            ),
        },
        # --- NEW Section 7: source documents behind each side -----------------
        {
            "position": 7,
            "heading_en": "The paper behind each number",
            "heading_fr": "Le papier derrière chaque chiffre",
            "body_en": (
                "Every figure in the equation must be traceable to a source document — the Lesson 1 rule applies here too. For Manka'a Provisions:\n"
                "• ASSETS are proved by the cash count and the Mobile Money statement (cash), the purchase invoices and stock count (stock), the purchase receipt for the freezer and the bicycle (equipment), and the signed delivery note (Mama Ndifor's 22,000 FCFA receivable).\n"
                "• LIABILITIES are proved by the supplier's invoice (the Nkwen Market rice debt), the bank's loan agreement with its repayment schedule (the loan), and the unpaid electricity bill.\n"
                "• EQUITY needs no single paper of its own: it is ARITHMETIC. You prove assets with their documents, you prove liabilities with theirs, and equity is whatever is left — Assets − Liabilities.\n\n"
                "If someone challenges a figure, the bookkeeper never argues from memory: they fetch the document. That is the whole audit trail of Lesson 1, now applied to the balance side of the business."
            ),
            "body_fr": (
                "Chaque chiffre de l'équation doit pouvoir être rattaché à une pièce justificative — la règle de la Leçon 1 s'applique ici aussi. Pour Manka'a Provisions :\n"
                "• L'ACTIF est prouvé par le comptage de caisse et le relevé Mobile Money (trésorerie), les factures d'achat et le comptage des stocks (stocks), le reçu d'achat du congélateur et du vélo (matériel), et le bon de livraison signé (la créance de 22 000 FCFA de Mama Ndifor).\n"
                "• LE PASSIF est prouvé par la facture du fournisseur (la dette de riz de Nkwen Market), le contrat d'emprunt de la banque avec son échéancier (l'emprunt), et la facture d'électricité impayée.\n"
                "• LES CAPITAUX PROPRES n'ont besoin d'aucun papier à eux seuls : ce sont de l'ARITHMÉTIQUE. Vous prouvez l'actif avec ses documents, vous prouvez le passif avec les siens, et les capitaux propres sont ce qui reste — Actif − Passif.\n\n"
                "Si quelqu'un conteste un chiffre, le comptable ne discute jamais de mémoire : il va chercher le document. C'est toute la piste d'audit de la Leçon 1, appliquée maintenant au côté bilan de l'entreprise."
            ),
        },
        # --- NEW Section 8: worked example ------------------------------------
        {
            "position": 8,
            "heading_en": "Worked example: the shop at closing time",
            "heading_fr": "Exemple corrigé : la boutique à la fermeture",
            "body_en": (
                "Wednesday evening at Manka'a Provisions. The owner counts everything and lays the documents on the counter. Follow line by line — the method is the whole lesson:\n\n"
                "ASSETS — cash in the till 96,000 FCFA + Mobile Money float 40,000 FCFA + stock on the shelves 145,000 FCFA + the freezer 120,000 FCFA + the delivery bicycle 45,000 FCFA + Mama Ndifor's unpaid rice bill 22,000 FCFA = 468,000 FCFA in total.\n\n"
                "LIABILITIES — the Nkwen Market rice invoice 60,000 FCFA + the bank loan still to repay 150,000 FCFA + the unpaid electricity bill 8,000 FCFA = 218,000 FCFA in total.\n\n"
                "EQUITY = 468,000 − 218,000 = 250,000 FCFA. Check: 218,000 + 250,000 = 468,000. Balanced — as always.\n\n"
                "And where did the 250,000 FCFA come from? The owner put in 200,000 FCFA of capital at the start, the shop has kept 54,000 FCFA of profits since, and the owner took 4,000 FCFA for a family errand: 200,000 + 54,000 − 4,000 = 250,000 FCFA. Same number, two different roads — the equation and the equity story agree, so the bookkeeper can trust both."
            ),
            "body_fr": (
                "Mercredi soir chez Manka'a Provisions. Le propriétaire compte tout et pose les documents sur le comptoir. Suivez ligne par ligne — la méthode est toute la leçon :\n\n"
                "ACTIF — argent en caisse 96 000 FCFA + flottant Mobile Money 40 000 FCFA + stocks sur les étagères 145 000 FCFA + le congélateur 120 000 FCFA + le vélo de livraison 45 000 FCFA + la facture de riz impayée de Mama Ndifor 22 000 FCFA = 468 000 FCFA au total.\n\n"
                "PASSIF — la facture de riz de Nkwen Market 60 000 FCFA + l'emprunt bancaire restant à rembourser 150 000 FCFA + la facture d'électricité impayée 8 000 FCFA = 218 000 FCFA au total.\n\n"
                "CAPITAUX PROPRES = 468 000 − 218 000 = 250 000 FCFA. Vérification : 218 000 + 250 000 = 468 000. Équilibré — comme toujours.\n\n"
                "Et d'où viennent ces 250 000 FCFA ? Le propriétaire a apporté 200 000 FCFA de capital au départ, la boutique a conservé 54 000 FCFA de bénéfices depuis, et le propriétaire a pris 4 000 FCFA pour une course familiale : 200 000 + 54 000 − 4 000 = 250 000 FCFA. Même nombre, deux chemins différents — l'équation et l'histoire des capitaux propres s'accordent, donc le comptable peut faire confiance aux deux."
            ),
        },
        # --- NEW Section 9: guided practice ------------------------------------
        {
            "position": 9,
            "heading_en": "Your turn: Thursday at the shop",
            "heading_fr": "À vous : jeudi à la boutique",
            "body_en": (
                "Work through this BEFORE answering the questions below — Question 14 tests it directly. Take the Wednesday closing figures from Section 8: assets 468,000 FCFA, liabilities 218,000 FCFA, equity 250,000 FCFA.\n\n"
                "Thursday at Manka'a Provisions:\n"
                "• Morning — the owner repays 30,000 FCFA of the bank loan in cash (bank receipt kept).\n"
                "• Midday — Mama Ndifor settles her 22,000 FCFA bill in cash, receipt 0114 issued.\n"
                "• Afternoon — the shop buys cooking oil worth 45,000 FCFA from Nkwen Market on 30-day credit (supplier invoice received).\n"
                "• Evening — the owner takes 5,000 FCFA from the till for a family need (dated note kept).\n\n"
                "Work it out, then check yourself:\n"
                "1. Loan repayment: cash (asset) down 30,000, bank loan (liability) down 30,000. Assets 438,000, liabilities 188,000, equity still 250,000.\n"
                "2. Mama Ndifor pays: cash up 22,000, receivable down 22,000 — one asset for another. Assets stay 438,000, equity still 250,000.\n"
                "3. Oil bought on credit: stock up 45,000, supplier debt up 45,000. Assets 483,000, liabilities 233,000, equity still 250,000.\n"
                "4. Family withdrawal: cash down 5,000, drawings — equity down 5,000. Assets 478,000, liabilities 233,000, equity 245,000.\n\n"
                "Final check: 233,000 + 245,000 = 478,000. Balanced — as always. Notice answers 1 and 2 changed nothing on the equity side: repaying debt and collecting a receivable only rearrange what is already there. Only the withdrawal touched equity."
            ),
            "body_fr": (
                "Travaillez ceci AVANT de répondre aux questions ci-dessous — la Question 14 la teste directement. Prenez les chiffres de clôture du mercredi de la Section 8 : actif 468 000 FCFA, passif 218 000 FCFA, capitaux propres 250 000 FCFA.\n\n"
                "Jeudi chez Manka'a Provisions :\n"
                "• Matin — le propriétaire rembourse 30 000 FCFA de l'emprunt bancaire en espèces (reçu de la banque conservé).\n"
                "• Midi — Mama Ndifor règle sa facture de 22 000 FCFA en espèces, reçu 0114 émis.\n"
                "• Après-midi — la boutique achète de l'huile de cuisine pour 45 000 FCFA à Nkwen Market à crédit de 30 jours (facture du fournisseur reçue).\n"
                "• Soir — le propriétaire prend 5 000 FCFA dans la caisse pour un besoin familial (note datée conservée).\n\n"
                "Calculez, puis vérifiez-vous :\n"
                "1. Remboursement de l'emprunt : trésorerie (actif) −30 000, emprunt bancaire (passif) −30 000. Actif 438 000, passif 188 000, capitaux propres toujours 250 000.\n"
                "2. Paiement de Mama Ndifor : trésorerie +22 000, créance −22 000 — un actif pour un autre. Actif toujours 438 000, capitaux propres toujours 250 000.\n"
                "3. Huile achetée à crédit : stocks +45 000, dette fournisseur +45 000. Actif 483 000, passif 233 000, capitaux propres toujours 250 000.\n"
                "4. Retrait familial : trésorerie −5 000, prélèvement — capitaux propres −5 000. Actif 478 000, passif 233 000, capitaux propres 245 000.\n\n"
                "Vérification finale : 233 000 + 245 000 = 478 000. Équilibré — comme toujours. Remarquez que les réponses 1 et 2 n'ont rien changé du côté des capitaux propres : rembourser une dette et encaisser une créance ne font que réorganiser ce qui existe déjà. Seul le retrait a touché les capitaux propres."
            ),
        },
        # --- NEW Section 10: references + honest note ------------------------
        {
            "position": 10,
            "heading_en": "Going further — and one honest note",
            "heading_fr": "Pour aller plus loin — et une note honnête",
            "body_en": (
                "AUTHORITATIVE SOURCES (freely verifiable; named by title — nothing reproduced):\n"
                "• OHADA, \"Uniform Act on Accounting Law and Financial Information\" (SYSCOHADA, adopted 26 January 2017, revised text) — ohada.org — the accounting law of Cameroon and the other OHADA member states. Its balance sheet (bilan) is one more presentation of exactly the equation you learned here: what the business owns on one side, what it owes and the owners' share on the other. Mentioning SYSCOHADA is a signpost, not the law itself; this platform's charts are an illustrative demo subset, not an official chart.\n"
                "• IFRS Foundation / International Accounting Standards Board, \"IFRS Accounting Standards\" and the Conceptual Framework for Financial Reporting — ifrs.org — the global reference for financial reporting (the other framework this platform can practise in).\n"
                "• IFAC / IAESB, \"International Education Standards\" — ifac.org — how professional accounting competence is built through study and PRACTISED experience.\n"
                "• ACCA, \"Foundations in Accountancy (FIA)\" syllabus overview — accaglobal.com — a public, free-to-view syllabus whose early progression this course sequence mirrors.\n\n"
                "OPTIONAL ACADEMIC READING (clearly labelled; supplementary only):\n"
                "• Neba, Akoso Wilfred — public academic work in accounting and finance education, University of Bamenda (UBa), Cameroon. Listed for learners who want a local academic perspective. Public listable work only; NO teaching materials are reproduced here and NO UBa endorsement of this platform is claimed or implied.\n"
                "• Kueda Wamba, Berthelo — public academic work in accounting/finance, Cameroon (listed under FEMS — Faculty of Economics and Management Sciences). Same terms: citation of public work only, no reproduction, no endorsement claimed.\n"
                "To find their public work, search an academic index (e.g. Google Scholar or AJOL — African Journals Online) for the author name.\n\n"
                "AN HONEST NOTE ABOUT WHAT THIS LESSON IS NOT: learning to sort assets, liabilities and equity — even with a perfect score — does NOT make you an accountant, and it does not authorise you to practise as one. Accounting is a regulated profession: professional designation requires recognised study, supervised experience and, in most places, membership of a professional body (for example ONECCA, the Ordre National des Experts Comptables du Cameroun, for professional accountants in Cameroon). What this course gives you is real, practical understanding: you can read a balance sheet, check that it balances, and explain where every number comes from. That is worth having — and it is not the same as being one."
            ),
            "body_fr": (
                "SOURCES FAISANT AUTORITÉ (librement vérifiables ; citées par leur titre — rien n'est reproduit) :\n"
                "• OHADA, « Acte uniforme relatif au droit comptable et à l'information financière » (SYSCOHADA, adopté le 26 janvier 2017, texte révisé) — ohada.org — le droit comptable du Cameroun et des autres États parties OHADA. Son bilan est une présentation de plus d'exactement l'équation apprise ici : ce que l'entreprise possède d'un côté, ce qu'elle doit et la part des propriétaires de l'autre. La mention du SYSCOHADA dans cette leçon est un panneau indicateur, pas le droit lui-même ; les plans comptables de cette plateforme sont un sous-ensemble de démonstration illustratif, pas un plan officiel.\n"
                "• IFRS Foundation / International Accounting Standards Board, « IFRS Accounting Standards » et le Conceptual Framework for Financial Reporting — ifrs.org — la référence mondiale en information financière (l'autre cadre dans lequel cette plateforme permet de s'exercer).\n"
                "• IFAC / IAESB, « International Education Standards » — ifac.org — comment la compétence comptable professionnelle se construit par l'étude et l'expérience PRATIQUE encadrée.\n"
                "• ACCA, « Foundations in Accountancy (FIA) » aperçu du programme — accaglobal.com — un programme public consultable gratuitement dont la progression initiale inspire l'ordre de ce cours.\n\n"
                "LECTURES ACADÉMIQUES OPTIONNELLES :\n"
                "• Neba, Akoso Wilfred — travaux académiques publics en comptabilité et enseignement de la finance, Université de Bamenda (UBa), Cameroun. Listé pour les apprenants qui veulent une perspective académique locale. Travaux publics listables uniquement ; AUCUN support de cours n'est reproduit ici et AUCUNE caution de l'UBa n'est revendiquée ni suggérée.\n"
                "• Kueda Wamba, Berthelo — travaux académiques publics en comptabilité/finance, Cameroun (listés sous FEMS — Faculté des Sciences Économiques et de Gestion). Mêmes termes : citation de travaux publics uniquement, aucune reproduction, aucune caution revendiquée.\n"
                "Pour trouver leurs travaux publics, cherchez le nom de l'auteur dans un index académique (par ex. Google Scholar ou AJOL — African Journals Online).\n\n"
                "UNE NOTE HONNÊTE SUR CE QUE CETTE LEÇON N'EST PAS : savoir classer actif, passif et capitaux propres — même avec un score parfait — ne fait PAS de vous un comptable, et ne vous autorise pas à exercer comme tel. La comptabilité est une profession réglementée : le titre professionnel exige des études reconnues, une expérience encadrée et, dans la plupart des pays, l'appartenance à un ordre professionnel (par exemple l'ONECCA, l'Ordre National des Experts Comptables du Cameroun, pour les professionnels comptables au Cameroun). Ce que ce cours vous donne, c'est une compréhension réelle et pratique : vous savez lire un bilan, vérifier qu'il est équilibré et expliquer d'où vient chaque chiffre. Cela vaut la peine — et ce n'est pas la même chose que d'être comptable."
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
            "question_en": "A business owns 200,000 FCFA of assets and owes 50,000 FCFA. What is the equity?",
            "question_fr": "Une entreprise possède 200 000 FCFA d'actif et doit 50 000 FCFA. Quel est le montant des capitaux propres ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "150,000 FCFA", "text_fr": "150 000 FCFA", "is_correct": True},
                {"option_key": "B", "position": 2, "text_en": "250,000 FCFA", "text_fr": "250 000 FCFA", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "50,000 FCFA", "text_fr": "50 000 FCFA", "is_correct": False},
            ],
            "explanation_en": "Assets = Liabilities + Equity, so Equity = 200,000 - 50,000 = 150,000 FCFA.",
            "explanation_fr": "Actif = Passif + Capitaux propres, donc Capitaux propres = 200 000 - 50 000 = 150 000 FCFA.",
            "correction_en": "Rearrange the equation: Equity = Assets - Liabilities, so 200,000 - 50,000.",
            "correction_fr": "Réorganisez l'équation : Capitaux propres = Actif - Passif, soit 200 000 - 50 000.",
            "remediation_section_position": 2,
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
            "correction_en": "The missing term is the owners' share — what is left once the liabilities are deducted from the assets.",
            "correction_fr": "Le terme manquant est la part des propriétaires — ce qui reste une fois le passif déduit de l'actif.",
            "remediation_section_position": 2,
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
            "correction_en": "Borrowing adds to an asset (cash) and to a liability (the loan) by the same amount, so both sides move together and the equation stays balanced.",
            "correction_fr": "Un emprunt augmente un actif (la trésorerie) et un passif (l'emprunt) du même montant : les deux côtés bougent ensemble et l'équation reste équilibrée.",
            "remediation_section_position": 3,
        },
        # --- NEW Q4 (formative): what counts as an asset -----------------------
        {
            "position": 4,
            "kind": "mcq",
            "question_en": "Mama Ndifor still owes Manka'a Provisions 22,000 FCFA for rice she took last week, and the delivery note is signed. Where does that 22,000 FCFA sit in the equation?",
            "question_fr": "Mama Ndifor doit encore 22 000 FCFA à Manka'a Provisions pour du riz pris la semaine dernière, et le bon de livraison est signé. Où se trouvent ces 22 000 FCFA dans l'équation ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "On the assets side — money owed TO the business is a receivable the shop owns", "text_fr": "Du côté de l'actif — l'argent dû À l'entreprise est une créance que la boutique possède", "is_correct": True},
                {"option_key": "B", "position": 2, "text_en": "On the liabilities side — it is money the shop owes", "text_fr": "Du côté du passif — c'est de l'argent que la boutique doit", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "Nowhere — until cash arrives, it is not recorded", "text_fr": "Nulle part — tant que l'argent n'arrive pas, rien n'est enregistré", "is_correct": False},
            ],
            "explanation_en": "The right to be paid is real value the business owns: an amount owed TO the business is an asset (a receivable). The signed delivery note proves the sale happened.",
            "explanation_fr": "Le droit d'être payé est une vraie valeur que l'entreprise possède : une somme due À l'entreprise est un actif (une créance). Le bon de livraison signé prouve que la vente a eu lieu.",
            "correction_en": "Check the direction of the debt: money the customer owes the SHOP is value the shop owns — an asset, not a liability, and it is recorded when the sale happens, not when the cash arrives.",
            "correction_fr": "Vérifiez le sens de la dette : l'argent que le client doit À LA BOUTIQUE est une valeur que la boutique possède — un actif, pas un passif — et elle s'enregistre quand la vente a lieu, pas quand l'argent arrive.",
            "remediation_section_position": 4,
        },
        # --- NEW Q5 (formative): what counts as a liability -------------------
        {
            "position": 5,
            "kind": "mcq",
            "question_en": "Nkwen Market delivered 10 bags of rice on 30-day credit and left its invoice. Where does that invoice sit in the equation?",
            "question_fr": "Nkwen Market a livré 10 sacs de riz à crédit de 30 jours et a laissé sa facture. Où se trouve cette facture dans l'équation ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "On the liabilities side — the shop must pay it within 30 days", "text_fr": "Du côté du passif — la boutique doit la payer sous 30 jours", "is_correct": True},
                {"option_key": "B", "position": 2, "text_en": "On the assets side — the invoice is a paper the shop holds", "text_fr": "Du côté de l'actif — la facture est un papier que la boutique détient", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "In equity — supplier credit always belongs to the owner", "text_fr": "Dans les capitaux propres — le crédit fournisseur appartient toujours au propriétaire", "is_correct": False},
            ],
            "explanation_en": "An unpaid supplier invoice is a payable: money the business owes to someone else — a liability — until cash or Mobile Money settles it. The paper being in the shop's hands does not make it an asset.",
            "explanation_fr": "Une facture fournisseur impayée est une dette : de l'argent que l'entreprise doit à quelqu'un d'autre — un passif — jusqu'à ce que les espèces ou le Mobile Money la règlent. Le fait que le papier soit entre les mains de la boutique n'en fait pas un actif.",
            "correction_en": "Follow the money outward: the shop OWES this amount to Nkwen Market, so it sits with what the business owes — liabilities, on the right side of the equation.",
            "correction_fr": "Suivez l'argent vers l'extérieur : la boutique DOIT cette somme à Nkwen Market, donc elle se trouve avec ce que l'entreprise doit — le passif, du côté droit de l'équation.",
            "remediation_section_position": 5,
        },
        # --- NEW Q6 (formative): the owners' share -----------------------------
        {
            "position": 6,
            "kind": "short_answer",
            "question_en": "The part of the assets that belongs to the owners, once the liabilities are taken away, is called ______",
            "question_fr": "La part de l'actif qui appartient aux propriétaires, une fois le passif retiré, s'appelle ______",
            "short_answer_en": "equity",
            "short_answer_fr": "capitaux propres",
            "explanation_en": "What is left for the owners is EQUITY: Assets − Liabilities.",
            "explanation_fr": "Ce qui reste aux propriétaires, ce sont les CAPITAUX PROPRES : Actif − Passif.",
            "correction_en": "The word you need names the owners' share — the last term of the equation Assets = Liabilities + the missing word.",
            "correction_fr": "Le mot dont vous avez besoin désigne la part des propriétaires — le dernier terme de l'équation Actif = Passif + le mot manquant.",
            "remediation_section_position": 2,
        },
        # --- NEW Q7 (consolidate): rearranging the equation -------------------
        {
            "position": 7,
            "kind": "mcq",
            "question_en": "A small tailor shop has 430,000 FCFA of assets and owes 130,000 FCFA. What is the equity?",
            "question_fr": "Un petit atelier de couture possède 430 000 FCFA d'actif et doit 130 000 FCFA. Quels sont les capitaux propres ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "300,000 FCFA", "text_fr": "300 000 FCFA", "is_correct": True},
                {"option_key": "B", "position": 2, "text_en": "560,000 FCFA", "text_fr": "560 000 FCFA", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "130,000 FCFA", "text_fr": "130 000 FCFA", "is_correct": False},
            ],
            "explanation_en": "Equity = Assets − Liabilities = 430,000 − 130,000 = 300,000 FCFA. Check: 130,000 + 300,000 = 430,000.",
            "explanation_fr": "Capitaux propres = Actif − Passif = 430 000 − 130 000 = 300 000 FCFA. Vérification : 130 000 + 300 000 = 430 000.",
            "correction_en": "Read the equation backwards for the missing number: Equity = Assets − Liabilities, so 430,000 − 130,000.",
            "correction_fr": "Lisez l'équation à l'envers pour le nombre manquant : Capitaux propres = Actif − Passif, soit 430 000 − 130 000.",
            "remediation_section_position": 2,
        },
        # --- NEW Q8 (consolidate): buying for cash moves nothing in total ------
        {
            "position": 8,
            "kind": "mcq",
            "question_en": "Manka'a buys 45,000 FCFA of cooking oil, paying cash. What happens to the totals?",
            "question_fr": "Manka'a achète 45 000 FCFA d'huile de cuisine en payant en espèces. Que deviennent les totaux ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "Total assets stay the same — cash falls 45,000 and stock rises 45,000", "text_fr": "Le total de l'actif ne change pas — la trésorerie baisse de 45 000 et les stocks montent de 45 000", "is_correct": True},
                {"option_key": "B", "position": 2, "text_en": "Total assets rise by 45,000 because the shop has more stock", "text_fr": "Le total de l'actif monte de 45 000 car la boutique a plus de stocks", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "Equity rises by 45,000 because the shop spent money", "text_fr": "Les capitaux propres montent de 45 000 car la boutique a dépensé de l'argent", "is_correct": False},
            ],
            "explanation_en": "One asset for another: cash −45,000 and stock +45,000. Total assets, liabilities and equity do not move at all.",
            "explanation_fr": "Un actif pour un autre : trésorerie −45 000 et stocks +45 000. Le total de l'actif, le passif et les capitaux propres ne bougent pas du tout.",
            "correction_en": "Follow both halves of the swap: the cash that leaves and the stock that arrives are both assets, so the asset total stays put — look for the answer where nothing grows.",
            "correction_fr": "Suivez les deux moitiés de l'échange : l'argent qui sort et le stock qui arrive sont tous deux des actifs, donc le total de l'actif reste en place — cherchez la réponse où rien ne grandit.",
            "remediation_section_position": 3,
        },
        # --- NEW Q9 (consolidate): a family withdrawal -------------------------
        {
            "position": 9,
            "kind": "mcq",
            "question_en": "The owner takes 5,000 FCFA from the till for a family need. What happens to the equation?",
            "question_fr": "Le propriétaire prend 5 000 FCFA dans la caisse pour un besoin familial. Que devient l'équation ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "Assets fall by 5,000 and equity falls by 5,000 — the equation still balances", "text_fr": "L'actif baisse de 5 000 et les capitaux propres baissent de 5 000 — l'équation reste équilibrée", "is_correct": True},
                {"option_key": "B", "position": 2, "text_en": "Assets fall by 5,000 and liabilities rise by 5,000", "text_fr": "L'actif baisse de 5 000 et le passif monte de 5 000", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "Nothing changes — family needs do not touch the books", "text_fr": "Rien ne change — les besoins familiaux ne touchent pas les livres", "is_correct": False},
            ],
            "explanation_en": "A withdrawal (drawings) is the owner taking back part of their own share: cash −5,000 and equity −5,000. Both sides fall together, so the equation still balances.",
            "explanation_fr": "Un retrait (prélèvement), c'est le propriétaire qui reprend une partie de sa propre part : trésorerie −5 000 et capitaux propres −5 000. Les deux côtés baissent ensemble, donc l'équation reste équilibrée.",
            "correction_en": "The till loses cash and the owner takes it, so neither a stranger's claim nor the stock moves — the fall lands on the owners' share, and it must fall on both sides together.",
            "correction_fr": "La caisse perd de l'argent et c'est le propriétaire qui le prend, donc ni la créance d'un tiers ni le stock ne bougent — la baisse tombe sur la part du propriétaire, et elle doit tomber des deux côtés ensemble.",
            "remediation_section_position": 6,
        },
        # --- NEW Q10 (consolidate): collecting a receivable --------------------
        {
            "position": 10,
            "kind": "mcq",
            "question_en": "Mama Ndifor settles her 22,000 FCFA rice bill in cash, and the shop issues a receipt. What happens to total assets?",
            "question_fr": "Mama Ndifor règle sa facture de riz de 22 000 FCFA en espèces, et la boutique émet un reçu. Que devient le total de l'actif ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "It stays the same — cash rises 22,000 and the receivable falls 22,000", "text_fr": "Il ne change pas — la trésorerie monte de 22 000 et la créance baisse de 22 000", "is_correct": True},
                {"option_key": "B", "position": 2, "text_en": "It rises by 22,000 because the shop received cash", "text_fr": "Il monte de 22 000 car la boutique a reçu de l'argent", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "It falls by 22,000 because a debt disappeared", "text_fr": "Il baisse de 22 000 car une dette a disparu", "is_correct": False},
            ],
            "explanation_en": "One asset for another: the cash received replaces the receivable. Total assets, liabilities and equity are completely untouched by collecting a debt.",
            "explanation_fr": "Un actif pour un autre : l'argent reçu remplace la créance. Le total de l'actif, le passif et les capitaux propres ne sont pas du tout touchés par l'encaissement d'une dette.",
            "correction_en": "The sale was already recorded when the delivery note was signed; the payment only swaps one owned thing for another — cash for the right to be paid. Nothing new enters the equation.",
            "correction_fr": "La vente a déjà été enregistrée quand le bon de livraison a été signé ; le paiement échange seulement une chose possédée contre une autre — de l'argent contre le droit d'être payé. Rien de nouveau n'entre dans l'équation.",
            "remediation_section_position": 4,
        },
        # --- NEW Q11 (consolidate): paying the supplier ------------------------
        {
            "position": 11,
            "kind": "mcq",
            "question_en": "Manka'a pays 30,000 FCFA of the Nkwen Market invoice in cash. What happens?",
            "question_fr": "Manka'a paie 30 000 FCFA de la facture de Nkwen Market en espèces. Que se passe-t-il ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "Cash falls by 30,000 and the supplier debt falls by 30,000 — the equation still balances", "text_fr": "La trésorerie baisse de 30 000 et la dette fournisseur baisse de 30 000 — l'équation reste équilibrée", "is_correct": True},
                {"option_key": "B", "position": 2, "text_en": "Cash falls by 30,000 and equity falls by 30,000", "text_fr": "La trésorerie baisse de 30 000 et les capitaux propres baissent de 30 000", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "Stock rises by 30,000 because the invoice is now paid", "text_fr": "Les stocks montent de 30 000 car la facture est maintenant payée", "is_correct": False},
            ],
            "explanation_en": "An asset and a liability fall together: cash −30,000 and the payable −30,000. Both sides shrink by the same amount, so the equation still balances.",
            "explanation_fr": "Un actif et un passif baissent ensemble : trésorerie −30 000 et dette −30 000. Les deux côtés diminuent du même montant, donc l'équation reste équilibrée.",
            "correction_en": "Paying a debt moves two places: the cash that leaves (asset) and the debt that dies (liability). The stock and the owners' share are not involved — both sides fall together.",
            "correction_fr": "Payer une dette déplace deux endroits : l'argent qui sort (actif) et la dette qui meurt (passif). Les stocks et la part du propriétaire ne sont pas concernés — les deux côtés baissent ensemble.",
            "remediation_section_position": 5,
        },
        # --- NEW Q12 (consolidate): equity from capital, profit, drawings ------
        {
            "position": 12,
            "kind": "mcq",
            "question_en": "Manka'a's owner put in 200,000 FCFA of capital, the shop kept 54,000 FCFA of profits, and the owner withdrew 4,000 FCFA. What is the equity?",
            "question_fr": "Le propriétaire de Manka'a a apporté 200 000 FCFA de capital, la boutique a conservé 54 000 FCFA de bénéfices, et le propriétaire a prélevé 4 000 FCFA. Quels sont les capitaux propres ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "250,000 FCFA", "text_fr": "250 000 FCFA", "is_correct": True},
                {"option_key": "B", "position": 2, "text_en": "254,000 FCFA", "text_fr": "254 000 FCFA", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "258,000 FCFA", "text_fr": "258 000 FCFA", "is_correct": False},
            ],
            "explanation_en": "Equity = capital put in + profits kept − drawings taken out: 200,000 + 54,000 − 4,000 = 250,000 FCFA.",
            "explanation_fr": "Capitaux propres = capital apporté + bénéfices conservés − prélèvements effectués : 200 000 + 54 000 − 4 000 = 250 000 FCFA.",
            "correction_en": "Build equity from its three sources: add the capital and the kept profits, then SUBTRACT the withdrawal — drawings pull the other way.",
            "correction_fr": "Construisez les capitaux propres à partir de leurs trois sources : ajoutez le capital et les bénéfices conservés, puis SOUSTRAYEZ le retrait — les prélèvements tirent dans l'autre sens.",
            "remediation_section_position": 6,
        },
        # --- NEW Q13 (final): worked-example totals -----------------------------
        {
            "position": 13,
            "kind": "mcq",
            "question_en": "At Wednesday closing time, Manka'a's assets total 468,000 FCFA and its liabilities total 218,000 FCFA. What is the equity?",
            "question_fr": "Le mercredi à la fermeture, l'actif de Manka'a totalise 468 000 FCFA et son passif totalise 218 000 FCFA. Quels sont les capitaux propres ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "250,000 FCFA", "text_fr": "250 000 FCFA", "is_correct": True},
                {"option_key": "B", "position": 2, "text_en": "686,000 FCFA", "text_fr": "686 000 FCFA", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "218,000 FCFA", "text_fr": "218 000 FCFA", "is_correct": False},
            ],
            "explanation_en": "Equity = 468,000 − 218,000 = 250,000 FCFA — the same figure the capital + profits − drawings road gives (200,000 + 54,000 − 4,000). Check: 218,000 + 250,000 = 468,000.",
            "explanation_fr": "Capitaux propres = 468 000 − 218 000 = 250 000 FCFA — le même chiffre que donne le chemin capital + bénéfices − prélèvements (200 000 + 54 000 − 4 000). Vérification : 218 000 + 250 000 = 468 000.",
            "correction_en": "Two roads lead to the same number: subtract liabilities from the Wednesday asset total (468,000 − 218,000), or add capital and kept profits and subtract the withdrawal.",
            "correction_fr": "Deux chemins mènent au même nombre : soustrayez le passif du total d'actif du mercredi (468 000 − 218 000), ou ajoutez le capital et les bénéfices conservés et soustrayez le retrait.",
            "remediation_section_position": 8,
        },
        # --- NEW Q14 (final): guided-practice totals ----------------------------
        {
            "position": 14,
            "kind": "mcq",
            "question_en": "At the end of Thursday, Manka'a's assets total 478,000 FCFA and its liabilities total 233,000 FCFA. What is the equity?",
            "question_fr": "À la fin du jeudi, l'actif de Manka'a totalise 478 000 FCFA et son passif totalise 233 000 FCFA. Quels sont les capitaux propres ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "245,000 FCFA", "text_fr": "245 000 FCFA", "is_correct": True},
                {"option_key": "B", "position": 2, "text_en": "250,000 FCFA — equity never moves", "text_fr": "250 000 FCFA — les capitaux propres ne bougent jamais", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "711,000 FCFA", "text_fr": "711 000 FCFA", "is_correct": False},
            ],
            "explanation_en": "Equity = 478,000 − 233,000 = 245,000 FCFA. It moved down 5,000 from Wednesday's 250,000 — exactly the family withdrawal. Check: 233,000 + 245,000 = 478,000.",
            "explanation_fr": "Capitaux propres = 478 000 − 233 000 = 245 000 FCFA. Ils ont baissé de 5 000 par rapport aux 250 000 du mercredi — exactement le retrait familial. Vérification : 233 000 + 245 000 = 478 000.",
            "correction_en": "Equity is not frozen: recompute it from the Thursday figures (478,000 − 233,000) and compare with Wednesday — the 5,000 drop is the drawings working through the equation.",
            "correction_fr": "Les capitaux propres ne sont pas figés : recalculez-les à partir des chiffres du jeudi (478 000 − 233 000) et comparez avec le mercredi — la baisse de 5 000, c'est le prélèvement qui traverse l'équation.",
            "remediation_section_position": 9,
        },
        # --- NEW Q15 (final): which side the document proves ---------------------
        {
            "position": 15,
            "kind": "mcq",
            "question_en": "The bank calls and asks for proof of the 150,000 FCFA loan figure. Which document does the bookkeeper fetch?",
            "question_fr": "La banque appelle et demande la preuve du chiffre de 150 000 FCFA de l'emprunt. Quel document le comptable va-t-il chercher ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "The bank's loan agreement with its repayment schedule", "text_fr": "Le contrat d'emprunt de la banque avec son échéancier", "is_correct": True},
                {"option_key": "B", "position": 2, "text_en": "The delivery note for Mama Ndifor's rice", "text_fr": "Le bon de livraison pour le riz de Mama Ndifor", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "The purchase receipt for the freezer", "text_fr": "Le reçu d'achat du congélateur", "is_correct": False},
            ],
            "explanation_en": "The 150,000 FCFA is a liability, and the document that proves a liability is the one that created the obligation — here, the signed loan agreement with its repayment schedule.",
            "explanation_fr": "Les 150 000 FCFA sont un passif, et le document qui prouve un passif, c'est celui qui a créé l'obligation — ici, le contrat d'emprunt signé avec son échéancier.",
            "correction_en": "Match the document to the SIDE of the equation: the loan agreement created the debt, so it proves the liability. The delivery note proves an asset (a receivable); the freezer receipt proves a different asset.",
            "correction_fr": "Associez le document au CÔTÉ de l'équation : le contrat d'emprunt a créé la dette, donc il prouve le passif. Le bon de livraison prouve un actif (une créance) ; le reçu du congélateur prouve un autre actif.",
            "remediation_section_position": 7,
        },
        # --- NEW Q16 (final): the French equation --------------------------------
        {
            "position": 16,
            "kind": "short_answer",
            "question_en": "In French, the equation reads: Actif = Passif + ______",
            "question_fr": "En français, l'équation se lit : Actif = Passif + ______",
            "short_answer_en": "equity",
            "short_answer_fr": "capitaux propres",
            "explanation_en": "Actif = Passif + Capitaux propres — the same equation in the other language.",
            "explanation_fr": "Actif = Passif + Capitaux propres — la même équation dans l'autre langue.",
            "correction_en": "Both languages carry the same three-word idea: Assets = Liabilities + the owners' share — in French, les capitaux propres.",
            "correction_fr": "Les deux langues portent la même idée en trois mots : Actif = Passif + la part des propriétaires — en français, les capitaux propres.",
            "remediation_section_position": 2,
        },
        # --- NEW Q17 (final): an unbalanced sheet means an error -----------------
        {
            "position": 17,
            "kind": "mcq",
            "question_en": "A balance sheet shows assets of 480,000 FCFA but Liabilities + Equity of only 475,000 FCFA. What is the right conclusion?",
            "question_fr": "Un bilan montre un actif de 480 000 FCFA mais Passif + Capitaux propres de seulement 475 000 FCFA. Quelle est la bonne conclusion ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "There is a recording error somewhere — the equation itself never breaks", "text_fr": "Il y a une erreur d'enregistrement quelque part — l'équation elle-même ne se brise jamais", "is_correct": True},
                {"option_key": "B", "position": 2, "text_en": "This transaction is the rare exception that breaks the equation", "text_fr": "Cette transaction est la rare exception qui brise l'équation", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "The 5,000 FCFA difference is too small to matter, so it can be ignored", "text_fr": "L'écart de 5 000 FCFA est trop petit pour compter, on peut donc l'ignorer", "is_correct": False},
            ],
            "explanation_en": "Every transaction moves two places that cancel out, so a disagreement always means a figure was missed, doubled or mistyped. The 5,000 FCFA gap is the trail that leads to the error.",
            "explanation_fr": "Chaque transaction déplace deux endroits qui s'annulent, donc un désaccord signifie toujours qu'un chiffre a été oublié, doublé ou mal saisi. L'écart de 5 000 FCFA est la piste qui mène à l'erreur.",
            "correction_en": "Blame the recording, never the equation: hunt for the missing or doubled entry — often a forgotten receipt, a twice-counted invoice, or a transposed digit.",
            "correction_fr": "Accusez l'enregistrement, jamais l'équation : cherchez l'écriture manquante ou doublée — souvent un reçu oublié, une facture comptée deux fois, ou un chiffre transposé.",
            "remediation_section_position": 3,
        },
        # --- NEW Q18 (final): honest boundary ------------------------------------
        {
            "position": 18,
            "kind": "mcq",
            "question_en": "A learner finishes this lesson on the accounting equation with a perfect score. Which statement is the honest one?",
            "question_fr": "Un apprenant termine cette leçon sur l'équation comptable avec un score parfait. Quelle affirmation est honnête ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "They can read and check a small balance sheet — but that does not make them an accountant", "text_fr": "Ils peuvent lire et vérifier un petit bilan — mais cela n'en fait pas des comptables", "is_correct": True},
                {"option_key": "B", "position": 2, "text_en": "They are now a fully qualified accountant, authorised to sign audits for any company", "text_fr": "Ils sont désormais comptable pleinement qualifié, autorisé à signer des audits pour n'importe quelle entreprise", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "They may call themselves an accountant as soon as the certificate is issued", "text_fr": "Ils peuvent se dire comptables dès que le certificat est délivré", "is_correct": False},
            ],
            "explanation_en": "This lesson builds real, practical skill — sorting assets, liabilities and equity, checking a balance sheet, tracing every number to its document — but accounting is a regulated profession: recognised study, supervised experience and professional membership (e.g. ONECCA in Cameroon) are required to be called an accountant. Knowing that boundary IS part of financial literacy.",
            "explanation_fr": "Cette leçon construit une compétence réelle et pratique — classer actif, passif et capitaux propres, vérifier un bilan, rattacher chaque chiffre à son document — mais la comptabilité est une profession réglementée : des études reconnues, une expérience encadrée et une inscription professionnelle (p. ex. l'ONECCA au Cameroun) sont exigées pour s'appeler comptable. Connaître cette limite FAIT partie de la culture financière.",
            "correction_en": "The lesson gives practical ability, not a professional title: the title requires recognised study, supervised experience and registration with a professional body.",
            "correction_fr": "La leçon donne une capacité pratique, pas un titre professionnel : le titre exige des études reconnues, une expérience encadrée et une inscription à un ordre professionnel.",
            "remediation_section_position": 10,
        },
    ],
}