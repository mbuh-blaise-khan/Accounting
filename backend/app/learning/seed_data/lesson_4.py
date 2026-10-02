"""Lesson 4 - Recording a transaction (journal entries), and the PRACTICE
connector.

Expanded IN PLACE (same slug "journal-entries", same curriculum position 4, same
EN/FR titles). The two ORIGINAL questions keep their positions (1, 2), their
question ids, answer ids, option keys, correct answers, explanations,
corrections and the practice-connector flag/amount, so historical attempts,
progress rows, review cards, current mastery and certificate eligibility are
untouched. The seed only INSERTs and UPDATEs - it never deletes - so nothing a
historical row points at can vanish. `attempts.selected_answer_id` is a foreign
key to `answers.id`, so a historic attempt records WHICH ANSWER ROW was picked,
never a display index: stored rows may never be reordered or removed.

SCOPE - this lesson is DISTINCT from its neighbours:
  Lesson 1 = what accounting is and why records exist;
  Lesson 2 = the accounting equation;
  Lesson 3 = WHICH SIDE (debit or credit) an account moves on;
  Lesson 4 = HOW A REAL BUSINESS EVENT, sitting on a piece of paper in a real
             shop, is turned into a dated, narrated, balanced journal entry.
Lesson 3 gave the rule; Lesson 4 applies it to documents, dates, narrations and
the written shape of an entry.

SCENARIO: "Manka'a Provisions" - the same neighbourhood food shop in Bamenda,
Cameroon used in Lessons 1-3, so the whole course follows one continuous
business (XAF/FCFA, zero decimals, per project convention).

ANSWER-POSITION INTEGRITY: the new closed-ended questions deliberately place the
correct option at DIFFERENT authored positions so the answer is never revealed
by layout alone, and this lesson is registered in the engine's deterministic
display-order gate (`_OPTION_ORDER_LESSON_SLUGS` in app/learning/service.py),
which permutes the SERVED option order from the immutable question/answer ids.
The gate is safe here because no question in this lesson asks the learner to
read options IN a meaningful order: every option list is a set of alternative
candidate entries, documents, dates or statements. The order that matters
(debit side vs credit side, date vs narration) lives INSIDE each option's text,
which the permutation never touches. Grading is unaffected: the server resolves
the submitted `option_key` to its Answer row by id.

PRACTICE CONNECTOR CONTRACT (unchanged): a CORRECT answer on the flagged
question posts the fixed, balanced cash sale (Cash Dr / Sales Cr, 25,000) into
the caller's own demo workspace, through the org's own chart (OHADA 5711/7011,
IFRS names), validated for membership by `get_organization_for_user`. Posting is
IDEMPOTENT: a refresh, a retry, or a duplicate submission returns the SAME
transaction id and creates no second transaction (see `_existing_practice_post`
in app/learning/service.py).

REFERENCES: (a) globally recognised, freely-verifiable authoritative accounting
bodies - cited by name, standard title and URL, with NO copyrighted text
reproduced; (b) clearly-labelled OPTIONAL academic reading. UBa and FEMS are
named only as the institutions of the cited authors - NO endorsement by any
institution is claimed or implied. Nothing here states or implies that
completing this lesson or the course makes anyone a professional or regulated
accountant.
"""
LESSON = {
    "slug": "journal-entries",
    "position": 4,
    "title_en": "Recording a transaction (journal entries)",
    "title_fr": "Enregistrer une opération (écritures de journal)",
    "summary_en": "A real business event arrives on a piece of paper. This lesson walks from the source document to a dated, narrated, balanced journal entry - using a real week in a Bamenda shop.",
    "summary_fr": "Une opération réelle arrive sur un papier. Ce cours va du document source vers une écriture de journal datée, narrée et équilibrée - en s'appuyant sur une vraie semaine dans une boutique de Bamenda.",
    "sections": [
        # --- Section 1: objectives, prerequisite, how the lesson works --------
        {
            "position": 1,
            "heading_en": "What you will learn",
            "heading_fr": "Ce que vous allez apprendre",
            "body_en": (
                "By the end of this lesson you will be able to:\n"
                "• name the source document behind a transaction, and say why the document comes before the entry;\n"
                "• analyse a transaction in four steps before you touch a single account;\n"
                "• write a journal entry with its date, its narration, its account names, its Dr/Cr marks and its amounts;\n"
                "• check that an entry balances before anybody tries to post it;\n"
                "• read an entry somebody else wrote and say, in plain words, what happened to the business;\n"
                "• deal with a mistake the honest way, instead of erasing history.\n\n"
                "BEFORE YOU START\n"
                "You need Lesson 1 (what accounting is), Lesson 2 (the accounting equation) and Lesson 3 (debits and credits). Lesson 3 taught you WHICH SIDE an account moves on. This lesson is about the other half of the job: turning a real event, on a real piece of paper, into a properly written entry.\n\n"
                "THE SHOP WE FOLLOW\n"
                "Every example in this lesson is one real week at Manka'a Provisions, the neighbourhood food shop in Bamenda used throughout this course. You are the person writing the entries. Nkwen Market is the supplier, Mama Ndifor is the customer who pays late, ENEO brings the electricity bill, and the owner takes cash out for her family. Amounts are all in XAF/FCFA with no decimals.\n\n"
                "HOW THIS LESSON WORKS\n"
                "Read the text first, then answer the 18 questions in a fixed order, one at a time. Get one wrong and you get an explanation, a plain correction, a link back to the section that covers it, and that question goes into your review queue. The lesson moves on to the NEXT question - it never repeats the same question to make you look busy.\n\n"
                "AN HONEST PROMISE\n"
                "This is teaching, not a qualification. Nothing here is an OHADA certificate, an IFRS accreditation, a university degree or a professional-body membership, and finishing this course does not turn anybody into an accountant."
            ),
            "body_fr": (
                "À la fin de cette leçon, vous serez capable de :\n"
                "• nommer le document source d'une opération, et dire pourquoi le document vient avant l'écriture ;\n"
                "• analyser une opération en quatre étapes avant de toucher au moindre compte ;\n"
                "• écrire une écriture de journal avec sa date, sa narration, ses noms de comptes, ses mentions Dr/Cr et ses montants ;\n"
                "• vérifier qu'une écriture s'équilibre avant que quiconque ne tente de la publier ;\n"
                "• lire une écriture écrite par quelqu'un d'autre et dire, en mots simples, ce qui est arrivé à l'entreprise ;\n"
                "• traiter une erreur honnêtement, au lieu d'effacer l'histoire.\n\n"
                "AVANT DE COMMENCER\n"
                "Vous avez besoin de la Leçon 1 (ce qu'est la comptabilité), de la Leçon 2 (l'équation comptable) et de la Leçon 3 (le débit et le crédit). La Leçon 3 vous a appris DE QUEL CÔTÉ un compte bouge. Cette leçon traite de l'autre moitié du travail : transformer un événement réel, posé sur un vrai papier, en une écriture correctement rédigée.\n\n"
                "LA BOUTIQUE QUE NOUS SUIVONS\n"
                "Tous les exemples de cette leçon forment une semaine réelle chez Manka'a Provisions, la boutique alimentaire de quartier de Bamenda utilisée dans tout ce cours. C'est vous qui rédigez les écritures. Nkwen Market est le fournisseur, Mama Ndifor la cliente qui paie tard, ENEO apporte la facture d'électricité, et la propriétaire retire de l'argent pour sa famille. Tous les montants sont en XAF/FCFA, sans décimales.\n\n"
                "COMMENT SE DÉROULE CETTE LEÇON\n"
                "Lisez d'abord le texte, puis répondez aux 18 questions dans un ordre fixe, une par une. Si vous vous trompez, vous obtenez une explication, une correction en langage clair, un lien vers la section qui traite du sujet, et la question rejoint votre file de révision. La leçon passe à la question SUIVANTE - elle ne répète jamais la même question pour vous donner l'illusion d'avancer.\n\n"
                "UNE PROMESSE HONNÊTE\n"
                "Ceci est un enseignement, pas une qualification. Rien ici n'est un certificat OHADA, une accréditation IFRS, un diplôme universitaire ou une adhésion à un ordre professionnel, et terminer ce cours ne transforme personne en comptable."
            ),
        },
        # --- Section 2: what the journal IS (original section-1 territory) ---
        {
            "position": 2,
            "heading_en": "The journal: the diary of the business",
            "heading_fr": "Le journal : l'agenda de l'entreprise",
            "body_en": (
                "The journal is where every transaction is first written down. Each journal entry shows the date, a short description of what happened, the account(s) to debit, the account(s) to credit, and the amounts. It is the first stop on a transaction's journey through the books - and because it is written in DATE ORDER, it is also the first place an auditor, a bank or a tax officer looks to see what really happened, and when.\n\n"
                "Two habits follow from that, and they are the habits of every bookkeeping office in Cameroon and across the OHADA region:\n"
                "• The journal is CHRONOLOGICAL. Wednesday's entries sit together, in order, before Thursday's. You may go back and add something you forgot, but you never shuffle an old entry to make the page look tidy.\n"
                "• The journal is APPEND-ONLY. A posted entry is never edited and never deleted. A mistake is fixed with a CORRECTING entry on a later date, or with a reversing entry - Section 9 comes back to this.\n\n"
                "Because every transaction reaches the journal from a real piece of paper, the next section looks at that paper first."
            ),
            "body_fr": (
                "Le journal est l'endroit où chaque transaction est d'abord écrite. Chaque écriture de journal indique la date, une courte description de ce qui s'est passé, le ou les comptes à débiter, le ou les comptes à créditer, et les montants. C'est la première étape du voyage d'une transaction dans les livres - et parce qu'il est rédigé DANS L'ORDRE DES DATES, c'est aussi le premier endroit où un auditeur, une banque ou un service fiscal ira voir ce qui s'est réellement passé, et quand.\n\n"
                "Deux habitudes en découlent, et ce sont celles de tous les services de comptabilité du Cameroun et de la zone OHADA :\n"
                "• Le journal est CHRONOLOGIQUE. Les écritures du mercredi sont regroupées, dans l'ordre, avant celles du jeudi. Vous pouvez revenir ajouter un oubli, mais vous ne réorganisez jamais une ancienne écriture pour rendre la page plus jolie.\n"
                "• Le journal s'AJOUTE SEULEMENT. Une écriture publiée n'est jamais modifiée ni supprimée. Une erreur se corrige par une écriture CORRECTIVE à une date ultérieure, ou par une écriture inverse - la Section 9 y reviendra.\n\n"
                "Comme chaque transaction arrive au journal depuis un vrai papier, la section suivante regarde d'abord ce papier."
            ),
        },
        # --- Section 3: source documents (what the paper proves) -------------
        {
            "position": 3,
            "heading_en": "Source documents: the paper behind the entry",
            "heading_fr": "Les documents sources : le papier derrière l'écriture",
            "body_en": (
                "Nothing goes into the journal because somebody remembered it. Every entry starts as a SOURCE DOCUMENT - the piece of paper that proves the event happened. The document is kept, and the journal line points back to it. That is the whole idea of an audit trail.\n\n"
                "The documents you will meet in a small shop in Cameroon:\n"
                "• SALES RECEIPT - goods sold for cash. Proves money came in AND what was sold.\n"
                "• INVOICE (facture) - goods received from a supplier. If it says 'to pay' or 'à payer', the shop now OWES the supplier: the debt exists the moment the invoice is booked, not when it is paid.\n"
                "• BANK / MOBILE MONEY SLIP - money moved through the bank account or a Mobile Money float. It proves the CASH side; it rarely tells you what the money was for, so it always needs a narration.\n"
                "• ELECTRICITY, WATER OR INTERNET BILL (ENEO, Camwater, Camtel) - a cost that must be split between what is a charge now and what is a fixed asset over time. In this beginner lesson, treat a shop's ordinary monthly bills as expenses.\n"
                "• CREDIT NOTE (avoir) - a supplier gives money back, or reduces what was owed. It is a credit-side event.\n"
                "• OWNER'S NOTE - cash the owner puts in, or takes out for personal use. Money in the till is not automatically profit.\n\n"
                "The habit to build: BEFORE you write anything, find the document. If you cannot find it, you do not have a transaction yet - you have a story."
            ),
            "body_fr": (
                "Rien n'entre au journal parce que quelqu'un s'en souvient. Chaque écriture part d'un DOCUMENT SOURCE - le papier qui prouve que l'événement a eu lieu. Le document est conservé, et la ligne du journal y renvoie. C'est toute l'idée d'une piste d'audit.\n\n"
                "Les documents que vous rencontrerez dans une petite boutique au Cameroun :\n"
                "• REÇU DE VENTE - marchandises vendues contre espèces. Prouve l'argent encaissé ET ce qui a été vendu.\n"
                "• FACTURE - marchandises reçues d'un fournisseur. Si elle porte la mention « à payer », la boutique DOIT désormais de l'argent au fournisseur : la dette existe dès l'enregistrement de la facture, pas au moment du paiement.\n"
                "• RELEVÉ BANCAIRE / REÇU MOBILE MONEY - l'argent est passé par la banque ou par un flottant Mobile Money. Il prouve le côté TRÉSORERIE ; il dit rarement à quoi sert l'argent, d'où la nécessité d'une narration.\n"
                "• FACTURE D'ÉLECTRICITÉ, D'EAU OU D'INTERNET (ENEO, Camwater, Camtel) - un coût à partager entre ce qui est une charge maintenant et ce qui est une immobilisation sur plusieurs exercices. Dans cette leçon pour débutants, traitez les factures mensuelles ordinaires de la boutique comme des charges.\n"
                "• AVOIR - un fournisseur rembourse, ou réduit ce qui était dû. C'est un événement côté crédit.\n"
                "• NOTE DU PROPRIÉTAIRE - l'argent que le propriétaire injecte, ou retire pour son usage personnel. L'argent dans la caisse n'est pas automatiquement un bénéfice.\n\n"
                "L'habitude à construire : AVANT d'écrire quoi que ce soit, trouvez le document. Si vous ne le trouvez pas, vous n'avez pas encore une transaction - vous avez une histoire."
            ),
        },
        # --- Section 4: transaction analysis, four steps ---------------------
        {
            "position": 4,
            "heading_en": "Transaction analysis: four questions before you write",
            "heading_fr": "Analyse de l'opération : quatre questions avant d'écrire",
            "body_en": (
                "A document in your hand is not yet an entry. Between the paper and the journal there are four questions, and you answer them in the same order every time.\n\n"
                "1) WHAT HAPPENED, in one sentence, without any accounting word? 'Sold 10 bags of rice for 120,000 FCFA, paid in cash.' 'Bought 10 bags of rice for 120,000 FCFA on credit.' 'Paid an 8,000 FCFA electricity bill in cash.'\n"
                "2) WHICH ACCOUNTS MOVE? Name every account whose balance changes. Two accounts in this lesson; three or four when tax or a discount is involved. If you cannot name them, you have not understood the event yet.\n"
                "3) WHICH WAY DOES EACH ONE MOVE? Apply Lesson 3, once per account: an asset or an expense grows with a DEBIT; a liability, an income or equity grows with a CREDIT. Write Dr or Cr after the account name.\n"
                "4) DOES IT BALANCE? Add the debit column, add the credit column, compare. This is not optional and it is not a formality. This app enforces the balance at the service layer - an unbalanced entry is refused before it can reach the ledger, exactly as it would be in a real bookkeeping office.\n\n"
                "A useful self-check that catches most beginner mistakes: after your four answers, ask 'has anything appeared from nowhere?' A transaction cannot create value by itself - cash always arrives from somewhere (capital, a loan, a sale) and always leaves to somewhere (stock, expenses, drawings, a debt)."
            ),
            "body_fr": (
                "Un document dans votre main n'est pas encore une écriture. Entre le papier et le journal, il y a quatre questions, et vous y répondez toujours dans le même ordre.\n\n"
                "1) QUE S'EST-IL PASSÉ, en une phrase, sans aucun mot comptable ? « Vendu 10 sacs de riz pour 120 000 FCFA, payé en espèces. » « Acheté 10 sacs de riz pour 120 000 FCFA à crédit. » « Payé une facture d'électricité de 8 000 FCFA en espèces. »\n"
                "2) QUELS COMPTES BOUGENT ? Nommez tous les comptes dont le solde change. Deux comptes dans cette leçon ; trois ou quatre quand la TVA ou une remise intervient. Si vous n'arrivez pas à les nommer, vous n'avez pas encore compris l'événement.\n"
                "3) DANS QUEL SENS ? Appliquez la Leçon 3, une fois par compte : un actif ou une charge augmente au DÉBIT ; un passif, un produit ou les capitaux propres augmentent au CRÉDIT. Écrivez Dr ou Cr après le nom du compte.\n"
                "4) EST-CE ÉQUILIBRÉ ? Additionnez la colonne débit, additionnez la colonne crédit, comparez. Ce n'est pas facultatif et ce n'est pas une formalité. Cette application impose l'équilibre au niveau du service - une écriture déséquilibrée est refusée avant d'atteindre le grand livre, exactement comme dans un vrai service de comptabilité.\n\n"
                "Un auto-contrôle qui attrape la plupart des erreurs de débutant : après vos quatre réponses, demandez-vous « quelque chose est-il apparu de nulle part ? » Une transaction ne peut pas créer de la valeur par elle-même - la trésorerie arrive toujours de quelque part (capital, emprunt, vente) et part toujours vers quelque chose (stocks, charges, prélèvements, dette)."
            ),
        },
        # --- Section 5: the anatomy of the entry (date, narration, Dr/Cr) ---
        {
            "position": 5,
            "heading_en": "The anatomy of a journal entry",
            "heading_fr": "L'anatomie d'une écriture de journal",
            "body_en": (
                "A journal entry has five parts. Learn the five, and you can write any entry this course asks for.\n\n"
                "THE DATE. The date of the TRANSACTION, not the date you got round to writing it. If Nkwen Market's invoice is dated 4 March and you type it on 6 March, it is a 4 March entry. This is the difference between correct and sloppy, and it is why the journal is read in date order.\n\n"
                "THE NARRATION (French: libellé). One short line saying what the entry is FOR. A bank slip by itself only says '25,000 moved'; the narration says '25,000 received from Mama Ndifor for goods sold on credit'. A good narration can be understood two years later by somebody who has never met you: name the document, the counterparty, and what it was for. 'Being a debit' is not a narration.\n\n"
                "THE ACCOUNT NAMES. Use the exact names from your own chart of accounts, never a nickname. The shop's cash is called Cash; the supplier you owe is called Trade payables. A nickname like 'money' or 'Nkwen' will not reconcile with anything.\n\n"
                "Dr OR Cr, WRITTEN AFTER THE ACCOUNT NAME. This is the standard convention in double-entry bookkeeping: 'Cash ........... Dr 25,000' and 'Sales ......... Cr 25,000'. Dr and Cr are labels for the two columns, not amounts, and they are never placed in the amount column.\n\n"
                "THE AMOUNTS. One amount per line, same currency, no decimals in XAF. If a line needs two amounts, it needs two lines.\n\n"
                "And the totals, written at the foot of the entry: total debits and total credits, and they must be equal. That single line is the most useful sentence in accounting."
            ),
            "body_fr": (
                "Une écriture de journal comporte cinq parties. Apprenez les cinq, et vous pourrez écrire n'importe quelle écriture demandée dans ce cours.\n\n"
                "LA DATE. La date de l'OPÉRATION, pas la date à laquelle vous avez trouvé le temps de la saisir. Si la facture de Nkwen Market est datée du 4 mars et que vous la saisissez le 6 mars, c'est une écriture du 4 mars. C'est la différence entre rigoureux et approximatif, et c'est pourquoi le journal se lit dans l'ordre des dates.\n\n"
                "LA NARRATION (libellé). Une ligne courte disant à quoi sert l'écriture. Un relevé bancaire seul dit seulement « 25 000 ont circulé » ; la narration dit « 25 000 reçus de Mama Ndifor pour marchandises vendues à crédit ». Une bonne narration doit être comprise deux ans plus tard par quelqu'un qui ne vous a jamais rencontré : nommez le document, le counterpartaire et l'objet de l'opération. « C'est un débit » n'est pas une narration.\n\n"
                "LES NOMS DE COMPTES. Utilisez les noms exacts de votre propre plan de comptes, jamais un surnom. La caisse de la boutique s'appelle Trésorerie ; le fournisseur que vous devez s'appelle Fournisseurs. Un surnom comme « argent » ou « Nkwen » ne rapprochera d'aucun compte.\n\n"
                "Dr OU Cr, ÉCRITS APRÈS LE NOM DU COMPTE. C'est la convention en comptabilité en partie double : « Trésorerie ......... Dr 25 000 » et « Ventes ............... Cr 25 000 ». Dr et Cr sont des étiquettes pour les deux colonnes, pas des montants, et ils ne vont jamais dans la colonne des montants.\n\n"
                "LES MONTANTS. Un montant par ligne, même devise, sans décimales en XAF. Si une ligne a besoin de deux montants, elle a besoin de deux lignes.\n\n"
                "Et les totaux, inscrits au pied de l'écriture : total des débits et total des crédits, et ils doivent être égaux. Cette seule ligne est la phrase la plus utile de la comptabilité."
            ),
        },
        # --- Section 6: the two columns, left and right ----------------------
        {
            "position": 6,
            "heading_en": "Two columns, and what belongs in each",
            "heading_fr": "Deux colonnes, et ce qui va dans chacune",
            "body_en": (
                "A journal page has a debit column on the LEFT and a credit column on the RIGHT. That is the whole layout. Everything else - the narration, the account names, the Dr/Cr marks - is arranged so that a reader can trace one line straight across to its partner on the other side.\n\n"
                "Debit column (left): assets that grow, expenses that happen, liabilities that shrink, income that shrinks.\n"
                "Credit column (right): assets that shrink, liabilities that grow, equity and income that grow, expenses that are reversed.\n\n"
                "Two habits make the page readable:\n"
                "• Indent the credit line under the debit line when the debit line's amount continues to several credits (one purchase, three suppliers). The amount is written ONCE, on the first line, never repeated.\n"
                "• Date every entry, and date it once. A page with an undated entry is a page nobody can trust at the end of the year.\n\n"
                "Note carefully: a debit and a credit are not 'money in' and 'money out', and they are not 'good' and 'bad'. They are simply the two sides of the same coin, and the entry is finished only when the two columns agree. Lesson 3 gave you the side; this section gives you the page."
            ),
            "body_fr": (
                "Une page de journal a une colonne débit à GAUCHE et une colonne crédit à DROITE. C'est toute la mise en page. Tout le reste - la narration, les noms de comptes, les mentions Dr/Cr - est disposé pour qu'un lecteur puisse suivre une ligne jusqu'à sa ligne partenaire en face.\n\n"
                "Colonne débit (gauche) : les actifs qui augmentent, les charges qui surviennent, les passifs qui diminuent, les produits qui diminuent.\n"
                "Colonne crédit (droite) : les actifs qui diminuent, les passifs qui augmentent, les capitaux propres et les produits qui augmentent, les charges reprises.\n\n"
                "Deux habitudes rendent la page lisible :\n"
                "• Indentez la ligne crédit sous la ligne débit lorsque le montant de la ligne débit se répartit sur plusieurs crédits (un achat, trois fournisseurs). Le montant s'écrit UNE SEULE FOIS, sur la première ligne, jamais répété.\n"
                "• Datez chaque écriture, et datez-la une seule fois. Une page avec une écriture non datée est une page en laquelle personne ne peut avoir confiance en fin d'exercice.\n\n"
                "À retenir : un débit et un crédit ne sont pas « l'argent qui rentre » et « l'argent qui sort », ni « bien » et « mal ». Ce sont simplement les deux faces de la même pièce, et l'écriture n'est terminée que lorsque les deux colonnes concordent. La Leçon 3 vous a donné le côté ; cette section vous donne la page."
            ),
        },
        # --- Section 7: worked example, a full day (documents -> entries) -----
        {
            "position": 7,
            "heading_en": "Worked example: Thursday at the shop",
            "heading_fr": "Exemple corrigé : jeudi à la boutique",
            "body_en": (
                "Work through this BEFORE answering Questions 11-15. Three documents, three entries, written the way a bookkeeper writes them. Every amount is in XAF.\n\n"
                "DOCUMENT 1 - a bank/Mobile Money slip for 25,000 FCFA received on 3 March, from Mama Ndifor.\n"
                "What happened: she paid 25,000 for goods sold on credit two weeks earlier.\n"
                "Accounts: Cash grows. Trade payables shrink (the shop no longer owes her).\n"
                "Entry, 3 March:\n"
                "   Cash ................. Dr 25,000\n"
                "       Trade payables .... Cr 25,000\n"
                "   Narration: Cash received from Mama Ndifor - settling the 25,000 owed.\n"
                "Balanced: 25,000 = 25,000.\n\n"
                "DOCUMENT 2 - supplier invoice from Nkwen Market, dated 3 March, 10 bags of rice at 12,000 each, 120,000 total, payable in 15 days.\n"
                "What happened: the shop bought goods on credit. The debt exists now, because the invoice says 'payable'.\n"
                "Accounts: Stock grows. Trade payables grow.\n"
                "Entry, 3 March:\n"
                "   Stock ................. Dr 120,000\n"
                "       Trade payables .... Cr 120,000\n"
                "   Narration: Purchase of 10 bags of rice from Nkwen Market, invoice 0117, payable in 15 days.\n"
                "Balanced: 120,000 = 120,000.\n\n"
                "DOCUMENT 3 - the owner takes 15,000 FCFA cash out of the till for her own family on 3 March.\n"
                "What happened: the owner's drawings. This is NOT an expense - the shop bought nothing.\n"
                "Accounts: Cash shrinks. Owner's drawings (equity) shrink.\n"
                "Entry, 3 March:\n"
                "   Owner's drawings ...... Dr 15,000\n"
                "       Cash .............. Cr 15,000\n"
                "   Narration: Cash withdrawn by the owner for personal use.\n"
                "Balanced: 15,000 = 15,000.\n\n"
                "Day totals: debits 25,000 + 120,000 + 15,000 = 160,000. Credits 25,000 + 120,000 + 15,000 = 160,000. The day balances.\n\n"
                "Three documents, three entries, three dates - and notice that not one of them involved a sale. Recording is not only about revenue."
            ),
            "body_fr": (
                "Faites cet exercice AVANT de répondre aux questions 11 à 15. Trois documents, trois écritures, rédigées comme les rédige un comptable. Tous les montants sont en XAF.\n\n"
                "DOCUMENT 1 - un relevé bancaire / Mobile Money de 25 000 FCFA reçus le 3 mars, de Mama Ndifor.\n"
                "Ce qui s'est passé : elle a payé 25 000 FCFA pour des marchandises vendues à crédit deux semaines plus tôt.\n"
                "Comptes : la Trésorerie augmente. Les Fournisseurs diminuent (la boutique ne lui doit plus rien).\n"
                "Écriture du 3 mars :\n"
                "   Trésorerie ............ Dr 25 000\n"
                "       Fournisseurs ..... Cr 25 000\n"
                "   Narration : Trésorerie reçue de Mama Ndifor - règlement des 25 000 dus.\n"
                "Équilibré : 25 000 = 25 000.\n\n"
                "DOCUMENT 2 - facture du fournisseur Nkwen Market, datée du 3 mars, 10 sacs de riz à 12 000 chacun, 120 000 au total, payable à 15 jours.\n"
                "Ce qui s'est passé : la boutique a acheté des marchandises à crédit. La dette existe dès maintenant, puisque la facture indique « payable ».\n"
                "Comptes : les Stocks augmentent. Les Fournisseurs augmentent.\n"
                "Écriture du 3 mars :\n"
                "   Stocks ................ Dr 120 000\n"
                "       Fournisseurs ..... Cr 120 000\n"
                "   Narration : Achat de 10 sacs de riz à Nkwen Market, facture 0117, payable à 15 jours.\n"
                "Équilibré : 120 000 = 120 000.\n\n"
                "DOCUMENT 3 - la propriétaire retire 15 000 FCFA en espèces de la caisse le 3 mars pour sa famille.\n"
                "Ce qui s'est passé : les prélèvements du propriétaire. Ce n'est PAS une charge - la boutique n'a rien acheté.\n"
                "Comptes : la Trésorerie diminue. Les prélèvements du propriétaire (capitaux propres) diminuent.\n"
                "Écriture du 3 mars :\n"
                "   Prélèvements ......... Dr 15 000\n"
                "       Trésorerie ....... Cr 15 000\n"
                "   Narration : Espèces retirées par le propriétaire pour usage personnel.\n"
                "Équilibré : 15 000 = 15 000.\n\n"
                "Totaux de la journée : débits 25 000 + 120 000 + 15 000 = 160 000. Crédits 25 000 + 120 000 + 15 000 = 160 000. La journée s'équilibre.\n\n"
                "Trois documents, trois écritures, trois dates - et remarquez qu'aucune ne concernait une vente. Enregistrer, ce n'est pas seulement parler de chiffre d'affaires."
            ),
        },
        # --- Section 8: guided practice ---------------------------------------
        {
            "position": 8,
            "heading_en": "Your turn: two more documents to analyse",
            "heading_fr": "À vous : deux documents de plus à analyser",
            "body_en": (
                "Try these yourself on paper first, then compare with the answers underneath. Same shop, Friday 4 March.\n\n"
                "DOCUMENT A - Nkwen Market's bank shows the shop paid 120,000 FCFA on 4 March, against invoice 0117.\n"
                "Think: which accounts move, and in which direction? This is the SECOND half of a purchase - the first half put a debt in the books, and this half removes it.\n\n"
                "DOCUMENT B - Mama Ndifor buys goods for 22,000 FCFA on 4 March and says she will come back and pay next week. The shop writes her a sales invoice.\n"
                "Think: has any cash moved? No. So which account replaces Cash on the debit side?\n\n"
                "THE ANSWERS.\n"
                "A) The debt is settled. Trade payables shrinks with a DEBIT; Cash shrinks with a CREDIT.\n"
                "   Trade payables ..... Dr 120,000\n"
                "       Cash ........... Cr 120,000\n"
                "   Narration: Payment to Nkwen Market, settling invoice 0117.\n\n"
                "B) No cash moved, but the shop has earned income and acquired a debtor. Cash is replaced by the customer's own account, which grows with a DEBIT.\n"
                "   Trade receivables .. Dr 22,000\n"
                "       Sales ........... Cr 22,000\n"
                "   Narration: Credit sale to Mama Ndifor, invoice 0121, to be paid next week.\n\n"
                "Notice that B is the entry Question 1 of this lesson asks about in its cash form. Same event, different moment: when the customer pays, Cash is debited and Trade receivables is credited for exactly the same 25,000 in Question 1's case. That pair is called a SETTLEMENT, and it is how a receivable is cleared."
            ),
            "body_fr": (
                "Essayez par vous-même sur une feuille avant de comparer avec les réponses ci-dessous. Même boutique, vendredi 4 mars.\n\n"
                "DOCUMENT A - la banque de Nkwen Market indique que la boutique a payé 120 000 FCFA le 4 mars, contre la facture 0117.\n"
                "Réfléchissez : quels comptes bougent, et dans quel sens ? C'est la SECONDE moitié d'un achat - la première moitié a inscrit une dette dans les livres, celle-ci la supprime.\n\n"
                "DOCUMENT B - Mama Ndifor achète des marchandises pour 22 000 FCFA le 4 mars et dit qu'elle reviendra payer la semaine prochaine. La boutique lui établit une facture de vente.\n"
                "Réfléchissez : de l'argent a-t-il bougé ? Non. Alors quel compte remplace la Trésorerie du côté débit ?\n\n"
                "LES RÉPONSES.\n"
                "A) La dette est réglée. Les Fournisseurs diminuent au DÉBIT ; la Trésorerie diminue au CRÉDIT.\n"
                "   Fournisseurs ........ Dr 120 000\n"
                "       Trésorerie ...... Cr 120 000\n"
                "   Narration : Versement à Nkwen Market, règlement de la facture 0117.\n\n"
                "B) Aucun argent n'a bougé, mais la boutique a gagné un produit et acquis un débiteur. La Trésorerie est remplacée par le compte du client, qui augmente au DÉBIT.\n"
                "   Créances clients ... Dr 22 000\n"
                "       Ventes ........... Cr 22 000\n"
                "   Narration : Vente à crédit à Mama Ndifor, facture 0121, payable la semaine prochaine.\n\n"
                "Remarquez que B est l'écriture que la question 1 de cette leçon demande, dans sa forme espèces. Même événement, moment différent : quand la cliente paie, la Trésorerie est débitée et les Créances clients créditées du même montant - 25 000 dans le cas de la question 1. Ce couple s'appelle un RÈGLEMENT, et c'est ainsi qu'une créance se solde."
            ),
        },
        # --- Section 9: errors, corrections, review support -------------------
        {
            "position": 9,
            "heading_en": "When you get it wrong: corrections, remediation and review",
            "heading_fr": "Quand vous vous trompez : corrections, remédiation et révision",
            "body_en": (
                "Everyone gets entries wrong at the start. What matters is what happens next, both in the books and in this lesson.\n\n"
                "A WRONG ENTRY IN THE BOOKS. A posted entry is never edited and never deleted. There are two honest repairs, and both keep the history intact:\n"
                "• CORRECTING ENTRY - you write a second entry on the date you noticed, with a narration that says plainly 'to correct the entry of 3 March: rent was 60,000, not 6,000'. The wrong figure stays visible forever; the reader can see both and understand what happened.\n"
                "• REVERSING ENTRY - you write an entry that exactly cancels the original (the same accounts, same amounts, sides swapped), then a fresh correct entry. This is the standard method for a wrong POSTED entry, and it is the only method used by this platform.\n\n"
                "A WRONG ANSWER IN THIS LESSON. Nothing bad happens. You get an explanation of the accounting idea behind the question, a plain correction, and a 'Review this concept' button that takes you to the exact section that covers it. That question is added to your spaced-review queue, so it comes back to you later at the right moment. Then you carry on with the NEXT question - which is a different question, not a repeat of the one you just missed. Answering the same question again immediately would only test your memory of the options, not your understanding.\n\n"
                "You can also flag how you answered. If you chose 'I got it, but I guessed', the question is scheduled for review even though it was right - which is exactly what you want, because a guessed answer that is not revisited is an answer you do not have. Confidence never changes your score; it only changes what gets scheduled."
            ),
            "body_fr": (
                "Tout le monde se trompe d'écriture au début. Ce qui compte, c'est ce qui se passe ensuite, tant dans les livres que dans cette leçon.\n\n"
                "UNE MAUVAISE ÉCRITURE DANS LES LIVRES. Une écriture publiée n'est jamais modifiée ni supprimée. Il existe deux réparations honnêtes, et les deux préservent l'historique :\n"
                "• ÉCRITURE CORRECTIVE - vous écrivez une seconde écriture à la date où vous avez constaté l'erreur, avec une narration qui dit clairement « pour corriger l'écriture du 3 mars : le loyer était de 60 000, non 6 000 ». Le mauvais chiffre reste visible indéfiniment ; le lecteur voit les deux et comprend ce qui s'est passé.\n"
                "• ÉCRITURE INVERSE - vous écrivez une écriture qui annule exactement l'originale (les mêmes comptes, les mêmes montants, les côtés inversés), puis une nouvelle écriture correcte. C'est la méthode standard pour une écriture publiée erronée, et c'est la seule méthode utilisée par cette plateforme.\n\n"
                "UNE MAUVAISE RÉPONSE DANS CETTE LEÇON. Rien de grave ne se passe. Vous obtenez une explication de l'idée comptable derrière la question, une correction en langage clair, et un bouton « Revoir ce concept » qui vous amène à la section exacte qui la traite. La question est ajoutée à votre file de révision espacée, pour revenir plus tard au bon moment. Vous poursuivez ensuite avec la question SUIVANTE - une question différente, et non une répétition de celle que vous venez de manquer. Répondre tout de suite à la même question ne testerait que votre mémoire des options, pas votre compréhension.\n\n"
                "Vous pouvez aussi indiquer comment vous avez répondu. Si vous choisissez « J'ai trouvé, mais j'ai deviné », la question est programmée pour révision même si elle était juste - et c'est exactement ce qu'il faut, car une réponse devinée et jamais revue n'est pas une réponse que vous possédez. La confiance ne change jamais votre score ; elle ne change que ce qui est programmé."
            ),
        },
        # --- Section 10: going further, sources, honest note ------------------
        {
            "position": 10,
            "heading_en": "Going further - and one honest note",
            "heading_fr": "Pour aller plus loin - et une note honnête",
            "body_en": (
                "AUTHORITATIVE SOURCES (freely verifiable; named by title - nothing reproduced):\n"
                "• OHADA, \"Acte uniforme relatif au droit comptable et a l'information financiere\" (SYSCOHADA, adopted 26 January 2017, revised text) - ohada.org - the accounting law of Cameroon and the other OHADA member states. It is the framework in which the journal concept taught here lives: an entry is written from a piece of justification and kept in a chronological register. Mentioning SYSCOHADA is a signpost, not the law itself; the charts of accounts in this platform are an illustrative demo subset, NOT an official chart.\n"
                "• IFRS Foundation / International Accounting Standards Board, \"IFRS Accounting Standards\" and the Conceptual Framework for Financial Reporting - ifrs.org - the global reference for financial reporting (the other framework this platform can practise in).\n"
                "• IFAC / IAESB, \"International Education Standards\" - ifac.org - how professional accounting competence is built through study and PRACTISED experience.\n"
                "• ACCA, \"Foundations in Accountancy (FIA)\" syllabus overview - accaglobal.com - a public, free-to-view syllabus whose early progression this course sequence mirrors.\n\n"
                "OPTIONAL ACADEMIC READING (clearly labelled; supplementary only):\n"
                "• Neba, Akoso Wilfred - public academic work in accounting and finance education, University of Bamenda (UBa), Cameroon. Listed for learners who want a local academic perspective. Public listable work only; NO teaching materials are reproduced here and NO UBa endorsement of this platform is claimed or implied.\n"
                "• Kueda Wamba, Berthelo - public academic work in accounting/finance, Cameroon (listed under FEMS - Faculty of Economics and Management Sciences). Same terms: citation of public work only, no reproduction, no endorsement claimed.\n"
                "To find their public work, search an academic index (e.g. Google Scholar or AJOL - African Journals Online) for the author name.\n\n"
                "AN HONEST NOTE ABOUT WHAT THIS LESSON IS NOT: being able to take a document and write a dated, narrated, balanced journal entry - even with a perfect score - does NOT make you an accountant, and it does not authorise you to practise as one, to sign a financial statement, or to file accounts on anyone's behalf. Accounting is a regulated profession: professional designation requires recognised study, supervised experience and, in most places, membership of a professional body (for example ONECCA, the Ordre National des Experts Comptables du Cameroun). What this course gives you is real, practical understanding: you can read a document and prove that the entry it produced balances. That is worth having - and it is not the same as being one."
            ),
            "body_fr": (
                "SOURCES FAISANT AUTORITÉ (librement vérifiables ; citées par leur titre - rien n'est reproduit) :\n"
                "• OHADA, « Acte uniforme relatif au droit comptable et à l'information financière » (SYSCOHADA, adopté le 26 janvier 2017, texte révisé) - ohada.org - le droit comptable du Cameroun et des autres États parties OHADA. C'est le cadre dans lequel vit la notion de journal enseignée ici : une écriture est établie à partir d'une pièce justificative et conservée dans un registre chronologique. La mention du SYSCOHADA est un panneau indicateur, pas le droit lui-même ; les plans de comptes de cette plateforme sont un sous-ensemble de démonstration illustratif, PAS un plan officiel.\n"
                "• IFRS Foundation / International Accounting Standards Board, « IFRS Accounting Standards » et le Conceptual Framework for Financial Reporting - ifrs.org - la référence mondiale en information financière (l'autre cadre dans lequel cette plateforme permet de s'exercer).\n"
                "• IFAC / IAESB, « International Education Standards » - ifac.org - comment la compétence comptable professionnelle se construit par l'étude et l'expérience PRATIQUE encadrée.\n"
                "• ACCA, « Foundations in Accountancy (FIA) » aperçu du programme - accaglobal.com - un programme public consultable gratuitement dont la progression initiale inspire l'ordre de ce cours.\n\n"
                "LECTURES ACADÉMIQUES OPTIONNELLES (clairement indiquées ; complémentaires uniquement) :\n"
                "• Neba, Akoso Wilfred - travaux académiques publics en comptabilité et enseignement de la finance, Université de Bamenda (UBa), Cameroun. Listé pour les apprenants qui veulent une perspective académique locale. Travaux publics listables uniquement ; AUCUN support de cours n'est reproduit ici et AUCUNE caution de l'UBa n'est revendiquée ni suggérée.\n"
                "• Kueda Wamba, Berthelo - travaux académiques publics en comptabilité/finance, Cameroun (listés sous FEMS - Faculté des Sciences Économiques et de Gestion). Mêmes termes : citation de travaux publics uniquement, aucune reproduction, aucune caution revendiquée.\n"
                "Pour trouver leurs travaux publics, cherchez le nom de l'auteur dans un index académique (par ex. Google Scholar ou AJOL - African Journals Online).\n\n"
                "UNE NOTE HONNÊTE SUR CE QUE CETTE LEÇON N'EST PAS : savoir transformer un document en une écriture de journal datée, narrée et équilibrée - même avec un score parfait - ne fait PAS de vous un comptable, et ne vous autorise pas à exercer comme tel, à signer des états financiers, ni à déposer des comptes pour qui que ce soit. La comptabilité est une profession réglementée : le titre professionnel exige des études reconnues, une expérience encadrée et, dans la plupart des pays, l'appartenance à un ordre professionnel (par exemple l'ONECCA, l'Ordre National des Experts Comptables du Cameroun). Ce que ce cours vous donne, c'est une compréhension réelle et pratique : vous savez lire un document et prouver que l'écriture qu'il a produite s'équilibre. Cela vaut la peine - et ce n'est pas la même chose que d'être comptable."
            ),
        },
    ],
    "questions": [
        # --- ORIGINAL Q1 (position 1) - UNCHANGED, incl. the PRACTICE
        #     CONNECTOR flag and amount. Its remediation pointer now resolves to
        #     section 5 (the anatomy of an entry), which carries the same
        #     "how do you write one" meaning the original section 2 had.
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
            "remediation_section_position": 5,
            # PRACTICE CONNECTOR: a correct answer posts this exact cash sale
            # into the user's demo workspace (Learn -> Practice). The flag, the
            # amount and the posting behaviour are UNCHANGED by this expansion.
            "posts_demo_transaction": True,
            "practice_amount": 25000,
        },
        # --- ORIGINAL Q2 (position 2) - UNCHANGED. Its remediation pointer now
        #     resolves to section 2 (what the journal IS), which carries the
        #     same "why does the journal exist" meaning the original section 1
        #     had.
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
            "remediation_section_position": 2,
        },
        # --- NEW Q3 (source documents) --------------------------------------
        {
            "position": 3,
            "kind": "mcq",
            "question_en": "Nkwen Market delivers 10 bags of rice and sends a document dated 3 March saying 'payable in 15 days', 120,000 FCFA total. Which document is that?",
            "question_fr": "Nkwen Market livre 10 sacs de riz et envoie un document daté du 3 mars mentionnant « payable à 15 jours », 120 000 FCFA au total. Quel est ce document ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "A sales receipt, because the shop has received goods", "text_fr": "Un reçu de vente, puisque la boutique a reçu des marchandises", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "A bank statement, because it mentions a payment date", "text_fr": "Un relevé bancaire, parce qu'il mentionne une date de paiement", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "A supplier invoice, because it states what was bought and that it is payable", "text_fr": "Une facture fournisseur, parce qu'elle indique ce qui a été acheté et que c'est payable", "is_correct": True},
            ],
            "explanation_en": "An invoice from a supplier is the source document for goods received. Because it says 'payable in 15 days', it proves the shop now OWES the supplier: the debt exists when the invoice is booked, not when it is paid.",
            "explanation_fr": "Une facture fournisseur est le document source des marchandises reçues. Parce qu'elle indique « payable à 15 jours », elle prouve que la boutique DOIT désormais de l'argent au fournisseur : la dette existe à l'enregistrement de la facture, pas au paiement.",
            "correction_en": "A sales receipt proves money came IN from a customer. An invoice from a supplier proves goods came IN and that the shop now owes for them. When the invoice says 'payable', record the debt immediately.",
            "correction_fr": "Un reçu de vente prouve l'argent reçu d'un client. Une facture fournisseur prouve les marchandises reçues et la dette qui en découle. Quand la facture indique « payable », enregistrez la dette immédiatement.",
            "remediation_section_position": 3,
        },
        # --- NEW Q4 (short answer: the source document) ----------------------
        {
            "position": 4,
            "kind": "short_answer",
            "question_en": "A supplier sends the shop a document saying 'payable in 15 days' for 120,000 FCFA of goods. In English, what is that document called? (one word)",
            "question_fr": "Un fournisseur envoie à la boutique un document indiquant « payable à 15 jours » pour 120 000 FCFA de marchandises. En anglais, comment appelle-t-on ce document ? (un seul mot)",
            "short_answer_en": "invoice",
            "short_answer_fr": "facture",
            "explanation_en": "An invoice is the supplier's document. French accountants call it a facture; the English word is invoice. It is the source document that justifies the purchase entry.",
            "explanation_fr": "Une facture est le document du fournisseur. Les comptables francophones l'appellent facture ; le mot anglais est invoice. C'est le document source qui justifie l'écriture d'achat.",
            "correction_en": "The document is an invoice (a facture). In English the word is invoice - the piece of paper that says what was supplied and whether it is payable now or later.",
            "correction_fr": "Le document est une facture. Le mot anglais est invoice - le papier qui indique ce qui a été fourni et si c'est payable maintenant ou plus tard.",
            "remediation_section_position": 3,
        },
        # --- NEW Q5 (four-step analysis, first question) --------------------
        {
            "position": 5,
            "kind": "mcq",
            "question_en": "You have a supplier invoice in your hand. What is the FIRST question you ask yourself before writing anything?",
            "question_fr": "Vous avez une facture fournisseur en main. Quelle est la PREMIÈRE question que vous vous posez avant d'écrire quoi que ce soit ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "Which account code should I use for this?", "text_fr": "Quel code de compte dois-je utiliser pour cela ?", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "Has any cash actually moved today?", "text_fr": "De l'argent a-t-il réellement bougé aujourd'hui ?", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "What happened, in one plain sentence with no accounting words?", "text_fr": "Que s'est-il passé, en une phrase simple sans mot comptable ?", "is_correct": True},
                {"option_key": "D", "position": 4, "text_en": "Which page of the journal is this for?", "text_fr": "À quelle page du journal cela appartient-il ?", "is_correct": False},
            ],
            "explanation_en": "Step 1 of transaction analysis is describing the event in ordinary words: 'Bought 10 bags of rice for 120,000 FCFA on credit.' Only once you can say it that plainly can you name the accounts. Choosing an account code first is backwards.",
            "explanation_fr": "L'étape 1 de l'analyse d'opération est de décrire l'événement en mots ordinaires : « Acheté 10 sacs de riz pour 120 000 FCFA à crédit. » Tant que vous ne pouvez pas le dire aussi simplement, vous ne pouvez pas nommer les comptes. Choisir d'abord un code de compte, c'est inverser la marche.",
            "correction_en": "Start by saying what happened in plain words, with no accounting vocabulary. Only then do you name the accounts that move, decide the direction of each, and check that the entry balances.",
            "correction_fr": "Commencez par dire ce qui s'est passé en mots simples, sans vocabulaire comptable. Ensuite seulement, nommez les comptes qui bougent, déterminez le sens de chacun, et vérifiez que l'écriture s'équilibre.",
            "remediation_section_position": 4,
        },
        # --- NEW Q6 (the date to use) ----------------------------------------
        {
            "position": 6,
            "kind": "mcq",
            "question_en": "Nkwen Market's invoice is dated 3 March. You only type the entry into the journal on 6 March. Which date goes on the entry?",
            "question_fr": "La facture de Nkwen Market est datée du 3 mars. Vous ne saisissez l'écriture au journal que le 6 mars. Quelle date inscrit-on sur l'écriture ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "6 March - the day the entry was actually typed in", "text_fr": "Le 6 mars - le jour où l'écriture a été réellement saisie", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "3 March - the date of the transaction itself", "text_fr": "Le 3 mars - la date de l'opération elle-même", "is_correct": True},
                {"option_key": "C", "position": 3, "text_en": "Both dates, side by side, to be safe", "text_fr": "Les deux dates, côte à côte, par prudence", "is_correct": False},
                {"option_key": "D", "position": 4, "text_en": "31 December, so every entry lands in the same year-end page", "text_fr": "Le 31 décembre, pour que toutes les écritures arrivent sur la même page de fin d'exercice", "is_correct": False},
            ],
            "explanation_en": "An entry carries the date of the TRANSACTION, not the date you got round to writing it. The journal is read in date order, so a 6 March date would move a March purchase into the wrong day - and could even push it into the wrong month at a month end.",
            "explanation_fr": "Une écriture porte la date de l'OPÉRATION, pas la date à laquelle vous avez trouvé le temps de la saisir. Le journal se lit dans l'ordre des dates : une date au 6 mars situerait un achat de mars au mauvais jour - et pourrait même le faire basculer dans le mauvais mois en fin de mois.",
            "correction_en": "Use the transaction's own date - 3 March. The date you happen to type it is a fact about you, not about the business, and the journal has to be readable as a true timeline.",
            "correction_fr": "Utilisez la date de l'opération - le 3 mars. La date à laquelle vous saisissez est un fait qui vous concerne, pas l'entreprise, et le journal doit se lire comme une chronologie fidèle.",
            "remediation_section_position": 5,
        },
        # --- NEW Q7 (short answer: narration / libelle) ----------------------
        {
            "position": 7,
            "kind": "short_answer",
            "question_en": "In French accounting, what single word names the short line under the date that says what the entry is for?",
            "question_fr": "En comptabilité française, quel mot unique nomme la courte ligne sous la date qui indique l'objet de l'écriture ?",
            "short_answer_en": "libellé",
            "short_answer_fr": "libellé",
            "explanation_en": "The French word is libellé (narration in English). A good libellé names the document, the counterparty and the purpose, so it can still be understood years later by somebody who has never met you.",
            "explanation_fr": "Le mot français est libellé (narration en anglais). Un bon libellé nomme le document, le counterpartaire et l'objet de l'opération, afin d'être encore compréhensible des années plus tard par quelqu'un qui ne vous a jamais rencontré.",
            "correction_en": "The word is libellé. In English we call it the narration: one short line saying what the entry is for, naming the document and the counterparty.",
            "correction_fr": "Le mot est libellé. En anglais on dit la narration : une courte ligne indiquant l'objet de l'écriture, en nommant le document et le counterpartaire.",
            "remediation_section_position": 5,
        },
        # --- NEW Q8 (a good narration vs a bad one) --------------------------
        {
            "position": 8,
            "kind": "mcq",
            "question_en": "Which of these is a USEFUL narration (libellé) for the entry?",
            "question_fr": "Lequel de ces libellés est UTILE pour l'écriture ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "'Being a debit'", "text_fr": "« C'est un débit »", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "'Money in - March'", "text_fr": "« Argent entrant - mars »", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "'Cash received from Mama Ndifor, settling invoice 0109'", "text_fr": "« Trésorerie reçue de Mama Ndifor, règlement de la facture 0109 »", "is_correct": True},
                {"option_key": "D", "position": 4, "text_en": "'Account 411 - entry 23'", "text_fr": "« Compte 411 - écriture 23 »", "is_correct": False},
            ],
            "explanation_en": "A useful narration names the counterparty, the document and what the money was for. 'Cash received from Mama Ndifor, settling invoice 0109' would still make sense to a reader two years later. 'Being a debit' and 'Money in' say nothing about the business; 'Account 411' is just a cross-reference.",
            "explanation_fr": "Un libellé utile nomme le counterpartaire, le document et l'objet de l'opération. « Trésorerie reçue de Mama Ndifor, règlement de la facture 0109 » resterait compréhensible deux ans plus tard. « C'est un débit » et « Argent entrant » ne disent rien sur l'entreprise ; « Compte 411 » n'est qu'un renvoi.",
            "correction_en": "Write the narration so it tells the story: who, which document, and what for. 'Cash received from Mama Ndifor, settling invoice 0109' does that; the others only describe the mechanics.",
            "correction_fr": "Rédigez le libellé pour qu'il raconte l'histoire : qui, quel document, pour quoi. « Trésorerie reçue de Mama Ndifor, règlement de la facture 0109 » le fait ; les autres ne décrivent que la mécanique.",
            "remediation_section_position": 5,
        },
        # --- NEW Q9 (Dr/Cr placement) ----------------------------------------
        {
            "position": 9,
            "kind": "mcq",
            "question_en": "Where do 'Dr' and 'Cr' belong when you write a journal entry by hand?",
            "question_fr": "Où doivent figurer « Dr » et « Cr » lorsque vous écrivez une écriture de journal à la main ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "In a column on the far left, before the date", "text_fr": "Dans une colonne à l'extrême gauche, avant la date", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "In the amount column, as a sign in front of the number", "text_fr": "Dans la colonne des montants, comme un signe devant le nombre", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "After the account name, on the same line as the amount", "text_fr": "Après le nom du compte, sur la même ligne que le montant", "is_correct": True},
                {"option_key": "D", "position": 4, "text_en": "Only in the totals at the foot of the entry", "text_fr": "Uniquement dans les totaux au pied de l'écriture", "is_correct": False},
            ],
            "explanation_en": "The standard convention is to write Dr or Cr AFTER the account name, on the same line: 'Cash ..... Dr 25,000'. They label the two columns; they are not amounts, so they never sit in the amount column.",
            "explanation_fr": "La convention est d'écrire Dr ou Cr APRÈS le nom du compte, sur la même ligne : « Trésorerie ..... Dr 25 000 ». Ils désignent les deux colonnes ; ce ne sont pas des montants et ne figurent donc jamais dans la colonne des montants.",
            "correction_en": "Write Dr or Cr after the account name, on the same line as the amount. They are column labels, not minus and plus signs.",
            "correction_fr": "Écrivez Dr ou Cr après le nom du compte, sur la même ligne que le montant. Ce sont des étiquettes de colonnes, pas des signes plus ou moins.",
            "remediation_section_position": 5,
        },
        # --- NEW Q10 (an unbalanced entry is refused) ------------------------
        {
            "position": 10,
            "kind": "mcq",
            "question_en": "You write 'Debit Cash 25,000 / Credit Sales 24,000'. What happens?",
            "question_fr": "Vous écrivez « Débit Trésorerie 25 000 / Crédit Ventes 24 000 ». Que se passe-t-il ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "It is posted, and the 1,000 difference is fixed at the end of the month", "text_fr": "Elle est publiée, et la différence de 1 000 est régularisée à la fin du mois", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "It cannot be posted: total debits must equal total credits before anything reaches the ledger", "text_fr": "Elle ne peut pas être publiée : le total des débits doit égaler le total des crédits avant d'atteindre le grand livre", "is_correct": True},
                {"option_key": "C", "position": 3, "text_en": "It is posted as a draft and reviewed by the tax office", "text_fr": "Elle est publiée en brouillon et examinée par le service fiscal", "is_correct": False},
                {"option_key": "D", "position": 4, "text_en": "It is posted but flagged as a rounding difference", "text_fr": "Elle est publiée mais signalée comme un écart d'arrondi", "is_correct": False},
            ],
            "explanation_en": "The entry does not balance, so it is refused. This app enforces total debits = total credits at the service layer, not just on screen - exactly as a real bookkeeping office would. An unbalanced entry is not 'nearly right'; it is wrong.",
            "explanation_fr": "L'écriture ne s'équilibre pas, elle est donc refusée. Cette application impose total des débits = total des crédits au niveau du service, et pas seulement à l'écran - exactement comme le ferait un vrai service de comptabilité. Une écriture déséquilibrée n'est pas « presque juste » ; elle est fausse.",
            "correction_en": "Go back and find the mistake before posting. Add the two columns: 25,000 against 24,000 is a 1,000 difference, and nothing may be posted until it is gone.",
            "correction_fr": "Revenez corriger avant de publier. Additionnez les deux colonnes : 25 000 contre 24 000 fait 1 000 d'écart, et rien ne peut être publié tant qu'il n'est pas résolu.",
            "remediation_section_position": 4,
        },
        # --- NEW Q11 (credit purchase, from the worked example) --------------
        {
            "position": 11,
            "kind": "mcq",
            "question_en": "The shop buys 10 bags of rice for 120,000 FCFA from Nkwen Market on credit (invoice dated 3 March, payable in 15 days). Which entry is correct?",
            "question_fr": "La boutique achète 10 sacs de riz pour 120 000 FCFA à Nkwen Market à crédit (facture du 3 mars, payable à 15 jours). Quelle écriture est correcte ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "Debit Stock 120,000 / Credit Sales 120,000", "text_fr": "Débit Stocks 120 000 / Crédit Ventes 120 000", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "Debit Trade payables 120,000 / Credit Stock 120,000", "text_fr": "Débit Fournisseurs 120 000 / Crédit Stocks 120 000", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "Debit Stock 120,000 / Credit Trade payables 120,000", "text_fr": "Débit Stocks 120 000 / Crédit Fournisseurs 120 000", "is_correct": True},
            ],
            "explanation_en": "Stock is an asset that grows, so it is debited. The invoice says 'payable in 15 days', so the shop now owes the supplier: Trade payables is a liability that grows, so it is credited. No cash has moved, and nothing is recognised as sales. Balanced: 120,000 = 120,000.",
            "explanation_fr": "Les stocks sont un actif qui grandit : ils sont débités. La facture indique « payable à 15 jours » : la boutique doit donc de l'argent au fournisseur, et les Fournisseurs (passif) augmentent, donc ils sont crédités. Aucun argent n'a bougé, et rien n'est comptabilisé en ventes. Équilibré : 120 000 = 120 000.",
            "correction_en": "On credit purchase: the STOCK increases (debit) and what you OWE increases (credit). Cash does not move, and sales are not involved until the goods are resold.",
            "correction_fr": "Sur un achat à crédit : les STOCKS augmentent (débit) et ce que vous DEVEZ augmente (crédit). La trésorerie ne bouge pas, et les ventes n'interviennent qu'au moment de la revente.",
            "remediation_section_position": 7,
        },
        # --- NEW Q12 (day totals from the worked example) -------------------
        {
            "position": 12,
            "kind": "mcq",
            "question_en": "Using the three entries of Thursday 3 March in Section 7, what is the total of the DEBIT column for the day?",
            "question_fr": "D'après les trois écritures du jeudi 3 mars de la Section 7, quel est le total de la colonne DÉBIT de la journée ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "145,000", "text_fr": "145 000", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "155,000", "text_fr": "155 000", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "160,000", "text_fr": "160 000", "is_correct": True},
                {"option_key": "D", "position": 4, "text_en": "175,000", "text_fr": "175 000", "is_correct": False},
            ],
            "explanation_en": "25,000 (Cash Dr) + 120,000 (Stock Dr) + 15,000 (Owner's drawings Dr) = 160,000. The credit column gives exactly the same total, which is how you know the day balances.",
            "explanation_fr": "25 000 (Trésorerie Dr) + 120 000 (Stocks Dr) + 15 000 (Prélèvements Dr) = 160 000. La colonne crédit donne exactement le même total : c'est ainsi qu'on sait que la journée s'équilibre.",
            "correction_en": "Add the three debit amounts: 25,000 + 120,000 + 15,000 = 160,000. Then check the credit column gives the same figure - if it does not, you have made a mistake.",
            "correction_fr": "Additionnez les trois montants de débit : 25 000 + 120 000 + 15 000 = 160 000. Vérifiez ensuite que la colonne crédit donne le même chiffre - sinon, vous vous êtes trompé.",
            "remediation_section_position": 7,
        },
        # --- NEW Q13 (the credit sale: no cash moved) -------------------------
        {
            "position": 13,
            "kind": "mcq",
            "question_en": "Mama Ndifor buys goods for 22,000 FCFA on 4 March and will pay next week. No cash has moved. Which entry is correct?",
            "question_fr": "Mama Ndifor achète des marchandises pour 22 000 FCFA le 4 mars et paiera la semaine prochaine. Aucun argent n'a bougé. Quelle écriture est correcte ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "Debit Cash 22,000 / Credit Sales 22,000", "text_fr": "Débit Trésorerie 22 000 / Crédit Ventes 22 000", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "Debit Sales 22,000 / Credit Trade receivables 22,000", "text_fr": "Débit Ventes 22 000 / Crédit Créances clients 22 000", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "Debit Trade receivables 22,000 / Credit Sales 22,000", "text_fr": "Débit Créances clients 22 000 / Crédit Ventes 22 000", "is_correct": True},
            ],
            "explanation_en": "No cash moved, so Cash is NOT debited. What grew is the amount the customer owes the shop, so Trade receivables is debited; and the shop has earned income, so Sales is credited. Balanced: 22,000 = 22,000.",
            "explanation_fr": "Aucun argent n'a bougé : la Trésorerie n'est donc PAS débitée. Ce qui a augmenté, c'est la somme que la cliente doit à la boutique : les Créances clients sont débitées ; et la boutique a gagné un produit : les Ventes sont créditées. Équilibré : 22 000 = 22 000.",
            "correction_en": "On a credit sale, Cash is replaced on the debit side by the customer's own account. Debit Trade receivables (what she owes grows), credit Sales (the income is earned).",
            "correction_fr": "Sur une vente à crédit, la Trésorerie est remplacée du côté débit par le compte de la cliente. Débit Créances clients (ce qu'elle doit augmente), crédit Ventes (le produit est acquis).",
            "remediation_section_position": 8,
        },
        # --- NEW Q14 (drawings are not an expense) ---------------------------
        {
            "position": 14,
            "kind": "mcq",
            "question_en": "The owner takes 15,000 FCFA out of the till for her family. Why is this NOT recorded as an expense?",
            "question_fr": "La propriétaire retire 15 000 FCFA de la caisse pour sa famille. Pourquoi n'est-ce pas enregistré comme une charge ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "Because it is too small to be worth recording", "text_fr": "Parce que c'est trop petit pour mériter d'être enregistré", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "Because the shop bought nothing, so no cost was incurred", "text_fr": "Parce que la boutique n'a rien acheté, donc aucune charge n'a été engagée", "is_correct": True},
                {"option_key": "C", "position": 3, "text_en": "Because the owner is not an employee of the shop", "text_fr": "Parce que le propriétaire n'est pas un salarié de la boutique", "is_correct": False},
                {"option_key": "D", "position": 4, "text_en": "Because expenses are only recognised at the end of the year", "text_fr": "Parce que les charges ne sont reconnues qu'à la fin de l'année", "is_correct": False},
            ],
            "explanation_en": "An expense is a cost the business incurred to earn income. Money drawn by the owner is not a cost - it is a distribution to the owner, recorded as Owner's drawings against equity. Calling it an expense would understate the profit.",
            "explanation_fr": "Une charge est un coût engagé par l'entreprise pour gagner un produit. L'argent retiré par le propriétaire n'est pas un coût : c'est une distribution au propriétaire, enregistrée en Prélèvements contre les capitaux propres. L'appeler « charge » sous-évalue le bénéfice.",
            "correction_en": "Drawings are the owner's own money leaving the business, not a cost of running it. Record Owner's drawings Dr / Cash Cr. If you treat it as an expense you will understate the shop's profit.",
            "correction_fr": "Les prélèvements, c'est l'argent du propriétaire qui sort de l'entreprise, pas un coût d'exploitation. Enregistrez Prélèvements Dr / Trésorerie Cr. Si vous le traitez comme une charge, vous sous-évaluez le bénéfice de la boutique.",
            "remediation_section_position": 7,
        },
        # --- NEW Q15 (the settlement pair) -----------------------------------
        {
            "position": 15,
            "kind": "mcq",
            "question_en": "Mama Ndifor finally pays the 25,000 FCFA she owed. Which entry clears the debt?",
            "question_fr": "Mama Ndifor finit par payer les 25 000 FCFA qu'elle devait. Quelle écriture solde la dette ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "Debit Trade receivables 25,000 / Credit Cash 25,000", "text_fr": "Débit Créances clients 25 000 / Crédit Trésorerie 25 000", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "Debit Cash 25,000 / Credit Trade receivables 25,000", "text_fr": "Débit Trésorerie 25 000 / Crédit Créances clients 25 000", "is_correct": True},
                {"option_key": "C", "position": 3, "text_en": "Debit Sales 25,000 / Credit Cash 25,000", "text_fr": "Débit Ventes 25 000 / Crédit Trésorerie 25 000", "is_correct": False},
            ],
            "explanation_en": "This is a SETTLEMENT: the receivable shrinks with a DEBIT and cash grows with a CREDIT. Sales is not touched again - the income was already recognised when the goods were sold on credit. Balanced: 25,000 = 25,000.",
            "explanation_fr": "C'est un RÈGLEMENT : la créance diminue au DÉBIT et la trésorerie augmente au CRÉDIT. Les Ventes ne sont plus touchées - le produit avait déjà été reconnu lors de la vente à crédit. Équilibré : 25 000 = 25 000.",
            "correction_en": "When the debtor pays, debit what she owed you (Trade receivables) and credit Cash. The Sales figure was already recorded at the moment of the credit sale - do not record it twice.",
            "correction_fr": "Quand la cliente paie, débitez ce qu'elle vous devait (Créances clients) et créditez la Trésorerie. Le montant des Ventes a déjà été enregistré au moment de la vente à crédit - ne l'enregistrez pas deux fois.",
            "remediation_section_position": 8,
        },
        # --- NEW Q16 (correcting vs reversing) -------------------------------
        {
            "position": 16,
            "kind": "mcq",
            "question_en": "A posted rent entry says 6,000 FCFA. The invoice actually said 60,000. What is the honest repair?",
            "question_fr": "Une écriture de loyer publiée indique 6 000 FCFA. La facture indiquait en réalité 60 000. Quelle est la réparation honnête ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "Edit the 6,000 to 60,000 in place and carry on", "text_fr": "Modifier les 6 000 en 60 000 sur place et continuer", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "Delete the entry and write the correct one instead", "text_fr": "Supprimer l'écriture et écrire la bonne à la place", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "Leave the posted entry and record a correcting entry today that says plainly what is being corrected and why", "text_fr": "Laisser l'écriture publiée et enregistrer aujourd'hui une écriture corrective indiquant clairement ce qui est corrigé et pourquoi", "is_correct": True},
            ],
            "explanation_en": "A posted entry is never edited and never deleted - the history has to stay readable. The honest repair is a CORRECTING entry dated today whose narration states plainly that rent was 60,000 and not 6,000. For a wrong posted entry you may instead post a REVERSING entry that cancels it exactly, followed by the correct entry.",
            "explanation_fr": "Une écriture publiée n'est jamais modifiée ni supprimée - l'historique doit rester lisible. La réparation honnête est une ÉCRITURE CORRECTIVE datée d'aujourd'hui, dont la narration dit clairement que le loyer était de 60 000 et non 6 000. Pour une écriture publiée erronée, on peut aussi publier une ÉCRITURE INVERSE qui l'annule exactement, suivie de l'écriture correcte.",
            "correction_en": "Never erase a posted entry. Write a correcting entry today, with a narration that names the mistake: 'To correct the entry of 3 March: rent was 60,000, not 6,000.' The wrong figure stays visible; both figures tell the truth.",
            "correction_fr": "N'effacez jamais une écriture publiée. Écrivez aujourd'hui une écriture corrective, avec une narration qui nomme l'erreur : « Pour corriger l'écriture du 3 mars : le loyer était de 60 000, non 6 000. » Le mauvais chiffre reste visible ; les deux chiffres disent la vérité.",
            "remediation_section_position": 9,
        },
        # --- NEW Q17 (confidence and review support) -------------------------
        {
            "position": 17,
            "kind": "mcq",
            "question_en": "You answer a question correctly but had to guess. What does flagging 'I got it, but I guessed' do?",
            "question_fr": "Vous répondez correctement à une question mais avez deviné. Que fait l'option « J'ai trouvé, mais j'ai deviné » ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "It reduces your score to reflect the guess", "text_fr": "Elle diminue votre score pour tenir compte de la divinette", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "It adds the question to your spaced-review queue so it comes back later", "text_fr": "Elle ajoute la question à votre file de révision espacée pour qu'elle revienne plus tard", "is_correct": True},
                {"option_key": "C", "position": 3, "text_en": "It restarts the lesson from question 1", "text_fr": "Elle relance la leçon depuis la question 1", "is_correct": False},
                {"option_key": "D", "position": 4, "text_en": "Nothing at all - the flag is decorative", "text_fr": "Rien du tout - l'option est décorative", "is_correct": False},
            ],
            "explanation_en": "Confidence never changes your score. Flagging 'guessed' schedules the question for spaced review, because a guessed answer that is never revisited is not an answer you actually have. Flagging 'I understand this' on a correct answer schedules nothing.",
            "explanation_fr": "La confiance ne change jamais votre score. L'option « deviné » programme la question pour une révision espacée, car une réponse devinée jamais revue n'est pas une réponse que vous possédez réellement. L'option « J'ai compris » sur une bonne réponse ne programme rien.",
            "correction_en": "The flag only decides what gets REVISED, never what you scored. A correct answer marked 'guessed' is scheduled for review; a correct answer marked 'understood' is left alone.",
            "correction_fr": "L'option ne décide que de ce qui sera RÉVISÉ, jamais de votre score. Une bonne réponse marquée « deviné » est programmée pour révision ; une bonne réponse marquée « compris » est laissée tranquille.",
            "remediation_section_position": 9,
        },
        # --- NEW Q18 (final: what this course is and is not) ----------------
        {
            "position": 18,
            "kind": "mcq",
            "question_en": "You score 100% on this lesson. Which statement is true?",
            "question_fr": "Vous obtenez 100 % à cette leçon. Quelle affirmation est vraie ?",
            "answers": [
                {"option_key": "A", "position": 1, "text_en": "You are now a professional accountant and may sign financial statements", "text_fr": "Vous êtes maintenant comptable professionnel et pouvez signer des états financiers", "is_correct": False},
                {"option_key": "B", "position": 2, "text_en": "You may file accounts on a client's behalf without further training", "text_fr": "Vous pouvez déposer des comptes pour un client sans formation complémentaire", "is_correct": False},
                {"option_key": "C", "position": 3, "text_en": "You have learned a real, practical skill: turning documents into balanced entries - and you are NOT a professional or regulated accountant", "text_fr": "Vous avez acquis une compétence réelle et pratique : transformer des documents en écritures équilibrées - et vous n'êtes PAS comptable professionnel ni réglementé", "is_correct": True},
                {"option_key": "D", "position": 4, "text_en": "You hold an OHADA certificate recognised by employers", "text_fr": "Vous détenez un certificat OHADA reconnu par les employeurs", "is_correct": False},
            ],
            "explanation_en": "A perfect score here means you can really do one thing well: take a source document and produce a dated, narrated, balanced journal entry. That is genuine practical value. It is not a qualification. Professional accounting is regulated: it requires recognised study, supervised experience and, in most places, membership of a professional body such as ONECCA in Cameroon.",
            "explanation_fr": "Un score parfait signifie que vous savez réellement faire une chose : prendre un document source et produire une écriture de journal datée, narrée et équilibrée. C'est une vraie valeur pratique. Ce n'est pas une qualification. La profession comptable est réglementée : elle exige des études reconnues, une expérience encadrée et, dans la plupart des pays, l'appartenance à un ordre professionnel comme l'ONECCA au Cameroun.",
            "correction_en": "This lesson gives you real practical skill, and nothing more. Completing the course does not make you an accountant, does not authorise you to practise as one, and does not authorise you to sign or file anything.",
            "correction_fr": "Cette leçon vous donne une compétence pratique réelle, et rien de plus. Terminer le cours ne fait pas de vous un comptable, ne vous autorise pas à exercer comme tel, et ne vous autorise pas à signer ni à déposer quoi que ce soit.",
            "remediation_section_position": 10,
        },
    ],
}
