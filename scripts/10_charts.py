"""Generate charts for the audit report."""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
CHARTS = os.path.join(os.path.dirname(__file__), "..", "charts")
os.makedirs(CHARTS, exist_ok=True)

plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "axes.grid": True, "grid.alpha": 0.25,
    "font.size": 10,
})
METS_BLUE = "#002D72"
METS_ORANGE = "#FF5910"


# ---------- 1) League R/G bars, Mets highlighted ----------
def chart_runs_per_game():
    df = pd.read_csv(os.path.join(DATA, "team_hitting_2026.csv"))
    df = df.sort_values("r_per_g", ascending=True)
    colors = [METS_ORANGE if "Mets" in t else "#4C72B0" for t in df["team"]]
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(df["team"], df["r_per_g"], color=colors)
    ax.set_xlabel("Runs scored per game (2026, thru Apr 21)")
    ax.set_title("MLB Runs Per Game — Mets are dead last", fontweight="bold")
    for i, (t, v) in enumerate(zip(df["team"], df["r_per_g"])):
        ax.text(v + 0.05, i, f"{v:.2f}", va="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(CHARTS, "01_runs_per_game.png"), dpi=140)
    plt.close(fig)


# ---------- 2) Mets team OPS 2025 vs 2026 by split ----------
def chart_splits_yoy():
    s25 = pd.read_csv(os.path.join(DATA, "team_splits_2025.csv"))
    s26 = pd.read_csv(os.path.join(DATA, "team_splits_2026.csv"))
    s25 = s25[s25["team"].str.contains("Mets")]
    s26 = s26[s26["team"].str.contains("Mets")]
    labels = {"risp": "RISP", "r10": "RISP, 2 out", "lc": "Late & close", "b1": "Bases empty", "b2": "Men on"}
    x = list(labels.keys())
    y25 = [float(s25[s25["split"] == k]["ops"].iloc[0]) if len(s25[s25["split"] == k]) else 0 for k in x]
    y26 = [float(s26[s26["split"] == k]["ops"].iloc[0]) if len(s26[s26["split"] == k]) else 0 for k in x]
    fig, ax = plt.subplots(figsize=(9, 5))
    idx = np.arange(len(x))
    w = 0.38
    ax.bar(idx - w/2, y25, w, label="2025 full season", color="#888")
    ax.bar(idx + w/2, y26, w, label="2026 YTD", color=METS_ORANGE)
    ax.set_xticks(idx); ax.set_xticklabels([labels[k] for k in x])
    ax.set_ylabel("OPS")
    ax.set_title("Mets OPS by situation: 2025 vs 2026", fontweight="bold")
    ax.legend()
    for i, v in enumerate(y25):
        ax.text(i - w/2, v + 0.008, f"{v:.3f}", ha="center", fontsize=8)
    for i, v in enumerate(y26):
        ax.text(i + w/2, v + 0.008, f"{v:.3f}", ha="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(CHARTS, "02_splits_yoy.png"), dpi=140)
    plt.close(fig)


# ---------- 3) Returnee Mets: xwOBA 2025 vs 2026 ----------
def chart_yoy_returnees():
    d25 = pd.read_csv(os.path.join(DATA, "mets_savant_2025.csv"))
    d26 = pd.read_csv(os.path.join(DATA, "mets_savant_2026.csv"))
    m = d25.merge(d26, on="player_id", suffixes=("_25", "_26"))
    m = m[m["pa_26"] >= 20].sort_values("pa_26", ascending=False).reset_index(drop=True)
    players = m["player_26"]
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    for ax, metric, title in [
        (axes[0], "xwoba", "Expected wOBA"),
        (axes[1], "barrel_batted_rate", "Barrel %"),
        (axes[2], "hard_hit_percent", "Hard-Hit %"),
    ]:
        y25 = m[f"{metric}_25"]
        y26 = m[f"{metric}_26"]
        idx = np.arange(len(players))
        w = 0.4
        ax.bar(idx - w/2, y25, w, label="2025 full yr", color="#888")
        ax.bar(idx + w/2, y26, w, label="2026 YTD", color=METS_ORANGE)
        ax.set_xticks(idx); ax.set_xticklabels(players, rotation=35, ha="right")
        ax.set_title(title, fontweight="bold")
        ax.legend()
    fig.suptitle("Returning Mets hitters: quality-of-contact regression", fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig(os.path.join(CHARTS, "03_returnees_yoy.png"), dpi=140, bbox_inches="tight")
    plt.close(fig)


# ---------- 4) Plate discipline regression: chase rate + whiff ----------
def chart_discipline():
    d25 = pd.read_csv(os.path.join(DATA, "mets_savant_2025.csv"))
    d26 = pd.read_csv(os.path.join(DATA, "mets_savant_2026.csv"))
    m = d25.merge(d26, on="player_id", suffixes=("_25", "_26"))
    m = m[m["pa_26"] >= 20].sort_values("pa_26", ascending=False).reset_index(drop=True)
    players = m["player_26"]
    idx = np.arange(len(players))
    w = 0.38
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    axes[0].bar(idx - w/2, m["oz_swing_percent_25"], w, label="2025", color="#888")
    axes[0].bar(idx + w/2, m["oz_swing_percent_26"], w, label="2026", color=METS_ORANGE)
    axes[0].set_title("Chase rate (O-Swing%)", fontweight="bold")
    axes[0].set_xticks(idx); axes[0].set_xticklabels(players, rotation=35, ha="right")
    axes[0].legend()

    axes[1].bar(idx - w/2, m["whiff_percent_25"], w, label="2025", color="#888")
    axes[1].bar(idx + w/2, m["whiff_percent_26"], w, label="2026", color=METS_ORANGE)
    axes[1].set_title("Whiff rate (% of swings missed)", fontweight="bold")
    axes[1].set_xticks(idx); axes[1].set_xticklabels(players, rotation=35, ha="right")
    axes[1].legend()
    fig.suptitle("Plate discipline regression for returning Mets hitters", fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig(os.path.join(CHARTS, "04_discipline_yoy.png"), dpi=140, bbox_inches="tight")
    plt.close(fig)


# ---------- 5) Team expected vs actual wOBA ----------
def chart_team_xwoba():
    df = pd.read_csv(os.path.join(DATA, "team_expected_2026.csv")).copy()
    df = df.sort_values("est_woba", ascending=True)
    colors = [METS_ORANGE if t == "Mets" else "#4C72B0" for t in df["team"]]
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(df["team"], df["est_woba"], color=colors, alpha=0.6, label="Expected wOBA")
    ax.plot(df["woba"], df["team"], "o", color="black", markersize=5, label="Actual wOBA")
    ax.set_title("Team offense: expected vs actual wOBA (2026)", fontweight="bold")
    ax.set_xlabel("wOBA")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(CHARTS, "05_team_xwoba.png"), dpi=140)
    plt.close(fig)


# ---------- 6) Runs scored — 2025 vs 2026 for every team (rank change) ----------
def chart_rank_change():
    a = pd.read_csv(os.path.join(DATA, "team_hitting_2025.csv"))[["team", "r_per_g"]].rename(columns={"r_per_g": "rpg_25"})
    b = pd.read_csv(os.path.join(DATA, "team_hitting_2026.csv"))[["team", "r_per_g"]].rename(columns={"r_per_g": "rpg_26"})
    m = a.merge(b, on="team")
    m["delta"] = m["rpg_26"] - m["rpg_25"]
    m = m.sort_values("delta")
    colors = [METS_ORANGE if t == "New York Mets" else "#4C72B0" for t in m["team"]]
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(m["team"], m["delta"], color=colors)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_title("R/G change from 2025 → 2026 (YTD)", fontweight="bold")
    ax.set_xlabel("Runs per game change (2026 YTD − 2025 full season)")
    for i, (t, v) in enumerate(zip(m["team"], m["delta"])):
        ax.text(v + (0.03 if v >= 0 else -0.03), i, f"{v:+.2f}", va="center", ha="left" if v >= 0 else "right", fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(CHARTS, "06_rank_change.png"), dpi=140)
    plt.close(fig)


# ---------- 7) Departures vs additions offense impact ----------
def chart_departures_additions():
    dep = pd.read_csv(os.path.join(DATA, "mets_departures.csv"))
    add = pd.read_csv(os.path.join(DATA, "mets_additions.csv"))
    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    d = dep.nlargest(8, "pa")
    axes[0].barh(d["player"], d["ops"], color="#888")
    axes[0].set_title("Departed hitters — 2025 OPS (top 8 by PA)", fontweight="bold")
    axes[0].set_xlabel("2025 OPS")
    axes[0].invert_yaxis()
    for i, (p, o, pa) in enumerate(zip(d["player"], d["ops"], d["pa"])):
        axes[0].text(o + 0.01, i, f"{o:.3f} ({pa} PA)", va="center", fontsize=9)
    axes[0].set_xlim(0, 1.0)

    a = add.nlargest(6, "pa")
    axes[1].barh(a["player"], a["ops"], color=METS_ORANGE)
    axes[1].set_title("New additions — 2026 YTD OPS", fontweight="bold")
    axes[1].set_xlabel("2026 YTD OPS")
    axes[1].invert_yaxis()
    for i, (p, o, pa) in enumerate(zip(a["player"], a["ops"], a["pa"])):
        axes[1].text(o + 0.01, i, f"{o:.3f} ({pa} PA)", va="center", fontsize=9)
    axes[1].set_xlim(0, 1.2)

    fig.suptitle("Roster churn: who left vs who arrived", fontweight="bold")
    fig.tight_layout()
    fig.savefig(os.path.join(CHARTS, "07_roster_churn.png"), dpi=140, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    chart_runs_per_game()
    chart_splits_yoy()
    chart_yoy_returnees()
    chart_discipline()
    chart_team_xwoba()
    chart_rank_change()
    chart_departures_additions()
    print("Charts written:")
    for p in sorted(os.listdir(CHARTS)):
        print("  ", p)
