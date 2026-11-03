"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, und jedes Preset zeigt den Effekt, den sein Hilfetext verspricht."""

import rbk_constants as C
import rbk_evaluation as ev
import rbk_presets as P


def _analysis(name):
    return ev.analyse(ev.Settings(**C.PRESETS[name]))


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_bounds_and_choices():
    for preset in C.PRESETS.values():
        assert C.N_MIN <= preset["n"] <= C.N_MAX and 0 <= preset["seed"] <= C.SEED_MAX and preset["system"] in C.SYSTEMS


def test_default_preset_equals_the_default_settings():
    assert ev.Settings(**C.PRESETS["Standardfall (Voreinstellung)"]) == ev.Settings()


def test_setting_specs_cover_every_preset_key_and_have_valid_defaults():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)
    for spec in P.SETTING_SPECS.values():
        assert spec.choices is None or (spec.default in spec.choices and spec.lo in spec.choices and spec.hi in spec.choices)
    assert P.SETTING_SPECS["system_select"].hi not in {p["system"] for p in C.PRESETS.values()}      # sonst fällt die Hervorhebung mit einem Preset zusammen


def test_matroid_presets_have_one_circuit_everywhere_and_the_help_numbers_hold():
    for name in ("Standardfall (Voreinstellung)", "Kabelfarben", "Fano-Ebene"):
        a = _analysis(name)
        stats = ev.contrast_stats(ev.Settings(**C.PRESETS[name]))
        assert a.is_matroid and set(stats["dist"]) == {1}, name
    fano = _analysis("Fano-Ebene")
    assert (fano.n_circuits, fano.n_flats) == (14, 16)


def test_non_matroid_presets_have_bases_with_several_circuits():
    for name in ("Paarung", "Wald und Farbregel"):
        a = _analysis(name)
        stats = ev.contrast_stats(ev.Settings(**C.PRESETS[name]))
        assert not a.is_matroid and set(stats["dist"]) - {1}, name
