"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jeder Zweig der Art steht hier."""

from dataclasses import replace

import rbk_constants as C
import rbk_evaluation as ev
from rbk_scenario import make_instance


def _a(**kw):
    base = dict(
        settings=ev.Settings(), inst=make_instance(6, 1), kind="kanten", m=3, labels=("a", "b", "c"), colors=(), n_independent=7, n_bases=3, n_circuits=1, n_flats=5, rank=2,
        girth=3, q=1.0, is_matroid=True, trips=(("Basen", True), ("Kreise", True), ("Rang", True), ("Abschluss", True)), flats_by_rank=((0, 1), (1, 3), (2, 1)),
        base_sizes=((2, 3),), circuit_sizes=((3, 1),),
    )
    base.update(kw)
    return ev.Analysis(**base)


def _res(circuits, rows, **kw):
    r = {"base": 0b011, "e": 2, "circuits": circuits, "unique": len(circuits) == 1, "rows": rows, "agree": all(x["swap"] == x["in_circuit"] for x in rows)}
    r.update(kw)
    return r


ROWS = [{"f": 0, "Element": "a", "swap": True, "in_circuit": True}, {"f": 1, "Element": "b", "swap": True, "in_circuit": True}]


def test_formatting_helpers():
    assert ev.de(0.6, 3) == "0,600" and ev.prozent(0.054) == "5,4" and ev.zahl(646367) == "646 367" and ev.zahl(7) == "7"
    assert ev.elemente(1) == "1 Element" and ev.elemente(0) == "0 Elemente" and ev.elemente(3) == "3 Elemente"


def test_fundamental_verdict_unique_circuit_for_a_matroid():
    kind, text = ev.verdict_fundamental(_a(), _res([0b111], ROWS))
    assert kind == "success" and "**genau ein** Kreis: {a, b, c} (3 Elemente)" in text and "Von den 2 Tauschen B − f + e sind 2 wieder eine Basis" in text
    assert "Nicht-Matroid" not in text


def test_fundamental_verdict_unique_circuit_in_a_non_matroid_names_the_exception():
    kind, text = ev.verdict_fundamental(_a(is_matroid=False), _res([0b111], ROWS))
    assert kind == "success" and "In diesem Nicht-Matroid ist das bei dieser Wahl von B und e so, aber nicht bei allen (Experiment 4)." in text


def test_fundamental_verdict_several_circuits_and_no_circuit():
    kind, text = ev.verdict_fundamental(_a(is_matroid=False), _res([0b011, 0b110], ROWS, unique=False))
    assert kind == "warning" and "**2 Kreise**" in text and "Fundamentalkreis ist hier nicht definiert" in text and "2 Tauschen" in text
    kind, text = ev.verdict_fundamental(_a(), _res([], ROWS, unique=False))
    assert kind == "info" and "kein Kreis" in text


def test_fundamental_table_and_result_on_a_real_plan():
    a = ev.analyse(ev.Settings(n=7, seed=8, system="wald"))
    base = ev.base_list(a.settings)[0]
    e = ev.outside_elements(a, base)[0]
    res = ev.fundamental(a, base, e)
    assert res["unique"] and res["agree"] and len(res["rows"]) == 6
    table = ev.fundamental_table(res)
    assert [r["B − f + e ist Basis"] for r in table] == [("ja" if r["swap"] else "nein") for r in res["rows"]] and table[0]["Element f"] == res["rows"][0]["Element"]


def test_description_rows_and_verdict():
    a = _a()
    rows = ev.description_rows(a)
    assert [r["Beschreibung"].split(" (")[0] for r in rows] == ["zulässige", "Basen", "Kreise", "Rangfunktion", "Abschluss und Flache"]
    assert rows[0]["Zahl"] == "7" and rows[1]["Zahl"] == "3" and rows[2]["Zahl"] == "1" and rows[3]["Zahl"] == "8 Werte" and rows[4]["Zahl"] == "5 Flache"
    assert all(r["Rundreise"] == "gelungen" for r in rows[1:])
    kind, text = ev.verdict_descriptions(a)
    assert kind == "info" and "**Kreise** (1 gegen 7 zulässige Mengen, etwa 7,0-mal kürzer)" in text
    bad = _a(trips=(("Basen", True), ("Kreise", False), ("Rang", True), ("Abschluss", True)))
    assert ev.description_rows(bad)[2]["Rundreise"] == "misslungen" and ev.verdict_descriptions(bad)[0] == "error"


def test_axiom_rows_and_verdict_branches():
    rows = [{"Axiomsystem": "x", "erfüllt": "ja", "wie das Austauschaxiom": "ja"}] * 5
    kind, text = ev.verdict_axioms(rows, True)
    assert kind == "success" and "alle fünf erfüllt: ein Matroid" in text
    rows2 = [{"Axiomsystem": "x", "erfüllt": "nein", "wie das Austauschaxiom": "ja"}] * 5
    assert "alle fünf verletzt: kein Matroid" in ev.verdict_axioms(rows2, False)[1]
    assert ev.verdict_axioms([dict(rows[0], **{"wie das Austauschaxiom": "nein"})], True)[0] == "error"
    kind, text = ev.verdict_axioms(None, True)
    assert kind == "info" and "mehr als 12 Elementen" in text
    assert ev.axiom_rows(ev.Settings(n=9, seed=8, system="wald"), True) is None


def test_axiom_rows_on_a_small_system():
    rows = ev.axiom_rows(ev.Settings(n=7, seed=8, system="fano"), True)
    assert [r["Axiomsystem"] for r in rows][0] == "Austausch (zulässige Mengen)" and len(rows) == 5 and all(r["erfüllt"] == "ja" and r["wie das Austauschaxiom"] == "ja" for r in rows)
    rows = ev.axiom_rows(ev.Settings(n=7, seed=8, system="paarung"), False)
    assert all(r["erfüllt"] == "nein" and r["wie das Austauschaxiom"] == "ja" for r in rows)


def test_closure_verdict_branches():
    a = _a()
    assert "Die leere Menge hat Rang 0" in ev.verdict_closure(a, {"f": 0, "rank": 0, "closure": 0, "flat": True, "added": 0})[1]
    kind, text = ev.verdict_closure(a, {"f": 0b011, "rank": 2, "closure": 0b111, "flat": False, "added": 0b100})
    assert kind == "info" and "Rang von F: 2 (F hat 2 Elemente)" in text and "Zum Abschluss kommen {c} dazu" in text and "Flach" not in text
    text = ev.verdict_closure(a, {"f": 0b001, "rank": 1, "closure": 0b001, "flat": True, "added": 0})[1]
    assert "Zum Abschluss kommen keine dazu" in text and "F ist ein **Flach**." in text and "F hat 1 Element" in text


def test_flats_verdict_lists_counts_by_rank():
    kind, text = ev.verdict_flats(_a())
    assert kind == "info" and "5 Flache: 1 vom Rang 0, 3 vom Rang 1, 1 vom Rang 2." in text


def test_agreement_verdict_branches():
    rows = [
        {"n": 4, "systems": 167, "counts": {"Austausch (zulässige Mengen)": 68}, "mismatch": {"Basenaustausch": 0}},
        {"n": 5, "systems": 7580, "counts": {"Austausch (zulässige Mengen)": 406}, "mismatch": {"Basenaustausch": 0}},
    ]
    fam = {0: 1, 1: 31, 2: 171, 3: 171, 4: 31, 5: 1}
    kind, text = ev.verdict_agreement(rows, fam)
    assert kind == "success" and "Bei allen 7 747 Unabhängigkeitssystemen mit höchstens 5 Elementen" in text and "(**0 Abweichungen**)" in text
    assert "406 von 7 580 Systemen Matroide" in text and "406 Familien gleich großer Mengen auf 5 Elementen" in text
    rows[0]["mismatch"] = {"Basenaustausch": 3}
    assert ev.verdict_agreement(rows, fam)[0] == "error" and "Bei 3 Prüfungen" in ev.verdict_agreement(rows, fam)[1]


def test_contrast_verdict_branches():
    base = {"dist": {1: 1080}, "total": 1080, "sampled": 180, "bases": 180, "share_one": 1.0, "sizes": {6: 180}}
    kind, text = ev.verdict_contrast(_a(), base)
    assert kind == "success" and "In allen 1 080 Fällen (B, e) (alle Basen) liegt in B + e **genau ein** Kreis, und alle Basen haben 2 Elemente" in text
    non = {"dist": {1: 64, 2: 100}, "total": 164, "sampled": 18, "bases": 18, "share_one": 64 / 164, "sizes": {2: 2, 3: 16}}
    kind, text = ev.verdict_contrast(_a(is_matroid=False), non)
    assert kind == "warning" and "Nur in **39,0 %** der 164 Fälle (alle maximale Mengen)" in text and "bis zu 2 Kreise" in text and "verschiedene Größen (2 mit 2, 16 mit 3)" in text
    single = dict(non, sizes={3: 40})
    assert "Alle maximalen Mengen haben 3 Elemente, und doch liegen manchmal mehrere Kreise" in ev.verdict_contrast(_a(is_matroid=False), single)[1]
    part = dict(non, sampled=10, bases=180)
    assert "(10 von 180 maximale Mengen)" in ev.verdict_contrast(_a(is_matroid=False), part)[1]
    assert ev.verdict_contrast(_a(), {"dist": {}, "total": 0, "sampled": 0, "bases": 1, "share_one": 1.0, "sizes": {}})[0] == "info"


def test_play_verdict_branches():
    a = _a()
    base = {"mask": 0b001, "e": 1, "independent": True, "maximal": True, "circuits": [0b011], "rank": 1}
    assert ev.verdict_play(a, dict(base, independent=False))[1].startswith("Die gewählte Menge ist nicht zulässig")
    assert "Rang 1" in ev.verdict_play(a, dict(base, e=None))[1]
    kind, text = ev.verdict_play(a, base)
    assert kind == "success" and "eine Basis (maximal)" in text and "In B + b liegt genau ein Kreis: {a, b}" in text
    kind, text = ev.verdict_play(a, dict(base, maximal=False, circuits=[0b011, 0b110]))
    assert kind == "warning" and "zulässig, aber nicht maximal" in text and "liegen 2 Kreise: {a, b}; {b, c}" in text
    kind, text = ev.verdict_play(a, dict(base, circuits=[]))
    assert kind == "info" and "kein Kreis in B + e" in text


def test_constants_used_in_texts():
    assert C.AXIOM_MAX_ELEMENTS == 12 and C.ENUM_MAX_N == 5 and C.CLOSURE_MAX_N == 5 and C.BASIS_FAMILY_N == 5
    assert len(C.SYSTEMS) == 11 and len(C.MATROID_SYSTEMS) == 6 and set(C.SYSTEM_NAMES) == set(C.SYSTEMS)
    assert replace(_a(), n_bases=4).n_bases == 4
