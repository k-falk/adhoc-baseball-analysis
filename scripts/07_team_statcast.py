"""Pull team-level Statcast batting data from Baseball Savant."""
import os
import pandas as pd
from lib import get_csv

DATA = os.path.join(os.path.dirname(__file__), "..", "data")


def expected_stats_team(year: int) -> pd.DataFrame:
    url = (
        "https://baseballsavant.mlb.com/leaderboard/expected_statistics"
        f"?type=batter-team&year={year}&position=&team=&filter=&csv=true"
    )
    return get_csv(url)


def statcast_team(year: int, metric: str) -> pd.DataFrame:
    """Generic per-team Statcast leaderboard (quality of contact, etc)."""
    # this endpoint returns team totals by rolling up batters
    url = (
        f"https://baseballsavant.mlb.com/statcast_search/csv?all=true"
        f"&hfPT=&hfAB=&hfGT=R%7C&hfPR=&hfZ=&stadium=&hfBBL=&hfNewZones=&hfPull=&hfC="
        f"&hfSea={year}%7C&hfSit=&player_type=batter&hfOuts=&hfOpponent="
        f"&pitcher_throws=&batter_stands=&hfSA=&game_date_gt=&game_date_lt="
        f"&hfMo=&hfTeam=&home_road=&hfRO=&position=&hfInfield=&team=&hfOutfield="
        f"&hfInn=&hfBBT=&hfFlag=&metric_1=&group_by={metric}&min_pitches=0&min_results=0"
        f"&min_pas=0&sort_col=pitches&player_event_sort=api_p_release_speed&sort_order=desc&type=details"
    )
    return get_csv(url, timeout=180)


if __name__ == "__main__":
    for year in (2026, 2025):
        df = expected_stats_team(year)
        out = os.path.join(DATA, f"team_expected_{year}.csv")
        df.to_csv(out, index=False)
        print(f"[{year}] team expected stats -> {out}  rows={len(df)}")
        df["woba_diff"] = df["woba"] - df["est_woba"]
        df["slg_diff"] = df["slg"] - df["est_slg"]
        df["ba_diff"] = df["ba"] - df["est_ba"]
        cols = ["team", "pa", "bip", "ba", "est_ba", "slg", "est_slg", "woba", "est_woba", "woba_diff"]
        df = df.sort_values("est_woba").reset_index(drop=True)
        df["est_woba_rank"] = df["est_woba"].rank(ascending=False, method="min").astype(int)
        df["woba_rank"] = df["woba"].rank(ascending=False, method="min").astype(int)
        print(df[cols + ["est_woba_rank", "woba_rank"]].to_string())
        mets = df[df["team"].isin(["Mets", "NYM"])]
        print(f"  >>> METS rank (est_wOBA): {int(mets.iloc[0]['est_woba_rank'])} of 30, (wOBA): {int(mets.iloc[0]['woba_rank'])}")
        print()
