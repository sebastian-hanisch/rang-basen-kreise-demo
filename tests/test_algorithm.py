"""Kern gegen Handrechnung (kleine Systeme aus conftest.py) und die Systeme auf dem Plan (DEMO-PLAYBOOK §1b)."""

import pytest

import rbk_constants as C
import rbk_systems as S
from rbk_algorithm import (
    System,
    all_systems,
    axiom_agreement,
    axiom_results,
    check_basis_exchange,
    check_circuit_elimination,
    check_closure_axioms,
    check_rank_submodular,
    count_basis_families,
    elements,
    independent_from_bases,
    independent_from_circuits,
    independent_from_closure,
    independent_from_rank,
    popcount,
    round_trips,
)
from rbk_scenario import make_instance


def test_triangle_by_hand(dreieck):
    s = dreieck
    assert len(s.ind) == 7 and s.bases == [3, 5, 6] and s.circuits == [7] and s.rank == 2 and s.is_matroid
    assert [s.rank_of(f) for f in range(8)] == [0, 1, 1, 2, 1, 2, 2, 2]
    assert [s.closure(f) for f in range(8)] == [0, 1, 2, 7, 4, 7, 7, 7]
    assert s.flats == [0, 1, 2, 4, 7] and s.flats_by_rank() == {0: 1, 1: 3, 2: 1}
    assert s.fundamental_circuit(3, 2) == 7 and s.swap_is_basis(3, 0, 2) and s.swap_is_basis(3, 1, 2)
    assert s.circuits_in(3) == [] and s.circuits_in(7) == [7]


def test_parallel_edges_plus_bridge_by_hand(parallel):
    s = parallel
    assert s.ind == [0, 1, 2, 4, 5, 6] and s.bases == [5, 6] and s.circuits == [3] and s.rank == 2 and s.is_matroid
    assert s.closure(1) == 3 and s.closure(0) == 0 and s.closure(5) == 7
    assert s.flats == [0, 3, 4, 7]
    assert s.fundamental_circuit(5, 1) == 3                      # B = {a, c}, e = b
    assert s.swap_is_basis(5, 0, 1) and not s.swap_is_basis(5, 2, 1)   # B − a + b = {b, c} Basis; B − c + b = {a, b} nicht


def test_pairing_on_a_path_is_not_a_matroid_and_b_plus_e_can_hold_two_circuits(paarung3):
    s = paarung3
    assert s.bases == [2, 5] and s.circuits == [3, 6] and not s.is_matroid and s.maximal_sizes() == {1: 1, 2: 1}
    assert s.circuits_in(7) == [3, 6] and s.fundamental_circuit(5, 1) is None       # B = {e0, e2}, e = e1: beide Kreise
    assert s.fundamental_circuit(2, 0) == 3 and s.fundamental_circuit(2, 2) == 6


def test_fano_plane_by_hand(fano):
    s = fano
    assert len(s.ind) == 57 and len(s.bases) == 28 and len(s.circuits) == 14 and len(s.flats) == 16 and s.rank == 3
    sizes = {}
    for c in s.circuits:
        sizes[popcount(c)] = sizes.get(popcount(c), 0) + 1
    assert sizes == {3: 7, 4: 7} and s.flats_by_rank() == {0: 1, 1: 7, 2: 7, 3: 1}
    assert s.closure(0b11) == 0b111                              # die Gerade {P1, P2, P3}
    assert all(popcount(f) == 3 for f in s.flats if s.rank_of(f) == 2)


def test_round_trips_on_the_hand_systems(dreieck, parallel, paarung3, fano):
    for s in (dreieck, parallel, paarung3, fano):
        assert all(round_trips(s).values()), s.name
    assert independent_from_bases(3, [3, 5, 6]) == [bin(m).count("1") <= 2 for m in range(8)]
    assert independent_from_circuits(3, [7]) == [bin(m).count("1") <= 2 for m in range(8)]
    assert independent_from_rank(3, [0, 1, 1, 2, 1, 2, 2, 2]) == [bin(m).count("1") <= 2 for m in range(8)]
    assert independent_from_closure(3, [0, 1, 2, 7, 4, 7, 7, 7]) == [bin(m).count("1") <= 2 for m in range(8)]


def test_axiom_checks_by_hand(dreieck, paarung3, fano):
    assert all(axiom_results(dreieck).values()) and all(axiom_results(fano).values())
    res = axiom_results(paarung3)
    assert not any(res.values()), res


def test_each_axiom_check_flags_a_single_known_failure():
    ok = [True, True, True, False, True, False, False, False]                 # nur ∅, a, b, c ... also {a}, {b}, {c} zulässig und keine Paare: U(1, 3)
    assert all(axiom_results(System("u13", 3, ok)).values())
    bad = System("bad", 3, [not (mask & 1 and mask & 2) and not (mask & 2 and mask & 4) for mask in range(8)])
    assert not check_basis_exchange(bad) and not check_circuit_elimination(bad) and not check_rank_submodular(bad) and not check_closure_axioms(bad)


def test_agreement_on_all_systems_up_to_four_elements():
    for n in (1, 2, 3, 4):
        r = axiom_agreement(n)
        assert all(v == 0 for v in r["mismatch"].values()) and r["closure_checked"]
        assert len(set(r["counts"].values())) == 1                       # alle Axiomsysteme zählen gleich viele Matroide
    assert axiom_agreement(4)["counts"]["Austausch (zulässige Mengen)"] == 68 and axiom_agreement(3)["systems"] == 19


def test_agreement_for_five_elements_and_the_basis_families():
    r = axiom_agreement(5)
    assert r["systems"] == 7580 and r["counts"]["Austausch (zulässige Mengen)"] == 406 and all(v == 0 for v in r["mismatch"].values())
    assert count_basis_families(5) == {0: 1, 1: 31, 2: 171, 3: 171, 4: 31, 5: 1} and sum(count_basis_families(5).values()) == 406
    assert len(all_systems(3)) == 19


def test_closure_check_can_be_skipped_for_large_n():
    r = axiom_agreement(3, closure_max_n=2)
    assert not r["closure_checked"] and r["counts"]["Abschlussoperator"] == 0 and r["mismatch"]["Abschlussoperator"] == 0


def test_standard_plan_numbers():
    expected = {  # unabhängig, Basen, Kreise, Flache, Rang
        "wald": (1316, 180, 32, 256, 6), "farben": (96, 42, 25, 8, 3), "anschluss": (2634, 311, 93, 1420, 7), "uniform": (794, 495, 792, 300, 4),
        "vektoren": (56, 28, 20, 19, 3), "fano": (57, 28, 14, 16, 3), "paarung": (60, 18, 35, 39, 3), "wald2": (690, 58, 59, 286, 6), "budget": (1093, 196, 234, 405, 6),
        "standorte": (19, 6, 12, 9, 3), "wald_farben": (94, 40, 27, 10, 3),
    }
    for key, (ind, bases, circuits, flats, rank) in expected.items():
        s = S.get_system(key, 7, 8)
        assert (len(s.ind), len(s.bases), len(s.circuits), len(s.flats), s.rank) == (ind, bases, circuits, flats, rank), key
        assert s.is_matroid == (key in C.MATROID_SYSTEMS), key


def test_wald_flats_by_rank_and_other_distributions_on_the_standard_plan():
    assert S.get_system("wald", 7, 8).flats_by_rank() == {0: 1, 1: 12, 2: 50, 3: 92, 4: 76, 5: 24, 6: 1}
    assert S.get_system("farben", 7, 8).flats_by_rank() == {0: 1, 1: 3, 2: 3, 3: 1}
    assert S.get_system("uniform", 7, 8).flats_by_rank() == {0: 1, 1: 12, 2: 66, 3: 220, 4: 1}


def test_systems_are_down_closed_and_the_rank_is_monotone_and_bounded():
    for key in C.SYSTEMS:
        s = S.get_system(key, 6, 3)
        assert s.check_down_closed()
        for f in range(1 << s.m):
            assert 0 <= s.rank_of(f) <= popcount(f)
            for e in range(s.m):
                assert s.rank_of(f) <= s.rank_of(f | 1 << e) <= s.rank_of(f) + 1


def test_elements_helper_and_popcount():
    assert elements(0b1010, 4) == [1, 3] and popcount(0b1010) == 2
    assert make_instance(7, 8).m == 12
