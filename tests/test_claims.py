"""Jede Zahl der README („Befunde“) wird hier mit den Funktionen der App nachgerechnet (DEMO-PLAYBOOK §4)."""

import random
import re
from pathlib import Path

import pytest

import rbk_constants as C
import rbk_evaluation as ev
import rbk_systems as S
from rbk_algorithm import axiom_agreement, count_basis_families, elements
from rbk_scenario import make_instance

README = (Path(__file__).resolve().parent.parent / "README.md").read_text(encoding="utf-8")
PLAN = (7, 8)


def test_the_eleven_system_table():
    expected = {  # zulässige Mengen, Basen, Kreise, Flache, Rang, Matroid
        "wald": (1316, 180, 32, 256, 6, True), "farben": (96, 42, 25, 8, 3, True), "anschluss": (2634, 311, 93, 1420, 7, True), "uniform": (794, 495, 792, 300, 4, True),
        "vektoren": (56, 28, 20, 19, 3, True), "fano": (57, 28, 14, 16, 3, True), "paarung": (60, 18, 35, 39, 3, False), "wald2": (690, 58, 59, 286, 6, False),
        "budget": (1093, 196, 234, 405, 6, False), "standorte": (19, 6, 12, 9, 3, False), "wald_farben": (94, 40, 27, 10, 3, False),
    }
    assert set(expected) == set(C.SYSTEMS)
    for key, (ind, bases, circuits, flats, rank, matroid) in expected.items():
        a = ev.analyse(ev.Settings(*PLAN, key))
        assert (a.n_independent, a.n_bases, a.n_circuits, a.n_flats, a.rank, a.is_matroid) == (ind, bases, circuits, flats, rank, matroid), key
        line = [l for l in README.splitlines() if l.startswith("| " + C.SYSTEM_NAMES[key] + " |")]
        assert line and f"| {ev.zahl(ind)} | {bases} | {circuits} | {ev.zahl(flats)} | {rank} | {'ja' if matroid else 'nein'} |" in line[0], key


def test_base_sizes_of_the_non_matroids():
    assert ev.analyse(ev.Settings(*PLAN, "paarung")).base_sizes == ((2, 2), (3, 16))
    assert ev.analyse(ev.Settings(*PLAN, "wald2")).base_sizes == ((5, 34), (6, 24))
    assert len(ev.analyse(ev.Settings(*PLAN, "wald_farben")).base_sizes) == 1


def test_five_axiom_systems_agree_on_all_systems_up_to_five_elements():
    rows = [axiom_agreement(n, C.CLOSURE_MAX_N) for n in range(1, 6)]
    assert [r["systems"] for r in rows] == [2, 5, 19, 167, 7580] and sum(r["systems"] for r in rows) == 7773
    assert [r["counts"]["Austausch (zulässige Mengen)"] for r in rows] == [2, 5, 16, 68, 406]
    assert all(v == 0 for r in rows for v in r["mismatch"].values()) and all(r["closure_checked"] for r in rows)


def test_basis_families():
    assert count_basis_families(5) == {0: 1, 1: 31, 2: 171, 3: 171, 4: 31, 5: 1} and sum(count_basis_families(5).values()) == 406
    assert count_basis_families(4) == {0: 1, 1: 15, 2: 36, 3: 15, 4: 1} and sum(count_basis_families(4).values()) == 68


def test_fundamental_circuit_agrees_with_the_swap_for_every_triple():
    expected = {"wald": (6480, 1080), "farben": (1134, 378), "anschluss": (10885, 1555), "uniform": (15840, 3960), "vektoren": (336, 112), "fano": (336, 112)}
    for key, (triples, cases) in expected.items():
        s = S.get_system(key, *PLAN)
        n_triples = n_cases = agree = 0
        for b in s.bases:
            for e in range(s.m):
                if b >> e & 1:
                    continue
                n_cases += 1
                c = s.fundamental_circuit(b, e)
                assert c is not None
                for f in elements(b, s.m):
                    n_triples += 1
                    agree += s.swap_is_basis(b, f, e) == bool(c >> f & 1)
        assert (n_triples, n_cases, agree) == (triples, cases, triples), key


def test_wald_fundamental_circuit_is_the_cycle_through_the_new_edge_with_the_tree_path():
    nx = pytest.importorskip("networkx")
    inst = make_instance(*PLAN)
    s = S.get_system("wald", *PLAN)
    index = {(min(u, v), max(u, v)): e for e, (u, v, _) in enumerate(inst.edges)}
    same = total = 0
    for b in s.bases:
        for e in range(s.m):
            if b >> e & 1:
                continue
            g = nx.Graph()
            g.add_edges_from((inst.edges[x][0], inst.edges[x][1]) for x in elements(b | 1 << e, s.m))
            expected = sum(1 << index[(min(u, v), max(u, v))] for u, v in nx.find_cycle(g))
            total += 1
            same += s.fundamental_circuit(b, e) == expected
    assert (same, total) == (1080, 1080)


def test_wald_closure_is_the_components_for_300_random_sets():
    nx = pytest.importorskip("networkx")
    inst = make_instance(*PLAN)
    s = S.get_system("wald", *PLAN)
    rng = random.Random(20261106)
    good = 0
    for _ in range(300):
        f = rng.getrandbits(s.m)
        g = nx.Graph()
        g.add_nodes_from(range(inst.n))
        g.add_edges_from((inst.edges[e][0], inst.edges[e][1]) for e in elements(f, s.m))
        comp = {v: i for i, c in enumerate(nx.connected_components(g)) for v in c}
        good += s.closure(f) == sum(1 << e for e in range(s.m) if comp[inst.edges[e][0]] == comp[inst.edges[e][1]])
    assert good == 300


def test_flats_by_rank():
    expected = {"fano": {0: 1, 1: 7, 2: 7, 3: 1}, "wald": {0: 1, 1: 12, 2: 50, 3: 92, 4: 76, 5: 24, 6: 1}, "farben": {0: 1, 1: 3, 2: 3, 3: 1}, "uniform": {0: 1, 1: 12, 2: 66, 3: 220, 4: 1}}
    for key, by_rank in expected.items():
        assert dict(ev.analyse(ev.Settings(*PLAN, key)).flats_by_rank) == by_rank, key
    fano = S.get_system("fano", *PLAN)
    assert all(bin(f).count("1") == 3 for f in fano.flats if fano.rank_of(f) == 2)
    sizes = {}
    for c in fano.circuits:
        sizes[bin(c).count("1")] = sizes.get(bin(c).count("1"), 0) + 1
    assert sizes == {3: 7, 4: 7}


def test_description_lengths():
    wald = ev.analyse(ev.Settings(*PLAN, "wald"))
    assert (wald.n_circuits, wald.n_bases, wald.n_independent) == (32, 180, 1316) and round(wald.n_independent / wald.n_circuits) == 41
    uniform = ev.analyse(ev.Settings(*PLAN, "uniform"))
    assert uniform.n_bases == 495 < uniform.n_circuits == 792


def test_contrast_distribution_and_shares():
    expected = {"paarung": ({1: 64, 2: 100}, "39,0"), "wald2": ({1: 80, 2: 168, 3: 134}, "20,9"), "wald_farben": ({1: 342, 2: 18}, "95,0"),
                "budget": ({1: 730, 2: 285, 3: 197, 4: 114, 5: 6, 6: 2}, "54,7"), "standorte": ({1: 18, 2: 8, 3: 2}, "64,3")}
    for key, (dist, share) in expected.items():
        st = ev.contrast_stats(ev.Settings(*PLAN, key))
        assert st["dist"] == dist and st["sampled"] == st["bases"] and ev.prozent(st["share_one"]) == share, key
    assert [ev.contrast_stats(ev.Settings(*PLAN, k))["total"] for k in expected] == [164, 382, 360, 1334, 28]
    wald = ev.contrast_stats(ev.Settings(*PLAN, "wald"))
    assert wald["dist"] == {1: 1080} and wald["total"] == 1080


def test_readme_names_every_checked_number():
    for needle in ("**406**", "7 773", "**0** Abweichungen", "(1, 15, 36, 15, 1)", "nach Größe 1, 31, 171, 171, 31, 1", "6 480", "10 885", "15 840", "1 080, 378, 1 555, 3 960, 112, 112",
                   "**1 080 von 1 080**", "**300 von 300**", "1, 12, 50, 92, 76, 24, 1", "1, 3, 3, 1", "1, 12, 66, 220, 1", "**32** Mengen", "etwa 41-mal kürzer", "14 Kreise (7 Geraden mit 3 Punkten und 7 Vierermengen)",
                   "**39,0 %**", "**20,9 %**", "**95,0 %**", "**54,7 %**", "**64,3 %**", "2 mit 2 und 16 mit 3", "34 mit 5 und 24 mit 6"):
        assert needle in README, needle


def test_readme_table_has_no_decimal_points():
    table = README.split("## Befunde (gemessen, keine Behauptungen)")[1].split("## Ehrliche Grenzen")[0]
    assert not re.search(r"\d\.\d", table)
