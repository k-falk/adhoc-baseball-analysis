"""Pull Baseball Savant leaderboard (Statcast) for all batters, 2026 & 2025.

We pull a wide set of quality-of-contact and plate discipline fields so we can
merge with Mets roster later.
"""
import os
import pandas as pd
from lib import get_csv

DATA = os.path.join(os.path.dirname(__file__), "..", "data")

# All interesting Savant custom leaderboard fields
SELECTIONS = ",".join([
    "b_total_pa", "b_ab", "b_total_hits", "b_home_run", "b_rbi",
    "b_k_percent", "b_bb_percent",
    "batting_avg", "on_base_percent", "slg_percent", "on_base_plus_slg",
    "isolated_power",
    "xba", "xslg", "xwoba", "xobp", "woba",
    "exit_velocity_avg", "launch_angle_avg", "sweet_spot_percent",
    "barrel_batted_rate", "hard_hit_percent",
    "z_swing_percent", "oz_swing_percent", "whiff_percent",
    "swing_percent", "meatball_swing_percent",
    "in_zone_swing_miss_percent", "out_zone_swing_miss_percent",
    "pull_percent", "straightaway_percent", "opposite_percent",
    "groundballs_percent", "flyballs_percent", "linedrives_percent", "popups_percent",
    "babip",
])


def savant_batter_leaderboard(year: int, min_pa: int = 1) -> pd.DataFrame:
    # Savant "custom leaderboard" as CSV
    url = (
        "https://baseballsavant.mlb.com/leaderboard/custom"
        f"?year={year}&type=batter&filter=&sort=1&sortDir=desc&min={min_pa}"
        f"&selections={SELECTIONS}&chart=false&x=b_total_pa&y=b_total_pa&r=no&chartType=beeswarm&csv=true"
    )
    df = get_csv(url)
    # normalize name col
    if "last_name, first_name" in df.columns:
        df["player"] = df["last_name, first_name"].apply(
            lambda s: " ".join(reversed([p.strip() for p in str(s).split(",")])) if isinstance(s, str) else s
        )
    return df


if __name__ == "__main__":
    for year in (2026, 2025):
        df = savant_batter_leaderboard(year, min_pa=1)
        out = os.path.join(DATA, f"savant_batters_{year}.csv")
        df.to_csv(out, index=False)
        print(f"[{year}] rows={len(df)} -> {out}")
