# OHADA SYSCOHADA Chart of Accounts & IFRS Structure — Verified Source Reference (v2)

Corrected and verified 2026-08-15. This replaces the earlier v1 file, which
used the outdated 2000 text. **Use this version.**

---

## Authenticity check — confirmed

**Site:** droit-afrique.com — a legal publisher operating since 2006,
providing free access to official legal texts across 24 francophone African
countries (laws, gazettes, a pan-African legal portal). This is a
legitimate legal-document repository, not a summary blog or AI-generated
content.

**Document:** explicitly labeled as the annex to the OHADA "Acte uniforme
relatif au droit comptable et à l'information financière," adopted 26
January 2017 — matching the same law published in OHADA's own official
Journal Officiel (15 February 2017), which I independently located and
confirmed earlier in this conversation.

**Currency check (is this still current for 2026?):** Yes. Independent
sources confirm the SYSCOHADA révisé chart currently in commercial use for
the 2024–2025 period is still built on the reform adopted in 2018/2019 —
i.e. the same 2017-adopted, 2018-effective text below. No further
account-numbering overhaul has happened since. This is the current,
authoritative structure.

**Link you can check yourself:**
https://www.droit-afrique.com/uploads/OHADA-Plan-comptable-2017.pdf
(If it doesn't render in your browser, right-click → "Save link as" to
download the PDF directly rather than viewing it in-browser.)

Official OHADA Journal Officiel version (for independent cross-check):
https://justice.sec.gouv.sn/wp-content/uploads/textes-reglements/OHADA/Acte-uniforme-relatif-droit-comptable-information-financiere-JAN-2017-JO.pdf

---

## Part 1 — OHADA: the real, current, official structure (SYSCOHADA révisé, 2017/2018)

### The numbering logic rules (important — build seed data using these rules, not just a copied list)

Straight from the source document's own "Constantes" section:

1. **Digit count = level.** A 2-digit code = main account (e.g. `10`). A
   3-digit code = sub-account (e.g. `101`). A 4-digit code = sub-sub-account
   (e.g. `1011`).
2. **First digit = class.** E.g. any code starting with `5` belongs to
   Class 5 (treasury/cash).
3. **The digit 9 in a 2-digit code (for classes 1–5) marks depreciation/
   provisions for that class.** E.g. `19` = provisions for risks/charges,
   `39` = stock depreciation. For classes 6/7, the same digit-9 pattern
   marks provision-related movements (`69` = depreciation/provision
   charges, `79` = provision reversals).
4. **A trailing 9 in 3+ digit codes is the "inverse/balancing" line** for
   the immediately higher-level account, covering what isn't captured in
   sub-codes 1–8.
5. **Trailing digits 1–8 in 3+ digit codes** detail sub-operations under the
   parent account. In classes 6/7 specifically, trailing `8` means "other,
   not covered by 1–7."
6. **Trailing 0 has no special meaning** in the OHADA system.

Encode these as generation rules where practical, not just a static list —
it'll make the hierarchy and any future expansion self-consistent.

### The 9 classes

| Class | Name (French) | Plain English |
|---|---|---|
| 1 | Comptes de ressources durables | Capital / durable resources (equity + long-term debt) |
| 2 | Comptes d'actif immobilisé | Fixed assets |
| 3 | Comptes de stocks | Inventory |
| 4 | Comptes de tiers | Third-party accounts (receivables, payables, staff, tax) |
| 5 | Comptes de trésorerie | Cash / treasury accounts |
| 6 | Comptes de charges des activités ordinaires | Ordinary operating expenses |
| 7 | Comptes de produits des activités ordinaires | Ordinary operating revenue |
| 8 | Comptes des autres charges et des autres produits | Other expenses/income (extraordinary items, asset disposals) |
| 9 | Comptes des engagements hors bilan et comptes de la comptabilité analytique de gestion | Off-balance-sheet commitments + internal cost/analytical accounting — SUPPLEMENTARY, not part of core financial statements |

### Complete verified account list (2017 révisé — current)

```
Classe 1 - Comptes de ressources durables

10 Capital
• 101 Capital social
- 1011 Capital souscrit, non appelé
- 1012 Capital souscrit, appelé, non versé
- 1013 Capital souscrit, appelé, versé, non amorti
- 1014 Capital souscrit, appelé, versé, amorti
- 1018 Capital souscrit soumis à des conditions particulières
• 102 Capital par dotation
- 1021 Dotation initiale
- 1022 Dotations complémentaires
- 1028 Autres dotations
• 103 Capital personnel
• 104 Compte de l'exploitant
- 1041 Apports temporaires
- 1042 Opérations courantes
- 1043 Rémunérations, impôts et autres charges personnelles
- 1047 Prélèvements d'autoconsommation
- 1048 Autres prélèvements
• 105 Primes liées au capital social
- 1051 Primes d'émission
- 1052 Primes d'apport
- 1053 Primes de fusion
- 1054 Primes de conversion
- 1058 Autres primes
• 106 Écarts de réévaluation
- 1061 Écarts de réévaluation légale
- 1062 Écarts de réévaluation libre
• 109 Apporteurs, capital souscrit, non appelé

11 Réserves
• 111 Réserve légale
• 112 Réserves statutaires ou contractuelles
• 113 Réserves réglementées
- 1131 Réserves de plus-values nettes à long terme
- 1132 Réserves d'attribution gratuite d'actions au personnel salarié et aux dirigeants
- 1133 Réserves consécutives à l'octroi de subventions d'investissement
- 1134 Réserves des valeurs mobilières donnant accès au capital
- 1138 Autres réserves réglementées
• 118 Autres réserves
- 1181 Réserves facultatives
- 1188 Réserves diverses

12 Report à nouveau
• 121 Report à nouveau créditeur
• 129 Report à nouveau débiteur
- 1291 Perte nette à reporter
- 1292 Perte - Amortissements réputés différés

13 Résultat net de l'exercice
• 130 Résultat en instance d'affectation
- 1301 Résultat en instance d'affectation : bénéfice
- 1309 Résultat en instance d'affectation : perte
• 131 Résultat net : bénéfice
• 132 Marge commerciale (MC)
• 133 Valeur ajoutée (VA)
• 134 Excédent brut d'exploitation (EBE)
• 135 Résultat d'exploitation (RE)
• 136 Résultat financier (RF)
• 137 Résultat des activités ordinaires (RAO)
• 138 Résultat hors activités ordinaires (RHAO)
- 1381 Résultat de fusion
- 1382 Résultat d'apport partiel d'actif
- 1383 Résultat de scission
- 1384 Résultat de liquidation
• 139 Résultat net : perte

14 Subventions d'investissement
• 141 Subventions d'équipement
- 1411 État / 1412 Régions / 1413 Départements / 1414 Communes et collectivités publiques décentralisées / 1415 Entités publiques ou mixtes / 1416 Entités et organismes privés / 1417 Organismes internationaux / 1418 Autres
• 148 Autres subventions d'investissement

15 Provisions réglementées et fonds assimilés
• 151 Amortissements dérogatoires
• 152 Plus-values de cession à réinvestir
• 153 Fonds réglementés (1531 Fonds National / 1532 Prélèvement pour le Budget)
• 154 Provisions spéciales de réévaluation
• 155 Provisions réglementées relatives aux immobilisations (1551 Reconstitution des gisements miniers et pétroliers)
• 156 Provisions réglementées relatives aux stocks (1561 Hausse de prix / 1562 Fluctuation des cours)
• 157 Provisions pour investissement
• 158 Autres provisions et fonds réglementés

16 Emprunts et dettes assimilées
• 161 Emprunts obligataires (1611 ordinaires / 1612 convertibles en actions / 1613 remboursables en actions / 1618 autres)
• 162 Emprunts et dettes auprès des établissements de crédit
• 163 Avances reçues de l'État
• 164 Avances reçues et comptes courants bloqués
• 165 Dépôts et cautionnements reçus (1651 Dépôts / 1652 Cautionnements)
• 166 Intérêts courus (1661-1668, par type de dette)
• 167 Avances assorties de conditions particulières (1671-1674)
• 168 Autres emprunts et dettes (1681-1686)

17 Dettes de location acquisition
• 172 crédit-bail immobilier / 173 crédit-bail mobilier / 174 location-vente
• 176 Intérêts courus (1762-1768) / 178 Autres dettes de location acquisition

18 Dettes liées à des participations et comptes de liaison
• 181 Dettes liées à des participations (1811 groupe / 1812 hors groupe)
• 182 Dettes liées à des sociétés en participation
• 183 Intérêts courus sur dettes liées à des participations
• 184-188 Comptes permanents/de liaison des établissements et sociétés en participation

19 Provisions pour risques et charges
• 191 Provisions pour litiges
• 192 Provisions pour garanties données aux clients
• 193 Provisions pour pertes sur marchés à achèvement futur
• 194 Provisions pour pertes de change
• 195 Provisions pour impôts
• 196 Provisions pour pensions et obligations similaires (1961 engagement de retraite / 1962 actif du régime de retraite)
• 197 Provisions pour restructuration
• 198 Autres provisions pour risques et charges (1981 amendes et pénalités / 1983 propre assureur / 1984 démantèlement / 1985 avantages en nature / 1988 divers)

Classe 2 - Comptes d'actif immobilisé

21 Immobilisations incorporelles
• 211 Frais de développement
• 212 Brevets, licences, concessions et droits similaires (2121-2128)
• 213 Logiciels et sites internet (2131 Logiciels / 2132 Sites internet)
• 214 Marques / 215 Fonds commercial / 216 Droit au bail / 217 Investissements de création
• 218 Autres droits et valeurs incorporels (2181-2188)
• 219 Immobilisations incorporelles en cours (2191/2193/2198)

22 Terrains
• 221 Terrains agricoles et forestiers (2211/2212/2218)
• 222 Terrains nus (2221/2228)
• 223 Terrains bâtis (2231-2238)
• 224 Travaux de mise en valeur des terrains (2241/2245/2248)
• 225 Terrains de carrières-tréfonds (2251) / 226 Terrains aménagés (2261) / 227 Terrains mis en concession
• 228 Autres terrains (2281-2288)
• 229 Aménagements de terrains en cours (2291-2298)

23 Bâtiments, installations techniques et agencements
• 231 sur sol propre (2311-2316) / 232 sur sol d'autrui (2321-2326)
• 233 Ouvrages d'infrastructure (2331-2338)
• 234 Aménagements, agencements et installations techniques (2341-2345)
• 235 Aménagements de bureaux (2351/2358)
• 237 mis en concession / 238 Autres installations et agencements
• 239 en cours (2391-2398)

24 Matériel, mobilier et actifs biologiques
• 241 industriel et commercial (2411-2416) / 242 agricole (2421/2422/2426)
• 243 Matériel d'emballage récupérable et identifiable
• 244 Matériel et mobilier (2441-2447)
• 245 Matériel de transport (2451-2458)
• 246 Actifs biologiques (2461-2468)
• 247 Agencements/aménagements matériel et actifs biologiques (2471/2472/2478)
• 248 Autres matériels et mobiliers (2481/2488)
• 249 en cours (2491-2498)

25 Avances et acomptes versés sur immobilisations (251/252)

26 Titres de participation (261/262/263/265/266/268)

27 Autres immobilisations financières
• 271 Prêts et créances (2711-2718) / 272 Prêts au personnel (2721/2722/2728)
• 273 Créances sur l'État (2731-2738) / 274 Titres immobilisés (2741-2748)
• 275 Dépôts et cautionnements versés (2751-2758)
• 276 Intérêts courus (2761-2768)
• 277 Créances rattachées à des participations et avances à des GIE (2771-2774)
• 278 Immobilisations financières diverses (2781-2788)

28 Amortissements
• 281 incorporelles (2811-2818) / 282 terrains (2824)
• 283 bâtiments/installations (2831-2838) / 284 matériel (2841-2848)

29 Dépréciations des immobilisations (291-297, mirrors the asset categories above)

Classe 3 - Comptes de stocks

31 Marchandises (311/312/313 actifs biologiques/318 HAO)
32 Matières premières et fournitures liées (321/322/323)
33 Autres approvisionnements (331-338)
34 Produits en cours (341-345, incl. actifs biologiques en cours)
35 Services en cours (351/352)
36 Produits finis (361/362/363 actifs biologiques)
37 Produits intermédiaires et résiduels (371/372/373)
38 Stocks en cours de route, en consignation ou en dépôt (381-388)
39 Dépréciations des stocks et encours de production (391-398)

Classe 4 - Comptes de tiers

40 Fournisseurs et comptes rattachés
• 401 dettes en compte (4011-4017) / 402 effets à payer (4021-4023)
• 404 acquisitions courantes d'immobilisations (4041-4047)
• 408 factures non parvenues (4081-4086) / 409 débiteurs (4091-4098)

41 Clients et comptes rattachés
• 411 Clients (4111-4118) / 412 effets à recevoir (4121-4125)
• 413 chèques/effets impayés (4131-4138)
• 414 créances sur cessions courantes d'immobilisations (4141-4147)
• 415 effets escomptés non échus / 416 créances litigieuses/douteuses (4161/4162)
• 418 produits à recevoir (4181/4186) / 419 clients créditeurs (4191-4198)

42 Personnel
• 421 avances et acomptes (4211-4213) / 422 rémunérations dues
• 423 oppositions, saisies-arrêts (4231-4233)
• 424 œuvres sociales internes (4241-4248) / 425 représentants du personnel (4251-4258)
• 426 participation aux bénéfices et au capital (4261/4264)
• 427 dépôts / 428 charges à payer et produits à recevoir (4281-4287)

43 Organismes sociaux
• 431 Sécurité sociale (4311-4318) / 432 retraite complémentaire
• 433 Autres organismes sociaux (4331-4333) / 438 charges à payer/produits à recevoir

44 État et collectivités publiques
• 441 impôt sur les bénéfices / 442 autres impôts et taxes (4421-4428)
• 443 TVA facturée (4431-4435) / 444 TVA due ou crédit (4441/4449)
• 445 TVA récupérable (4451-4456) / 446 autres taxes sur le CA
• 447 impôts retenus à la source (4471-4478)
• 448 charges à payer/produits à recevoir (4486/4487)
• 449 créances et dettes diverses (4491-4499)

45 Organismes internationaux (451/452/458)

46 Apporteurs, associés et groupe
• 461 opérations sur le capital (4611-4619) / 462 comptes courants (4621/4626)
• 463 opérations faites en commun et GIE (4631/4636)
• 465 dividendes à payer / 466 groupe comptes courants / 467 restant dû sur capital appelé

47 Débiteurs et créditeurs divers
• 471 divers (4711-4719) / 472 créances et dettes sur titres de placement (4721/4726)
• 473 opérations pour compte de tiers (4731-4739)
• 474 répartition périodique (4746/4747)
• 475 compte transitoire ajustement SYSCOHADA (4751/4752)
• 476 charges constatées d'avance / 477 produits constatés d'avance
• 478 écarts de conversion actif (4781-4788) / 479 écarts de conversion passif (4791-4798)

48 Créances et dettes hors activités ordinaires (HAO)
• 481 fournisseurs d'investissements (4811-4818) / 482 effets à payer (4821/4822)
• 484 autres dettes HAO / 485 créances sur cessions d'immobilisations (4851-4858)
• 488 autres créances HAO

49 Dépréciations et provisions pour risques à court terme (tiers)
• 490 fournisseurs / 491 clients (4911/4912) / 492-497 (par catégorie de tiers)
• 498 créances HAO (4985/4986/4988) / 499 provisions pour risques à court terme (4991/4997/4998)

Classe 5 - Comptes de trésorerie

50 Titres de placement (501-508, incl. actions, obligations, bons de souscription)
51 Valeurs à encaisser (511-518)
52 Banques
• 521 locales (5211 monnaie nationale / 5215 devises)
• 522-524 autres États/zones / 525 dépôt à terme / 526 intérêts courus (5261/5267)
53 Établissements financiers et assimilés (531-538)
54 Instruments de trésorerie (541-545)
55 Instruments de monnaie électronique
• 551 carte carburant / 552 téléphone portable / 553 carte péage / 554 porte-monnaie électronique / 558 autres
56 Banques, crédits de trésorerie et d'escompte (561-566)
57 Caisse
• 571 siège social (5711 monnaie nationale / 5712 devises)
• 572/573 succursales A/B (mêmes subdivisions)
58 Régies d'avances, accréditifs et virements internes (581-588)
59 Dépréciations et provisions pour risque à court terme (590-599)

Classe 6 - Comptes de charges des activités ordinaires

60 Achats et variations de stocks
• 601 marchandises (6011-6019) / 602 matières premières (6021-6029)
• 603 variations des stocks de biens achetés (6031-6033)
• 604 matières et fournitures consommables (6041-6049)
• 605 autres achats (6051-6059) / 608 emballages (6081-6089)

61 Transports (612/613/614/616/618, incl. voyages, déplacements)

62 Services extérieurs
• 621 sous-traitance générale / 622 locations charges locatives (6221-6228)
• 623 redevances de location acquisition (6232-6238)
• 624 entretien, réparations, maintenance (6241-6248)
• 625 primes d'assurance (6251-6258)
• 626 études, recherches, documentation (6261-6266)
• 627 publicité, publications, relations publiques (6271-6278)
• 628 télécommunications (6281-6288)

63 Autres services extérieurs
• 631 frais bancaires (6311-6318) / 632 intermédiaires et conseils (6322-6328)
• 633 formation du personnel / 634 redevances brevets/licences/logiciels (6342-6346)
• 635 cotisations (6351/6358) / 637 personnel extérieur (6371/6372)
• 638 autres charges externes (6381-6385)

64 Impôts et taxes
• 641 directs (6411-6418) / 645 indirects / 646 droits d'enregistrement (6461-6468)
• 647 pénalités, amendes fiscales (6471-6478) / 648 autres impôts et taxes

65 Autres charges
• 651 pertes sur créances (6511/6515) / 652 quote-part opérations communes (6521/6525)
• 654 valeurs comptables cessions courantes (6541/6542)
• 656 perte de change commerciale / 657 pénalités et amendes pénales
• 658 charges diverses (6581-6588) / 659 dépréciations/provisions court terme exploitation (6591-6598)

66 Charges de personnel
• 661 personnel national (6611-6618) / 662 personnel non national (6621-6628)
• 663 indemnités forfaitaires (6631-6638) / 664 charges sociales (6641/6642)
• 666 exploitant individuel (6661/6662) / 667 personnel extérieur transféré (6671/6672)
• 668 autres charges sociales (6681-6688)

67 Frais financiers et charges assimilées
• 671 intérêts des emprunts (6711-6714) / 672 intérêts location acquisition (6722-6728)
• 673 escomptes accordés / 674 autres intérêts (6741-6748)
• 675 escomptes effets de commerce / 676 pertes de change financières
• 677 pertes sur titres de placement (6771/6772) / 678 pertes risques financiers (6781-6784)
• 679 dépréciations/provisions court terme financières (6791-6798)

68 Dotations aux amortissements (681: 6812/6813)

69 Dotations aux provisions et aux dépréciations
• 691 exploitation (6911/6913/6914) / 697 financières (6971/6972)

Classe 7 - Comptes de produits des activités ordinaires

70 Ventes
• 701 marchandises (7011-7019) / 702 produits finis (7021-7029)
• 703 produits intermédiaires (7031-7039) / 704 produits résiduels (7041-7049)
• 705 travaux facturés (7051-7059) / 706 services vendus (7061-7069)
• 707 produits accessoires (7071-7078)

71 Subventions d'exploitation (711-714/718)

72 Production immobilisée
• 721 incorporelles / 722 corporelles (7221/7222) / 724 auto-consommée / 726 financières

73 Variations des stocks de biens et de services produits
• 734 produits en cours (7341/7342) / 735 en-cours de services (7351/7352)
• 736 produits finis / 737 produits intermédiaires et résiduels (7371/7372)

75 Autres produits
• 751 profits sur créances / 752 quote-part opérations communes (7521/7525)
• 754 cessions courantes d'immobilisations (7541/7542)
• 756 gains de change commerciaux / 758 produits divers (7581-7588)
• 759 reprises dépréciations/provisions court terme exploitation (7591-7598)

77 Revenus financiers et produits assimilés
• 771 intérêts de prêts et créances (7712/7713) / 772 revenus de participations (7721/7722)
• 773 escomptes obtenus / 774 revenus de placement (7745/7746)
• 775 intérêts location acquisition / 776 gains de change financiers
• 777 gains sur cessions de titres / 778 gains risques financiers (7781-7784)
• 779 reprises dépréciations/provisions court terme financières (7791-7798)

78 Transferts de charges (781/787)

79 Reprises de provisions, de dépréciations et autres
• 791 exploitation (7911/7913/7914) / 797 financières (7971/7972)
• 798 reprises d'amortissements / 799 reprises de subventions d'investissement

Classe 8 - Comptes des autres charges et des autres produits

81 Valeurs comptables des cessions d'immobilisations (811/812/816)
82 Produits des cessions d'immobilisations (821/822/826)

83 Charges hors activités ordinaires
• 831 constatées / 833 restructuration / 834 pertes sur créances HAO
• 835 dons et libéralités accordés / 836 abandons de créances consentis
• 837 opérations de liquidation / 839 dépréciations/provisions court terme HAO

84 Produits hors activités ordinaires
• 841 constatés / 843 restructuration / 844 indemnités/subventions HAO (agricole)
• 845 dons et libéralités obtenus / 846 abandons de créances obtenus
• 847 opérations de liquidation / 848 transferts de charges HAO
• 849 reprises dépréciations/provisions court terme HAO

85 Dotations hors activités ordinaires (851-858)
86 Reprises de charges, provisions et dépréciations HAO (861-868)

87 Participation des travailleurs (871/874/878)
88 Subventions d'équilibre (881/884/886/888)

89 Impôts sur le résultat
• 891 impôts sur les bénéfices (8911-8913) / 892 rappel d'impôts antérieurs
• 895 impôt minimum forfaitaire IMF / 899 dégrèvements et annulations (8991/8994)

Classe 9 - Comptes des engagements hors bilan et comptes de la
comptabilité analytique de gestion (SUPPLEMENTARY — optional, not part of
core financial statements; seed minimally or skip for v1)

I. Comptes des engagements hors bilan
90 Engagements obtenus et engagements accordés
• 901-904 obtenus (financement/garantie/réciproques/autres)
• 905-908 accordés (financement/garantie/réciproques/autres)
91 Contreparties des engagements (911-918)

II. Comptes de la comptabilité analytique de gestion (CAGE)
92 Comptes réfléchis / 93 Comptes de reclassements / 94 Comptes de coûts /
95 Comptes de stocks / 96 Écarts sur coûts préétablis /
97 Différences de traitement comptable / 98 Comptes de résultats /
99 Comptes de liaisons internes
```

**Translation note for Cline:** name_fr uses the French names exactly as
above; name_en should be a reasonable plain-English translation (e.g. "101
Capital social" → "Share capital"), since this is a bilingual product.

---

## Part 2 — IFRS: confirmed, there is NO numbered chart of accounts

Unchanged from the prior version of this file — verified via IFRS's own
standard-setting body. IAS 1 specifies minimum required line items for
financial statement presentation (property/plant/equipment, intangibles,
inventories, trade receivables/payables, cash and equivalents, provisions,
financial liabilities, tax assets/liabilities, share capital and reserves),
not account numbers. Companies design their own internal numbering.

Sources:
- https://www.ifrs.org/issued-standards/list-of-standards/ias-1-presentation-of-financial-statements/
- https://ifrscommunity.com/knowledge-base/ias-1-presentation-of-financial-statements/

**What this means for the app:** OHADA gets the real, numbered, hierarchical
list above. IFRS gets an editable starting template organized around IAS
1's categories — not a fixed official list, because none exists.
