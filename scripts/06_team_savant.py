"""Pull team-level Savant leaderboard for quality of contact and plate discipline."""
import os
import pandas as pd
from lib import get_csv

DATA = os.path.join(os.path.dirname(__file__), "..", "data")

SELECTIONS = ",".join([
    "b_total_pa", "b_total_hits", "b_home_run",
    "batting_avg", "on_base_percent", "slg_percent", "on_base_plus_slg", "isolated_power",
    "xba", "xslg", "xwoba", "woba",
    "exit_velocity_avg", "launch_angle_avg", "sweet_spot_percent",
    "barrel_batted_rate", "hard_hit_percent",
    "z_swing_percent", "oz_swing_percent", "whiff_percent",
    "swing_percent", "meatball_swing_percent",
    "pull_percent", "opposite_percent",
    "groundballs_percent", "flyballs_percent", "linedrives_percent",
    "babip",
])


def savant_team(year: int) -> pd.DataFrame:
    # type=batter-team gives team-aggregated batter metrics
    url = (
        "https://baseballsavant.mlb.com/leaderboard/custom"
        f"?year={year}&type=batter-team&filter=&sort=1&sortDir=desc&min=1"
        f"&selections={SELECTIONS}&chart=false&x=b_total_pa&y=b_total_pa&r=no&chartType=beeswarm&csv=true"
    )
    return get_csv(url)


if __name__ == "__main__":
    for year in (2026, 2025):
        df = savant_team(year)
        out = os.path.join(DATA, f"savant_team_{year}.csv")
        df.to_csv(out, index=False)
        print(f"[{year}] rows={len(df)} cols={list(df.columns)}")

        # rank Mets
        name_col = [c for c in df.columns if "name" in c.lower() or c.lower() in ("entity_name", "team_name")]
        print(f"[{year}] name col candidates: {name_col}")
        print(df.head(5).to_string())
        print()
