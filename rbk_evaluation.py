"""Kennzahlen, Messreihen und Verdikte. Alle sichtbaren Zahlen kommen aus diesen Funktionen."""

from dataclasses import dataclass

import rbk_constants as C
from rbk_algorithm import AXIOM_CHECKS, axiom_agreement, count_basis_families, elements, popcount, round_trips
from rbk_scenario import Instance, make_instance
from rbk_systems import edge_colors, get_system, ground_kind, labels

EPS = 1e-9


def de(x: float, digits: int = 1) -> str:
    """Zahl mit Dezimalkomma."""
    return f"{x:.{digits}f}".replace(".", ",")


def prozent(x: float, digits: int = 1) -> str:
    return de(100.0 * x, digits)


def zahl(n: int) -> str:
    """Ganze Zahl mit Leerzeichen als Tausendertrenner."""
    return f"{n:,}".replace(",", " ")


def elemente(k: int) -> str:
    return "1 Element" if k == 1 else f"{k} Elemente"


@dataclass(frozen=True)
class Settings:
    n: int = C.DEFAULT_N
    seed: int = C.DEFAULT_SEED
    system: str = "wald"


@dataclass(frozen=True)
class Analysis:
    settings: Settings
    inst: Instance
    kind: str               # "kanten", "knoten" oder "punkte"
    m: int                  # Zahl der Elemente der Grundmenge
    labels: tuple
    colors: tuple           # Kabelfarbe je Leitung (leer, wenn die Grundmenge keine Leitungen sind)
    n_independent: int
    n_bases: int            # Zahl der maximalen zulässigen Mengen
    n_circuits: int
    n_flats: int
    rank: int
    girth: int | None       # Größe des kleinsten Kreises
    q: float
    is_matroid: bool
    trips: tuple            # ((Beschreibung, Rundreise gelungen), ...)
    flats_by_rank: tuple    # ((Rang, Zahl), ...)
    base_sizes: tuple       # ((Größe, Zahl), ...)
    circuit_sizes: tuple    # ((Größe, Zahl), ...)


def analyse(settings: Settings) -> Analysis:
    sys_ = get_system(settings.system, settings.n, settings.seed)
    inst = make_instance(settings.n, settings.seed)
    kind = ground_kind(settings.system)
    sizes: dict[int, int] = {}
    for c in sys_.circuits:
        sizes[popcount(c)] = sizes.get(popcount(c), 0) + 1
    return Analysis(
        settings, inst, kind, sys_.m, tuple(labels(settings.system, inst)), tuple(edge_colors(inst, settings.seed)) if kind == "kanten" else (), len(sys_.ind), len(sys_.bases),
        len(sys_.circuits), len(sys_.flats), sys_.rank, min(sizes) if sizes else None, sys_.q, sys_.is_matroid, tuple(round_trips(sys_).items()),
        tuple(sys_.flats_by_rank().items()), tuple(sys_.maximal_sizes().items()), tuple(sorted(sizes.items())),
    )


def names(a: Analysis, mask: int) -> str:
    return ", ".join(a.labels[e] for e in elements(mask, a.m)) or "keine"


# --- Fundamentalkreis und Tausch ------------------------------------------------------------------------------------------------------------


def base_list(settings: Settings) -> list[int]:
    return list(get_system(settings.system, settings.n, settings.seed).bases)


def outside_elements(a: Analysis, base: int) -> list[int]:
    return [e for e in range(a.m) if not base >> e & 1]


def fundamental(a: Analysis, base: int, e: int) -> dict:
    """Die Kreise in B + e und für jedes f in B: Ist B − f + e eine Basis, und liegt f in einem Kreis von B + e?"""
    sys_ = get_system(a.settings.system, a.settings.n, a.settings.seed)
    inside = sys_.circuits_in(base | 1 << e)
    union = 0
    for c in inside:
        union |= c
    rows = []
    for f in elements(base, a.m):
        swap = sys_.swap_is_basis(base, f, e)
        rows.append({"f": f, "Element": a.labels[f], "swap": swap, "in_circuit": bool(union >> f & 1)})
    return {"base": base, "e": e, "circuits": inside, "unique": len(inside) == 1, "rows": rows, "agree": all(r["swap"] == r["in_circuit"] for r in rows)}


def fundamental_table(res: dict) -> list[dict]:
    return [{"Element f": r["Element"], "B − f + e ist Basis": "ja" if r["swap"] else "nein", "f liegt im Kreis": "ja" if r["in_circuit"] else "nein"} for r in res["rows"]]


def verdict_fundamental(a: Analysis, res: dict) -> tuple[str, str]:
    k = len(res["circuits"])
    swaps = sum(r["swap"] for r in res["rows"])
    if res["unique"] and res["agree"]:
        c = res["circuits"][0]
        note = "" if a.is_matroid else " In diesem Nicht-Matroid ist das bei dieser Wahl von B und e so, aber nicht bei allen (Experiment 4)."
        return "success", (
            f"In B + e liegt **genau ein** Kreis: {{{names(a, c)}}} ({elemente(popcount(c))}). Von den {len(res['rows'])} Tauschen B − f + e sind {swaps} wieder eine Basis, "
            f"und das sind genau die Elemente f auf diesem Kreis (außer e selbst).{note}"
        )
    if k == 0:
        return "info", "In B + e liegt kein Kreis: B + e ist zulässig, B war also nicht maximal."
    return "warning", (
        f"In B + e liegen **{k} Kreise**, nicht genau einer: Der Fundamentalkreis ist hier nicht definiert. Von den {len(res['rows'])} Tauschen B − f + e sind {swaps} wieder eine Basis; "
        f"ob f auf einem der Kreise liegt, sagt darüber nichts verlässlich."
    )


# --- Fünf Beschreibungen ---------------------------------------------------------------------------------------------------------------------


def description_rows(a: Analysis) -> list[dict]:
    trips = dict(a.trips)
    return [
        {"Beschreibung": "zulässige (unabhängige) Mengen", "Zahl": zahl(a.n_independent), "Rundreise": "–"},
        {"Beschreibung": "Basen (maximale zulässige Mengen)", "Zahl": zahl(a.n_bases), "Rundreise": "gelungen" if trips["Basen"] else "misslungen"},
        {"Beschreibung": "Kreise (minimale unzulässige Mengen)", "Zahl": zahl(a.n_circuits), "Rundreise": "gelungen" if trips["Kreise"] else "misslungen"},
        {"Beschreibung": "Rangfunktion (Rang jeder Teilmenge)", "Zahl": f"{zahl(2 ** a.m)} Werte", "Rundreise": "gelungen" if trips["Rang"] else "misslungen"},
        {"Beschreibung": "Abschluss und Flache", "Zahl": f"{zahl(a.n_flats)} Flache", "Rundreise": "gelungen" if trips["Abschluss"] else "misslungen"},
    ]


def verdict_descriptions(a: Analysis) -> tuple[str, str]:
    if not all(dict(a.trips).values()):
        return "error", "Eine Rundreise ist misslungen. Das darf nicht sein: Rechenfehler."
    shortest = min(("Basen", a.n_bases), ("Kreise", a.n_circuits), ("Flache", a.n_flats), key=lambda x: x[1])
    factor = a.n_independent / shortest[1] if shortest[1] else 0.0
    return "info", (
        f"Aus jeder Beschreibung lassen sich die zulässigen Mengen zurückgewinnen (Rundreise gelungen). Die kürzeste Liste hat das System als **{shortest[0]}** "
        f"({zahl(shortest[1])} gegen {zahl(a.n_independent)} zulässige Mengen, etwa {de(factor, 1)}-mal kürzer)."
    )


def axiom_rows(settings: Settings, matroid: bool):
    """Die fünf Axiomprüfungen am gewählten System, oder None, wenn das System zu groß dafür ist."""
    s = get_system(settings.system, settings.n, settings.seed)
    if s.m > C.AXIOM_MAX_ELEMENTS:
        return None
    rows = []
    for name, check in AXIOM_CHECKS.items():
        ok = check(s)
        rows.append({"Axiomsystem": name, "erfüllt": "ja" if ok else "nein", "wie das Austauschaxiom": "ja" if ok == matroid else "nein"})
    return rows


def verdict_axioms(rows, matroid: bool) -> tuple[str, str]:
    if rows is None:
        return "info", f"Bei mehr als {C.AXIOM_MAX_ELEMENTS} Elementen ist die Prüfung aller fünf Axiomsysteme hier zu aufwendig; auf einem Plan mit höchstens 7 Standorten ist sie möglich."
    if any(r["wie das Austauschaxiom"] != "ja" for r in rows):
        return "error", "Ein Axiomsystem widerspricht dem Austauschaxiom. Das darf nicht sein: Rechenfehler."
    word = "alle fünf erfüllt: ein Matroid" if matroid else "alle fünf verletzt: kein Matroid"
    return "success", f"Die fünf Axiomsysteme (zulässige Mengen, Basen, Kreise, Rang, Abschluss) sind {word}."


# --- Abschluss und Flache ----------------------------------------------------------------------------------------------------------------------


def closure_info(settings: Settings, f: int) -> dict:
    s = get_system(settings.system, settings.n, settings.seed)
    cl = s.closure(f)
    return {"f": f, "rank": s.rank_of(f), "closure": cl, "flat": cl == f, "added": cl & ~f}


def verdict_closure(a: Analysis, info: dict) -> tuple[str, str]:
    if not info["f"]:
        return "info", "Die leere Menge hat Rang 0; ihr Abschluss besteht aus den Elementen vom Rang 0 (Schleifen), hier " + ("keinen." if not info["closure"] else f"{{{names(a, info['closure'])}}}.")
    added = "keine" if not info["added"] else f"{{{names(a, info['added'])}}}"
    flat = " F ist ein **Flach**." if info["flat"] else ""
    return "info", f"Rang von F: {info['rank']} (F hat {elemente(popcount(info['f']))}). Zum Abschluss kommen {added} dazu: Diese Elemente erhöhen den Rang nicht.{flat}"


def verdict_flats(a: Analysis) -> tuple[str, str]:
    by = ", ".join(f"{zahl(c)} vom Rang {r}" for r, c in a.flats_by_rank)
    return "info", f"{zahl(a.n_flats)} Flache: {by}. Das größte Flach ist die ganze Grundmenge, das kleinste die Menge der Schleifen (Rang 0)."


# --- alle kleinen Systeme ---------------------------------------------------------------------------------------------------------------------------


def agreement_rows(max_n: int = C.ENUM_MAX_N) -> list[dict]:
    return [axiom_agreement(n, C.CLOSURE_MAX_N) for n in range(1, max_n + 1)]


def verdict_agreement(rows: list[dict], families: dict[int, int]) -> tuple[str, str]:
    total = sum(r["systems"] for r in rows)
    bad = sum(sum(r["mismatch"].values()) for r in rows)
    if bad:
        return "error", f"Bei {bad} Prüfungen widerspricht ein Axiomsystem dem Austauschaxiom. Das darf nicht sein: Rechenfehler."
    last = rows[-1]
    matroids = last["counts"]["Austausch (zulässige Mengen)"]
    return "success", (
        f"Bei allen {zahl(total)} Unabhängigkeitssystemen mit höchstens {last['n']} Elementen stimmen alle fünf Axiomsysteme mit dem Austauschaxiom überein "
        f"(**0 Abweichungen**); auf {last['n']} Elementen sind {zahl(matroids)} von {zahl(last['systems'])} Systemen Matroide. "
        f"Dazu passt: {zahl(sum(families.values()))} Familien gleich großer Mengen auf {last['n']} Elementen erfüllen den Basenaustausch."
    )


def basis_families(n: int = C.BASIS_FAMILY_N) -> dict[int, int]:
    return count_basis_families(n)


# --- Kontrast ----------------------------------------------------------------------------------------------------------------------------------


def contrast_stats(settings: Settings, limit: int = 200) -> dict:
    """Zahl der Kreise in B + e über (eine Stichprobe von bis zu `limit` gleichmäßig gewählten) Basen B und alle e außerhalb."""
    s = get_system(settings.system, settings.n, settings.seed)
    bases = s.bases
    step = max(1, len(bases) // limit)
    sample = bases[::step][:limit]
    dist: dict[int, int] = {}
    for b in sample:
        for e in range(s.m):
            if not b >> e & 1:
                k = len(s.circuits_in(b | 1 << e))
                dist[k] = dist.get(k, 0) + 1
    total = sum(dist.values())
    return {"dist": dict(sorted(dist.items())), "total": total, "sampled": len(sample), "bases": len(bases), "share_one": dist.get(1, 0) / total if total else 1.0,
            "sizes": dict(s.maximal_sizes())}


def verdict_contrast(a: Analysis, stats: dict) -> tuple[str, str]:
    part = "alle" if stats["sampled"] == stats["bases"] else f"{zahl(stats['sampled'])} von {zahl(stats['bases'])}"
    if not stats["total"]:
        return "info", "Es gibt keine Elemente außerhalb der Basis."
    if a.is_matroid:
        return "success", (
            f"In allen {zahl(stats['total'])} Fällen (B, e) ({part} Basen) liegt in B + e **genau ein** Kreis, und alle Basen haben {elemente(a.rank)}."
        )
    sizes = ", ".join(f"{zahl(c)} mit {s}" for s, c in stats["sizes"].items())
    maxk = max(stats["dist"])
    if len(stats["sizes"]) == 1:
        (size,) = stats["sizes"]
        tail = f"Alle maximalen Mengen haben {elemente(size)}, und doch liegen manchmal mehrere Kreise in B + e: Es sind keine Basen eines Matroids."
    else:
        tail = f"Die maximalen Mengen haben verschiedene Größen ({sizes}): Es sind keine Basen eines Matroids."
    return "warning", (
        f"Nur in **{prozent(stats['share_one'])} %** der {zahl(stats['total'])} Fälle ({part} maximale Mengen) liegt in B + e genau ein Kreis; bis zu {maxk} Kreise kommen vor. {tail}"
    )


# --- Spielwiese ---------------------------------------------------------------------------------------------------------------------------------


def play_check(settings: Settings, mask: int, e) -> dict:
    s = get_system(settings.system, settings.n, settings.seed)
    out = {"mask": mask, "e": e, "independent": s.ok[mask], "maximal": s.is_maximal(mask), "circuits": [], "rank": s.rank_of(mask)}
    if e is not None and not mask >> e & 1:
        out["circuits"] = s.circuits_in(mask | 1 << e)
    return out


def verdict_play(a: Analysis, r: dict) -> tuple[str, str]:
    if not r["independent"]:
        return "info", "Die gewählte Menge ist nicht zulässig; sie enthält einen Kreis. Wählen Sie eine zulässige Menge."
    if r["e"] is None:
        return "info", f"Die Menge ist zulässig (Rang {r['rank']}); wählen Sie ein Element außerhalb, um die Kreise in B + e zu sehen."
    k = len(r["circuits"])
    base = "eine Basis (maximal)" if r["maximal"] else "zulässig, aber nicht maximal"
    if k == 0:
        return "info", f"Die Menge ist {base}. Mit {a.labels[r['e']]} bleibt sie zulässig: kein Kreis in B + e."
    listing = "; ".join("{" + names(a, c) + "}" for c in r["circuits"])
    if k == 1:
        return "success", f"Die Menge ist {base}. In B + {a.labels[r['e']]} liegt genau ein Kreis: {listing}."
    return "warning", f"Die Menge ist {base}. In B + {a.labels[r['e']]} liegen {k} Kreise: {listing}."
