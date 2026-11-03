"""Eigenschaftstests (ORACLE-PLAYBOOK §5): Aussagen, die für jedes System gelten müssen, auf festen Zufallsinstanzen."""

import os
import random
import subprocess
import sys
from pathlib import Path

import rbk_constants as C
import rbk_evaluation as ev
import rbk_systems as S
from rbk_algorithm import all_systems, popcount, round_trips, System

ROOT = Path(__file__).resolve().parent.parent
PLANS = ((6, 1), (6, 5), (7, 8))


def _systems():
    for key in C.SYSTEMS:
        for n, seed in PLANS:
            yield key, n, seed, S.get_system(key, n, seed)


def test_matroids_have_equal_size_bases_equal_to_the_rank_and_the_others_do_not_always():
    for key, n, seed, s in _systems():
        if key in C.MATROID_SYSTEMS:
            assert list(s.maximal_sizes()) == [s.rank], (key, n, seed)
    assert any(len(S.get_system(key, 7, 8).maximal_sizes()) > 1 for key in ("paarung", "wald2", "budget", "standorte"))


def test_exactly_one_circuit_in_b_plus_e_for_every_matroid_and_not_for_every_non_matroid():
    for key, n, seed, s in _systems():
        counts = set()
        for b in s.bases[::3]:
            for e in range(s.m):
                if not b >> e & 1:
                    counts.add(len(s.circuits_in(b | 1 << e)))
        if key in C.MATROID_SYSTEMS:
            assert counts <= {1}, (key, n, seed, counts)
        else:
            assert counts - {1} or (n, seed) != (7, 8), (key, n, seed, counts)


def test_rank_is_submodular_and_closure_is_idempotent_and_monotone_on_the_matroid_examples():
    rng = random.Random(41)
    for key, n, seed, s in _systems():
        if key not in C.MATROID_SYSTEMS:
            continue
        for _ in range(100):
            a, b = rng.getrandbits(s.m), rng.getrandbits(s.m)
            assert s.rank_of(a | b) + s.rank_of(a & b) <= s.rank_of(a) + s.rank_of(b)
            assert s.closure(s.closure(a)) == s.closure(a)
            if a & ~b == 0:
                assert s.closure(a) & ~s.closure(b) == 0


def test_every_circuit_is_minimal_dependent_and_every_dependent_set_contains_a_circuit():
    for key, n, seed, s in _systems():
        if s.m > 12:
            continue
        for c in s.circuits:
            assert not s.ok[c] and all(s.ok[c & ~(1 << e)] for e in range(s.m) if c >> e & 1)
        for mask in range(1 << s.m):
            assert s.ok[mask] != bool(s.circuits_in(mask))


def test_flats_are_closed_and_the_whole_set_and_the_loops_are_flats():
    for key, n, seed, s in _systems():
        assert s.closure(s.full) == s.full and s.full in s.flats and s.closure(0) in s.flats
        assert all(s.closure(f) == f for f in s.flats)


def test_round_trips_hold_for_every_system_on_every_plan():
    for key, n, seed, s in _systems():
        assert all(round_trips(s).values()), (key, n, seed)


def test_rank_of_the_whole_set_equals_the_basis_size_of_a_matroid_and_the_largest_maximal_set_otherwise():
    for key, n, seed, s in _systems():
        assert s.rank == max(s.maximal_sizes())


def test_renaming_the_elements_keeps_counts_of_bases_circuits_and_flats():
    rng = random.Random(7)
    for ok in all_systems(4):
        s = System("a", 4, list(ok))
        perm = list(range(4))
        rng.shuffle(perm)
        image = [False] * 16
        for mask in range(16):
            image[sum(1 << perm[e] for e in range(4) if mask >> e & 1)] = ok[mask]
        t = System("b", 4, image)
        assert (len(s.bases), len(s.circuits), len(s.flats), s.rank, s.is_matroid) == (len(t.bases), len(t.circuits), len(t.flats), t.rank, t.is_matroid)


def test_the_circuit_list_is_the_shortest_description_of_the_wald_and_the_bases_of_the_uniform_matroid():
    wald = S.get_system("wald", 7, 8)
    assert len(wald.circuits) < len(wald.bases) < len(wald.ind)
    uniform = S.get_system("uniform", 7, 8)
    assert len(uniform.bases) < len(uniform.circuits)


def test_statistics_are_identical_in_two_processes_with_different_hash_seeds():
    code = (
        "import sys; sys.path.insert(0, %r); import rbk_evaluation as ev; "
        "a = ev.analyse(ev.Settings(n=6, seed=3, system='wald_farben')); print(a); print(ev.contrast_stats(ev.Settings(n=6, seed=3, system='paarung'))); "
        "print(ev.agreement_rows(3)); print(ev.axiom_rows(ev.Settings(n=6, seed=3, system='farben'), True))"
    ) % str(ROOT)
    outs = []
    for hash_seed in ("1", "2"):
        env = dict(os.environ, PYTHONHASHSEED=hash_seed)
        outs.append(subprocess.run([sys.executable, "-X", "utf8", "-c", code], capture_output=True, text=True, encoding="utf-8", env=env, timeout=120, check=True).stdout)
    assert outs[0] == outs[1] and outs[0].strip()
