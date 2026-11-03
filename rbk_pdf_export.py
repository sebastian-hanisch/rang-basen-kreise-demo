"""PDF-Export der Beschreibungen des aktuellen Systems (fpdf2). Kernschriften sind latin-1: Umlaute gehen, Sonderzeichen werden ersetzt."""

from __future__ import annotations

from fpdf import FPDF

import rbk_constants as C
from rbk_evaluation import Analysis, Settings, description_rows, verdict_descriptions

_REPLACE = {"→": "->", "–": "-", "—": "-", "−": "-", "≤": "<=", "≥": ">=", "·": "*", "€": "EUR", "„": '"', "“": '"', "×": "x", "≈": "~", "₁": "1", "₂": "2", "³": "3"}


def _s(text) -> str:
    out = str(text).replace("**", "")
    for old, new in _REPLACE.items():
        out = out.replace(old, new)
    return out.encode("latin-1", "replace").decode("latin-1")


def build_pdf(a: Analysis, settings: Settings) -> bytes:
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 9, _s("Rang, Basen, Kreise, Abschluss"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    plan = "feste sieben Punkte" if settings.system == "fano" else f"{a.inst.n} Standorte, Plan-Seed {settings.seed}"
    pdf.multi_cell(0, 5, _s(f"{C.SYSTEM_NAMES[settings.system]}; {plan}; {'Matroid' if a.is_matroid else 'kein Matroid'}."), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 8)
    widths = (80, 40, 40)
    heads = ("Beschreibung", "Zahl", "Rundreise")
    for h, w in zip(heads, widths):
        pdf.cell(w, 6, _s(h), border=1)
    pdf.ln()
    pdf.set_font("Helvetica", "", 8)
    for row in description_rows(a):
        for key, w in zip(heads, widths):
            pdf.cell(w, 5.5, _s(row[key]), border=1)
        pdf.ln()
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(0, 5, _s(f"Rang {a.rank}; kleinster Kreis: {a.girth if a.girth else '-'} Elemente; Flache nach Rang: " + ", ".join(f"{c} vom Rang {r}" for r, c in a.flats_by_rank) + "."), new_x="LMARGIN", new_y="NEXT")
    pdf.multi_cell(0, 5, _s(verdict_descriptions(a)[1]), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(0, 4, _s("Quelle: rang-basen-kreise-demo, Sebastian Hanisch."), new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())
