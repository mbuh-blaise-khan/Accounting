"""Lesson 1 — What Accounting Is and Why It Matters.

Session 15 — full beginner expansion of the original 3-section Lesson 1,
UPGRADED IN PLACE: same slug ("what-is-accounting"), same curriculum position,
and the two ORIGINAL questions keep their positions (1 and 2), question ids,
answer ids, option keys and correct answers, so historical attempts, progress
rows, review cards, certificate eligibility and the Lesson 4 practice connector
are all untouched. The seed still only INSERTs and UPDATEs by position — it
never deletes (per the Session-13 hotfix design), so nothing that historical
rows point at can vanish.

SCENARIO: "Manka'a Provisions" — a small neighbourhood food shop in Bamenda,
Cameroon. Concrete, local, and used consistently by every section, example and
question (amounts in XAF/FCFA, zero decimals, per project convention).

REFERENCES: (a) globally recognized, freely-verifiable authoritative accounting
bodies — cited by name, standard title and URL, with NO copyrighted text
reproduced; (b) clearly-labelled OPTIONAL academic reading. UBa and FEMS are
named only as the institutions of the cited authors — NO endorsement by any
institution is claimed or implied. Nothing here states or implies that
completing this lesson or course makes anyone a professional or regulated
accountant (see the closing section, and the final exam question that pins it).
"""
LESSON = {
    # UNCHANGED identity + position: the sync upserts by slug; attempts,
    # progress and review rows reference the lesson and its questions by id.
    "slug": "what-is-accounting",
    "position": 1,
    "title_en": "What Accounting Is and Why It Matters",
    "title_fr": "Ce qu'est la comptabilité et pourquoi elle compte",
    "summary_en": "Meet a real neighbourhood shop, see why every business needs records, and learn the words accountants use — the starting point for everything else in this course.",
    "summary_fr": "Rencontrez une boutique de quartier, découvrez pourquoi toute entreprise a besoin de registres et apprenez les mots que les comptables utilisent — le point de départ de tout le reste du cours.",
    "sections": [
        # --- NEW Section 1: learning objectives + prerequisite note ----------
        {
            "position": 1,
            "heading_en": "What you will learn",
            "heading_fr": "Ce que vous allez apprendre",
            "body_en": (
                "By the end of this lesson you will be able to:\n"
                "• explain in one sentence what accounting is for;\n"
                "• tell bookkeeping apart from accounting;\n"
                "• name who reads accounting information, inside and outside a business;\n"
                "• recognise the everyday business events that must be recorded, and the source documents that prove them;\n"
                "• use the five core words — transaction, asset, liability, income, expense — correctly;\n"
                "• follow a worked example that records one day of a real shop's business.\n\n"
                "BEFORE YOU START (prerequisite): no prior accounting knowledge is needed. You should be able to read simple numbers and do basic addition and subtraction. Nothing to install — the whole lesson works on a phone.\n\n"
                "HOW THIS LESSON WORKS: read the sections in order — the worked example and the guided practice show you the method. Then answer the questions. Questions 1–6 are quick checks; Questions 7–10 are the final check of the whole lesson. Every answer gets instant feedback, and anything you miss (or answer on a guess) can come back to you later as a short scheduled review, so finishing with a perfect score is realistic, not lucky.\n\n"
                "One promise about honesty: this course teaches you accounting. It does not make you an accountant — see the last section."
            ),
            "body_fr": (
                "À la fin de cette leçon, vous serez capable de :\n"
                "• expliquer en une phrase à quoi sert la comptabilité ;\n"
                "• distinguer la tenue de livres de la comptabilité ;\n"
                "• nommer qui lit l'information comptable, à l'intérieur comme à l'extérieur d'une entreprise ;\n"
                "• reconnaître les événements d'entreprise du quotidien qui doivent être enregistrés, et les pièces justificatives qui les prouvent ;\n"
                "• utiliser correctement les cinq mots de base — transaction, actif, passif, produit, charge ;\n"
                "• suivre un exemple détaillé qui enregistre une journée d'un vrai commerce.\n\n"
                "AVANT DE COMMENCER (prérequis) : aucune connaissance préalable en comptabilité n'est nécessaire. Vous devez savoir lire des nombres simples et faire des additions et des soustractions de base. Rien à installer — toute la leçon fonctionne sur un téléphone.\n\n"
                "COMMENT SE DÉROULE CETTE LEÇON : lisez les sections dans l'ordre — l'exemple détaillé et l'exercice guidé vous montrent la méthode. Puis répondez aux questions. Les questions 1 à 6 sont des contrôles rapides ; les questions 7 à 10 sont le contrôle final de toute la leçon. Chaque réponse donne un retour immédiat, et tout ce que vous manquez (ou répondez au hasard) peut vous revenir plus tard sous forme de petite révision programmée : finir avec un score parfait est réaliste, pas une question de chance.\n\n"
                "Une promesse d'honnêteté : ce cours vous enseigne la comptabilité. Il ne fait pas de vous un comptable — voir la dernière section."
            ),
        },
        {
            "position": 2,
            "heading_en": "What accounting is",
            "heading_fr": "Ce qu'est la comptabilité",
            "body_en": (
                "Accounting is the language of business. It records what a business owns, what it owes, and what happens to its money over time. When you write down every sale and every purchase, you can look back and see clearly how the business is doing.\n\n"
                "Picture a small provisions shop in Bamenda — call it Manka'a Provisions. It sells rice, oil, soap, sugar and phone credit from dawn to dusk. The owner knows the shop \"feels busy\", but a feeling is not a fact. Accounting turns that feeling into facts: how much was sold this month, how much is owed, what is left in the till.\n\n"
                "One warning about words: the shop's daily notes are not yet accounting. They are bookkeeping — see Section 4 for the difference."
            ),
            "body_fr": (
                "La comptabilité est le langage des affaires. Elle enregistre ce qu'une entreprise possède, ce qu'elle doit et ce qu'il advient de son argent au fil du temps. Lorsque vous notez chaque vente et chaque achat, vous pouvez revenir en arrière et voir clairement comment va l'entreprise.\n\n"
                "Imaginez une petite boutique de provisions à Bamenda — appelons-la Manka'a Provisions. Elle vend du riz, de l'huile, du savon, du sucre et du crédit téléphonique du matin au soir. Le propriétaire sent que « la boutique tourne », mais un sentiment n'est pas un fait. La comptabilité transforme ce sentiment en faits : combien a été vendu ce mois-ci, combien est dû, ce qui reste dans la caisse.\n\n"
                "Une précision sur les mots : les notes quotidiennes de la boutique ne sont pas encore de la comptabilité. C'est de la tenue de livres (bookkeeping) — voir la Section 4 pour la différence."
            ),
        },
        {
            "position": 3,
            "heading_en": "Why it matters",
            "heading_fr": "Pourquoi c'est important",
            "body_en": (
                "Without records, you cannot know if your business makes money or loses it. Good accounting helps you make better decisions, pay the right taxes, and show banks or investors exactly how the business is doing.\n\n"
                "For Manka'a Provisions this is not theory. The owner wants a loan to add a small freezer. The bank asks: \"How much do you sell each month? What do you owe your suppliers? Can you repay?\" Without records the honest answer is \"I don't know\" — and the loan is refused. With twelve months of clean records, the answer is on paper.\n\n"
                "The same records serve five jobs: knowing if you made a profit, managing your cash, paying the right taxes (no more, no less), proving the truth to a bank, landlord or partner, and spotting problems early — like a supplier you quietly pay twice.\n\n"
                "In Cameroon and across the OHADA region, registered businesses keep their accounts under SYSCOHADA, the OHADA accounting system (Acte uniforme relatif au droit comptable et à l'information financière, adopted 26 January 2017, in force since 2018). You do not need to memorise that name today — only to know that the record-keeping you are learning has a legal home. See the reference list at the end of this lesson."
            ),
            "body_fr": (
                "Sans registres, vous ne pouvez pas savoir si votre entreprise gagne de l'argent ou en perd. Une bonne comptabilité vous aide à prendre de meilleures décisions, à payer les bons impôts et à montrer aux banques ou aux investisseurs exactement comment va l'entreprise.\n\n"
                "Pour Manka'a Provisions, ce n'est pas de la théorie. Le propriétaire veut un prêt pour ajouter un petit congélateur. La banque demande : « Combien vendez-vous par mois ? Que devez-vous à vos fournisseurs ? Pouvez-vous rembourser ? » Sans registres, la réponse honnête est « je ne sais pas » — et le prêt est refusé. Avec douze mois de registres propres, la réponse est sur papier.\n\n"
                "Les mêmes registres servent cinq usages : savoir si vous avez fait un bénéfice, gérer votre trésorerie, payer les bons impôts (ni plus ni moins), prouver la vérité à une banque, un bailleur ou un associé, et repérer tôt les problèmes — comme un fournisseur que vous payez deux fois sans le savoir.\n\n"
                "Au Cameroun et dans toute la zone OHADA, les entreprises enregistrées tiennent leur comptabilité selon le SYSCOHADA, le système comptable OHADA (Acte uniforme relatif au droit comptable et à l'information financière, adopté le 26 janvier 2017, en vigueur depuis 2018). Inutile de mémoriser ce nom aujourd'hui — sachez seulement que la tenue de registres que vous apprenez a un cadre légal. Voir la liste de références à la fin de cette leçon."
            ),
        },
        {
            "position": 4,
            "heading_en": "Bookkeeping is not (yet) accounting",
            "heading_fr": "La tenue de livres n'est pas (encore) la comptabilité",
            "body_en": (
                "Bookkeeping is the daily recording: every sale, every purchase, every payment, written down in date order. Accounting is what happens after and around that recording: classifying it, checking it totals up, summarising it, and explaining what the numbers mean.\n\n"
                "At Manka'a Provisions: writing \"sold 2 bags of rice, 22,000 FCFA\" in a notebook is bookkeeping. Deciding that the money is sales revenue, adding the day's totals, putting the month on an income statement, and telling the owner \"you earned about 60,000 FCFA this month after costs — the freezer loan is affordable\" is accounting.\n\n"
                "A useful image: bookkeeping lays the bricks; accounting builds — and reads — the building. Neither works without the other, and both start from the same source: the business's real events.\n\n"
                "Both bookkeeping and accounting work from business events backed by source documents — see Section 6."
            ),
            "body_fr": (
                "La tenue de livres est l'enregistrement quotidien : chaque vente, chaque achat, chaque paiement, noté dans l'ordre des dates. La comptabilité est ce qui se passe après et autour de cet enregistrement : le classer, vérifier qu'il s'additionne juste, le résumer et expliquer ce que les chiffres veulent dire.\n\n"
                "Chez Manka'a Provisions : écrire « vendu 2 sacs de riz, 22 000 FCFA » dans un cahier, c'est de la tenue de livres. Décider que cet argent est un produit des ventes, additionner les totaux du jour, placer le mois dans un compte de résultat et dire au propriétaire « vous avez gagné environ 60 000 FCFA ce mois après charges — le prêt pour le congélateur est abordable », c'est de la comptabilité.\n\n"
                "Une image utile : la tenue de livres pose les briques ; la comptabilité construit — et lit — le bâtiment. L'une ne va pas sans l'autre, et les deux partent de la même source : les événements réels de l'entreprise.\n\n"
                "La tenue de livres et la comptabilité s'appuient toutes deux sur des événements justifiés par des pièces justificatives — voir la Section 6."
            ),
        },
        {
            "position": 5,
            "heading_en": "Who reads the numbers?",
            "heading_fr": "Qui lit les chiffres ?",
            "body_en": (
                "Accounting information has readers beyond the owner. Each reader asks a different question, and the same well-kept records answer them all.\n\n"
                "Inside the business: the owner decides what to stock and whether the freezer loan is affordable; a shop manager checks margins and wants the numbers to show honest work.\n\n"
                "Outside the business: the bank asks \"can you repay?\" before lending; suppliers ask \"will you pay on time?\" before delivering on credit; the tax authority asks \"what is the right tax?\"; a potential partner or investor asks \"what is my share worth?\"; staff ask whether the business can keep them employed.\n\n"
                "Notice the pattern at Manka'a Provisions: the SAME set of records — sales, purchases, debts, cash — answers every one of them. One well-kept set of books serves all readers; a second, secret set serves none of them well."
            ),
            "body_fr": (
                "L'information comptable a des lecteurs au-delà du propriétaire. Chaque lecteur pose une question différente, et les mêmes registres bien tenus y répondent tous.\n\n"
                "À l'intérieur de l'entreprise : le propriétaire décide quoi stocker et si le prêt du congélateur est abordable ; un gérant surveille les marges et veut que les chiffres montrent un travail honnête.\n\n"
                "À l'extérieur : la banque demande « pouvez-vous rembourser ? » avant de prêter ; les fournisseurs demandent « paierez-vous à temps ? » avant de livrer à crédit ; l'administration fiscale demande « quel est le bon impôt ? » ; un associé ou investisseur potentiel demande « que vaut ma part ? » ; le personnel demande si l'entreprise peut le garder employé.\n\n"
                "Remarquez le schéma chez Manka'a Provisions : les MÊMES registres — ventes, achats, dettes, trésorerie — répondent à chacun. Un seul jeu de livres bien tenu sert tous les lecteurs ; un second jeu secret ne sert aucun d'eux."
            ),
        },
        {
            "position": 6,
            "heading_en": "Where records come from: events and source documents",
            "heading_fr": "D'où viennent les registres : événements et pièces justificatives",
            "body_en": (
                "Nothing should be written in the books because of a feeling. A record starts with a business EVENT: a sale, a purchase, a payment received, a payment made, a loan taken. And every event worth recording leaves a piece of PAPER (or its digital twin) called a source document — the evidence that the event really happened, when, for how much, and between whom.\n\n"
                "At Manka'a Provisions you will meet: the supplier's invoice for 10 bags of rice (purchase); the cash-sale receipt for 1,500 FCFA of soap (sale); the bank deposit slip (money in); the Mobile Money transaction SMS for 5,000 FCFA (money in or out — it counts); the delivery note signed when goods arrive; the cash book itself, the running written record of money in and out.\n\n"
                "Why the paper matters: a customer claims he already paid for the rice? The receipt copy settles it. The tax office asks how the month's sales were reached? The receipt book shows it. The supplier's total is wrong? The invoice says so. No document, no entry — that habit is what auditors call an audit trail: a paper path from every number in the books back to a real event.\n\n"
                "A pedantic but useful rule of thumb: records are about the BUSINESS'S money, not the owner's. When the owner takes 5,000 FCFA from the till for a family errand, that is recorded too — as the owner's own withdrawal, not as shop expense. Mixing the two is the fastest way to lose the picture."
            ),
            "body_fr": (
                "Rien ne doit être écrit dans les livres par simple impression. Un enregistrement commence par un ÉVÉNEMENT d'entreprise : une vente, un achat, un encaissement, un paiement, un emprunt. Et chaque événement digne d'enregistrement laisse un PAPIER (ou son jumeau numérique) appelé pièce justificative — la preuve que l'événement a vraiment eu lieu, quand, pour combien, et entre qui.\n\n"
                "Chez Manka'a Provisions, vous rencontrerez : la facture du fournisseur pour 10 sacs de riz (achat) ; le reçu de vente au comptant de 1 500 FCFA de savon (vente) ; le bordereau de dépôt bancaire (argent entrant) ; le SMS de transaction Mobile Money de 5 000 FCFA (entrée ou sortie — il compte) ; le bon de livraison signé à l'arrivée des marchandises ; le cahier de caisse, registre écrit et continu des entrées et sorties d'argent.\n\n"
                "Pourquoi le papier compte : un client prétend avoir déjà payé le riz ? La copie du reçu tranche. Le bureau des impôts demande comment les ventes du mois ont été obtenues ? Le carnet de reçus le montre. Le total du fournisseur est faux ? La facture le dit. Pas de document, pas d'écriture — cette habitude est ce que les auditeurs appellent une piste d'audit : un chemin papier qui relie chaque chiffre des livres à un événement réel.\n\n"
                "Une règle pédante mais utile : les registres concernent l'argent de l'ENTREPRISE, pas celui du propriétaire. Quand le propriétaire prend 5 000 FCFA dans la caisse pour une course familiale, cela s'enregistre aussi — comme retrait du propriétaire, pas comme charge de la boutique. Mélanger les deux est le moyen le plus rapide de perdre la vision claire."
            ),
        },
        {
            "position": 7,
            "heading_en": "Five words you will meet everywhere",
            "heading_fr": "Cinq mots que vous rencontrerez partout",
            "body_en": (
                "These five words carry the whole course. Learn them once, in the shop's own terms.\n\n"
                "TRANSACTION — a business event that changes the money picture and gets recorded. Selling a bag of rice for 22,000 FCFA is a transaction. Counting the bags on the shelf is not.\n\n"
                "ASSET — something the business OWNS that has value: cash in the till, rice and soap on the shelves (stock), the shop's freezer.\n\n"
                "LIABILITY — something the business OWES to others: the supplier who delivered rice on 30 days' credit, the bank loan, rent not yet paid.\n\n"
                "INCOME (revenue) — value the business EARNS by selling. Each day's cash sales at Manka'a Provisions are income, whether the money is received in cash or by Mobile Money.\n\n"
                "EXPENSE — value the business SPENDS to earn that income: transport for the stock, a freezer's electricity, the assistant's wages, airtime for the business phone.\n\n"
                "Quick check of the idea: a freezer is an asset; the electricity it uses is an expense; the bank loan that bought it is a liability; the frozen-fish sales it enables are income. Same shop, four different words — and in Lesson 2 you will see how they balance in one equation."
            ),
            "body_fr": (
                "Ces cinq mots portent tout le cours. Apprenez-les une fois, dans les termes de la boutique.\n\n"
                "TRANSACTION — un événement d'entreprise qui change la situation de l'argent et s'enregistre. Vendre un sac de riz à 22 000 FCFA est une transaction. Compter les sacs sur l'étagère n'en est pas une.\n\n"
                "ACTIF — ce que l'entreprise POSSÈDE et qui a de la valeur : la caisse, le riz et le savon sur les étagères (le stock), le congélateur.\n\n"
                "PASSIF — ce que l'entreprise DOIT à d'autres : le fournisseur qui a livré le riz à 30 jours, l'emprunt bancaire, le loyer non encore payé.\n\n"
                "PRODUIT (revenu) — de la valeur que l'entreprise GAGNE en vendant. Les ventes au comptant de chaque jour chez Manka'a Provisions sont des produits, que l'argent soit reçu en espèces ou par Mobile Money.\n\n"
                "CHARGE — de la valeur que l'entreprise DÉPENSE pour gagner ce produit : le transport du stock, l'électricité du congélateur, le salaire de l'aide, le crédit téléphonique du téléphone de la boutique.\n\n"
                "Petit contrôle de l'idée : un congélateur est un actif ; l'électricité qu'il consomme est une charge ; l'emprunt bancaire qui l'a acheté est un passif ; les ventes de poisson congelé qu'il permet sont des produits. Même boutique, quatre mots différents — et à la Leçon 2 vous verrez comment ils s'équilibrent dans une seule équation."
            ),
        },
        {
            "position": 8,
            "heading_en": "One day in the shop, written down",
            "heading_fr": "Une journée à la boutique, consignée",
            "body_en": (
                "Here is one ordinary day at Manka'a Provisions, followed by exactly what a bookkeeper writes. Follow it line by line — this is the whole skill in miniature.\n\n"
                "The day's events:\n"
                "1. Morning: buy 10 bags of rice at Nkwen wholesale market — 150,000 FCFA, paid in cash. Supplier's invoice received.\n"
                "2. Midday: sell 2 bags of rice for 44,000 FCFA cash. Receipt number 0112 issued.\n"
                "3. Afternoon: sell 1 bag for 22,000 FCFA to Mama Ndifor's kati-kati restaurant — on credit, 15 days. Delivery note signed.\n"
                "4. Evening: pay the shop's electricity bill, 8,000 FCFA cash. Receipt kept.\n\n"
                "What the records show (keep the five words in mind):\n"
                "1. Buying rice: stock goes UP 150,000 (asset up), cash goes DOWN 150,000 (another asset down). Value simply moved within the business — nothing owed, nothing earned.\n"
                "2. Cash sale: cash UP 44,000, income UP 44,000 — the business earned.\n"
                "3. Credit sale: Mama Ndifor now OWES 22,000 — and money a customer owes the shop is still an ASSET (the business owns the right to collect it). Income UP 22,000.\n"
                "4. Electricity: cash DOWN 8,000, expense UP 8,000 — value spent to run the shop.\n\n"
                "The day's result: cash 150,000 - 44,000 + 8,000 = 102,000 FCFA left after buying stock; income for the day 66,000; expenses 8,000; one debt owed TO the shop, none BY it beyond the day. Every line above traces to a source document — the invoice, receipt 0112, the delivery note, the electricity receipt. That is the audit trail from Section 6, alive on an ordinary Tuesday.\n\n"
                "Two things this day does NOT show: no double-entry debits and credits yet (Lesson 4 — for now, notice only that each event touches at least two things: stock AND cash, cash AND income, debt AND income), and no full statements yet (Lesson 7). One step at a time."
            ),
            "body_fr": (
                "Voici une journée ordinaire chez Manka'a Provisions, suivie de ce qu'un comptable écrit exactement. Suivez-la ligne par ligne — c'est toute la compétence en miniature.\n\n"
                "Les événements du jour :\n"
                "1. Matin : achat de 10 sacs de riz au marché de gros de Nkwen — 150 000 FCFA, payés en espèces. Facture du fournisseur reçue.\n"
                "2. Midi : vente de 2 sacs de riz pour 44 000 FCFA en espèces. Reçu n° 0112 émis.\n"
                "3. Après-midi : vente d'1 sac pour 22 000 FCFA au restaurant kati-kati de Mama Ndifor — à crédit, 15 jours. Bon de livraison signé.\n"
                "4. Soir : paiement de la facture d'électricité de la boutique, 8 000 FCFA en espèces. Reçu conservé.\n\n"
                "Ce que les registres montrent (gardez les cinq mots en tête) :\n"
                "1. Achat de riz : le stock AUGMENTE de 150 000 (actif en hausse), la caisse DIMINUE de 150 000 (un autre actif en baisse). La valeur a simplement bougé à l'intérieur de l'entreprise — rien n'est dû, rien n'est gagné.\n"
                "2. Vente au comptant : caisse +44 000, produit +44 000 — l'entreprise a gagné.\n"
                "3. Vente à crédit : Mama Ndifor DOIT maintenant 22 000 — et l'argent qu'un client doit à la boutique reste un ACTIF (l'entreprise possède le droit de l'encaisser). Produit +22 000.\n"
                "4. Électricité : caisse -8 000, charge +8 000 — de la valeur dépensée pour faire tourner la boutique.\n\n"
                "Le résultat du jour : trésorerie 150 000 - 44 000 + 8 000 = 102 000 FCFA restants après l'achat de stock ; produit du jour 66 000 ; charges 8 000 ; une dette DUE À la boutique, aucune DUE PAR elle au-delà de la journée. Chaque ligne ci-dessus renvoie à une pièce justificative — la facture, le reçu 0112, le bon de livraison, le reçu d'électricité. C'est la piste d'audit de la Section 6, vivante un mardi ordinaire.\n\n"
                "Deux choses que cette journée ne montre PAS : pas encore de débits et crédits en partie double (Leçon 4 — pour l'instant, remarquez seulement que chaque événement touche au moins deux choses : stock ET caisse, caisse ET produit, dette ET produit), et pas encore d'états financiers complets (Leçon 7). Une étape à la fois."
            ),
        },
        {
            "position": 9,
            "heading_en": "Your turn: read a day the bookkeeper's way",
            "heading_fr": "À vous : lire une journée comme le comptable",
            "body_en": (
                "Work through this BEFORE answering the questions below — the last questions test it directly.\n\n"
                "Wednesday at Manka'a Provisions:\n"
                "• 9:00 — buy cooking oil for 30,000 FCFA cash (supplier invoice).\n"
                "• 11:00 — sell soap for 9,000 FCFA cash (your receipt 0115).\n"
                "• 14:00 — sell rice on credit to Mama Ndifor for 18,000 FCFA (delivery note).\n"
                "• 17:00 — pay the shop assistant 5,000 FCFA for the week (signed voucher).\n"
                "• 19:00 — owner takes 4,000 FCFA from the till for a family errand.\n\n"
                "Try these three, then check yourself:\n"
                "1. Which of the five items are transactions, and which are not? (All five — each changes the money picture and has a document.)\n"
                "2. For each, name what rises and what falls in the five words: asset, liability, income, expense.\n"
                "• Oil purchase: stock (asset) up, cash (asset) down.\n"
                "• Soap sale: cash (asset) up, income up.\n"
                "• Credit rice sale: amount owed by Mama Ndifor (asset) up, income up.\n"
                "• Assistant's pay: cash down, expense up.\n"
                "• Owner's 4,000 FCFA: cash down — and NOT a shop expense; it is the owner's own withdrawal.\n"
                "3. Which documents form the audit trail for each event? (Invoice, receipt 0115, delivery note, signed voucher, and a dated note or voucher for the owner's withdrawal.)\n\n"
                "If you followed the pattern, you are ready for the questions below. It never changes: every event touches at least two of the five words, and every event has its paper."
            ),
            "body_fr": (
                "Travaillez ceci AVANT de répondre aux questions ci-dessous — les dernières questions la testent directement.\n\n"
                "Mercredi chez Manka'a Provisions :\n"
                "• 9h00 — achat d'huile de cuisine pour 30 000 FCFA en espèces (facture du fournisseur).\n"
                "• 11h00 — vente de savon pour 9 000 FCFA en espèces (votre reçu n° 0115).\n"
                "• 14h00 — vente de riz à crédit à Mama Ndifor pour 18 000 FCFA (bon de livraison).\n"
                "• 17h00 — paiement de l'aide de boutique, 5 000 FCFA pour la semaine (bon signé).\n"
                "• 19h00 — le propriétaire prend 4 000 FCFA dans la caisse pour une course familiale.\n\n"
                "Essayez ces trois points, puis vérifiez-vous :\n"
                "1. Quels éléments parmi les cinq sont des transactions, et lesquels ne le sont pas ? (Les cinq — chacun change la situation de l'argent et a un document.)\n"
                "2. Pour chacun, nommez ce qui augmente et ce qui diminue avec les cinq mots : actif, passif, produit, charge.\n"
                "• Achat d'huile : stock (actif) en hausse, caisse (actif) en baisse.\n"
                "• Vente de savon : caisse (actif) en hausse, produit en hausse.\n"
                "• Vente de riz à crédit : la somme due par Mama Ndifor (actif) en hausse, produit en hausse.\n"
                "• Paie de l'aide : caisse en baisse, charge en hausse.\n"
                "• Les 4 000 FCFA du propriétaire : caisse en baisse — et PAS une charge de la boutique ; c'est un retrait du propriétaire.\n"
                "3. Quels documents forment la piste d'audit de chaque événement ? (Facture, reçu n° 0115, bon de livraison, bon signé, et une note datée ou un bon pour le retrait du propriétaire.)\n\n"
                "Si vous avez suivi le schéma, vous êtes prêt pour les questions ci-dessous. Il ne change jamais : chaque événement touche au moins deux des cinq mots, et chaque événement a son papier."
            ),
        },
        {
            "position": 10,
            "heading_en": "Where these ideas come from — and an honest note",
            "heading_fr": "D'où viennent ces idées — et une note honnête",
            "body_en": (
                "AUTHORITATIVE SOURCES (freely verifiable; cited by name — no text reproduced):\n"
                "• OHADA, \"Acte uniforme relatif au droit comptable et à l'information financière\" (SYSCOHADA, adopted 26 January 2017, revised text) — ohada.org — the accounting law for Cameroon and the other OHADA member states. This lesson's mention of SYSCOHADA is a signpost, not the law itself; this platform's charts are an illustrative demo subset, not an official chart.\n"
                "• IFRS Foundation / International Accounting Standards Board, \"IFRS Accounting Standards\" and the Conceptual Framework for Financial Reporting — ifrs.org — the global reference for financial reporting (the other framework this platform can practise in).\n"
                "• IFAC / IAESB, \"International Education Standards\" — ifac.org — how professional accounting competence is built through study and PRACTISED experience.\n"
                "• ACCA, \"Foundations in Accountancy (FIA)\" syllabus overview — accaglobal.com — a public, free-to-view syllabus whose early progression this course sequence mirrors.\n\n"
                "OPTIONAL ACADEMIC READING (clearly labelled; supplementary only):\n"
                "• Neba, Akoso Wilfred — public academic work in accounting and finance education, University of Bamenda (UBa), Cameroon. Listed for learners who want a local academic perspective. Public listable work only; NO teaching materials are reproduced here and NO UBa endorsement of this platform is claimed or implied.\n"
                "• Kueda Wamba, Berthelo — public academic work in accounting/finance, Cameroon (listed under FEMS — Faculty of Economics and Management Sciences). Same terms: citation of public work only, no reproduction, no endorsement claimed.\n"
                "To find their public work, search an academic index (e.g. Google Scholar or AJOL — African Journals Online) for the author name. Their published papers are independent works; nothing from them is copied into this platform.\n\n"
                "AN HONEST NOTE ABOUT WHAT THIS LESSON IS NOT: completing this lesson — or this whole course with its certificate — does NOT make you an accountant, and it does not authorise you to practise as one. Accounting is a regulated profession: professional designation requires recognised study, supervised experience and, in most places, membership of a professional body (for example ONECCA, the Ordre National des Experts Comptables du Cameroun, for professional accountants in Cameroon). What this course gives you is real, practical understanding: you will be able to keep the books of a small business, read its statements, and speak the language accountants use. That is worth having — and it is not the same as being one."
            ),
            "body_fr": (
                "SOURCES FAISANT AUTORITÉ (librement vérifiables ; citées par leur nom — aucun texte reproduit) :\n"
                "• OHADA, « Acte uniforme relatif au droit comptable et à l'information financière » (SYSCOHADA, adopté le 26 janvier 2017, texte révisé) — ohada.org — le droit comptable du Cameroun et des autres États parties OHADA. La mention du SYSCOHADA dans cette leçon est un panneau indicateur, pas le droit lui-même ; les plans comptables de cette plateforme sont un sous-ensemble de démonstration illustratif, pas un plan officiel.\n"
                "• IFRS Foundation / International Accounting Standards Board, « IFRS Accounting Standards » et le Conceptual Framework for Financial Reporting — ifrs.org — la référence mondiale en information financière (l'autre cadre dans lequel cette plateforme permet de s'exercer).\n"
                "• IFAC / IAESB, « International Education Standards » — ifac.org — comment la compétence comptable professionnelle se construit par l'étude et l'expérience PRATIQUE encadrée.\n"
                "• ACCA, « Foundations in Accountancy (FIA) » aperçu du programme — accaglobal.com — un programme public consultable gratuitement dont la progression initiale inspire l'ordre de ce cours.\n\n"
                "LECTURES ACADÉMIQUES OPTIONNELLES (clairement étiquetées ; complémentaires seulement) :\n"
                "• Neba, Akoso Wilfred — travaux académiques publics en comptabilité et enseignement de la finance, Université de Bamenda (UBa), Cameroun. Listé pour les apprenants qui veulent une perspective académique locale. Travaux publics listables uniquement ; AUCUN support de cours n'est reproduit ici et AUCUNE caution de l'UBa n'est revendiquée ni suggérée.\n"
                "• Kueda Wamba, Berthelo — travaux académiques publics en comptabilité/finance, Cameroun (listés sous FEMS — Faculté des Sciences Économiques et de Gestion). Mêmes termes : citation de travaux publics uniquement, aucune reproduction, aucune caution revendiquée.\n"
                "Pour trouver leurs travaux publics, cherchez le nom de l'auteur dans un index académique (par ex. Google Scholar ou AJOL — African Journals Online). Leurs articles publiés sont des œuvres indépendantes ; rien de leur contenu n'est copié dans cette plateforme.\n\n"
                "UNE NOTE HONNÊTE SUR CE QUE CETTE LEÇON N'EST PAS : terminer cette leçon — ou tout ce cours avec son certificat — ne fait PAS de vous un comptable, et ne vous autorise pas à exercer comme tel. La comptabilité est une profession réglementée : le titre professionnel exige des études reconnues, une expérience encadrée et, dans la plupart des pays, l'appartenance à un ordre professionnel (par exemple l'ONECCA, l'Ordre National des Experts Comptables du Cameroun, pour les professionnels comptables au Cameroun). Ce que ce cours vous donne, c'est une compréhension réelle et pratique : vous saurez tenir les livres d'une petite entreprise, lire ses états financiers et parler le langage des comptables. Cela vaut la peine — et ce n'est pas la même chose que d'être comptable."
            ),
        },
    ],
    "questions": [
        # --- Q1/Q2: the ORIGINAL two questions. Same positions (1, 2), same
        # kind, same option keys and correct flags (A correct on both), so the
        # upsert keeps every existing question/answer id, and every historical
        # attempt / review card / progress row stays valid. Only the
        # remediation pointer of Q2 moves (to the new vocabulary section).
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
            "remediation_section_position": 3,
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
            "remediation_section_position": 7,
        },
        # --- NEW Q3 (formative): bookkeeping vs accounting -------------------
        {
            "position": 3,
            "kind": "mcq",
            "question_en": "Which statement about bookkeeping and accounting is TRUE?",
            "question_fr": "Quelle affirmation sur la tenue de livres et la comptabilité est VRAIE ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "They are two names for exactly the same job", "text_fr": "Ce sont deux noms pour exactement le même travail", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "Bookkeeping is the daily recording; accounting is the wider work of classifying, checking, summarising and explaining", "text_fr": "La tenue de livres est l'enregistrement quotidien ; la comptabilité est le travail plus large de classement, de vérification, de résumé et d'explication", "is_correct": True},
                {"option_key": "C", "position": 3, "text_en": "Accounting is only needed by big companies", "text_fr": "La comptabilité n'est nécessaire qu'aux grandes entreprises", "is_correct": False},
                {"option_key": "D", "position": 4, "text_en": "Bookkeeping happens only once a year, at tax time", "text_fr": "La tenue de livres se fait une fois par an, au moment des impôts", "is_correct": False},
            ],
            "explanation_en": "The daily, in-date-order recording is bookkeeping. Accounting classifies, checks, summarises and explains those numbers — for the owner, the bank and the tax authority alike.",
            "explanation_fr": "L'enregistrement quotidien dans l'ordre des dates est la tenue de livres. La comptabilité classe, vérifie, résume et explique ces chiffres — pour le propriétaire, la banque et l'administration fiscale.",
            "correction_en": "The daily recording is one job; the wider work of classifying, checking, summarising and explaining it is the other. They are related but not identical.",
            "correction_fr": "L'enregistrement quotidien est un travail ; le travail plus large de classement, de vérification, de résumé et d'explication en est un autre. Ils sont liés mais pas identiques.",
            "remediation_section_position": 4,
        },
        # --- NEW Q4 (formative): source documents ----------------------------
        {
            "position": 4,
            "kind": "mcq",
            "question_en": "Which of these is a source document proving a PURCHASE?",
            "question_fr": "Lequel de ces éléments est une pièce justificative prouvant un ACHAT ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "The supplier's invoice for the goods", "text_fr": "La facture du fournisseur pour les marchandises", "is_correct": True},
                {"option_key": "B", "position": 2, "text_en": "The owner's memory of the deal", "text_fr": "Le souvenir du propriétaire de l'accord", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "A customer's kind compliment", "text_fr": "Un compliment gentil d'un client", "is_correct": False},
                {"option_key": "D", "position": 4, "text_en": "The shop's painted signboard", "text_fr": "L'enseigne peinte de la boutique", "is_correct": False},
            ],
            "explanation_en": "A source document is written (or digital) evidence of a real event. The supplier's invoice proves the purchase — its date, amount and parties.",
            "explanation_fr": "Une pièce justificative est une preuve écrite (ou numérique) d'un événement réel. La facture du fournisseur prouve l'achat — sa date, son montant et ses parties.",
            "correction_en": "Look for written evidence of the event itself: what was bought, for how much, when, and between whom.",
            "correction_fr": "Cherchez une preuve écrite de l'événement lui-même : ce qui a été acheté, pour combien, quand, et entre qui.",
            "remediation_section_position": 6,
        },
        # --- NEW Q5 (formative): vocabulary — asset vs expense ----------------
        {
            "position": 5,
            "kind": "mcq",
            "question_en": "The shop buys a freezer to keep drinks cold. The ELECTRICITY the freezer uses every evening is best described as…",
            "question_fr": "La boutique achète un congélateur pour garder les boissons au frais. L'ÉLECTRICITÉ que le congélateur consomme chaque soir se décrit mieux comme…",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "An asset — something the business owns for years", "text_fr": "Un actif — quelque chose que l'entreprise possède pendant des années", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "A liability — money the business owes the electric company", "text_fr": "Un passif — de l'argent que l'entreprise doit à la société d'électricité", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "An expense — a cost of running the shop", "text_fr": "Une charge — un coût de fonctionnement de la boutique", "is_correct": True},
                {"option_key": "D", "position": 4, "text_en": "Income — money coming in", "text_fr": "Un produit — de l'argent qui entre", "is_correct": False},
            ],
            "explanation_en": "The freezer itself is the asset (the business owns it and will use it for years). The electricity it consumes is an expense — value used up to keep the shop running.",
            "explanation_fr": "Le congélateur lui-même est l'actif (l'entreprise le possède et l'utilisera pendant des années). L'électricité qu'il consomme est une charge — de la valeur consommée pour faire tourner la boutique.",
            "correction_en": "The electricity is value used up by the business to earn its sales — it is consumed, not owned. The freezer is what is owned; an unpaid electricity bill would be what is owed.",
            "correction_fr": "L'électricité est de la valeur consommée par l'entreprise pour réaliser ses ventes — elle est consommée, pas possédée. Le congélateur est ce qui est possédé ; une facture d'électricité impayée serait ce qui est dû.",
            "remediation_section_position": 7,
        },
        # --- NEW Q6 (formative): users of accounting information -------------
        {
            "position": 6,
            "kind": "mcq",
            "question_en": "The owner wants a bank loan for a freezer. Which users of accounting information does this involve?",
            "question_fr": "Le propriétaire veut un prêt bancaire pour un congélateur. Quels utilisateurs de l'information comptable cela concerne-t-il ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "Nobody — the accounting records stay private and unused", "text_fr": "Personne — les registres comptables restent privés et inutilisés", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "Only the tax authority, which sets the loan rate", "text_fr": "Uniquement l'administration fiscale, qui fixe le taux du prêt", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "The owner (an internal user) and the bank (an external user) — both read the same records", "text_fr": "Le propriétaire (un utilisateur interne) et la banque (une utilisatrice externe) — tous deux lisent les mêmes registres", "is_correct": True},
            ],
            "explanation_en": "Inside the business, the owner decides the loan is worth applying for. Outside it, the bank reads the records to judge whether the loan is safe. One well-kept set of books serves both.",
            "explanation_fr": "À l'intérieur, le propriétaire décide que le prêt vaut la peine d'être demandé. À l'extérieur, la banque lit les registres pour juger si le prêt est sûr. Un seul jeu de livres bien tenu sert les deux.",
            "correction_en": "A loan decision has a reader inside the business (the owner) and one outside it (the bank) — the same records answer both.",
            "correction_fr": "Une décision de prêt a un lecteur à l'intérieur de l'entreprise (le propriétaire) et un à l'extérieur (la banque) — les mêmes registres répondent aux deux.",
            "remediation_section_position": 5,
        },
        # --- NEW Q7 (FINAL CHECK): short answer — the "owes" word -------------
        {
            "position": 7,
            "kind": "short_answer",
            "question_en": "One word completes this sentence: something a business OWES to others — like the rice supplier who delivered on 30 days' credit — is called a ______.",
            "question_fr": "Un mot complète cette phrase : ce que l'entreprise DOIT à d'autres — comme le fournisseur de riz qui a livré à 30 jours — s'appelle un ______.",
            "short_answer_en": "liability",
            "short_answer_fr": "passif",
            "explanation_en": "A liability is something the business owes to others. The unpaid supplier bill is the classic small-business example — and in Lesson 2 you will see liabilities standing beside assets in the one equation that never breaks.",
            "explanation_fr": "Un passif est ce que l'entreprise doit à d'autres. La facture fournisseur impayée en est l'exemple classique des petites entreprises — et à la Leçon 2 vous verrez les passifs à côté des actifs dans l'unique équation qui ne se casse jamais.",
            "correction_en": "The word you need names what the business OWES to others — the opposite side of the five-word set from what it OWNS. The vocabulary section spells it out in capital letters.",
            "correction_fr": "Le mot dont vous avez besoin désigne ce que l'entreprise DOIT à d'autres — le côté opposé de l'ensemble de cinq mots commençant par ce qu'elle POSSÈDE. La section de vocabulaire l'épelle en lettres majuscules.",
            "remediation_section_position": 7,
        },
        # --- NEW Q8 (FINAL CHECK): worked-example application -----------------
        {
            "position": 8,
            "kind": "mcq",
            "question_en": "The shop sells 1 bag of rice for 22,000 FCFA to a restaurant, to be paid in 15 days, and the delivery note is signed. Immediately after this single event…",
            "question_fr": "La boutique vend 1 sac de riz à 22 000 FCFA à un restaurant, payable dans 15 jours, et le bon de livraison est signé. Immédiatement après cet événement unique…",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "Nothing is recorded yet, because no cash was received", "text_fr": "Rien n'est encore enregistré, parce qu'aucune espèce n'a été reçue", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "An asset rises by 22,000 (the amount owed by the customer) and income rises by 22,000", "text_fr": "Un actif augmente de 22 000 (la somme due par le client) et un produit augmente de 22 000", "is_correct": True},
                {"option_key": "C", "position": 3, "text_en": "An expense rises by 22,000 because the rice left the shop", "text_fr": "Une charge augmente de 22 000 parce que le riz a quitté la boutique", "is_correct": False},
                {"option_key": "D", "position": 4, "text_en": "A liability rises by 22,000 because the shop now owes the customer", "text_fr": "Un passif augmente de 22 000 parce que la boutique doit maintenant de l'argent au client", "is_correct": False},
            ],
            "explanation_en": "The sale happened, so it is recorded: the customer now owes the shop 22,000 — money the business owns the right to collect, an asset — and income of 22,000 was earned. Credit sales are recorded when they happen, not when cash arrives.",
            "explanation_fr": "La vente a eu lieu, donc elle s'enregistre : le client doit désormais 22 000 à la boutique — de l'argent que l'entreprise possède le droit d'encaisser, un actif — et un produit de 22 000 a été gagné. Les ventes à crédit s'enregistrent quand elles ont lieu, pas quand l'argent arrive.",
            "correction_en": "Record the event when it happens: the customer's debt TO the shop is an asset (not a liability — that would be what the SHOP owes), and the income is earned at the sale itself.",
            "correction_fr": "Enregistrez l'événement quand il a lieu : la dette du client ENVERS la boutique est un actif (pas un passif — le passif serait ce que la BOUTIQUE doit), et le produit est gagné au moment de la vente.",
            "remediation_section_position": 8,
        },
        # --- NEW Q9 (FINAL CHECK): guided-practice application — audit trail --
        {
            "position": 9,
            "kind": "mcq",
            "question_en": "Wednesday's records say the till should hold 21,000 FCFA, but counting it gives only 19,000 FCFA. What should the bookkeeper do first?",
            "question_fr": "Les registres du mercredi indiquent que la caisse devrait contenir 21 000 FCFA, mais en la comptant on ne trouve que 19 000 FCFA. Que devrait faire d'abord le comptable ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "Adjust the records down to 19,000 so the books match the cash", "text_fr": "Ajuster les registres à 19 000 pour que les livres correspondent à la caisse", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "Ignore it — small differences are normal and never matter", "text_fr": "L'ignorer — les petits écarts sont normaux et n'ont jamais d'importance", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "Re-check the day's source documents and entries to find where the 2,000 went", "text_fr": "Revérifier les pièces justificatives et les écritures du jour pour trouver où sont passés les 2 000", "is_correct": True},
            ],
            "explanation_en": "The audit trail is exactly for this: trace each entry back to its source document and re-check the arithmetic until the 2,000 difference is explained (a missed sale, a mis-copied figure, a note never written). Changing the books to hide a difference destroys the trail — and in this app, posted records are never silently edited; corrections go through reversing entries.",
            "explanation_fr": "La piste d'audit sert exactement à cela : remonter chaque écriture à sa pièce justificative et revérifier les calculs jusqu'à ce que l'écart de 2 000 soit expliqué (une vente oubliée, un chiffre mal recopié, une note jamais écrite). Modifier les livres pour masquer un écart détruit la piste — et dans cette application, les écritures publiées ne sont jamais modifiées en silence ; les corrections passent par des écritures inverses.",
            "correction_en": "Follow the paper first: re-check the day's documents and entries one by one until the difference is explained. Never rewrite the books to match the cash.",
            "correction_fr": "Suivez d'abord le papier : revérifiez les documents et les écritures du jour un par un jusqu'à ce que l'écart soit expliqué. Ne réécrivez jamais les livres pour les faire correspondre à la caisse.",
            "remediation_section_position": 9,
        },
        # --- NEW Q10 (FINAL CHECK): the honest boundary ------------------------
        {
            "position": 10,
            "kind": "mcq",
            "question_en": "After finishing this whole course, a learner can keep the books of a small business. Which statement is TRUE?",
            "question_fr": "Après avoir terminé tout ce cours, un apprenant peut tenir les livres d'une petite entreprise. Quelle affirmation est VRAIE ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "They are now a fully qualified accountant, authorised to sign audits for any company", "text_fr": "Ils sont désormais comptable pleinement qualifié, autorisé à signer des audits pour n'importe quelle entreprise", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "They can keep real books and read statements, but that does not by itself make them an accountant — that requires recognised study, supervised experience and professional registration", "text_fr": "Ils peuvent tenir de vrais livres et lire des états financiers, mais cela n'en fait pas pour autant des comptables — cela exige des études reconnues, une expérience encadrée et une inscription professionnelle", "is_correct": True},
                {"option_key": "C", "position": 3, "text_en": "They may call themselves an accountant as soon as the certificate is issued", "text_fr": "Ils peuvent se dire comptables dès que le certificat est délivré", "is_correct": False},
            ],
            "explanation_en": "This course builds real, practical skill — recording, source documents, the five words, reading a day's numbers — but accounting is a regulated profession: recognised study, supervised experience and professional membership (e.g. ONECCA in Cameroon) are required to be called an accountant. Knowing that boundary IS part of financial literacy.",
            "explanation_fr": "Ce cours construit une compétence réelle et pratique — enregistrement, pièces justificatives, les cinq mots, lecture des chiffres d'une journée — mais la comptabilité est une profession réglementée : des études reconnues, une expérience encadrée et une inscription professionnelle (p. ex. l'ONECCA au Cameroun) sont exigées pour s'appeler comptable. Connaître cette limite FAIT partie de la culture financière.",
            "correction_en": "The course gives practical ability, not a professional title: the title requires recognised study, supervised experience and registration with a professional body.",
            "correction_fr": "Le cours donne une capacité pratique, pas un titre professionnel : le titre exige des études reconnues, une expérience encadrée et une inscription à un ordre professionnel.",
            "remediation_section_position": 10,
        },
    ],
}