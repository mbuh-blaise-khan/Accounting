"""OHADA SYSCOHADA chart of accounts — real official structure (2017 révisé).

SOURCE: docs/ohada-ifrs-source-reference.md — the annex to the OHADA "Acte
uniforme relatif au droit comptable et à l'information financière", adopted
26 January 2017 (Journal Officiel 15 Feb 2017), currently in force.

This list is a REPRESENTATIVE subset covering all 9 classes and going at least
3 levels deep in the most-used sub-classes (10 Capital, 21 Immobilisations
incorporelles, 40 Fournisseurs, 41 Clients, 52 Banques, 57 Caisse, 60 Achats,
66 Charges de personnel, 70 Ventes). It is NOT the full ~900-line official list
— seed coverage is representative so hierarchy/autocomplete are demonstrable.
Deeper measurement/convention rules are deliberately out of scope.

Numbering logic (from the source's own "Constantes"): digit count = level
(2 = main account, 3 = sub-account, 4 = sub-sub-account); first digit = class;
a trailing 9 in 3+ digit codes is the inverse/balancing line. `parent` stores
the code of the parent; the seeder resolves it to a `parent_account_id`.

`account_class` is the simplified 5-category view (its normal-balance logic).
Class 9 (off-balance-sheet / supplementary) and Class 8 are represented truly
by `ohada_class`, so they are not flattened into 5 buckets. Class 9 accounts
carry a best-fit `account_class` (liability) as a placeholder because they do
not belong to a financial-statement category.
"""
from app.models.enums import AccountClass as AC

# normal_balance derived deterministically from the plain account class.
_CLASS_BALANCE = {
    AC.asset.value: "debit",
    AC.liability.value: "credit",
    AC.equity.value: "credit",
    AC.revenue.value: "credit",
    AC.expense.value: "debit",
}


def _o(code, name_en, name_fr, cls, parent=None, desc=""):
    return {
        "code": code,
        "name_en": name_en,
        "name_fr": name_fr,
        "account_class": cls.value,
        "normal_balance": _CLASS_BALANCE[cls.value],
        "parent": parent,
        "description": desc,
    }


# Class 1 - Comptes de ressources durables (equity + long-term debt)
# Class 2 - Comptes d'actif immobilisé (fixed assets)
# Class 3 - Comptes de stocks (inventory)
# Class 4 - Comptes de tiers (third parties)
# Class 5 - Comptes de trésorerie (cash / treasury)
# Class 6 - Comptes de charges des activités ordinaires (ordinary expenses)
# Class 7 - Comptes de produits des activités ordinaires (ordinary revenue)
# Class 8 - Autres charges & produits (extraordinary / asset disposals)
# Class 9 - Engagements hors bilan + CAGE (SUPPLEMENTARY/optional)

# (ohada_class is derived from the code's first digit during seeding; the
# entries only carry code/name/class/parent.)

OHADA_CHART: list[dict] = [
    # --- Class 1 : ressources durables ---
    _o("10", "Capital", "Capital", AC.equity),
    _o("101", "Share capital", "Capital social", AC.equity, "10"),
    _o("1011", "Capital subscribed, called, paid, not amortised", "Capital souscrit, appelé, versé, non amorti", AC.equity, "101"),
    _o("1014", "Capital subscribed, called, paid, amortised", "Capital souscrit, appelé, versé, amorti", AC.equity, "101"),
    _o("109", "Subscribers - capital subscribed not called", "Apporteurs, capital souscrit, non appelé", AC.equity, "10"),
    _o("11", "Reserves", "Réserves", AC.equity),
    _o("111", "Legal reserve", "Réserve légale", AC.equity, "11"),
    _o("118", "Other reserves", "Autres réserves", AC.equity, "11"),
    _o("12", "Retained earnings", "Report à nouveau", AC.equity),
    _o("13", "Net income of the year", "Résultat net de l'exercice", AC.equity),
    _o("16", "Borrowings and assimilated liabilities", "Emprunts et dettes assimilées", AC.liability),
    _o("19", "Provisions for risks and charges", "Provisions pour risques et charges", AC.liability),

    # --- Class 2 : actif immobilisé ---
    _o("21", "Intangible fixed assets", "Immobilisations incorporelles", AC.asset),
    _o("211", "Development costs", "Frais de développement", AC.asset, "21"),
    _o("212", "Patents, licences, concessions and similar rights", "Brevets, licences, concessions et droits similaires", AC.asset, "21"),
    _o("2121", "Patents", "Brevets", AC.asset, "212"),
    _o("213", "Software and websites", "Logiciels et sites internet", AC.asset, "21"),
    _o("2131", "Software", "Logiciels", AC.asset, "213"),
    _o("2132", "Websites", "Sites internet", AC.asset, "213"),
    _o("22", "Land", "Terrains", AC.asset),
    _o("221", "Agricultural and forest land", "Terrains agricoles et forestiers", AC.asset, "22"),
    _o("23", "Buildings, technical installations and fittings", "Bâtiments, installations techniques et agencements", AC.asset),
    _o("231", "Buildings on own land", "Bâtiments sur sol propre", AC.asset, "23"),
    _o("24", "Plant, furniture and biological assets", "Matériel, mobilier et actifs biologiques", AC.asset),
    _o("241", "Industrial and commercial plant", "Matériel industriel et commercial", AC.asset, "24"),
    _o("25", "Advances and prepayments on fixed assets", "Avances et acomptes versés sur immobilisations", AC.asset),
    _o("26", "Investments in associates", "Titres de participation", AC.asset),
    _o("27", "Other fixed financial assets", "Autres immobilisations financières", AC.asset),
    _o("271", "Loans and receivables", "Prêts et créances", AC.asset, "27"),
    _o("28", "Accumulated depreciation", "Amortissements", AC.asset),

    # --- Class 3 : stocks ---
    _o("31", "Goods for resale", "Marchandises", AC.asset),
    _o("32", "Raw materials and related supplies", "Matières premières et fournitures liées", AC.asset),
    _o("34", "Goods in progress", "Produits en cours", AC.asset),
    _o("36", "Finished goods", "Produits finis", AC.asset),

    # --- Class 4 : tiers ---
    _o("40", "Suppliers and related accounts", "Fournisseurs et comptes rattachés", AC.liability),
    _o("401", "Suppliers - amounts payable", "Fournisseurs, dettes en compte", AC.liability, "40"),
    _o("4011", "Suppliers - ordinary", "Fournisseurs ordinaires", AC.liability, "401"),
    _o("408", "Suppliers - invoices not yet received", "Fournisseurs, factures non parvenues", AC.liability, "40"),
    _o("41", "Customers and related accounts", "Clients et comptes rattachés", AC.asset),
    _o("411", "Customers", "Clients", AC.asset, "41"),
    _o("4111", "Customers - ordinary", "Clients ordinaires", AC.asset, "411"),
    _o("419", "Customers - credit balances", "Clients créditeurs", AC.liability, "41"),
    _o("42", "Personnel", "Personnel", AC.liability),
    _o("422", "Remuneration due", "Rémunérations dues", AC.liability, "42"),
    _o("43", "Social organisations", "Organismes sociaux", AC.liability),
    _o("431", "Social security", "Sécurité sociale", AC.liability, "43"),
    _o("44", "State and public authorities", "État et collectivités publiques", AC.liability),
    _o("441", "Corporate income tax", "Impôt sur les bénéfices", AC.liability, "44"),

    # --- Class 5 : trésorerie ---
    _o("50", "Short-term investments", "Titres de placement", AC.asset),
    _o("52", "Banks", "Banques", AC.asset),
    _o("521", "Banks - local", "Banques locales", AC.asset, "52"),
    _o("5211", "Banks - local, national currency", "Banques locales - monnaie nationale", AC.asset, "521"),
    _o("5215", "Banks - local, foreign currency", "Banques locales - devises", AC.asset, "521"),
    _o("57", "Cash", "Caisse", AC.asset),
    _o("571", "Cash - head office", "Caisse - siège social", AC.asset, "57"),
    _o("5711", "Cash - head office, national currency", "Caisse - monnaie nationale", AC.asset, "571"),
    _o("5712", "Cash - head office, foreign currency", "Caisse - devises", AC.asset, "571"),

    # --- Class 6 : charges des activités ordinaires ---
    _o("60", "Purchases and stock variations", "Achats et variations de stocks", AC.expense),
    _o("601", "Purchases of goods for resale", "Achats de marchandises", AC.expense, "60"),
    _o("6011", "Purchases of goods - local", "Achats de marchandises - marché local", AC.expense, "601"),
    _o("602", "Purchases of raw materials", "Achats de matières premières", AC.expense, "60"),
    _o("62", "External services", "Services extérieurs", AC.expense),
    _o("622", "Rent and rental charges", "Locations et charges locatives", AC.expense, "62"),
    _o("63", "Other external services", "Autres services extérieurs", AC.expense),
    _o("64", "Taxes and duties", "Impôts et taxes", AC.expense),
    _o("65", "Other charges", "Autres charges", AC.expense),
    _o("66", "Personnel costs", "Charges de personnel", AC.expense),
    _o("661", "Remuneration - national staff", "Rémunérations du personnel national", AC.expense, "66"),
    _o("6611", "Salaries and wages", "Salaires et appointements", AC.expense, "661"),
    _o("67", "Financial expenses and similar charges", "Frais financiers et charges assimilées", AC.expense),
    _o("68", "Depreciation expense", "Dotations aux amortissements", AC.expense),

    # --- Class 7 : produits des activités ordinaires ---
    _o("70", "Sales", "Ventes", AC.revenue),
    _o("701", "Sales of goods for resale", "Ventes de marchandises", AC.revenue, "70"),
    _o("7011", "Sales of goods - local", "Ventes de marchandises - marché local", AC.revenue, "701"),
    _o("706", "Sales of services", "Services vendus", AC.revenue, "70"),
    _o("71", "Operating subsidies", "Subventions d'exploitation", AC.revenue),
    _o("75", "Other operating income", "Autres produits", AC.revenue),
    _o("77", "Financial income and similar revenue", "Revenus financiers et produits assimilés", AC.revenue),

    # --- Class 8 : autres charges et autres produits ---
    _o("81", "Carrying amounts of fixed asset disposals", "Valeurs comptables des cessions d'immobilisations", AC.expense),
    _o("82", "Proceeds of fixed asset disposals", "Produits des cessions d'immobilisations", AC.revenue),
    _o("83", "Expenses outside ordinary activities", "Charges hors activités ordinaires", AC.expense),
    _o("84", "Income outside ordinary activities", "Produits hors activités ordinaires", AC.revenue),
    _o("89", "Income tax on result", "Impôts sur le résultat", AC.expense),

    # --- Class 9 : engagements hors bilan + CAGE (SUPPLEMENTARY, optional,
    #     not part of core financial statements; seeded minimally) ---
    _o("90", "Commitments received and given (off-balance-sheet)", "Engagements obtenus et engagements accordés", AC.liability),
    _o("901", "Commitments received", "Engagements obtenus", AC.liability, "90"),
    _o("905", "Commitments given", "Engagements accordés", AC.liability, "90"),
    _o("92", "Management accounting accounts (CAGE)", "Comptes de la comptabilité analytique de gestion", AC.liability),
]