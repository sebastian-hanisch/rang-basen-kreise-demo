"""Orakel-Tests (DEMO-PLAYBOOK §12, ORACLE-PLAYBOOK): Kernroutinen gegen einen anderen Rechenweg.

Orakel: (1) Rang, Basen und Kreise direkt aus der Definition über alle Teilmengen (ohne die Teilmengen-Rekursion des Moduls); (2) Submodularität gegen die volle
Definition über alle Paare von Mengen; (3) Abschluss im Wald gegen `networkx.connected_components`; (4) Fundamentalkreis im Wald gegen `networkx.find_cycle`;
(5) Rundreisen auf zufälligen Systemen; (6) die vier anderen Axiomsysteme gegen das Austauschaxiom auf allen Systemen mit höchstens 4 Elementen; (7) die Zahl der
Basenfamilien gegen die bekannte Matroidzahl 406. Alles unter 10 s."""

import random

import pytest

import rbk_systems as S
from rbk_algorithm import (
    System,
    all_systems,
    check_circuit_elimination,
    check_closure_axioms,
    check_basis_exchange,
    check_rank_submodular,
    count_basis_families,
    elements,
    popcount,
    round_trips,
)
from rbk_scenario import make_instance


def _random_system(rng, m):
    tops = [rng.getrandbits(m) for _ in range(rng.randint(1, 5))]
    ok = [any(mask & ~t == 0 for t in tops) for mask in range(1 << m)]
    ok[0] = True
    return System("zufällig", m, ok)


def _naive_rank(s, f):
    return max(popcount(i) for i in range(1 << s.m) if i & ~f == 0 and s.ok[i])


def _naive_bases(s):
    return [i for i in range(1 << s.m) if s.ok[i] and not any(s.ok[j] for j in range(1 << s.m) if i & ~j == 0 and j != i)]


def _naive_circuits(s):
    return [c for c in range(1, 1 << s.m) if not s.ok[c] and not any(not s.ok[d] for d in range(1, 1 << s.m) if d != c and d & ~c == 0)]


def test_rank_bases_and_circuits_match_the_definitions_on_random_systems():
    rng = random.Random(31)
    for _ in range(40):
        s = _random_system(rng, rng.randint(2, 6))
        assert [s.rank_of(f) for f in range(1 << s.m)] == [_naive_rank(s, f) for f in range(1 << s.m)]
        assert sorted(s.bases) == sorted(_naive_bases(s))
        assert sorted(s.circuits) == sorted(_naive_circuits(s))


def test_closure_matches_the_definition_and_flats_are_the_closed_sets():
    rng = random.Random(32)
    for _ in range(30):
        s = _random_system(rng, rng.randint(2, 6))
        for f in range(1 << s.m):
            expected = f | sum(1 << e for e in range(s.m) if _naive_rank(s, f | 1 << e) == _naive_rank(s, f))
            assert s.closure(f) == expected
        assert s.flats == [f for f in range(1 << s.m) if s.closure(f) == f]


def test_rank_submodularity_check_matches_the_full_definition():
    rng = random.Random(33)
    both = {True: 0, False: 0}
    for _ in range(150):
        s = _random_system(rng, rng.randint(2, 6))
        full = all(s.rank_of(a | b) + s.rank_of(a & b) <= s.rank_of(a) + s.rank_of(b) for a in range(1 << s.m) for b in range(1 << s.m))
        assert check_rank_submodular(s) == full
        both[full] += 1
    assert both[True] > 5 and both[False] > 5


def test_round_trips_on_random_systems():
    rng = random.Random(34)
    for _ in range(40):
        s = _random_system(rng, rng.randint(2, 7))
        assert all(round_trips(s).values())


def test_axiom_systems_agree_with_the_exchange_axiom_on_all_systems_up_to_four_elements():
    for n in (1, 2, 3, 4):
        for ok in all_systems(n):
            s = System("x", n, list(ok))
            reference = s.exchange_scan()[1] == 0
            assert check_basis_exchange(s) == reference
            assert check_circuit_elimination(s) == reference
            assert check_rank_submodular(s) == reference
            assert check_closure_axioms(s) == reference


def test_wald_closure_is_the_union_of_connected_components():
    nx = pytest.importorskip("networkx")
    inst = make_instance(7, 8)
    s = S.get_system("wald", 7, 8)
    rng = random.Random(35)
    for _ in range(200):
        f = rng.getrandbits(s.m)
        g = nx.Graph()
        g.add_nodes_from(range(inst.n))
        g.add_edges_from((inst.edges[e][0], inst.edges[e][1]) for e in elements(f, s.m))
        comp = {v: i for i, c in enumerate(nx.connected_components(g)) for v in c}
        expected = sum(1 << e for e in range(s.m) if comp[inst.edges[e][0]] == comp[inst.edges[e][1]])
        assert s.closure(f) == expected


def test_wald_fundamental_circuit_matches_networkx_find_cycle():
    nx = pytest.importorskip("networkx")
    inst = make_instance(6, 3)
    s = S.get_system("wald", 6, 3)
    index = {(min(u, v), max(u, v)): e for e, (u, v, _) in enumerate(inst.edges)}
    for b in s.bases[::7]:
        for e in range(s.m):
            if b >> e & 1:
                continue
            g = nx.Graph()
            g.add_edges_from((inst.edges[x][0], inst.edges[x][1]) for x in elements(b | 1 << e, s.m))
            cycle = nx.find_cycle(g)
            expected = sum(1 << index[(min(u, v), max(u, v))] for u, v in cycle)
            assert s.fundamental_circuit(b, e) == expected


def test_fundamental_circuit_describes_the_swaps_for_every_matroid_example():
    for key in ("wald", "farben", "anschluss", "uniform", "vektoren", "fano"):
        s = S.get_system(key, 6, 3)
        for b in s.bases[::5]:
            for e in range(s.m):
                if b >> e & 1:
                    continue
                c = s.fundamental_circuit(b, e)
                assert c is not None and c >> e & 1 and c & ~(b | 1 << e) == 0
                for f in elements(b, s.m):
                    assert s.swap_is_basis(b, f, e) == bool(c >> f & 1), (key, b, e, f)


def test_number_of_basis_families_with_basis_exchange_is_the_number_of_matroids():
    by_size = count_basis_families(4)
    assert sum(by_size.values()) == 68 and by_size == {0: 1, 1: 15, 2: 36, 3: 15, 4: 1}
    assert sum(count_basis_families(5).values()) == 406
