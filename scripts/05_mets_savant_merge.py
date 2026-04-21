"""Merge Mets roster (MLB Stats API) with Savant leaderboard by player_id.

Produces mets_savant_2026.csv and mets_savant_2025.csv and a year-over-year
comparison table for any player who appeared in both years.
"""
import os
import pandas as pd

DATA = os.path.join(os.path.dirname(__file__), "..", "data")

KEEP_COLS = [
    "player_id", "player", "season", "pos", "g", "pa", "ab", "h", "hr", "rbi",
    "bb", "so", "avg", "obp", "slg", "ops", "iso", "k_pct", "bb_pct", "babip",
    # savant
    "xba", "xslg", "xwoba", "woba",
    "exit_velocity_avg", "launch_angle_avg", "sweet_spot_percent",
    "barrel_batted_rate", "hard_hit_percent",
    "z_swing_percent", "oz_swing_percent", "whiff_percent",
    "swing_percent", "meatball_swing_percent",
    "in_zone_swing_miss_percent", "out_zone_swing_miss_percent",
    "pull_percent", "straightaway_percent", "opposite_percent",
    "groundballs_percent", "flyballs_percent", "linedrives_percent",
    "popups_percent",
]


def merge_year(year: int) -> pd.DataFrame:
    roster = pd.read_csv(os.path.join(DATA, f"mets_players_{year}.csv"))
    sav = pd.read_csv(os.path.join(DATA, f"savant_batters_{year}.csv"))
    sav_core = sav.rename(columns={"player_id": "player_id"})
    merged = roster.merge(sav_core.drop(columns=[c for c in ["year", "player", "last_name, first_name"] if c in sav_core.columns]), on="player_id", how="left")
    # select + order
    cols = [c for c in KEEP_COLS if c in merged.columns]
    return merged[cols].sort_values("pa", ascending=False).reset_index(drop=True)


if __name__ == "__main__":
    d26 = merge_year(2026)
    d25 = merge_year(2025)
    d26.to_csv(os.path.join(DATA, "mets_savant_2026.csv"), index=False)
    d25.to_csv(os.path.join(DATA, "mets_savant_2025.csv"), index=False)

    pd.set_option("display.width", 240)
    pd.set_option("display.max_columns", 40)

    print("=" * 100)
    print("2026 Mets — core + Statcast")
    print("=" * 100)
    cols_show = ["player", "g", "pa", "hr", "avg", "obp", "slg", "ops",
                 "xba", "xslg", "xwoba", "barrel_batted_rate", "hard_hit_percent",
                 "exit_velocity_avg", "k_pct", "bb_pct", "whiff_percent", "oz_swing_percent"]
    print(d26[cols_show].to_string())
    print()
    print("=" * 100)
    print("2025 Mets — core + Statcast (regulars)")
    print("=" * 100)
    print(d25[cols_show].head(16).to_string())

    # yoy comparison for returnees
    print("\n" + "=" * 100)
    print("YEAR-OVER-YEAR for returning Mets (2025 vs 2026, season-to-date)")
    print("=" * 100)
    yoy = d25.merge(d26, on="player_id", suffixes=("_25", "_26"))
    yoy = yoy[yoy["pa_26"] >= 15].sort_values("pa_26", ascending=False)
    show = ["player_26", "pa_25", "pa_26",
            "ops_25", "ops_26",
            "xwoba_25", "xwoba_26",
            "barrel_batted_rate_25", "barrel_batted_rate_26",
            "hard_hit_percent_25", "hard_hit_percent_26",
            "whiff_percent_25", "whiff_percent_26",
            "oz_swing_percent_25", "oz_swing_percent_26",
            "k_pct_25", "k_pct_26",
            "bb_pct_25", "bb_pct_26"]
    print(yoy[show].to_string())

    out = os.path.join(DATA, "mets_yoy.csv")
    yoy[show].to_csv(out, index=False)
    print(f"\nwrote {out}")
