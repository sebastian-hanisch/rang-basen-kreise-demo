"""Gemeinsame Fixtures: kleine Systeme, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rbk_algorithm import System  # noqa: E402
from rbk_systems import fano_system  # noqa: E402


@pytest.fixture
def dreieck():
    """Graphisches Matroid eines Dreiecks, Kanten a, b, c = Elemente 0, 1, 2: zulässig sind alle Mengen mit höchstens 2 Kanten (U(2, 3)).
    Basen ab, ac, bc (Masken 3, 5, 6); einziger Kreis {a, b, c} (7); Rang min(|F|, 2); Flache ∅, a, b, c, abc (5)."""
    return System("Dreieck", 3, [bin(mask).count("1") <= 2 for mask in range(8)])


@pytest.fixture
def parallel():
    """Zwei parallele Kanten a, b (0, 1) zwischen 1 und 2 und eine Brücke c (2): a und b schließen sich aus. Basen ac, bc (5, 6); Kreis {a, b} (3);
    cl({a}) = {a, b}; Flache ∅, {a, b}, {c}, {a, b, c} (0, 3, 4, 7)."""
    return System("parallel", 3, [not (mask & 1 and mask & 2) for mask in range(8)])


@pytest.fixture
def paarung3():
    """Paarung auf einem Pfad mit 3 Kanten e0, e1, e2: zulässig ∅, e0, e1, e2, e0e2. Maximal: {e1} (2) und {e0, e2} (5); Kreise {e0, e1} (3) und {e1, e2} (6)."""
    return System("Paarung", 3, [not (mask & 1 and mask & 2) and not (mask & 2 and mask & 4) for mask in range(8)])


@pytest.fixture
def fano():
    """Fano-Ebene: die 7 von 0 verschiedenen Vektoren des GF(2)^3; 57 zulässige Mengen, 28 Basen, 14 Kreise (7 Geraden, 7 Vierermengen), 16 Flache (1, 7, 7, 1)."""
    return fano_system()
