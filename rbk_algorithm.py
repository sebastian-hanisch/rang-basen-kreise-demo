"""Kern der Demo: Unabhängigkeitssysteme auf höchstens 16 Elementen (Bitmasken) mit Rang, Basen, Kreisen, Abschluss und Flachen, den Axiomprüfungen und der Rundreise.

Ein Unabhängigkeitssystem ist eine nach unten abgeschlossene Familie von Teilmengen einer Grundmenge. Elemente sind Zahlen 0 .. m − 1, eine Menge ist die Bitmaske.
Rang r(F) = Größe der größten zulässigen Teilmenge von F. Basen = maximale zulässige Mengen. Kreise = minimale unzulässige Mengen.
Abschluss cl(F) = F plus alle e mit r(F + e) = r(F). Flach = Menge F mit cl(F) = F. Fundamentalkreis C(B, e) = der Kreis in B + e (Basis B, e nicht in B).
Matroid = Austauschaxiom der zulässigen Mengen; dieselbe Eigenschaft in den Sprachen von Basen, Kreisen, Rang und Abschluss prüfen die check_*-Funktionen."""

import itertools
from functools import cached_property

import numpy as np


def popcount(x: int) -> int:
    return bin(x).count("1")


def elements(mask: int, m: int) -> list[int]:
    return [e for e in range(m) if mask >> e & 1]


class System:
    """Unabhängigkeitssystem auf m Elementen; ok[mask] sagt, ob die Menge `mask` zulässig ist."""

    def __init__(self, name: str, m: int, ok):
        if not 1 <= m <= 16:
            raise ValueError(f"m = {m} außerhalb von 1 bis 16")
        if len(ok) != 1 << m or not ok[0]:
            raise ValueError("ok braucht 2**m Einträge, und die leere Menge muss zulässig sein")
        self.name, self.m, self.ok = name, m, list(ok)
        self.full = (1 << m) - 1
        self.ind = [mask for mask in range(1 << m) if self.ok[mask]]
        self.ind_array = np.array(self.ind, dtype=np.int64)
        self.sizes = np.array([popcount(i) for i in self.ind], dtype=np.int64)
        self._ranks()

    # --- Grundbegriffe ------------------------------------------------------------------------------------------------------------------

    def check_down_closed(self) -> bool:
        """Mit jeder zulässigen Menge sind alle Mengen ohne ein Element zulässig (genügt für alle Teilmengen)."""
        return all(self.ok[mask & ~(1 << e)] for mask in self.ind for e in range(self.m) if mask >> e & 1)

    def can_add(self, mask: int, e: int) -> bool:
        return not mask >> e & 1 and self.ok[mask | 1 << e]

    def addable(self, mask: int) -> int:
        """Maske aller Elemente, die zu `mask` passen."""
        out = 0
        for e in range(self.m):
            if self.can_add(mask, e):
                out |= 1 << e
        return out

    def is_maximal(self, mask: int) -> bool:
        return self.ok[mask] and self.addable(mask) == 0

    def _ranks(self):
        m, ok = self.m, self.ok
        ur = [0] * (1 << m)
        for mask in range(1, 1 << m):
            ur[mask] = popcount(mask) if ok[mask] else max(ur[mask & ~(1 << e)] for e in range(m) if mask >> e & 1)
        self.ur = ur
        lr = [0] * (1 << m)
        for i in sorted(self.ind, key=popcount):
            free = self.full & ~i & ~self.addable(i)
            s = free
            while True:
                f = i | s
                if f and lr[f] == 0:
                    lr[f] = popcount(i)
                if s == 0:
                    break
                s = (s - 1) & free
        self.lr = lr
        best = None
        for f in range(1, 1 << m):
            if ur[f] > 0:
                q = lr[f] / ur[f]
                if best is None or q < best[0] - 1e-15:
                    best = (q, f)
        self.q = best[0] if best else 1.0

    # --- Rang, Basen, Kreise, Abschluss, Flache -------------------------------------------------------------------------------------------

    @property
    def rank(self) -> int:
        """Rang der ganzen Grundmenge: Größe der größten zulässigen Menge."""
        return self.ur[self.full]

    def rank_of(self, f: int) -> int:
        return self.ur[f]

    @cached_property
    def bases(self) -> list[int]:
        """Maximale zulässige Mengen (bei einem Matroid alle gleich groß)."""
        return [i for i in self.ind if self.is_maximal(i)]

    @cached_property
    def circuits(self) -> list[int]:
        """Minimale unzulässige Mengen."""
        out = []
        for c in range(1, 1 << self.m):
            if not self.ok[c] and all(self.ok[c & ~(1 << e)] for e in range(self.m) if c >> e & 1):
                out.append(c)
        return out

    def closure(self, f: int) -> int:
        """cl(F) = F plus alle e, deren Hinzunahme den Rang nicht erhöht."""
        r = self.ur[f]
        out = f
        for e in range(self.m):
            if not f >> e & 1 and self.ur[f | 1 << e] == r:
                out |= 1 << e
        return out

    @cached_property
    def closures(self) -> list[int]:
        return [self.closure(f) for f in range(1 << self.m)]

    @cached_property
    def flats(self) -> list[int]:
        return [f for f in range(1 << self.m) if self.closures[f] == f]

    def flats_by_rank(self) -> dict[int, int]:
        out: dict[int, int] = {}
        for f in self.flats:
            out[self.ur[f]] = out.get(self.ur[f], 0) + 1
        return dict(sorted(out.items()))

    def circuits_in(self, mask: int) -> list[int]:
        """Alle Kreise, die in `mask` enthalten sind."""
        return [c for c in self.circuits if c & ~mask == 0]

    def fundamental_circuit(self, base: int, e: int):
        """Der Kreis in B + e, wenn es genau einen gibt (bei einem Matroid immer), sonst None."""
        inside = self.circuits_in(base | 1 << e)
        return inside[0] if len(inside) == 1 else None

    def swap_is_basis(self, base: int, f: int, e: int) -> bool:
        """Ist B − f + e wieder eine Basis (maximale zulässige Menge)?"""
        new = (base & ~(1 << f)) | 1 << e
        return self.is_maximal(new)

    def maximal_sizes(self) -> dict[int, int]:
        sizes: dict[int, int] = {}
        for i in self.bases:
            sizes[popcount(i)] = sizes.get(popcount(i), 0) + 1
        return dict(sorted(sizes.items()))

    # --- Austauschprobe (Stück 3) -------------------------------------------------------------------------------------------------------

    def exchange_scan(self, weak: bool = False) -> tuple[int, int]:
        """(Zahl der Paare (I1, I2) mit |I1| < |I2|, Zahl der Paare ohne Austauschpartner); je I1 ein Maskenvergleich über alle I2."""
        pairs = viol = 0
        for i1, s1 in zip(self.ind, self.sizes):
            bigger = self.sizes == s1 + 1 if weak else self.sizes > s1
            count = int(bigger.sum())
            if not count:
                continue
            pairs += count
            viol += int(((self.ind_array[bigger] & ~i1 & self.addable(i1)) == 0).sum())
        return pairs, viol

    @cached_property
    def is_matroid(self) -> bool:
        return self.exchange_scan()[1] == 0


# --- Rundreise: aus einer Beschreibung die zulässigen Mengen zurückgewinnen -------------------------------------------------------------------


def independent_from_bases(m: int, bases) -> list[bool]:
    """Zulässig ist, was in einer Basis liegt: nach unten abgeschlossene Hülle der Basen."""
    ok = [False] * (1 << m)
    for b in bases:
        ok[b] = True
    for mask in sorted(range(1 << m), key=lambda x: -popcount(x)):
        if ok[mask]:
            for e in range(m):
                if mask >> e & 1:
                    ok[mask & ~(1 << e)] = True
    return ok


def independent_from_circuits(m: int, circuits) -> list[bool]:
    """Zulässig ist, was keinen Kreis enthält."""
    dependent = [False] * (1 << m)
    for c in circuits:
        dependent[c] = True
    for mask in range(1 << m):
        if dependent[mask]:
            for e in range(m):
                dependent[mask | 1 << e] = True
    return [not d for d in dependent]


def independent_from_rank(m: int, rank_values) -> list[bool]:
    """Zulässig ist, was r(I) = |I| erfüllt."""
    return [rank_values[mask] == popcount(mask) for mask in range(1 << m)]


def independent_from_closure(m: int, closures) -> list[bool]:
    """Zulässig ist, was kein Element im Abschluss der übrigen enthält."""
    return [all(not closures[mask & ~(1 << e)] >> e & 1 for e in range(m) if mask >> e & 1) for mask in range(1 << m)]


def round_trips(s: System) -> dict[str, bool]:
    """Gewinnt man aus Basen, Kreisen, Rang und Abschluss genau die zulässigen Mengen zurück?"""
    return {
        "Basen": independent_from_bases(s.m, s.bases) == s.ok,
        "Kreise": independent_from_circuits(s.m, s.circuits) == s.ok,
        "Rang": independent_from_rank(s.m, s.ur) == s.ok,
        "Abschluss": independent_from_closure(s.m, s.closures) == s.ok,
    }


# --- Axiomprüfungen, jeweils in der Sprache einer Beschreibung ----------------------------------------------------------------------------------


def check_exchange(s: System) -> bool:
    """Austauschaxiom der zulässigen Mengen (Stück 3)."""
    return s.exchange_scan()[1] == 0


def check_basis_exchange(s: System) -> bool:
    """Basenaustausch: Zu Basen B1, B2 und x in B1 ohne B2 gibt es y in B2 ohne B1 mit B1 − x + y eine Basis."""
    bases = set(s.bases)
    for b1 in bases:
        for b2 in bases:
            for x in elements(b1 & ~b2, s.m):
                if not any(((b1 & ~(1 << x)) | 1 << y) in bases for y in elements(b2 & ~b1, s.m)):
                    return False
    return True


def check_circuit_elimination(s: System) -> bool:
    """Kreiseliminierung: Zu verschiedenen Kreisen C1, C2 und e in beiden ist (C1 ∪ C2) − e abhängig (enthält einen Kreis)."""
    for c1, c2 in itertools.combinations(s.circuits, 2):
        for e in elements(c1 & c2, s.m):
            if s.ok[(c1 | c2) & ~(1 << e)]:
                return False
    return True


def check_rank_submodular(s: System) -> bool:
    """Submodularität des Rangs in der Form des abnehmenden Zusatznutzens: r(A + x) + r(A + y) ≥ r(A + x + y) + r(A) für alle A, x, y."""
    r = s.ur
    for a in range(1 << s.m):
        for x in range(s.m):
            if a >> x & 1:
                continue
            for y in range(x + 1, s.m):
                if a >> y & 1:
                    continue
                if r[a | 1 << x] + r[a | 1 << y] < r[a | 1 << x | 1 << y] + r[a]:
                    return False
    return True


def check_closure_axioms(s: System) -> bool:
    """Abschlussoperator: F ⊆ cl(F), cl(cl(F)) = cl(F), Monotonie, und der Austausch y in cl(F + x) ohne cl(F) ⇒ x in cl(F + y)."""
    cl = s.closures
    for f in range(1 << s.m):
        if cl[f] & f != f or cl[cl[f]] != cl[f]:
            return False
        for x in range(s.m):
            if f >> x & 1:
                continue
            if cl[f] & ~cl[f | 1 << x]:
                return False
            for y in range(s.m):
                if y == x or f >> y & 1:
                    continue
                if cl[f | 1 << x] >> y & 1 and not cl[f] >> y & 1 and not cl[f | 1 << y] >> x & 1:
                    return False
    return True


AXIOM_CHECKS = {
    "Austausch (zulässige Mengen)": check_exchange,
    "Basenaustausch": check_basis_exchange,
    "Kreiseliminierung": check_circuit_elimination,
    "Rang submodular": check_rank_submodular,
    "Abschlussoperator": check_closure_axioms,
}


def axiom_results(s: System) -> dict[str, bool]:
    return {name: check(s) for name, check in AXIOM_CHECKS.items()}


# --- alle Unabhängigkeitssysteme auf n Elementen ----------------------------------------------------------------------------------------------


def all_systems(n: int) -> list[tuple[bool, ...]]:
    """Alle nach unten abgeschlossenen Familien auf n Elementen mit leerer Menge, jeweils als Tupel ok[mask]."""
    masks = sorted(range(1 << n), key=lambda x: (popcount(x), x))
    out: list[tuple[bool, ...]] = []
    family = [False] * (1 << n)

    def rec(i):
        if i == len(masks):
            if family[0]:
                out.append(tuple(family))
            return
        mask = masks[i]
        allowed = mask == 0 or all(family[mask & ~(1 << e)] for e in range(n) if mask >> e & 1)
        family[mask] = False
        rec(i + 1)
        if allowed:
            family[mask] = True
            rec(i + 1)
            family[mask] = False

    rec(0)
    return out


def axiom_agreement(n: int, closure_max_n: int = 5) -> dict:
    """Für alle Systeme auf n Elementen: Zahl der Matroide nach dem Austauschaxiom, nach den anderen vier Axiomsystemen und Zahl der Abweichungen."""
    systems = all_systems(n)
    counts = {name: 0 for name in AXIOM_CHECKS}
    mismatch = {name: 0 for name in AXIOM_CHECKS}
    checked_closure = n <= closure_max_n
    for ok in systems:
        s = System("x", n, list(ok))
        reference = check_exchange(s)
        for name, check in AXIOM_CHECKS.items():
            if name == "Abschlussoperator" and not checked_closure:
                continue
            value = check(s)
            counts[name] += value
            mismatch[name] += value != reference
    return {"n": n, "systems": len(systems), "counts": counts, "mismatch": mismatch, "closure_checked": checked_closure}


def count_basis_families(n: int) -> dict[int, int]:
    """Zahl der nichtleeren Familien gleich großer Teilmengen von {0, …, n − 1}, die den Basenaustausch erfüllen, nach Rang."""
    by_size: dict[int, int] = {}
    for k in range(n + 1):
        sets = [sum(1 << e for e in c) for c in itertools.combinations(range(n), k)]
        for bits_mask in range(1, 1 << len(sets)):
            fam = {sets[i] for i in range(len(sets)) if bits_mask >> i & 1}
            ok = True
            for b1 in fam:
                for b2 in fam:
                    for x in elements(b1 & ~b2, n):
                        if not any(((b1 & ~(1 << x)) | 1 << y) in fam for y in elements(b2 & ~b1, n)):
                            ok = False
                            break
                    if not ok:
                        break
                if not ok:
                    break
            if ok:
                by_size[k] = by_size.get(k, 0) + 1
    return by_size
