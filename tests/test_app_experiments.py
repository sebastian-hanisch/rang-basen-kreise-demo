"""AppTest: Hauptansicht, Experimente, Spielwiese, Permalink und PDF (DEMO-PLAYBOOK §3, §5)."""

import os
from pathlib import Path

from streamlit.testing.v1 import AppTest

import rbk_constants as C
import rbk_evaluation as ev
from rbk_pdf_export import build_pdf

APP = str(Path(__file__).resolve().parent.parent / "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))


def _app(params=None) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    for key, value in (params or {}).items():
        at.query_params[key] = value
    at.run()
    assert not at.exception, [str(e) for e in at.exception]
    return at


def _texts(at):
    return [m.value for m in list(at.success) + list(at.info) + list(at.warning) + list(at.error)]


def _click_preset(at, name):
    at.sidebar.button(key=f"preset_{name}").click().run()
    assert not at.exception, [str(e) for e in at.exception]


def test_kernfrage_verdict_matches_each_preset():
    expected = {
        "Standardfall (Voreinstellung)": "**genau ein** Kreis",
        "Kabelfarben": "**genau ein** Kreis",
        "Fano-Ebene": "**genau ein** Kreis",
        "Paarung": "**2 Kreise**",
        "Wald und Farbregel": "**genau ein** Kreis",
    }
    at = _app()
    for name, needle in expected.items():
        _click_preset(at, name)
        assert any(needle in t for t in _texts(at)), name


def test_contrast_verdict_differs_between_matroids_and_non_matroids():
    at = _app()
    assert any("In allen 1 080 Fällen (B, e) (alle Basen) liegt in B + e **genau ein** Kreis" in t for t in _texts(at))
    _click_preset(at, "Paarung")
    assert any("Nur in **39,0 %** der 164 Fälle" in t for t in _texts(at))
    _click_preset(at, "Wald und Farbregel")
    assert any("Nur in **95,0 %** der 360 Fälle" in t and "Alle maximalen Mengen haben 3 Elemente" in t for t in _texts(at))


def test_description_verdict_and_axiom_button():
    at = _app()
    assert any("Die kürzeste Liste hat das System als **Kreise** (32 gegen 1 316 zulässige Mengen" in t for t in _texts(at))
    assert not any("alle fünf erfüllt" in t for t in _texts(at))
    at.button(key="axiom_run").click().run()
    assert not at.exception and any("alle fünf erfüllt: ein Matroid" in t for t in _texts(at))
    _click_preset(at, "Paarung")
    at.button(key="axiom_run").click().run()
    assert any("alle fünf verletzt: kein Matroid" in t for t in _texts(at))


def test_axiom_check_is_skipped_for_large_plans_with_a_note():
    at = _app(dict(n="9", system="wald"))
    at.button(key="axiom_run").click().run()
    assert not at.exception and any("mehr als 12 Elementen" in t for t in _texts(at))


def test_agreement_button_runs_the_enumeration():
    at = _app()
    assert not any("7 773" in t for t in _texts(at))
    at.button(key="agree_run").click().run()
    assert not at.exception and any("Bei allen 7 773 Unabhängigkeitssystemen mit höchstens 5 Elementen" in t and "(**0 Abweichungen**)" in t for t in _texts(at))


def test_experiment_results_stay_after_other_changes():
    at = _app()
    at.button(key="agree_run").click().run()
    at.sidebar.selectbox(key="system_select").set_value("paarung").run()
    assert not at.exception and any("7 773" in t for t in _texts(at))


def test_every_system_runs_without_exception_and_has_the_matching_verdict():
    at = _app()
    for system in C.SYSTEMS:
        at.sidebar.selectbox(key="system_select").set_value(system).run()
        assert not at.exception, (system, [str(e) for e in at.exception])
        texts = _texts(at)
        if system in C.MATROID_SYSTEMS:
            assert any("In allen" in t and "**genau ein** Kreis" in t for t in texts), system
        else:
            assert any(t.startswith("Nur in **") for t in texts), system


def test_fundamental_tab_changes_with_the_base_and_the_element():
    s = ev.Settings(n=7, seed=8, system="uniform")
    a = ev.analyse(s)
    play_id = "uniform_7_8"
    at = _app(dict(system="uniform"))
    at.slider(key=f"base_{play_id}").set_value(5).run()
    assert not at.exception and any("**genau ein** Kreis" in t for t in _texts(at))
    base = ev.base_list(s)[4]
    outside = ev.outside_elements(a, base)
    at.selectbox(key=f"e_{play_id}_{base}").set_value(outside[-1]).run()
    assert not at.exception and any("**genau ein** Kreis" in t for t in _texts(at))
    res = ev.fundamental(a, base, outside[-1])
    assert res["unique"] and res["agree"] and len(res["circuits"]) == 1


def test_closure_experiment_shows_rank_and_added_elements():
    at = _app()
    play_id = "wald_7_8"
    at.multiselect(key=f"closure_{play_id}").set_value([0, 1, 2]).run()
    assert not at.exception and any(t.startswith("Rang von F:") for t in _texts(at))
    at.multiselect(key=f"closure_{play_id}").set_value([]).run()
    assert any("Die leere Menge hat Rang 0" in t for t in _texts(at))


def test_playground_branches():
    at = _app(dict(system="paarung"))
    play_id = "paarung_7_8"
    at.multiselect(key=f"play_b_{play_id}").set_value([0, 1]).run()               # A–B und A–C teilen A: nicht zulässig
    assert not at.exception and any("nicht zulässig" in t for t in _texts(at))
    at.multiselect(key=f"play_b_{play_id}").set_value([0]).run()
    assert any("wählen Sie ein Element außerhalb" in t for t in _texts(at))


def test_permalink_loads_valid_values_and_ignores_invalid_choices():
    at = _app(dict(n="8", seed="3", system="paarung"))
    assert at.sidebar.slider(key="n_slider").value == 8 and at.sidebar.number_input(key="seed_input").value == 3 and at.sidebar.selectbox(key="system_select").value == "paarung"
    bad = _app(dict(n="99", seed="-4", system="gibtsnicht"))
    assert bad.sidebar.slider(key="n_slider").value == C.N_MAX and bad.sidebar.number_input(key="seed_input").value == 0 and bad.sidebar.selectbox(key="system_select").value == "wald"


def test_address_line_mirrors_the_settings():
    at = _app(dict(system="budget"))
    assert str(at.query_params["system"]) in ("budget", "['budget']")


def test_pdf_button_makes_a_download():
    at = _app()
    at.button(key="pdf_make").click().run()
    assert not at.exception and "pdf_made" in at.session_state and at.session_state["pdf_made"][1][:4] == b"%PDF"


def test_pdf_builds_for_every_system():
    for key in C.SYSTEMS:
        s = ev.Settings(n=6, seed=2, system=key)
        assert build_pdf(ev.analyse(s), s)[:4] == b"%PDF", key


def test_extreme_plan_sizes_with_slow_systems_do_not_raise():
    for n in (C.N_MIN, C.N_MAX):
        for system in ("anschluss", "uniform", "fano"):
            at = _app(dict(n=str(n), system=system))
            assert not at.exception, (n, system)
