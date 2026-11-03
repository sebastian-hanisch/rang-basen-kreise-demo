"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

N_MIN, N_MAX, DEFAULT_N = 6, 9, 7           # Standorte inklusive Depot (Knoten A); bis 9 (16 mögliche Leitungen)
SEED_MAX, DEFAULT_SEED = 999999, 8
HUB_FACTOR = 0.4                            # nur vom Plan-Erzeuger gebraucht (keine Nabe in dieser Demo)
COST_SCALE = 100                            # Kosten einer Leitung = Entfernung auf dem Plan mal 100 (für das Budget-System)
BUDGET_SHARE = 0.4                          # Budget-System: zulässig ist, was zusammen höchstens 40 % der Kosten aller Leitungen kostet
UNIFORM_K = 4                               # uniformes Matroid: höchstens 4 Leitungen
GRID = 4                                    # Standorte als Vektoren: Koordinaten mal 4, gerundet, Vektor (x, y, 1)
CABLE_COLORS = ("rot", "grün", "blau")      # Kabelfarben der Leitungen
AXIOM_MAX_ELEMENTS = 12                     # die fünf Axiomprüfungen am gewählten System nur bis zu so vielen Elementen (sonst zu langsam)
ENUM_MAX_N = 5                              # alle Unabhängigkeitssysteme bis zu so vielen Elementen aufzählen
CLOSURE_MAX_N = 5                           # den Abschlussoperator bei der Aufzählung bis zu so vielen Elementen prüfen
BASIS_FAMILY_N = 5                          # Basenfamilien mit Basenaustausch zählen für diese Elementzahl

SYSTEMS = ("wald", "farben", "anschluss", "uniform", "vektoren", "fano", "paarung", "wald2", "budget", "standorte", "wald_farben")
MATROID_SYSTEMS = ("wald", "farben", "anschluss", "uniform", "vektoren", "fano")
SYSTEM_NAMES = {
    "wald": "Wald (graphisches Matroid)",
    "farben": "höchstens eine Leitung je Kabelfarbe (Partitionsmatroid)",
    "anschluss": "jede Leitung mit eigenem Anschluss-Standort (bizirkulares Matroid)",
    "uniform": "höchstens 4 Leitungen (uniformes Matroid)",
    "vektoren": "Standorte als Vektoren über R (lineares Matroid)",
    "fano": "Fano-Ebene (lineares Matroid über GF(2))",
    "paarung": "Paarung (höchstens 1 Leitung je Standort)",
    "wald2": "Wald, höchstens 2 Leitungen je Standort",
    "budget": "Budget-Auswahl (Rucksack auf den Leitungen)",
    "standorte": "Standorte ohne Nachbarn (unabhängige Menge)",
    "wald_farben": "Wald und höchstens eine Leitung je Kabelfarbe (Schnitt zweier Matroide)",
}

COLOR_BASE = "#2F6B65"
COLOR_CIRCUIT = "#d95f02"
COLOR_ELEMENT = "#1b9e77"
COLOR_FLAT = "#4c78a8"
COLOR_CLOSURE = "#f0a30a"
COLOR_OTHER = "rgba(150,150,150,0.55)"
COLOR_NODE = "#4c78a8"
COLOR_DEPOT = "#f0a30a"
COLOR_LINE = "#4c78a8"
COLOR_LINE2 = "#d95f02"
CABLE_RGB = {"rot": "rgba(200,60,60,0.55)", "grün": "rgba(60,150,80,0.55)", "blau": "rgba(70,110,200,0.55)"}

PRESETS = {
    "Standardfall (Voreinstellung)": {"n": DEFAULT_N, "seed": DEFAULT_SEED, "system": "wald"},
    "Kabelfarben": {"n": DEFAULT_N, "seed": DEFAULT_SEED, "system": "farben"},
    "Fano-Ebene": {"n": DEFAULT_N, "seed": DEFAULT_SEED, "system": "fano"},
    "Paarung": {"n": DEFAULT_N, "seed": DEFAULT_SEED, "system": "paarung"},
    "Wald und Farbregel": {"n": DEFAULT_N, "seed": DEFAULT_SEED, "system": "wald_farben"},
}
PRESET_HELP = {
    "Standardfall (Voreinstellung)": "Wald auf dem Leitungsnetz: zu jeder Basis und jeder weiteren Leitung gibt es genau einen Kreis.",
    "Kabelfarben": "Höchstens eine Leitung je Kabelfarbe: ein Partitionsmatroid, die Kreise sind die Paare gleicher Farbe.",
    "Fano-Ebene": "Sieben Punkte, 14 Kreise (7 Geraden und 7 Vierermengen), 16 Flache.",
    "Paarung": "Höchstens eine Leitung je Standort: kein Matroid, in B + e liegen oft mehrere Kreise.",
    "Wald und Farbregel": "Wald und eine Leitung je Farbe zugleich: ein Schnitt zweier Matroide, bei dem in B + e auch zwei Kreise liegen können.",
}
