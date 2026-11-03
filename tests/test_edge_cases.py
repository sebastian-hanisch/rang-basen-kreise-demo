"""Randfälle, an denen Kernroutinen erfahrungsgemäß brechen (DEMO-PLAYBOOK §12): ein Element, leere Familien, Schleifen, parallele Elemente, ungültige Systeme."""

import pytest

import rbk_constants as C
import rbk_evaluation as ev
import rbk_systems as S
from rbk_algorithm import System, round_trips


def test_a_single_free_element():
    s = System("ein Element", 1, [True, True])
    assert s.bases == [1] and s.circuits == [] and s.rank == 1 and s.flats == [0, 1] and s.closure(0) == 0 and s.fundamental_circuit(1, 0) is None
    assert all(round_trips(s).values()) and s.is_matroid


def test_a_loop_is_a_circuit_of_size_one_and_lies_in_every_closure():
    s = System("Schleife", 2, [True, True, False, False])           # Element 1 ist eine Schleife
    assert s.circuits == [2] and s.bases == [1] and s.rank == 1 and s.closure(0) == 2 and s.closure(1) == 3
    assert s.flats == [2, 3] and s.flats_by_rank() == {0: 1, 1: 1}
    assert s.fundamental_circuit(1, 1) == 2 and s.swap_is_basis(1, 0, 1) is False


def test_the_system_with_only_the_empty_set_has_one_basis_the_empty_set():
    s = System("leer", 3, [True] + [False] * 7)
    assert s.bases == [0] and s.rank == 0 and s.circuits == [1, 2, 4] and s.flats == [7] and s.is_matroid
    assert s.closure(0) == 7                                           # alle Elemente sind Schleifen


def test_free_system_has_no_circuits_and_one_basis():
    s = System("frei", 3, [True] * 8)
    assert s.circuits == [] and s.bases == [7] and s.rank == 3 and s.flats == list(range(8)) and s.fundamental_circuit(7, 0) is None


def test_two_parallel_elements_form_a_circuit_of_size_two():
    s = System("parallel", 2, [True, True, True, False])
    assert s.circuits == [3] and s.bases == [1, 2] and s.flats == [0, 3] and s.closure(1) == 3


def test_invalid_systems_are_rejected():
    for m in (0, 17):
        with pytest.raises(ValueError):
            System("x", m, [True] * (1 << min(m, 3)))
    with pytest.raises(ValueError):
        System("x", 2, [False, True, True, True])
    with pytest.raises(ValueError):
        System("x", 2, [True, True])


def test_every_system_runs_on_the_smallest_and_the_largest_plan():
    for n in (C.N_MIN, C.N_MAX):
        for key in ("wald", "farben", "paarung", "standorte", "vektoren"):
            a = ev.analyse(ev.Settings(n=n, seed=3, system=key))
            assert a.n_bases >= 1 and a.n_flats >= 2 and a.rank >= 1 and all(dict(a.trips).values()), (n, key)
            assert a.is_matroid == (key in C.MATROID_SYSTEMS), (n, key)


def test_fano_does_not_depend_on_the_plan():
    a, b = ev.analyse(ev.Settings(6, 1, "fano")), ev.analyse(ev.Settings(9, 77, "fano"))
    assert (a.n_independent, a.n_bases, a.n_circuits, a.n_flats, a.rank) == (b.n_independent, b.n_bases, b.n_circuits, b.n_flats, b.rank) == (57, 28, 14, 16, 3)


def test_fundamental_helpers_for_a_base_that_contains_every_element():
    a = ev.analyse(ev.Settings(n=6, seed=1, system="uniform"))                         # höchstens 4 von 10: keine Basis enthält alles
    assert all(ev.outside_elements(a, b) for b in ev.base_list(ev.Settings(n=6, seed=1, system="uniform")))
    free = ev.Analysis(**{**a.__dict__, "m": 3, "labels": ("a", "b", "c")})
    assert ev.outside_elements(free, 0b111) == []


def test_play_check_with_dependent_sets_and_without_an_element():
    s = ev.Settings(n=7, seed=8, system="paarung")
    r = ev.play_check(s, 0b11, None)
    assert not r["independent"] and r["circuits"] == []
    r = ev.play_check(s, 0b1, None)
    assert r["independent"] and r["circuits"] == [] and r["rank"] == 1
    r = ev.play_check(s, 0b1, 1)                                                      # A–B plus A–C: Kreis {A–B, A–C}
    assert r["circuits"] == [0b11]


def test_contrast_with_a_limit_samples_evenly():
    st = ev.contrast_stats(ev.Settings(n=7, seed=8, system="wald"), limit=10)
    assert st["sampled"] == 10 and st["bases"] == 180 and set(st["dist"]) == {1} and st["share_one"] == 1.0


def test_unknown_system_in_build_is_rejected():
    with pytest.raises(ValueError):
        S.build_system("unbekannt", S.make_instance(6, 1))
