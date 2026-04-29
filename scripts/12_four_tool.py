"""Four-dimensional 'elite hitter' analysis.

We score each qualified hitter on four orthogonal skills and combine into one
composite that flags the rare players who are good at *all four*:

  1. Power               --> avg exit velocity (mph)
  2. Timing              --> Pulled-Air% = (pulled FB + pulled LD) / batted balls
  3. Contact ability     --> In-zone contact% (1 - in-zone whiff%)
  4. Swing decision      --> SEAGER proxy = (Z-Swing% + (100 - O-Swing%)) / 2

We z-score each metric across qualified batters, then take the mean. The
"elite four-tool" filter requires >=+0.5 SD on every dimension.
"""
import os
import math
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
CHARTS = os.path.join(os.path.dirname(__file__), "..", "charts")

MIN_PA = 50          # qualifier for plate-discipline metrics
MIN_BB = 25          # qualifier for batted-ball-direction metrics

METS_BLUE = "#002D72"
METS_ORANGE = "#FF5910"

plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "axes.grid": True, "grid.alpha": 0.25, "font.size": 10,
})


def load_inputs() -> pd.DataFrame:
    sav = pd.read_csv(os.path.join(DATA, "savant_batters_2026.csv"))
    pa  = pd.read_csv(os.path.join(DATA, "savant_pull_air_2026.csv"))

    # standardize player name col
    sav["player"] = sav["last_name, first_name"].apply(
        lambda s: " ".join(reversed([p.strip() for p in str(s).split(",")])) if isinstance(s, str) else s
    )

    # in-zone contact% direct from Savant (iz_contact_percent)
    sav["iz_contact_pct"] = sav["iz_contact_percent"]

    # SEAGER proxy
    sav["swg_dec"] = (sav["z_swing_percent"] + (100 - sav["oz_swing_percent"])) / 2

    # merge with computed pull-air
    df = sav.merge(pa[["player_id", "bb_count", "pull_air_pct", "pull_fb_pct"]], on="player_id", how="left")
    return df


def zscore(s: pd.Series) -> pd.Series:
    return (s - s.mean()) / s.std(ddof=0)


def build_composite(df: pd.DataFrame) -> pd.DataFrame:
    q = df[(df["b_total_pa"] >= MIN_PA) & (df["bb_count"].fillna(0) >= MIN_BB)].copy()
    print(f"Qualified universe: {len(q)} hitters with >= {MIN_PA} PA and >= {MIN_BB} batted balls")

    q["z_ev"]      = zscore(q["exit_velocity_avg"])
    q["z_pullair"] = zscore(q["pull_air_pct"])
    q["z_izcon"]   = zscore(q["iz_contact_pct"])
    q["z_swgdec"]  = zscore(q["swg_dec"])

    # drop rows missing any z-component (can't fairly score)
    q = q.dropna(subset=["z_ev", "z_pullair", "z_izcon", "z_swgdec"]).copy()

    q["composite_z"] = q[["z_ev", "z_pullair", "z_izcon", "z_swgdec"]].mean(axis=1)
    # min(z) — tells us the *weakest* dimension. An elite four-tool hitter has high min.
    q["min_z"] = q[["z_ev", "z_pullair", "z_izcon", "z_swgdec"]].min(axis=1)

    # rank metrics
    for c in ["z_ev", "z_pullair", "z_izcon", "z_swgdec", "composite_z", "min_z"]:
        rank_name = c.replace("z_", "rank_") if c.startswith("z_") else f"rank_{c}"
        q[rank_name] = q[c].rank(ascending=False, method="min").astype(int)

    return q.sort_values("composite_z", ascending=False).reset_index(drop=True)


# ---------- Visualizations ----------

def chart_bubble(q: pd.DataFrame):
    """4-D scatter:  x = SwgDec   y = EV   size = Z-Contact%   color = PullAir%"""
    fig, ax = plt.subplots(figsize=(13, 9))
    sizes = (q["iz_contact_pct"] - q["iz_contact_pct"].min()) ** 2 * 0.5 + 30
    sc = ax.scatter(q["swg_dec"], q["exit_velocity_avg"], s=sizes,
                    c=q["pull_air_pct"], cmap="viridis", alpha=0.55,
                    edgecolor="white", linewidth=0.4)
    cbar = plt.colorbar(sc, ax=ax, label="Pulled-Air %")
    ax.set_xlabel("Swing Decision  =  (Z-Swing% + (100 − O-Swing%)) / 2  →  SEAGER proxy")
    ax.set_ylabel("Average Exit Velocity (mph)")
    ax.set_title("Four-tool hitter map (2026 YTD)\n"
                 "X: swing decision   Y: exit velo   Bubble size: in-zone contact %   Color: pulled-air %",
                 fontweight="bold")

    # annotate top 12 composite + all Mets
    label_set = set(q.head(12)["player"].tolist())
    mets = q[q["player_id"].isin(load_mets_ids())]
    label_set.update(mets["player"].tolist())
    for _, r in q.iterrows():
        if r["player"] in label_set:
            color = METS_ORANGE if r["player"] in set(mets["player"]) else "black"
            ax.annotate(r["player"], (r["swg_dec"], r["exit_velocity_avg"]),
                        fontsize=8, color=color,
                        xytext=(4, 4), textcoords="offset points")

    # legend for size
    handles = []
    for sval, lbl in [(40, "75%"), (90, "85%"), (160, "92%")]:
        handles.append(plt.scatter([], [], s=sval, c="grey", alpha=0.6, edgecolor="white"))
    ax.legend(handles, ["Z-Contact ≈75%", "≈85%", "≈92%"], title="Bubble size", loc="upper left", framealpha=0.9)
    fig.tight_layout()
    fig.savefig(os.path.join(CHARTS, "08_four_tool_bubble.png"), dpi=140)
    plt.close(fig)


def load_mets_ids():
    return set(pd.read_csv(os.path.join(DATA, "mets_players_2026.csv"))["player_id"].tolist())


def chart_radar(q: pd.DataFrame, n: int = 10):
    """Radar chart for top-N composite hitters and Mets' best."""
    metrics = ["exit_velocity_avg", "pull_air_pct", "iz_contact_pct", "swg_dec"]
    labels  = ["Exit Velo (mph)", "Pulled-Air %", "Z-Contact %", "Swing Decision"]

    # normalize each axis 0-1 across the qualified universe
    norm = pd.DataFrame()
    for m in metrics:
        norm[m] = (q[m] - q[m].min()) / (q[m].max() - q[m].min())

    angles = np.linspace(0, 2 * math.pi, len(metrics), endpoint=False).tolist()
    angles += angles[:1]

    top = q.head(n)
    mets_ids = load_mets_ids()
    mets_best = q[q["player_id"].isin(mets_ids)].sort_values("composite_z", ascending=False).head(2)

    fig, axes = plt.subplots(1, 2, figsize=(14, 7), subplot_kw=dict(polar=True))

    # Panel A: top 10 composite hitters
    ax = axes[0]
    for i, (idx, row) in enumerate(top.iterrows()):
        vals = norm.loc[idx, metrics].tolist()
        vals += vals[:1]
        ax.plot(angles, vals, label=row["player"], linewidth=1.5, alpha=0.7)
    ax.set_xticks(angles[:-1]); ax.set_xticklabels(labels)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0]); ax.set_yticklabels(["25", "50", "75", "100"])
    ax.set_ylim(0, 1.05)
    ax.set_title(f"Top-{n} four-tool hitters (composite z)", fontweight="bold", pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.4, 1.0), fontsize=8)

    # Panel B: best Mets vs MLB elite reference player
    ax = axes[1]
    ref = top.iloc[0]
    show_rows = pd.concat([top.iloc[[0]], mets_best])
    colors = ["#888"] + [METS_ORANGE, METS_BLUE]
    for color, (_, row) in zip(colors, show_rows.iterrows()):
        idx = row.name
        vals = norm.loc[idx, metrics].tolist()
        vals += vals[:1]
        ax.plot(angles, vals, label=row["player"], linewidth=2.4, color=color, alpha=0.85)
        ax.fill(angles, vals, alpha=0.10, color=color)
    ax.set_xticks(angles[:-1]); ax.set_xticklabels(labels)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0]); ax.set_yticklabels(["25", "50", "75", "100"])
    ax.set_ylim(0, 1.05)
    ax.set_title("Best Mets vs MLB top hitter", fontweight="bold", pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.4, 1.0), fontsize=9)

    fig.tight_layout()
    fig.savefig(os.path.join(CHARTS, "09_four_tool_radar.png"), dpi=140, bbox_inches="tight")
    plt.close(fig)


def chart_parallel(q: pd.DataFrame, n: int = 30):
    """Parallel coordinates for top N composite hitters + Mets."""
    metrics = ["exit_velocity_avg", "pull_air_pct", "iz_contact_pct", "swg_dec"]
    labels = ["Exit Velo", "Pulled-Air %", "Z-Contact %", "Swing Dec"]
    mets_ids = load_mets_ids()

    norm = pd.DataFrame(index=q.index)
    for m in metrics:
        norm[m] = (q[m] - q[m].min()) / (q[m].max() - q[m].min())

    fig, ax = plt.subplots(figsize=(13, 7))
    x = np.arange(len(metrics))
    # gray background for everyone
    for _, row in q.iterrows():
        ax.plot(x, norm.loc[row.name, metrics].tolist(), color="#d0d0d0", linewidth=0.7, alpha=0.6, zorder=1)
    # top-N
    top = q.head(n)
    for i, (_, row) in enumerate(top.iterrows()):
        c = plt.cm.plasma(i / max(n - 1, 1))
        ax.plot(x, norm.loc[row.name, metrics].tolist(), color=c, linewidth=1.6, alpha=0.85, zorder=3)
        if i < 8:
            ax.text(x[-1] + 0.02, norm.loc[row.name, metrics[-1]], row["player"],
                    fontsize=8, color=c, va="center")
    # Mets in orange
    mets = q[q["player_id"].isin(mets_ids)]
    for _, row in mets.iterrows():
        ax.plot(x, norm.loc[row.name, metrics].tolist(),
                color=METS_ORANGE, linewidth=2.2, alpha=0.95, zorder=4)
        ax.text(x[-1] + 0.02, norm.loc[row.name, metrics[-1]], row["player"],
                fontsize=8, color=METS_ORANGE, va="center", fontweight="bold")

    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylabel("Percentile within qualified hitters (0-1)")
    ax.set_title(f"Parallel coordinates — top {n} composite + all Mets (orange)", fontweight="bold")
    ax.set_ylim(-0.02, 1.02)
    ax.set_xlim(-0.1, len(metrics) - 1 + 0.6)
    fig.tight_layout()
    fig.savefig(os.path.join(CHARTS, "10_four_tool_parallel.png"), dpi=140)
    plt.close(fig)


def chart_heatmap(q: pd.DataFrame, n: int = 30):
    """Heatmap of percentile rank for top-N + every Met."""
    mets_ids = load_mets_ids()
    top = q.head(n).copy()
    mets = q[q["player_id"].isin(mets_ids) & ~q["player_id"].isin(top["player_id"])]
    show = pd.concat([top, mets]).reset_index(drop=True)

    cols = ["exit_velocity_avg", "pull_air_pct", "iz_contact_pct", "swg_dec"]
    labels = ["Exit Velo", "Pulled-Air %", "Z-Contact %", "Swing Dec"]
    pct = pd.DataFrame()
    for c in cols:
        pct[c] = q[c].rank(pct=True) * 100
    pct["player_id"] = q["player_id"].values
    pct["player"] = q["player"].values
    pct = pct.merge(show[["player_id", "composite_z"]], on="player_id")
    pct = pct.sort_values("composite_z", ascending=False).reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(10, max(6, 0.27 * len(pct))))
    M = pct[cols].values
    im = ax.imshow(M, aspect="auto", cmap="RdYlGn", vmin=0, vmax=100)
    ax.set_xticks(range(len(cols))); ax.set_xticklabels(labels)
    ax.set_yticks(range(len(pct)))
    yticks = []
    for _, r in pct.iterrows():
        is_met = r["player_id"] in mets_ids
        yticks.append(("● " if is_met else "  ") + r["player"])
    ax.set_yticklabels(yticks, fontsize=8)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            ax.text(j, i, f"{M[i, j]:.0f}", ha="center", va="center", fontsize=7,
                    color="black" if 25 < M[i, j] < 75 else "white")
    ax.set_title(f"Percentile rank — top {n} composite + Mets hitters", fontweight="bold")
    plt.colorbar(im, ax=ax, label="Percentile rank (100 = best)")
    fig.tight_layout()
    fig.savefig(os.path.join(CHARTS, "11_four_tool_heatmap.png"), dpi=140)
    plt.close(fig)


# ---------- Main ----------

if __name__ == "__main__":
    df = load_inputs()
    q = build_composite(df)

    out = os.path.join(DATA, "four_tool_2026.csv")
    cols_out = ["player", "player_id", "b_total_pa", "bb_count",
                "exit_velocity_avg", "pull_air_pct", "iz_contact_pct", "swg_dec",
                "z_ev", "z_pullair", "z_izcon", "z_swgdec",
                "composite_z", "min_z",
                "rank_ev", "rank_pullair", "rank_izcon", "rank_swgdec", "rank_composite_z", "rank_min_z",
                "z_swing_percent", "oz_swing_percent", "iz_contact_percent",
                "woba", "xwoba", "barrel_batted_rate", "hard_hit_percent"]
    q[cols_out].to_csv(out, index=False)

    print("\n" + "=" * 100)
    print("TOP 25 COMPOSITE FOUR-TOOL HITTERS  (2026 YTD)")
    print("=" * 100)
    show = q.head(25)[["player", "b_total_pa", "exit_velocity_avg", "pull_air_pct", "iz_contact_pct", "swg_dec",
                       "composite_z", "min_z", "woba", "xwoba"]]
    print(show.to_string(index=False))

    for thresh, label in [(0.5, "ELITE  (>= +0.5 SD on every dim)"),
                          (0.25, "STRONG (>= +0.25 SD on every dim)"),
                          (0.0,  "WELL-ROUNDED (>= 0 SD on every dim)")]:
        print("\n" + "=" * 100)
        print(f"'{label}'")
        print("=" * 100)
        sub = q[(q["z_ev"] >= thresh) & (q["z_pullair"] >= thresh) &
                (q["z_izcon"] >= thresh) & (q["z_swgdec"] >= thresh)].copy()
        sub = sub.sort_values("composite_z", ascending=False)
        print(f"{len(sub)} of {len(q)} qualified hitters meet all 4 thresholds:")
        print(sub[["player", "b_total_pa", "exit_velocity_avg", "pull_air_pct",
                   "iz_contact_pct", "swg_dec", "composite_z", "min_z", "woba", "xwoba"]].to_string(index=False))
        if thresh == 0.25:
            sub.to_csv(os.path.join(DATA, "four_tool_elite_2026.csv"), index=False)

    print("\n" + "=" * 100)
    print("METS HITTERS — composite ranking (universe = qualified hitters)")
    print("=" * 100)
    mets_ids = load_mets_ids()
    mets = q[q["player_id"].isin(mets_ids)].sort_values("composite_z", ascending=False)
    print(mets[["player", "b_total_pa", "exit_velocity_avg", "pull_air_pct",
                "iz_contact_pct", "swg_dec", "composite_z",
                "rank_composite_z"]].to_string(index=False))

    chart_bubble(q)
    chart_radar(q, n=10)
    chart_parallel(q, n=30)
    chart_heatmap(q, n=30)
    print("\nWrote:")
    for f in ["08_four_tool_bubble.png", "09_four_tool_radar.png",
              "10_four_tool_parallel.png", "11_four_tool_heatmap.png"]:
        print("  charts/" + f)
