"""Backend-generated PDF export (Session 12) using ReportLab.

WHY backend PDF instead of browser print: window.print() unavoidably shows
browser-injected headers/footers (URL, timestamp, page numbers) that page
CSS CANNOT remove — that is a browser limitation, not a codebase fix. A
backend PDF gives us full layout control and a clean, professional document.

This service renders a generic report spec (called by per-report builders)
into a branded, controlled PDF:
  * on EVERY page: a thin header bar (business name, report title,
    "Page X of Y") and a footer bar (framework, generated timestamp) — all
    drawn by us, never by the browser.
  * page 1 identity block mirrors ReportHeader: business name, statement
    title (framework-correct, including the purpose-adapted names from the
    statement service), plus the report's period/framework/address rows.
  * section heading rows (bold, shaded), subtotal rows, and right-aligned
    numeric columns for a real financial layout.

Bilingual labels live HERE (not in the frontend i18n) because the backend
builds the document; `lang` selects which half is used. For OHADA financial
statements the names are identical in both languages by design (see
financial_statement_service._STATEMENT_NAMES — this service simply renders
whatever title it is handed).

Deterministic and read-only: this service never touches the ledger; it only
renders report payloads the routes pass in.
"""
from datetime import datetime, timezone
from decimal import Decimal
from typing import Iterable

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as canvas_module
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

PAGE_MARGIN = 16 * mm

# Framework/system label rows rendered in the identity block (EN / FR).
_LABELS: dict[str, dict[str, str]] = {
    "en": {
        "page_of": "Page {page} of {total}",
        "generated": "Generated on {ts}",
        "framework": "Framework",
        "period": "Period",
        "address": "Address",
        "rccm": "RCCM",
        "tax_id": "Tax ID",
        "date": "Date",
        "reference": "Reference",
        "description": "Description",
        "account_no": "N° compte",
        "account": "Account",
        "narration": "Narration",
        "debit": "Debit",
        "credit": "Credit",
        "source": "Source",
        "status": "Status",
        "cash_debit": "Cash Debit",
        "bank_debit": "Bank Debit",
        "cash_credit": "Cash Credit",
        "bank_credit": "Bank Credit",
        "balance": "Balance",
        "opening": "Opening",
        "movement": "Movement",
        "closing": "Closing",
        "dr": "Dr",
        "cr": "Cr",
        "total": "Total",
    },
    "fr": {
        "page_of": "Page {page} sur {total}",
        "generated": "Généré le {ts}",
        "framework": "Référentiel",
        "period": "Période",
        "address": "Adresse",
        "rccm": "RCCM",
        "tax_id": "N° fiscal",
        "date": "Date",
        "reference": "Référence",
        "description": "Libellé",
        "account_no": "N° compte",
        "account": "Compte",
        "narration": "Narration",
        "debit": "Débit",
        "credit": "Crédit",
        "source": "Source",
        "status": "Statut",
        "cash_debit": "Débit caisse",
        "bank_debit": "Débit banque",
        "cash_credit": "Crédit caisse",
        "bank_credit": "Crédit banque",
        "balance": "Solde",
        "opening": "Ouverture",
        "movement": "Mouvement",
        "closing": "Clôture",
        "dr": "Débit",
        "cr": "Crédit",
        "total": "Total",
    },
}


def _fmt_money(value) -> str:
    """Thousands-separated, up to 2 decimals (mirrors formatReportNumber)."""
    try:
        n = Decimal(str(value))
    except Exception:
        n = Decimal("0")
    if n == n.to_integral_value():
        return f"{int(n):,}"
# ---------------------------------------------------------------------------
# Canvas with controlled page furniture (header bar + footer, page X of Y)
# ---------------------------------------------------------------------------
class _ReportCanvas(canvas_module.Canvas):
    """Canvas that draws our header/footer on EVERY page.

    BaseDocTemplate onPage callbacks can't know the final total page count,
    so defer drawing until save() to make "Page X of Y" exact.
    """

    _furniture: dict = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_states: list[dict] = []

    def showPage(self):
        self._saved_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._saved_states)
        for state in self._saved_states:
            self.__dict__.update(state)
            self._draw_furniture(total)
            super().showPage()
        super().save()

    def _draw_furniture(self, total: int):
        f = type(self)._furniture
        w, h = self._pagesize
        lang = f.get("lang", "en")
        labels = _LABELS[lang]
        self.setStrokeColor(colors.HexColor("#334155"))
        self.setLineWidth(0.8)
        self.line(PAGE_MARGIN, h - 16 * mm, w - PAGE_MARGIN, h - 16 * mm)
        self.setFillColor(colors.HexColor("#0f172a"))
        self.setFont("Helvetica-Bold", 8.5)
        self.drawString(PAGE_MARGIN, h - 12 * mm, f.get("org_name", ""))
        self.setFont("Helvetica", 8.5)
        self.setFillColor(colors.HexColor("#475569"))
        self.drawString(
            PAGE_MARGIN,
            h - 14.5 * mm,
            f"{f.get('title', '')} · {f.get('period', '')}",
        )
        self.setFillColor(colors.HexColor("#64748b"))
        self.setFont("Helvetica", 8.5)
        self.drawRightString(
            w - PAGE_MARGIN,
            h - 12 * mm,
            labels["page_of"].format(page=self._pageNumber, total=total),
        )
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.6)
        self.line(PAGE_MARGIN, 12 * mm, w - PAGE_MARGIN, 12 * mm)
        self.setFont("Helvetica", 7.5)
        self.drawString(
            PAGE_MARGIN,
            8 * mm,
            labels["generated"].format(
                ts=f.get("generated_at", "").strftime("%d/%m/%Y %H:%M")
            ),
        )
        self.drawRightString(
            w - PAGE_MARGIN,
            8 * mm,
            f"{labels['framework']}: {f.get('framework', '')}",
        )
# ---------------------------------------------------------------------------
# Generic report builder
# ---------------------------------------------------------------------------
Row = tuple[str, list[str]]  # ('section'|'total'|'data', cells)


def _style() -> dict[str, ParagraphStyle]:
    ss = getSampleStyleSheet()
    base = ss["BodyText"]
    return {
        "org_name": ParagraphStyle(
            "org_name", parent=base, fontName="Helvetica-Bold", fontSize=17,
            leading=20, textColor=colors.HexColor("#0f172a"), spaceAfter=1,
        ),
        "title": ParagraphStyle(
            "title", parent=base, fontName="Helvetica-Bold", fontSize=12.5,
            leading=15, textColor=colors.HexColor("#1e3a8a"), spaceAfter=2,
        ),
        "meta": ParagraphStyle(
            "meta", parent=base, fontName="Helvetica", fontSize=8.5,
            leading=11, textColor=colors.HexColor("#475569"), spaceAfter=0,
        ),
        "section": ParagraphStyle(
            "section", parent=base, fontName="Helvetica-Bold", fontSize=9.5,
            leading=12, textColor=colors.HexColor("#0f172a"),
        ),
        "cell": ParagraphStyle(
            "cell", parent=base, fontName="Helvetica", fontSize=8.5,
            leading=10.5, textColor=colors.HexColor("#1e293b"),
        ),
        "cell_bold": ParagraphStyle(
            "cell_bold", parent=base, fontName="Helvetica-Bold", fontSize=8.5,
            leading=10.5, textColor=colors.HexColor("#0f172a"),
        ),
        "header_cell": ParagraphStyle(
            "header_cell", parent=base, fontName="Helvetica-Bold", fontSize=8,
            leading=10, textColor=colors.HexColor("#0f172a"),
        ),
    }


def _cell(text: str, bold: bool = False) -> Paragraph:
    return Paragraph(str(text), _style()["cell_bold" if bold else "cell"])


def _num_cell(text) -> Paragraph:
    return Paragraph(_fmt_money(text), ParagraphStyle(
        "num", fontName="Helvetica", fontSize=8.5, leading=10.5,
        alignment=TA_RIGHT, textColor=colors.HexColor("#1e293b"),
    ))


def _is_numeric_cell(cells: list[str]) -> bool:
    cleaned = "".join(str(c).replace(",", "").replace(" ", "") for c in cells if c != "")
    if not cleaned:
        return False
    return all(ch in "-0123456789." for ch in cleaned)


def build_report_pdf(
    *,
    org_name: str,
    title: str,
    period: str,
    footer_rows: list[tuple[str, str]],
    columns: list[tuple[str, str]],
    rows: Iterable[Row],
    lang: str = "en",
    generated_at: datetime | None = None,
) -> bytes:
    """Render a branded, controlled PDF for a report spec (see module doc)."""
    lang = lang if lang in ("en", "fr") else "en"
    generated_at = generated_at or datetime.now(timezone.utc)
    fw = ""
    for k, _v in footer_rows:
        if k.lower() == _LABELS[lang]["framework"].lower() or k.lower() == "framework":
            fw = _v
    _ReportCanvas._furniture = {
        "org_name": org_name,
        "title": title,
        "period": period,
        "framework": fw,
        "lang": lang,
        "generated_at": generated_at,
    }

    import io
    out = io.BytesIO()
    doc = BaseDocTemplate(
        out, pagesize=A4,
        leftMargin=PAGE_MARGIN, rightMargin=PAGE_MARGIN,
        topMargin=20 * mm, bottomMargin=18 * mm,
        pageCompression=0,
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
    doc.addPageTemplates([PageTemplate(id="all", frames=[frame])])

    st = _style()
    story = []

    # --- Identity block (page 1): mirrors the on-screen ReportHeader ---
    story.append(_cell(org_name)); story[-1].style = st["org_name"]
    story.append(_cell(title)); story[-1].style = st["title"]
    for k, v in footer_rows:
        story.append(_cell(f"{k}: {v}")); story[-1].style = st["meta"]
    story.append(Spacer(1, 3 * mm))

    # --- Table ---
    header_r = [_cell(c) for c, _ in columns]
    for h in header_r:
        h.style = st["header_cell"]
    data: list[list[Paragraph]] = [header_r]
    section_indexes: list[int] = []
    total_indexes: list[int] = []
    for kind, cells in rows:
        cells = list(cells)
        if kind == "section":
            data.append([_cell("  ".join(str(c) for c in cells))])
            section_indexes.append(len(data) - 1)
        elif kind == "total":
            data.append([_num_cell(c) if str(c) != "" else _cell("") for c in cells])
            total_indexes.append(len(data) - 1)
        else:
            data.append(
                [_num_cell(c) if _is_numeric_cell([str(c)]) else _cell(str(c)) for c in cells]
            )

    widths = []
    for _, a in columns:
        if a == "right":
            widths.append(0.13)
        elif a == "left":
            widths.append(0.44)
        else:
            widths.append(0.2)
    total_w = sum(widths)
    widths = [w / total_w * doc.width for w in widths]

    table = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    tstyle = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e8f0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    for i in section_indexes:
        tstyle.append(("SPAN", (0, i), (-1, i)))
        tstyle.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#e2e8f0")))
    for i in total_indexes:
        tstyle.append(("LINEABOVE", (0, i), (-1, i), 0.6, colors.HexColor("#94a3b8")))
    table.setStyle(TableStyle(tstyle))
    story.append(table)

    doc.build(story, canvasmaker=_ReportCanvas)
    return out.getvalue()
    return f"{n:,.2f}"