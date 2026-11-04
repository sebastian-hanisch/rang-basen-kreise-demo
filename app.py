"""Rang, Basen, Kreise, Abschluss - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 4 der Reihe „Matroide und Submodularität“ (Bereich Kombinatorik). Aufbau und Regeln: DEMO-PLAYBOOK.md (§2).

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import rbk_constants as C
from rbk_algorithm import elements, popcount
from rbk_evaluation import (
    Settings,
    agreement_rows,
    analyse,
    axiom_rows,
    base_list,
    basis_families,
    closure_info,
    contrast_stats,
    de,
    description_rows,
    elemente,
    fundamental,
    fundamental_table,
    names,
    outside_elements,
    play_check,
    verdict_agreement,
    verdict_axioms,
    verdict_closure,
    verdict_contrast,
    verdict_descriptions,
    verdict_flats,
    verdict_fundamental,
    verdict_play,
    zahl,
)
from rbk_layout import dunkles_design, kopf_css
from rbk_pdf_export import build_pdf
from rbk_presets import bounds, init_session_state_defaults, load_permalink_settings, randomize_seed, sidebar_presets, sync_query_params
from rbk_visualization import build_contrast_chart, build_flats_chart, build_plan

st.set_page_config(page_title="Rang, Basen, Kreise – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner="Basen, Kreise und Flache bestimmen …")
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _bases(settings):
    return base_list(settings)


@st.cache_data(show_spinner="Die fünf Axiomsysteme prüfen …")
def _axioms(settings, matroid):
    return axiom_rows(settings, matroid)


@st.cache_data(show_spinner="Alle Unabhängigkeitssysteme aufzählen (bei 5 Elementen einige Sekunden) …")
def _agreement():
    return agreement_rows(), basis_families()


@st.cache_data(show_spinner=False)
def _contrast(settings):
    return contrast_stats(settings)


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in rbk_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🧩 Rang, Basen, Kreise, Abschluss")
st.markdown(
    """
Ein Matroid ist durch seine zulässigen (unabhängigen) Mengen bestimmt, aber das ist nur **eine** von fünf gleichwertigen Beschreibungen: **Basen** (die größten zulässigen Mengen), **Kreise** (die minimalen unzulässigen Mengen), die **Rangfunktion** (wie groß die größte zulässige Teilmenge ist) und der **Abschluss** (welche Elemente den Rang nicht erhöhen). Jede hat ihre eigenen Axiome, jede bestimmt die anderen. Und der Tausch aus Stück 1 bekommt hier seine Struktur: Legt man zu einer Basis B ein Element e dazu, entsteht **genau ein Kreis**, der **Fundamentalkreis**; B − f + e ist **genau dann** wieder eine Basis, wenn f auf diesem Kreis liegt.

Dies ist das **vierte Stück** der Reihe „Matroide und Submodularität“. Weiter unten: vier Experimente (🔬), eine **Spielwiese**, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So hängen die fünf Beschreibungen zusammen", expanded=True):
    st.markdown(
        """
1. **Basen:** die maximalen zulässigen Mengen. Bei einem Matroid sind alle gleich groß, und diese Größe ist der **Rang**. Zulässig ist, was in einer Basis liegt.
2. **Kreise:** die kleinsten Mengen, die nicht zulässig sind (bei einem Wald genau die Kreise des Graphen). Zulässig ist, was keinen Kreis enthält.
3. **Rang** r(F): die Größe der größten zulässigen Teilmenge von F. Zulässig ist, was r(I) = |I| erfüllt.
4. **Abschluss** cl(F): F plus alle Elemente, die den Rang nicht erhöhen. Ein **Flach** ist eine Menge mit cl(F) = F. Zulässig ist, was kein Element im Abschluss der übrigen enthält.
5. **Fundamentalkreis:** Zu einer Basis B und einem Element e außerhalb liegt in B + e genau ein Kreis C(B, e). Der Tausch B − f + e ist genau dann eine Basis, wenn f in C(B, e) liegt. Beim Wald ist das der Weg im Baum plus die neue Leitung.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Plan**")
    n = st.slider("Standorte (mit Depot A)", *bounds("n_slider"), key="n_slider", help="Wie viele Standorte der Plan hat. Bis 9 (16 mögliche Leitungen); die Prüfung der fünf Axiomsysteme geht bis 12 Elemente, also bis 7 Standorte.")
    seed = st.number_input("Zufalls-Seed des Plans", *bounds("seed_input"), key="seed_input", step=1)
    st.button("🎲 Neuen Plan generieren", width="stretch", on_click=randomize_seed)
    st.markdown("**System**")
    system = st.selectbox("Zulässige Mengen", C.SYSTEMS, key="system_select", format_func=lambda k: C.SYSTEM_NAMES[k] + ("" if k in C.MATROID_SYSTEMS else " (kein Matroid)"),
                          help="Sechs Matroide und fünf Systeme, die keine sind. Die Fano-Ebene hat feste sieben Punkte und hängt nicht vom Plan ab.")

sync_query_params({"n_slider": int(n), "seed_input": int(seed), "system_select": system})

settings = Settings(int(n), int(seed), system)
a = _analysis(settings)
inst = a.inst
play_id = f"{system}_{settings.n}_{settings.seed}"
ground = {"kanten": "Leitungen", "knoten": "Standorte", "punkte": "Punkte der Fano-Ebene"}[a.kind]

# --- Fundamentalkreis und Tausch ---------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Fundamentalkreis und Tausch")
st.caption(f"{C.SYSTEM_NAMES[system]}: Grundmenge sind die {ground} ({a.m} Elemente), {zahl(a.n_independent)} zulässige Mengen aufgezählt.")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Rang", a.rank)
m2.metric("Basen", zahl(a.n_bases), delta="alle gleich groß" if len(a.base_sizes) == 1 else f"{len(a.base_sizes)} verschiedene Größen", delta_color="off")
m3.metric("Kreise", zahl(a.n_circuits), delta=f"kleinster hat {a.girth} Elemente" if a.girth else None, delta_color="off")
m4.metric("Flache", zahl(a.n_flats))

bases = _bases(settings)
if len(bases) > 1:
    idx = st.slider("Basis Nr.", 1, len(bases), 1, key=f"base_{play_id}", help="Welche Basis B betrachtet wird (in der Reihenfolge der Bitmasken).")
else:
    idx = 1
base = bases[idx - 1]
outside = outside_elements(a, base)
if not outside:
    st.info("Die Basis enthält alle Elemente: Es gibt kein Element e außerhalb, das man dazulegen könnte.")
    res = None
else:
    e = st.selectbox("Element e außerhalb von B", outside, key=f"e_{play_id}_{base}", format_func=lambda x: a.labels[x])
    res = fundamental(a, base, e)
    col_a, col_b = st.columns(2)
    with col_a:
        groups = [("Basis B", elements(base, a.m), C.COLOR_BASE)]
        circuit_union = 0
        for c in res["circuits"]:
            circuit_union |= c
        if circuit_union:
            groups.append(("Kreis in B + e", elements(circuit_union & ~(1 << e), a.m), C.COLOR_CIRCUIT))
        groups.append(("Element e", [e], C.COLOR_ELEMENT))
        st.plotly_chart(build_plan(inst, a.kind, groups, a.colors), width="stretch", key="map_fundamental")
    with col_b:
        st.markdown("**Tausch B − f + e für jedes f in B**")
        st.dataframe(fundamental_table(res), hide_index=True, width="stretch")
        st.caption("Blaugrün: die Basis B, orange: der Rest des Kreises (ohne e) in B + e, grün: das Element e.")

if st.button("📄 PDF des aktuellen Systems erstellen", key="pdf_make"):
    st.session_state["pdf_made"] = (settings, build_pdf(a, settings))
made = st.session_state.get("pdf_made")
if made and made[0] == settings:
    st.download_button("⬇️ PDF herunterladen", data=made[1], file_name="rang-basen-kreise.pdf", mime="application/pdf", key="pdf_download")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Liegt der Tausch auf dem Kreis?")
if res is not None:
    kind_v, text_v = verdict_fundamental(a, res)
    getattr(st, kind_v)(text_v)

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 1: Fünf Beschreibungen desselben Systems")
st.caption("Wie viele Mengen jede Beschreibung braucht, ob man aus ihr die zulässigen Mengen zurückgewinnt (Rundreise), und ob das System die Axiome der fünf Sprachen erfüllt.")
st.dataframe(description_rows(a), hide_index=True, width="stretch")
kind_v, text_v = verdict_descriptions(a)
getattr(st, kind_v)(text_v)
if st.button("🧮 Die fünf Axiomsysteme prüfen", key="axiom_run"):
    st.session_state["axiom_done"] = play_id
if st.session_state.get("axiom_done") == play_id:
    rows = _axioms(settings, a.is_matroid)
    if rows is not None:
        st.dataframe(rows, hide_index=True, width="stretch")
    kind_v, text_v = verdict_axioms(rows, a.is_matroid)
    getattr(st, kind_v)(text_v)

st.subheader("🔬 Experiment 2: Abschluss und Flache")
st.caption("Wählen Sie eine Menge F. Der Abschluss nimmt alle Elemente dazu, die den Rang nicht erhöhen; ein Flach ist eine Menge, die ihren Abschluss schon enthält.")
f_default = elements(base, a.m)[:2] if len(bases) else []
sel_f = st.multiselect("Menge F", list(range(a.m)), default=f_default, key=f"closure_{play_id}", format_func=lambda x: a.labels[x])
f_mask = sum(1 << x for x in sel_f)
info = closure_info(settings, f_mask)
groups = [("F", sel_f, C.COLOR_FLAT)]
if info["added"]:
    groups.append(("zusätzlich im Abschluss", elements(info["added"], a.m), C.COLOR_CLOSURE))
st.plotly_chart(build_plan(inst, a.kind, groups, a.colors), width="stretch", key="map_closure")
kind_v, text_v = verdict_closure(a, info)
getattr(st, kind_v)(text_v)
st.plotly_chart(build_flats_chart(dict(a.flats_by_rank)), width="stretch", key="flats_chart")
kind_v, text_v = verdict_flats(a)
getattr(st, kind_v)(text_v)

st.subheader("🔬 Experiment 3: Stimmen die fünf Axiomsysteme auf allen kleinen Systemen überein?")
st.caption("Alle Unabhängigkeitssysteme auf 1 bis 5 Elementen, für jedes die fünf Axiomprüfungen gegen das Austauschaxiom; dazu die Familien gleich großer Mengen mit Basenaustausch auf 5 Elementen.")
if st.button("📊 Alle Systeme bis 5 Elemente prüfen", key="agree_run"):
    st.session_state["agree_done"] = True
if st.session_state.get("agree_done"):
    rows, families = _agreement()
    st.dataframe(
        [
            {
                "Elemente n": r["n"], "Systeme": zahl(r["systems"]), "Matroide": zahl(r["counts"]["Austausch (zulässige Mengen)"]),
                **{f"{name}: Abweichungen": r["mismatch"][name] for name in r["mismatch"] if name != "Austausch (zulässige Mengen)"},
            }
            for r in rows
        ],
        hide_index=True, width="stretch",
    )
    st.caption("Familien gleich großer Mengen auf 5 Elementen mit Basenaustausch, nach Größe der Basen: " + ", ".join(f"{k}: {zahl(v)}" for k, v in families.items()) + f" (zusammen {zahl(sum(families.values()))}).")
    kind_v, text_v = verdict_agreement(rows, families)
    getattr(st, kind_v)(text_v)

st.subheader("🔬 Experiment 4: Wann liegt in B + e genau ein Kreis?")
st.caption("Für (eine Stichprobe von bis zu 200) maximale zulässige Mengen B und jedes Element e außerhalb: Wie viele Kreise liegen in B + e? Bei einem Matroid immer genau einer.")
stats = _contrast(settings)
st.plotly_chart(build_contrast_chart(stats["dist"]), width="stretch", key="contrast_chart")
kind_v, text_v = verdict_contrast(a, stats)
getattr(st, kind_v)(text_v)

st.markdown("---")

# --- Spielwiese ----------------------------------------------------------------------------------------------------------------------------

st.subheader("🛠️ Spielwiese: Kreise in B + e von Hand")
st.caption("Wählen Sie eine Menge B und ein Element e außerhalb. Die App sagt, ob B zulässig und maximal ist und welche Kreise in B + e liegen.")
sel_b = st.multiselect("Menge B", list(range(a.m)), default=elements(base, a.m), key=f"play_b_{play_id}", format_func=lambda x: a.labels[x])
b_mask = sum(1 << x for x in sel_b)
free = [x for x in range(a.m) if x not in sel_b]
e_play = st.selectbox("Element e (optional)", [None] + free, key=f"play_e_{play_id}_{b_mask}", format_func=lambda x: "– keines –" if x is None else a.labels[x])
pr = play_check(settings, b_mask, e_play)
kind_v, text_v = verdict_play(a, pr)
getattr(st, kind_v)(text_v)

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Die Grundmenge ist klein (höchstens 16 Elemente)** | Rang, Basen, Kreise und Flache werden hier aus allen Teilmengen berechnet. Die Prüfung aller fünf Axiomsysteme geht nur bis 12 Elemente, die Aufzählung aller Systeme nur bis 5 Elemente. Bei großen Matroiden rechnet man mit der Struktur (Rangorakel, Darstellung). | Stück 17 (Verfahrenswahl) |
| **Das System ist ein Matroid** | Bei vier der fünf Systeme, die keine Matroide sind, liegen in B + e oft mehrere Kreise (beim Schnitt aus Wald und Farbregel nur selten; Experiment 4), und bei vier haben die maximalen Mengen verschiedene Größen; Fundamentalkreis und Rang sind dort nicht mehr dasselbe Gerüst. | Stück 2 (Unabhängigkeitssysteme) |
| **Beispiele sind klein und zufällig** | Die Zahlen gelten für den gezeigten Plan, nicht allgemein; dass Wald, Farben, Anschluss, uniforme und lineare Systeme Matroide sind, ist bekannt und wird hier nur an den gezeigten Systemen gemessen. | Stück 3 (Beispiele) |
| **Kreise und Basen, nicht Kokreise** | Das Gegenstück zum Kreis (der Kokreis, im Graphen ein minimaler Schnitt) und das duale Matroid gehören zur Dualität. | Stück 6 |
| **Rangform bei Submodularität** | Dass der Rang eines Matroids submodular ist, wird hier an kleinen Systemen geprüft (abnehmender Zusatznutzen); die Submodularität als Verfahren (Greedy 1 − 1/e) kommt in Stück 11. | Stück 11 |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Gegeben** ein Matroid $M = (E, \mathcal{I})$ auf einer endlichen Grundmenge $E$ (Stück 3: Unabhängigkeitssystem mit Austauschaxiom).

| Symbol | Bedeutung |
|---|---|
| $\mathcal{I}$ | zulässige (unabhängige) Mengen |
| $\mathcal{B}$ | Basen: die maximalen Mengen in $\mathcal{I}$ |
| $\mathcal{C}$ | Kreise: die minimalen Mengen außerhalb von $\mathcal{I}$ |
| $r(F)$ | Rang: $\max\{\lvert I \rvert : I \in \mathcal{I},\ I \subseteq F\}$ |
| $\operatorname{cl}(F)$ | Abschluss: $F \cup \{e : r(F \cup e) = r(F)\}$ |
| $C(B, e)$ | Fundamentalkreis zu $B \in \mathcal{B}$ und $e \notin B$ |

**Basenaustausch.** Zu $B_1, B_2 \in \mathcal{B}$ und $x \in B_1 \setminus B_2$ gibt es $y \in B_2 \setminus B_1$ mit $(B_1 \setminus x) \cup y \in \mathcal{B}$.

**Kreiseliminierung.** Zu verschiedenen $C_1, C_2 \in \mathcal{C}$ und $e \in C_1 \cap C_2$ enthält $(C_1 \cup C_2) \setminus e$ einen Kreis.

**Rang.** $0 \le r(F) \le \lvert F \rvert$; $F \subseteq G \Rightarrow r(F) \le r(G)$; $r(A \cup B) + r(A \cap B) \le r(A) + r(B)$ (Submodularität); $I$ ist zulässig genau dann, wenn $r(I) = \lvert I \rvert$.

**Abschluss.** $F \subseteq \operatorname{cl}(F)$, $\operatorname{cl}(\operatorname{cl}(F)) = \operatorname{cl}(F)$, $F \subseteq G \Rightarrow \operatorname{cl}(F) \subseteq \operatorname{cl}(G)$, und aus $y \in \operatorname{cl}(F \cup x) \setminus \operatorname{cl}(F)$ folgt $x \in \operatorname{cl}(F \cup y)$.

**Fundamentalkreis.** Für $B \in \mathcal{B}$ und $e \notin B$ enthält $B \cup e$ genau einen Kreis $C(B, e)$, und $(B \setminus f) \cup e$ ist genau dann eine Basis, wenn $f \in C(B, e)$.

**Literatur.** Die Gleichwertigkeit der Axiomsysteme (Kryptomorphismen) steht in Zusammenfassungen der Matroid-Theorie (Quelle: Websuche, nicht die Originalarbeit; Standardwerk: Oxley, *Matroid Theory*, nicht eingesehen). Hier wird sie an allen Unabhängigkeitssystemen mit höchstens 5 Elementen nachgerechnet.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zur Reihe: [Matroide: vom Spannbaum zur Verfahrenswahl](https://sebastianhanisch.net/konzepte-matroide.html)."
)
