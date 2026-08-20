"""IFRS starting template — NOT a fixed official chart (none exists).

Per docs/ohada-ifrs-source-reference.md, IFRS (IAS 1) specifies minimum
required presentation categories — property/plant/equipment, intangibles,
inventories, trade receivables/payables, cash and equivalents, provisions,
financial liabilities, tax assets/liabilities, share capital and reserves —
but NO mandated account numbering. Companies design their own.

Part B: IFRS accounts therefore carry NO code. Each entry omits `code`
entirely; the seeder stores `code=NULL` (the shared `accounts.code` column is
kept for the OHADA side, where numbering is legally mandated). The template is
an EDITABLE STARTING TEMPLATE under the plain 5-class model
(asset/liability/equity/revenue/expense); `ohada_class_number` stays NULL.
"""
from app.models.enums import AccountClass as AC

_CLASS_BALANCE = {
    AC.asset.value: "debit",
    AC.liability.value: "credit",
    AC.equity.value: "credit",
    AC.revenue.value: "credit",
    AC.expense.value: "debit",
}


def _o(name_en, name_fr, cls, desc=""):
    # No "code" key: IFRS accounts never get a code (Part B).
    return {
        "name_en": name_en,
        "name_fr": name_fr,
        "account_class": cls.value,
        "normal_balance": _CLASS_BALANCE[cls.value],
        "parent": None,
        "description": desc,
    }


IFRS_TEMPLATE: list[dict] = [
    # IAS 1.54-aligned asset categories
    _o("Cash and cash equivalents", "Trésorerie et équivalents de trésorerie", AC.asset),
    _o("Trade and other receivables", "Clients et autres créances", AC.asset),
    _o("Inventories", "Stocks", AC.asset),
    _o("Property, plant and equipment", "Immobilisations corporelles", AC.asset),
    _o("Intangible assets", "Immobilisations incorporelles", AC.asset),
    _o("Investments", "Placements", AC.asset),
    _o("Current tax assets", "Créances d'impôt exigible", AC.asset),
    _o("Prepayments", "Charges constatées d'avance", AC.asset),
    # IAS 1.54-aligned liability categories
    _o("Trade and other payables", "Fournisseurs et autres dettes", AC.liability),
    _o("Provisions", "Provisions", AC.liability),
    _o("Borrowings (financial liabilities)", "Emprunts (passifs financiers)", AC.liability),
    _o("Current tax liabilities", "Dettes d'impôt exigible", AC.liability),
    _o("Deferred tax liabilities", "Impôts différés", AC.liability),
    _o("Accruals", "Dettes constatées d'avance", AC.liability),
    # Equity
    _o("Share capital", "Capital social", AC.equity),
    _o("Share premium", "Primes d'émission", AC.equity),
    _o("Retained earnings", "Résultats non distribués", AC.equity),
    _o("Other reserves", "Autres réserves", AC.equity),
    # Revenue
    _o("Sales revenue", "Produits des ventes", AC.revenue),
    _o("Service revenue", "Produits des services", AC.revenue),
    _o("Other income", "Autres produits", AC.revenue),
    # Expenses
    _o("Cost of sales", "Coût des ventes", AC.expense),
    _o("Operating expenses", "Charges opérationnelles", AC.expense),
    _o("Personnel costs", "Charges de personnel", AC.expense),
    _o("Depreciation and amortisation", "Dotations aux amortissements", AC.expense),
    _o("Finance costs", "Charges financières", AC.expense),
    _o("Other expenses", "Autres charges", AC.expense),
]