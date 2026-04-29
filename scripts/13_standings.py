"""Pull 2026 standings and compute run differential / pythagorean to flag
'underperforming' teams (sellers / rebuilders).
"""
import os
import pandas as pd
from lib import get_json

DATA = os.path.join(os.path.dirname(__file__), "..", "data")


def standings(season: int) -> pd.DataFrame:
    data = get_json(
        "https://statsapi.mlb.com/api/v1/standings",
        params={"leagueId": "103,104", "season": season, "standingsTypes": "regularSeason"},
    )
    rows = []
    for rec in data.get("records", []):
        for tr in rec.get("teamRecords", []):
            rs = int(tr.get("runsScored") or tr.get("runs") or 0)
            ra = int(tr.get("runsAllowed") or 0)
            rows.append({
                "team": tr["team"]["name"],
                "team_id": tr["team"]["id"],
                "league_id": rec.get("league", {}).get("id"),
                "division_id": rec.get("division", {}).get("id"),
                "w": tr["wins"], "l": tr["losses"],
                "pct": float(tr["winningPercentage"]),
                "gb": tr.get("gamesBack", "-"),
                "rs": rs, "ra": ra, "diff": rs - ra,
            })
    df = pd.DataFrame(rows)
    df["g"] = df["w"] + df["l"]
    df["pyth_pct"] = df["rs"] ** 2 / (df["rs"] ** 2 + df["ra"] ** 2 + 1e-9)
    df["luck"] = df["pct"] - df["pyth_pct"]
    df = df.sort_values("pct", ascending=False).reset_index(drop=True)
    return df


if __name__ == "__main__":
    df = standings(2026)
    df.to_csv(os.path.join(DATA, "standings_2026.csv"), index=False)
    print(df.to_string(index=False))
    print()

    # Underperforming = bottom 12 by win pct OR by run diff (whichever broader)
    # We want sellers / rebuilders we could plausibly trade with.
    df["bottom_pct"] = df["pct"].rank(ascending=True, method="min").astype(int) <= 12
    df["bottom_diff"] = df["diff"].rank(ascending=True, method="min").astype(int) <= 12
    df["seller_candidate"] = df["bottom_pct"] | df["bottom_diff"]
    df["seller_candidate"] = df["seller_candidate"] & ~df["team"].isin(["New York Mets"])  # exclude self
    sellers = df[df["seller_candidate"]].sort_values("pct")
    print("\n>>> Underperforming teams (bottom-12 in either W% or run diff):")
    print(sellers[["team", "w", "l", "pct", "rs", "ra", "diff", "pyth_pct"]].to_string(index=False))

    df.to_csv(os.path.join(DATA, "standings_2026.csv"), index=False)
