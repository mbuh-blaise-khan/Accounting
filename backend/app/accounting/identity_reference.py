"""Business-identity reference data (Business Profile Part 2).

FACTS USED HERE (verified against OHADA sources, do not "fix" from memory):
- OHADA has exactly 17 member states: Benin, Burkina Faso, Cameroon, Central
  African Republic, Chad, Comoros, Republic of Congo, Côte d'Ivoire,
  Democratic Republic of Congo, Gabon, Guinea, Guinea-Bissau, Equatorial
  Guinea, Mali, Niger, Senegal, Togo.
- OHADA's legal business forms come from the AUSCGIE uniform act: SARL
  (incl. the SARLU one-person variant), SA (incl. one-person variant), SAS
  (incl. SASU one-person variant), SNC, SCS, GIE, and Entreprise Individuelle
  (sole proprietor; informal/unregistered businesses commonly use this or no
  formal form at all).
- An OHADA workspace's country list is RESTRICTED to those 17 member states;
  an IFRS workspace may pick any ISO 3166-1 alpha-2 country.
"""
from app.models.enums import FrameworkCode

# The 17 OHADA member states, as ISO 3166-1 alpha-2 codes, with English and
# French display names (bilingual app). Sorted by French name for a stable,
# locale-friendly dropdown order.
OHADA_MEMBER_STATES = {
    "BJ": ("Benin", "Bénin"),
    "BF": ("Burkina Faso", "Burkina Faso"),
    "CM": ("Cameroon", "Cameroun"),
    "CF": ("Central African Republic", "République centrafricaine"),
    "TD": ("Chad", "Tchad"),
    "KM": ("Comoros", "Comores"),
    "CG": ("Republic of Congo", "République du Congo"),
    "CI": ("Côte d'Ivoire", "Côte d'Ivoire"),
    "CD": ("Democratic Republic of Congo", "République démocratique du Congo"),
    "GA": ("Gabon", "Gabon"),
    "GN": ("Guinea", "Guinée"),
    "GW": ("Guinea-Bissau", "Guinée-Bissau"),
    "GQ": ("Equatorial Guinea", "Guinée équatoriale"),
    "ML": ("Mali", "Mali"),
    "NE": ("Niger", "Niger"),
    "SN": ("Senegal", "Sénégal"),
    "TG": ("Togo", "Togo"),
}

# Legal business forms by framework: code -> (label, description_en,
# description_fr). Codes are the stored values (organizations.legal_form).
# OHADA list follows the AUSCGIE uniform act (see module docstring).
LEGAL_FORMS = {
    FrameworkCode.OHADA.value: [
        ("SARL", "SARL",
         "Limited liability company — the most common small-business form.",
         "Société à Responsabilité Limitée — la forme la plus courante pour les petites entreprises."),
        ("SARLU", "SARLU",
         "One-person variant of the SARL (a single shareholder).",
         "Variante unipersonnelle de la SARL (associé unique)."),
        ("SA", "SA",
         "Société Anonyme — company with a board structure, for larger businesses.",
         "Société Anonyme — structure avec conseil d'administration, pour les grandes entreprises."),
        ("SA_UNI", "SA (one-person)",
         "Société Anonyme with a single shareholder (one-person variant).",
         "Société Anonyme à associé unique (variante unipersonnelle)."),
        ("SAS", "SAS",
         "Société par Actions Simplifiée — flexible company whose internal rules are freely set.",
         "Société par Actions Simplifiée — société souple dont le fonctionnement est librement fixé."),
        ("SASU", "SASU",
         "One-person variant of the SAS (a single shareholder).",
         "Variante unipersonnelle de la SAS (associé unique)."),
        ("SNC", "SNC",
         "Société en Nom Collectif — general partnership; partners are jointly liable.",
         "Société en Nom Collectif — les associés sont indéfiniment et solidairement responsables."),
        ("SCS", "SCS",
         "Société en Commandite Simple — limited partnership with active and sleeping partners.",
         "Société en Commandite Simple — associés commandités et commanditaires."),
        ("GIE", "GIE",
         "Groupement d'Intérêt Économique — a grouping to pool economic activity, not a full company.",
         "Groupement d'Intérêt Économique — groupement pour mettre en commun une activité économique."),
        ("EI", "Entreprise Individuelle",
         "Sole proprietorship — the business and the owner are one legal person; common for informal businesses.",
         "Entreprise Individuelle — l'entreprise et son propriétaire ne font qu'un ; courante pour les activités informelles."),
    ],
    FrameworkCode.IFRS.value: [
        ("SOLE_PROP", "Sole Proprietorship",
         "One owner, personally responsible for the business.",
         "Un seul propriétaire, personnellement responsable de l'entreprise."),
        ("PARTNERSHIP", "Partnership",
         "Two or more owners sharing responsibility and profit.",
         "Deux propriétaires ou plus qui partagent responsabilités et bénéfices."),
        ("LLC", "LLC (Limited Liability Company)",
         "Owners' liability is limited to their investment.",
         "La responsabilité des associés est limitée à leurs apports."),
        ("LTD", "Ltd (Private Limited Company)",
         "Private company; shares are not traded publicly.",
         "Société privée ; les actions ne sont pas cotées en bourse."),
        ("PLC", "PLC (Public Limited Company)",
         "Public company whose shares may be traded on a stock exchange.",
         "Société ouverte dont les actions peuvent être cotées en bourse."),
        ("CORPORATION", "Corporation",
         "Legal entity separate from its owners, common in North America.",
         "Personne morale distincte de ses propriétaires, courante en Amérique du Nord."),
        ("NONPROFIT", "Nonprofit / NGO",
         "Organization that does not distribute profits to owners.",
         "Organisation qui ne distribue pas de bénéfices à des propriétaires."),
        ("COOPERATIVE", "Cooperative",
         "Owned and run by its members, with democratic control.",
         "Détenue et gérée par ses membres, avec un contrôle démocratique."),
    ],
}

# Explicit skip value for identity_type=learner (no business form applies).
LEGAL_FORM_NOT_APPLICABLE = "NOT_APPLICABLE"


def legal_form_options(framework: str) -> list[dict]:
    """Options for the searchable legal-form dropdown of one framework."""
    return [
        {"code": code, "label": label, "description_en": den, "description_fr": dfr}
        for code, label, den, dfr in LEGAL_FORMS.get(framework, [])
    ]


def is_valid_legal_form(framework: str, code: str | None) -> bool:
    if code is None:
        return True  # PATCH semantics: not provided
    if code == LEGAL_FORM_NOT_APPLICABLE:
        return True  # allowed only for learners — checked by the caller
    return any(entry[0] == code for entry in LEGAL_FORMS.get(framework, []))


def is_valid_country(framework: str, code: str | None) -> bool:
    """An OHADA workspace accepts ONLY the 17 member states; IFRS accepts any
    real ISO 3166-1 alpha-2 country. None = not provided (PATCH semantics)."""
    if code is None:
        return True
    code = code.upper()
    if framework == FrameworkCode.OHADA.value:
        return code in OHADA_MEMBER_STATES
    return code in COUNTRIES


def country_options(framework: str) -> list[dict]:
    """Country dropdown data: only the 17 member states for OHADA, the full
    international list for anything else (IFRS)."""
    if framework == FrameworkCode.OHADA.value:
        return [
            {"code": c, "name_en": en, "name_fr": fr}
            for c, (en, fr) in sorted(
                OHADA_MEMBER_STATES.items(), key=lambda kv: (kv[1][1], kv[1][0])
            )
        ]
    return [
        {"code": c, "name_en": en, "name_fr": fr}
        for c, (en, fr) in sorted(COUNTRIES.items(), key=lambda kv: (kv[1][1], kv[1][0]))
    ]


# Full ISO 3166-1 alpha-2 country list: code -> (name_en, name_fr).
COUNTRIES = {
    "AF": ("Afghanistan", "Afghanistan"),
    "AL": ("Albania", "Albanie"),
    "DZ": ("Algeria", "Algérie"),
    "AD": ("Andorra", "Andorre"),
    "AO": ("Angola", "Angola"),
    "AG": ("Antigua and Barbuda", "Antigua-et-Barbuda"),
    "AR": ("Argentina", "Argentine"),
    "AM": ("Armenia", "Arménie"),
    "AU": ("Australia", "Australie"),
    "AT": ("Austria", "Autriche"),
    "AZ": ("Azerbaijan", "Azerbaïdjan"),
    "BS": ("Bahamas", "Bahamas"),
    "BH": ("Bahrain", "Bahreïn"),
    "BD": ("Bangladesh", "Bangladesh"),
    "BB": ("Barbados", "Barbade"),
    "BY": ("Belarus", "Bélarus"),
    "BE": ("Belgium", "Belgique"),
    "BZ": ("Belize", "Belize"),
    "BJ": ("Benin", "Bénin"),
    "BT": ("Bhutan", "Bhoutan"),
    "BO": ("Bolivia", "Bolivie"),
    "BA": ("Bosnia and Herzegovina", "Bosnie-Herzégovine"),
    "BW": ("Botswana", "Botswana"),
    "BR": ("Brazil", "Brésil"),
    "BN": ("Brunei", "Brunei"),
    "BG": ("Bulgaria", "Bulgarie"),
    "BF": ("Burkina Faso", "Burkina Faso"),
    "BI": ("Burundi", "Burundi"),
    "CV": ("Cabo Verde", "Cap-Vert"),
    "KH": ("Cambodia", "Cambodge"),
    "CM": ("Cameroon", "Cameroun"),
    "CA": ("Canada", "Canada"),
    "CF": ("Central African Republic", "République centrafricaine"),
    "TD": ("Chad", "Tchad"),
    "CL": ("Chile", "Chili"),
    "CN": ("China", "Chine"),
    "CO": ("Colombia", "Colombie"),
    "KM": ("Comoros", "Comores"),
    "CG": ("Republic of Congo", "République du Congo"),
    "CD": ("Democratic Republic of Congo", "République démocratique du Congo"),
    "CR": ("Costa Rica", "Costa Rica"),
    "CI": ("Côte d'Ivoire", "Côte d'Ivoire"),
    "HR": ("Croatia", "Croatie"),
    "CU": ("Cuba", "Cuba"),
    "CY": ("Cyprus", "Chypre"),
    "CZ": ("Czechia", "Tchéquie"),
    "DJ": ("Djibouti", "Djibouti"),
    "DM": ("Dominica", "Dominique"),
    "DO": ("Dominican Republic", "République dominicaine"),
    "EC": ("Ecuador", "Équateur"),
    "EG": ("Egypt", "Égypte"),
    "SV": ("El Salvador", "Salvador"),
    "GQ": ("Equatorial Guinea", "Guinée équatoriale"),
    "ER": ("Eritrea", "Érythrée"),
    "EE": ("Estonia", "Estonie"),
    "SZ": ("Eswatini", "Eswatini"),
    "ET": ("Ethiopia", "Éthiopie"),
    "FJ": ("Fiji", "Fidji"),
    "FI": ("Finland", "Finlande"),
    "FR": ("France", "France"),
    "GA": ("Gabon", "Gabon"),
    "GM": ("Gambia", "Gambie"),
    "GE": ("Georgia", "Géorgie"),
    "DE": ("Germany", "Allemagne"),
    "GH": ("Ghana", "Ghana"),
    "GR": ("Greece", "Grèce"),
    "GD": ("Grenada", "Grenade"),
    "GT": ("Guatemala", "Guatemala"),
    "GN": ("Guinea", "Guinée"),
    "GW": ("Guinea-Bissau", "Guinée-Bissau"),
    "GY": ("Guyana", "Guyana"),
    "HT": ("Haiti", "Haïti"),
    "HN": ("Honduras", "Honduras"),
    "HU": ("Hungary", "Hongrie"),
    "IS": ("Iceland", "Islande"),
    "IN": ("India", "Inde"),
    "ID": ("Indonesia", "Indonésie"),
    "IR": ("Iran", "Iran"),
    "IQ": ("Iraq", "Irak"),
    "IE": ("Ireland", "Irlande"),
    "IL": ("Israel", "Israël"),
    "IT": ("Italy", "Italie"),
    "JM": ("Jamaica", "Jamaïque"),
    "JP": ("Japan", "Japon"),
    "JO": ("Jordan", "Jordanie"),
    "KZ": ("Kazakhstan", "Kazakhstan"),
    "KE": ("Kenya", "Kenya"),
    "KI": ("Kiribati", "Kiribati"),
    "KP": ("North Korea", "Corée du Nord"),
    "KR": ("South Korea", "Corée du Sud"),
    "KW": ("Kuwait", "Koweït"),
    "KG": ("Kyrgyzstan", "Kirghizistan"),
    "LA": ("Laos", "Laos"),
    "LV": ("Latvia", "Lettonie"),
    "LB": ("Lebanon", "Liban"),
    "LS": ("Lesotho", "Lesotho"),
    "LR": ("Liberia", "Liberia"),
    "LY": ("Libya", "Libye"),
    "LI": ("Liechtenstein", "Liechtenstein"),
    "LT": ("Lithuania", "Lituanie"),
    "LU": ("Luxembourg", "Luxembourg"),
    "MG": ("Madagascar", "Madagascar"),
    "MW": ("Malawi", "Malawi"),
    "MY": ("Malaysia", "Malaisie"),
    "MV": ("Maldives", "Maldives"),
    "ML": ("Mali", "Mali"),
    "MT": ("Malta", "Malte"),
    "MH": ("Marshall Islands", "Îles Marshall"),
    "MR": ("Mauritania", "Mauritanie"),
    "MU": ("Mauritius", "Maurice"),
    "MX": ("Mexico", "Mexique"),
    "FM": ("Micronesia", "Micronésie"),
    "MD": ("Moldova", "Moldavie"),
    "MC": ("Monaco", "Monaco"),
    "MN": ("Mongolia", "Mongolie"),
    "ME": ("Montenegro", "Monténégro"),
    "MA": ("Morocco", "Maroc"),
    "MZ": ("Mozambique", "Mozambique"),
    "MM": ("Myanmar", "Myanmar"),
    "NA": ("Namibia", "Namibie"),
    "NR": ("Nauru", "Nauru"),
    "NP": ("Nepal", "Népal"),
    "NL": ("Netherlands", "Pays-Bas"),
    "NZ": ("New Zealand", "Nouvelle-Zélande"),
    "NI": ("Nicaragua", "Nicaragua"),
    "NE": ("Niger", "Niger"),
    "NG": ("Nigeria", "Nigéria"),
    "MK": ("North Macedonia", "Macédoine du Nord"),
    "NO": ("Norway", "Norvège"),
    "OM": ("Oman", "Oman"),
    "PK": ("Pakistan", "Pakistan"),
    "PW": ("Palau", "Palaos"),
    "PS": ("Palestine", "Palestine"),
    "PA": ("Panama", "Panama"),
    "PG": ("Papua New Guinea", "Papouasie-Nouvelle-Guinée"),
    "PY": ("Paraguay", "Paraguay"),
    "PE": ("Peru", "Pérou"),
    "PH": ("Philippines", "Philippines"),
    "PL": ("Poland", "Pologne"),
    "PT": ("Portugal", "Portugal"),
    "QA": ("Qatar", "Qatar"),
    "RO": ("Romania", "Roumanie"),
    "RU": ("Russia", "Russie"),
    "RW": ("Rwanda", "Rwanda"),
    "KN": ("Saint Kitts and Nevis", "Saint-Kitts-et-Nevis"),
    "LC": ("Saint Lucia", "Sainte-Lucie"),
    "VC": ("Saint Vincent and the Grenadines", "Saint-Vincent-et-les-Grenadines"),
    "WS": ("Samoa", "Samoa"),
    "SM": ("San Marino", "Saint-Marin"),
    "ST": ("Sao Tome and Principe", "Sao Tomé-et-Principe"),
    "SA": ("Saudi Arabia", "Arabie saoudite"),
    "SN": ("Senegal", "Sénégal"),
    "RS": ("Serbia", "Serbie"),
    "SC": ("Seychelles", "Seychelles"),
    "SL": ("Sierra Leone", "Sierra Leone"),
    "SG": ("Singapore", "Singapour"),
    "SK": ("Slovakia", "Slovaquie"),
    "SI": ("Slovenia", "Slovénie"),
    "SB": ("Solomon Islands", "Îles Salomon"),
    "SO": ("Somalia", "Somalie"),
    "ZA": ("South Africa", "Afrique du Sud"),
    "SS": ("South Sudan", "Soudan du Sud"),
    "ES": ("Spain", "Espagne"),
    "LK": ("Sri Lanka", "Sri Lanka"),
    "SD": ("Sudan", "Soudan"),
    "SR": ("Suriname", "Suriname"),
    "SE": ("Sweden", "Suède"),
    "CH": ("Switzerland", "Suisse"),
    "SY": ("Syria", "Syrie"),
    "TJ": ("Tajikistan", "Tadjikistan"),
    "TZ": ("Tanzania", "Tanzanie"),
    "TH": ("Thailand", "Thaïlande"),
    "TL": ("Timor-Leste", "Timor oriental"),
    "TG": ("Togo", "Togo"),
    "TO": ("Tonga", "Tonga"),
    "TT": ("Trinidad and Tobago", "Trinité-et-Tobago"),
    "TN": ("Tunisia", "Tunisie"),
    "TR": ("Türkiye", "Turquie"),
    "TM": ("Turkmenistan", "Turkménistan"),
    "TV": ("Tuvalu", "Tuvalu"),
    "UG": ("Uganda", "Ouganda"),
    "UA": ("Ukraine", "Ukraine"),
    "AE": ("United Arab Emirates", "Émirats arabes unis"),
    "GB": ("United Kingdom", "Royaume-Uni"),
    "US": ("United States", "États-Unis"),
    "UY": ("Uruguay", "Uruguay"),
    "UZ": ("Uzbekistan", "Ouzbékistan"),
    "VU": ("Vanuatu", "Vanuatu"),
    "VA": ("Vatican City", "Vatican"),
    "VE": ("Venezuela", "Venezuela"),
    "VN": ("Viet Nam", "Viêt Nam"),
    "YE": ("Yemen", "Yémen"),
    "ZM": ("Zambia", "Zambie"),
    "ZW": ("Zimbabwe", "Zimbabwe"),
}
