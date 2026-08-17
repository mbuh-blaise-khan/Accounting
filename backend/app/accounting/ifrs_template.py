"""IFRS starting template — NOT a fixed official chart (none exists).

Per docs/ohada-ifrs-source-reference.md, IFRS (IAS 1) specifies minimum
required presentation categories — property/plant/equipment, intangibles,
inventories, trade receivables/payables, cash and equivalents, provisions,
financial liabilities, tax assets/liabilities, share capital and reserves —
but NO mandated account numbering. Companies design their own.

So IFRS workspaces get an EDITABLE STARTING TEMPLATE organized under the plain
5-class model (asset/liability/equity/revenue/expense), with friendly codes the
business is expected to adapt to its own chart. `ohada_class` stays NULL for
these accounts.
"""
from app.models.enums import AccountClass as AC

_CLASS_BALANCE = {
    AC.asset.value: "debit",
    AC.liability.value: "credit",
    AC.equity.value: "credit",
    AC.revenue.value: "credit",
    AC.expense.value: "debit",
}


def _o(code, name_en, name_fr, cls, desc=""):
    return {
        "code": code,
        "name_en": name_en,
        "name_fr": name_fr,
        "account_class": cls.value,
        "normal_balance": _CLASS_BALANCE[cls.value],
        "parent": None,
        "description": desc,
    }


IFRS_TEMPLATE: list[dict] = [
    # IAS 1.54-aligned asset categories
    _o("1000", "Cash and cash equivalents", "Trésorerie et équivalents de trésorerie", AC.asset),
    _o("1100", "Trade and other receivables", "Clients et autres créances", AC.asset),
    _o("1200", "Inventories", "Stocks", AC.asset),
    _o("1300", "Property, plant and equipment", "Immobilisations corporelles", AC.asset),
    _o("1400", "Intangible assets", "Immobilisations incorporelles", AC.asset),
    _o("1500", "Investments", "Placements", AC.asset),
    _o("1600", "Current tax assets", "Créances d'impôt exigible", AC.asset),
    _o("1700", "Prepayments", "Charges constatées d'avance", AC.asset),
    # IAS 1.54-aligned liability categories
    _o("2000", "Trade and other payables", "Fournisseurs et autres dettes", AC.liability),
    _o("2100", "Provisions", "Provisions", AC.liability),
    _o("2200", "Borrowings (financial liabilities)", "Emprunts (passifs financiers)", AC.liability),
    _o("2300", "Current tax liabilities", "Dettes d'impôt exigible", AC.liability),
    _o("2400", "Deferred tax liabilities", "Impôts différés", AC.liability),
    _o("2500", "Accruals", "Dettes constatées d'avance", AC.liability),
    # Equity
    _o("3000", "Share capital", "Capital social", AC.equity),
    _o("3100", "Share premium", "Primes d'émission", AC.equity),
    _o("3200", "Retained earnings", "Résultats non distribués", AC.equity),
    _o("3300", "Other reserves", "Autres réserves", AC.equity),
    # Revenue
    _o("4000", "Sales revenue", "Produits des ventes", AC.revenue),
    _o("4100", "Service revenue", "Produits des services", AC.revenue),
    _o("4200", "Other income", "Autres produits", AC.revenue),
    # Expenses
    _o("5000", "Cost of sales", "Coût des ventes", AC.expense),
    _o("5100", "Operating expenses", "Charges opérationnelles", AC.expense),
    _o("5200", "Personnel costs", "Charges de personnel", AC.expense),
    _o("5300", "Depreciation and amortisation", "Dotations aux amortissements", AC.expense),
    _o("5400", "Finance costs", "Charges financières", AC.expense),
    _o("5500", "Other expenses", "Autres charges", AC.expense),
]