# Rang, Basen, Kreise, Abschluss – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-rang-basen-kreise-demo.streamlit.app/)** -->

Viertes Stück der Reihe **Matroide und Submodularität** (Bereich Kombinatorik) in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“. Ein Matroid ist durch seine zulässigen (unabhängigen) Mengen bestimmt, aber das ist nur **eine** von fünf gleichwertigen Beschreibungen: **Basen** (die größten zulässigen Mengen), **Kreise** (die minimalen unzulässigen Mengen), die **Rangfunktion** (wie groß die größte zulässige Teilmenge ist) und der **Abschluss** (welche Elemente den Rang nicht erhöhen). Die Demo zeigt, dass jede Beschreibung die anderen bestimmt, dass die fünf Axiomsysteme auf allen kleinen Systemen übereinstimmen, und dass der Tausch aus Stück 1 der **Fundamentalkreis** ist.

**Einordnung in die Reihe:** Nachfolger von [matroid-demo](../matroid-demo) (Stück 3: Austauschaxiom, Zertifikat, elf Beispielsysteme), [unabhängigkeitssystem-demo](../unabhaengigkeitssystem-demo) (Stück 2) und [greedy-austausch-demo](../greedy-austausch-demo) (Stück 1: der Tausch beim Spannbaum). Vorgriff: Stück 5 („Greedy genau dann optimal für alle Gewichte, wenn Matroid“), Stück 6 (Dualität: der Kokreis als Gegenstück zum Kreis, Nicht-Graphisches), Stück 7 (Schnitt zweier Matroide). Nachbarn: [mst-sensitivity-demo](../mst-sensitivity-demo) (Fundamentalkreise im Spannbaum für Toleranzen und Ausfall; hier die Struktur dahinter).

## Warum dieses Problem

Stück 3 hat ein Matroid über das Austauschaxiom der zulässigen Mengen eingeführt. Das lässt offen, **wie sich dasselbe Matroid sonst beschreiben lässt** und **was der Tausch aus Stück 1 strukturell ist**. Die Antwort: Legt man zu einer Basis B ein Element e dazu, entsteht **genau ein Kreis**, der Fundamentalkreis C(B, e), und B − f + e ist genau dann wieder eine Basis, wenn f auf diesem Kreis liegt. Dazu kommt eine praktische Beobachtung: Die Beschreibungen sind sehr verschieden lang. Beim Wald auf dem Plan hat das System 1316 zulässige Mengen, 180 Basen, aber nur 32 Kreise.

## Befunde und Korrekturen gegenüber dem Plan

- **Abschlussoperator bis 5 Elemente statt 4:** Der Plan (`PLAN-04-rang-basen-kreise.md` im Planungsordner der Linie) hatte den Abschlussoperator nur bis 4 Elemente geprüft. Mit einer Prüfung über einzelne Elemente (statt über alle Obermengen) läuft er auch auf 5 Elementen in wenigen Sekunden.
- **Submodularität in lokaler Form:** Die App prüft die Submodularität des Rangs in der Form des abnehmenden Zusatznutzens (r(A + x) + r(A + y) ≥ r(A + x + y) + r(A) für alle A, x, y). Das ist gleichwertig zur Form über alle Paare von Mengen und weit schneller; der Test vergleicht beide an 150 zufälligen Systemen.
- **Axiomprüfung auf Abruf und nur bis 12 Elemente:** Die Prüfung aller fünf Axiomsysteme am gewählten System läuft auf Knopfdruck und bis 12 Elemente (7 Standorte); bei 16 Elementen wären es zu viele Basen- und Kreispaare.
- **Hauptansicht plus vier Experimente:** Die fünf geplanten Prüfungen (Fundamentalkreis und Tausch, fünf Beschreibungen, Abschluss und Flache, alle kleinen Systeme, Kontrast) stehen als Hauptansicht und vier nummerierte Experimente; die Spielwiese prüft von Hand die Kreise in B + e.
- **Fano-Zahlen:** 14 Kreise und 16 Flache sind in den eingesehenen Quellen nicht belegt; hier gemessen.

## Modell

Dieselben elf Systeme wie in Stück 3 auf einem **Leitungsnetz mit farbigen Kabeln** (n Standorte, Depot A in der Mitte, min(n(n − 1)/2, 2n − 2) mögliche Leitungen, drei Kabelfarben), davon sechs Matroide (Wald, Kabelfarben, Anschluss-Standort bizirkular, höchstens 4 Leitungen, Standorte als Vektoren, Fano-Ebene) und fünf, die keine sind (Paarung, Wald mit höchstens 2 Leitungen je Standort, Budget-Auswahl, Standorte ohne Nachbarn, Wald mit Farbregel). Formeln und Axiomsysteme stehen im 📐-Expander der App.

## Methodik

- **Rang** r(F): größte zulässige Teilmenge von F, für alle Teilmengen per Rekursion (`System._ranks`).
- **Basen:** maximale zulässige Mengen. **Kreise:** minimale unzulässige Mengen (`System.bases`, `System.circuits`).
- **Abschluss und Flache:** cl(F) = F plus alle e mit r(F + e) = r(F); ein Flach ist eine Menge mit cl(F) = F (`System.closure`, `System.flats`).
- **Fundamentalkreis:** der einzige Kreis in B + e, wenn es genau einen gibt (`System.fundamental_circuit`); Tausch B − f + e ist Basis, wenn die Menge maximal zulässig ist.
- **Rundreise:** aus Basen (Hülle nach unten), Kreisen (kein Kreis enthalten), Rang (r(I) = |I|) und Abschluss (kein Element im Abschluss der übrigen) werden die zulässigen Mengen zurückgewonnen und mit den ursprünglichen verglichen (`round_trips`).
- **Axiomprüfungen:** Austausch (Stück 3), Basenaustausch, Kreiseliminierung, Submodularität des Rangs und die vier Eigenschaften des Abschlussoperators (`check_*`); aufgezählt über alle Unabhängigkeitssysteme mit höchstens 5 Elementen (`axiom_agreement`).
- **Basenfamilien:** alle nichtleeren Familien gleich großer Teilmengen von {1, …, n}, die den Basenaustausch erfüllen (`count_basis_families`).

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen stehen in `tests/test_claims.py` und werden dort mit den Funktionen der App nachgerechnet. Plan: 7 Standorte, 12 mögliche Leitungen, Seed 8 (die Fano-Ebene ist vom Plan unabhängig).

| System | zulässige Mengen | Basen | Kreise | Flache | Rang | Matroid |
|---|---|---|---|---|---|---|
| Wald (graphisches Matroid) | 1 316 | 180 | 32 | 256 | 6 | ja |
| höchstens eine Leitung je Kabelfarbe (Partitionsmatroid) | 96 | 42 | 25 | 8 | 3 | ja |
| jede Leitung mit eigenem Anschluss-Standort (bizirkulares Matroid) | 2 634 | 311 | 93 | 1 420 | 7 | ja |
| höchstens 4 Leitungen (uniformes Matroid) | 794 | 495 | 792 | 300 | 4 | ja |
| Standorte als Vektoren über R (lineares Matroid) | 56 | 28 | 20 | 19 | 3 | ja |
| Fano-Ebene (lineares Matroid über GF(2)) | 57 | 28 | 14 | 16 | 3 | ja |
| Paarung (höchstens 1 Leitung je Standort) | 60 | 18 | 35 | 39 | 3 | nein |
| Wald, höchstens 2 Leitungen je Standort | 690 | 58 | 59 | 286 | 6 | nein |
| Budget-Auswahl (Rucksack auf den Leitungen) | 1 093 | 196 | 234 | 405 | 6 | nein |
| Standorte ohne Nachbarn (unabhängige Menge) | 19 | 6 | 12 | 9 | 3 | nein |
| Wald und höchstens eine Leitung je Kabelfarbe (Schnitt zweier Matroide) | 94 | 40 | 27 | 10 | 3 | nein |

Bei den Systemen, die keine Matroide sind, sind „Basen“ die maximalen zulässigen Mengen; sie haben verschiedene Größen (Paarung: 2 mit 2 und 16 mit 3; Wald mit Grad ≤ 2: 34 mit 5 und 24 mit 6), ausgenommen der Schnitt aus Wald und Farbregel.

| Frage | Befund |
|---|---|
| **Fünf Axiomensysteme gleich?** (alle 7 773 Unabhängigkeitssysteme auf 1 bis 5 Elementen) | Austausch, Basenaustausch, Kreiseliminierung, Submodularität des Rangs und Abschlussoperator stimmen bei **allen** überein: **0** Abweichungen. Matroide 2, 5, 16, 68, **406** bei n = 1 bis 5 (von 2, 5, 19, 167, 7 580 Systemen). |
| **Basenfamilien** | Auf 5 Elementen erfüllen **406** Familien gleich großer Mengen den Basenaustausch (nach Größe 1, 31, 171, 171, 31, 1), auf 4 Elementen 68 (1, 15, 36, 15, 1): genau die Zahl der Matroide. |
| **Fundamentalkreis und Tausch** (alle Basen B, e nicht in B, f in B) | „B − f + e ist Basis“ und „f liegt im Fundamentalkreis von e“ stimmen bei **allen** Tripeln überein: Wald 6 480, Kabelfarben 1 134, Anschluss 10 885, uniform 15 840, Vektoren 336, Fano 336. In B + e liegt **jedes Mal genau ein** Kreis (1 080, 378, 1 555, 3 960, 112, 112 Fälle). |
| **Wald: Fundamentalkreis = Weg im Baum** | In **1 080 von 1 080** Fällen (B, e) ist der Fundamentalkreis die neue Leitung plus der Weg im Baum zwischen ihren Endpunkten. |
| **Abschluss im Wald** | Der Abschluss einer zufälligen Leitungsmenge sind alle Leitungen innerhalb der Komponenten dieser Menge: **300 von 300** Mengen. |
| **Flache** | Fano: 16 Flache, nach Rang 1, 7, 7, 1 (Rang 0 bis 3); die 7 Flache vom Rang 2 sind die 7 Geraden mit je 3 Punkten. Wald: 1, 12, 50, 92, 76, 24, 1 (Rang 0 bis 6). Kabelfarben: 1, 3, 3, 1. Uniform: 1, 12, 66, 220, 1. |
| **Beschreibungen sind verschieden lang** | Beim Wald hat die Liste der Kreise **32** Mengen, die der Basen 180 und die der zulässigen Mengen 1 316 (die Kreise sind etwa 41-mal kürzer). Bei Fano: 14 Kreise (7 Geraden mit 3 Punkten und 7 Vierermengen), 28 Basen, 57 zulässige Mengen. Beim uniformen Matroid sind es dagegen die Basen (495), die kürzer sind als die Kreise (792). |
| **Kontrast** (Kreise in B + e, B maximale zulässige Menge) | Genau ein Kreis in **39,0 %** (Paarung, 164 Fälle), **20,9 %** (Wald mit Grad ≤ 2, 382), **95,0 %** (Wald und Farbregel, 360), **54,7 %** (Budget, 1 334), **64,3 %** (Standorte ohne Nachbarn, 28) der Fälle; bis zu 3 Kreise bei Wald mit Grad ≤ 2, bis zu 6 beim Budget. |

## Ehrliche Grenzen

- **Kleine Grundmengen.** Höchstens 16 Elemente; Rang, Basen, Kreise und Flache werden aus allen Teilmengen berechnet. Die Prüfung aller fünf Axiomsysteme am gewählten System geht nur bis 12 Elemente, die Aufzählung aller Systeme nur bis 5 Elemente.
- **Rechenzeit bei 9 Standorten.** Der erste Aufruf eines Systems mit 16 Leitungen braucht 2 bis 10 Sekunden (am längsten das Anschluss-System mit 34 654 zulässigen Mengen); danach liegt das Ergebnis im Zwischenspeicher.
- **Beispiele auf einem Plan.** Die Zahlen gelten für den gezeigten Plan, nicht allgemein; dass Wald, Farben, Anschluss, uniforme und lineare Systeme Matroide sind, ist bekannt und wird hier an den gezeigten Systemen gemessen.
- **Die Gleichwertigkeit der Axiomsysteme ist bekannt, hier nachgerechnet.** 0 Abweichungen auf 7 773 Systemen sind kein Beweis für größere Systeme; die Quellen (Zusammenfassungen der Matroid-Theorie, Websuche) wurden nur über Auszüge eingesehen, nicht die Originalarbeit.
- **Fano-Zahlen:** 14 Kreise und 16 Flache sind hier gemessen und in den eingesehenen Quellen nicht belegt.
- **Nur Kreise, keine Kokreise.** Das Gegenstück zum Kreis (im Graphen ein minimaler Schnitt) und das duale Matroid gehören zu Stück 6.
- **Die Zeichnung der Fano-Ebene** ist eine Skizze (6 Strecken und ein Kreis für die 7 Geraden), keine Darstellung über einem Körper.

## Verifikation

- **Kern:** Rang, Basen, Kreise, Abschluss, Flache, Fundamentalkreis gegen Handrechnung auf vier kleinen Systemen (Dreieck, parallele Kanten mit Brücke, Paarung auf Pfad, Fano-Ebene, `tests/conftest.py`); Randfälle: ein Element, eine Schleife, nur die leere Menge, das freie System, zwei parallele Elemente, ungültige Systeme (`tests/test_edge_cases.py`).
- **Orakel** (`tests/test_oracle_rang_basen_kreise.py`): Rang, Basen und Kreise direkt aus der Definition über alle Teilmengen auf 40 Zufallssystemen; Abschluss aus der Definition; Submodularität gegen die volle Definition über alle Paare (150 Systeme); Rundreisen auf Zufallssystemen; die vier anderen Axiomsysteme gegen das Austauschaxiom auf allen Systemen mit höchstens 4 Elementen; Abschluss im Wald gegen `networkx.connected_components`; Fundamentalkreis im Wald gegen `networkx.find_cycle`; die Zahl der Basenfamilien (68 und 406).
- **Eigenschaften** (`tests/test_properties.py`): Basen eines Matroids haben die Größe des Rangs; in B + e liegt genau ein Kreis (Matroide) oder nicht immer (Nicht-Matroide); Rang submodular, Abschluss idempotent und monoton; jeder Kreis ist minimal unzulässig, jede unzulässige Menge enthält einen Kreis; Flache sind abgeschlossen; Rundreisen auf allen Systemen und Plänen; Umbenennung der Elemente ändert die Zahlen nicht; gleiche Ergebnisse in zwei Prozessen mit verschiedener Hash-Reihenfolge.
- **Verdikte und Presets:** jeder Zweig und jede Zahl der Verdikte an handgesetzten Werten; jedes Preset zeigt den versprochenen Effekt.
- **Zahlen aus dieser README:** `tests/test_claims.py`.
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler an den Grenzen), Hauptansicht, Experimente, Spielwiese, Permalink, PDF; Layout (Kopf, Schnellstart, Hervorhebung) und Footer.
- **Umfang:** 110 Tests (`pytest --collect-only -q tests`), seriell etwa zwei Minuten.

## Dateistruktur

| Datei | Inhalt |
|---|---|
| `app.py` | Streamlit-Oberfläche: Fundamentalkreis und Tausch, Kernfrage, vier Experimente, Spielwiese, Grenzen, Formeln |
| `rbk_constants.py` | Reglergrenzen, Systeme und ihre Namen, Prüfgrenzen, Farben, Presets |
| `rbk_scenario.py` | Plan: Standorte, mögliche Leitungen, Kosten (wie in den Stücken 1 bis 3) |
| `rbk_algorithm.py` | Kern: Unabhängigkeitssystem auf Bitmasken, Rang, Basen, Kreise, Abschluss, Flache, Rundreisen, Axiomprüfungen, Aufzählen aller Systeme |
| `rbk_systems.py` | die elf Systeme auf dem Plan mit Kabelfarben, die Fano-Ebene |
| `rbk_evaluation.py` | Kennzahlen, Fundamentalkreis und Tausch, Kontrast, Verdikte |
| `rbk_visualization.py` | Plan, Fano-Zeichnung, Flache je Rang, Kreise in B + e |
| `rbk_presets.py` | Permalink, Presets, Zufalls-Seed |
| `rbk_layout.py` | fester Kopf |
| `rbk_pdf_export.py` | PDF des aktuellen Systems |
| `tests/` | Kern, Orakel, Eigenschaften, Verdikte, Presets, Claims, Randfälle, Oberfläche, Layout, Footer, Importe |

## Bewusst nicht umgesetzt

- Dualmatroid, Kokreise, Minoren (Stück 6); Greedy gegen Optimum auf Matroiden (Stück 5); Schnitt zweier Matroide (Stück 7).
- Flache als eigene Axiomatik und ihr Verband; Rundreise aus Flachen.
- Aufzählung aller Systeme mit 6 und mehr Elementen; Rang- und Kreisaxiome für große Matroide ohne Aufzählen.
- Erklärseite „verständlich erklärt“ und Website-Einbindung (erst mit der vollständigen Linie).

## Lokal ausführen

```bash
pip install -r requirements.txt
streamlit run app.py
```

Tests: `pip install -r requirements-dev.txt`, dann `python -m pytest tests -q`. Die CI läuft mit Python 3.12 (`.github/workflows/tests.yml`); die in Streamlit Cloud eingestellte Python-Version ist beim Deploy zu nennen. Testzahl: siehe `pytest --collect-only -q tests` (zuletzt: 110 Tests, seriell etwa zwei Minuten).

Gebaut mit Streamlit, Plotly, numpy und fpdf2.

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zur Reihe: [Matroide: vom Spannbaum zur Verfahrenswahl](https://sebastianhanisch.net/konzepte-matroide.html).
