"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import math

import plotly.graph_objects as go

import rbk_constants as C

# Fano-Ebene als Zeichnung: Mittelpunkt P1, Ecken P2, P4, P7, Seitenmitten P3 (gegenüber P2), P5 (gegenüber P4), P6 (gegenüber P7); sieben Geraden.
FANO_POINTS = {0: (0.5, 0.383), 1: (0.5, 0.95), 2: (0.5, 0.1), 3: (0.05, 0.1), 4: (0.725, 0.525), 5: (0.275, 0.525), 6: (0.95, 0.1)}
FANO_LINES = ((0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 3, 5), (1, 4, 6), (2, 3, 6), (2, 4, 5))   # Punkte als Index 0 bis 6, P1 bis P7


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.2), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def _lines(inst, edge_ids):
    xs, ys = [], []
    for e in edge_ids:
        u, v, _ = inst.edges[e]
        xs += [inst.points[u][0], inst.points[v][0], None]
        ys += [inst.points[u][1], inst.points[v][1], None]
    return xs, ys


def build_plan(inst, kind, groups, colors=(), height=430):
    """Plan der Standorte oder die Fano-Zeichnung. kind: "kanten" (Elemente sind Leitungen), "knoten" (Standorte), "punkte" (Fano).
    groups: Liste (Name, Elemente, Farbe) in Zeichenreihenfolge, hervorgehoben (Leitungen dick, Standorte groß). colors: Kabelfarbe je Leitung (dünn gezeichnet)."""
    fig = go.Figure()
    marked = {e for _, ids, _ in groups for e in ids}
    if kind == "punkte":
        return _fano_figure(groups, height)
    if kind == "kanten":
        for color in sorted(set(colors)) or [None]:
            ids = [e for e in range(inst.m) if e not in marked and (color is None or colors[e] == color)]
            if ids:
                xs, ys = _lines(inst, ids)
                fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=C.CABLE_RGB[color] if color else C.COLOR_OTHER, width=2), name=f"Kabel {color}" if color else "mögliche Leitung", hoverinfo="skip"))
        for name, ids, color in groups:
            if ids:
                xs, ys = _lines(inst, ids)
                fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=color, width=6), name=name, hoverinfo="skip"))
    node_colors, sizes = [], []
    for v in range(inst.n):
        node_colors.append(C.COLOR_DEPOT if v == 0 else C.COLOR_NODE)
        sizes.append(16)
    if kind == "knoten":
        for name, ids, color in groups:
            for v in ids:
                node_colors[v] = color
                sizes[v] = 26
    fig.add_trace(go.Scatter(
        x=[p[0] for p in inst.points], y=[p[1] for p in inst.points], mode="markers+text", text=[inst.name(v) for v in range(inst.n)],
        textposition="top center", textfont=dict(size=14), marker=dict(size=sizes, color=node_colors, line=dict(color="white", width=1.5)),
        name="Standort", hovertemplate="%{text}<extra></extra>", showlegend=False,
    ))
    if kind == "knoten":
        for name, ids, color in groups:
            if ids:
                fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(size=14, color=color), name=name))
    fig.add_trace(go.Scatter(x=[-0.05, 1.05], y=[-0.05, 1.05], mode="markers", marker=dict(opacity=0), hoverinfo="skip", showlegend=False))
    fig.update_xaxes(visible=False, scaleanchor="y", scaleratio=1)
    fig.update_yaxes(visible=False)
    return _base(fig, height)


def _fano_figure(groups, height):
    fig = go.Figure()
    for tri in FANO_LINES[:6]:
        a, b, c = tri
        ends = sorted(tri, key=lambda i: (FANO_POINTS[i][0], FANO_POINTS[i][1]))
        xs = [FANO_POINTS[ends[0]][0], FANO_POINTS[ends[-1]][0]]
        ys = [FANO_POINTS[ends[0]][1], FANO_POINTS[ends[-1]][1]]
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=C.COLOR_OTHER, width=1.5), hoverinfo="skip", showlegend=False))
    (ax, ay), (bx, by), (qx, qy) = FANO_POINTS[2], FANO_POINTS[4], FANO_POINTS[5]          # die Gerade P3, P5, P6 ist der Kreis durch diese drei Punkte
    d = 2 * (ax * (by - qy) + bx * (qy - ay) + qx * (ay - by))
    cx = ((ax ** 2 + ay ** 2) * (by - qy) + (bx ** 2 + by ** 2) * (qy - ay) + (qx ** 2 + qy ** 2) * (ay - by)) / d
    cy = ((ax ** 2 + ay ** 2) * (qx - bx) + (bx ** 2 + by ** 2) * (ax - qx) + (qx ** 2 + qy ** 2) * (bx - ax)) / d
    r = math.dist((cx, cy), (ax, ay))
    circle =[(cx + r * math.cos(t / 50 * 2 * math.pi), cy + r * math.sin(t / 50 * 2 * math.pi)) for t in range(51)]
    fig.add_trace(go.Scatter(x=[p[0] for p in circle], y=[p[1] for p in circle], mode="lines", line=dict(color=C.COLOR_OTHER, width=1.5), hoverinfo="skip", showlegend=False))
    marked = {}
    for name, ids, color in groups:
        for e in ids:
            marked[e] = color
    fig.add_trace(go.Scatter(
        x=[FANO_POINTS[e][0] for e in range(7)], y=[FANO_POINTS[e][1] for e in range(7)], mode="markers+text", text=[f"P{e + 1}" for e in range(7)],
        textposition="top center", textfont=dict(size=14),
        marker=dict(size=[26 if e in marked else 16 for e in range(7)], color=[marked.get(e, C.COLOR_NODE) for e in range(7)], line=dict(color="white", width=1.5)),
        hovertemplate="%{text}<extra></extra>", showlegend=False,
    ))
    for name, ids, color in groups:
        if ids:
            fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(size=14, color=color), name=name))
    fig.add_trace(go.Scatter(x=[-0.05, 1.05], y=[-0.05, 1.05], mode="markers", marker=dict(opacity=0), hoverinfo="skip", showlegend=False))
    fig.update_xaxes(visible=False, scaleanchor="y", scaleratio=1)
    fig.update_yaxes(visible=False)
    return _base(fig, height)


def build_flats_chart(by_rank):
    """Zahl der Flache je Rang."""
    fig = go.Figure(go.Bar(x=[str(r) for r in by_rank], y=list(by_rank.values()), marker_color=C.COLOR_FLAT, hovertemplate="Rang %{x}: %{y} Flache<extra></extra>"))
    fig.update_xaxes(title_text="Rang des Flachs", type="category")
    fig.update_yaxes(title_text="Zahl der Flache")
    return _base(fig, 300)


def build_contrast_chart(dist):
    """Wie oft liegen 1, 2, 3 ... Kreise in B + e (B maximale zulässige Menge, e außerhalb)?"""
    fig = go.Figure(go.Bar(x=[str(k) for k in dist], y=list(dist.values()), marker_color=[C.COLOR_ELEMENT if k == 1 else C.COLOR_CIRCUIT for k in dist],
                           hovertemplate="%{x} Kreise: %{y} Fälle<extra></extra>"))
    fig.update_xaxes(title_text="Zahl der Kreise in B + e", type="category")
    fig.update_yaxes(title_text="Fälle (B, e)")
    return _base(fig, 300)
