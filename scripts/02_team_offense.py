"""Pull league-wide team hitting for 2026 (and 2025) and rank Mets."""
import os, sys, json
import pandas as pd
from lib import get_json

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATA, exist_ok=True)


def team_hitting(season: int) -> pd.DataFrame:
    data = get_json(
        "https://statsapi.mlb.com/api/v1/teams/stats",
        params={"season": season, "sportId": 1, "stats": "season", "group": "hitting"},
    )
    rows = []
    for s in data["stats"][0]["splits"]:
        team = s["team"]["name"]
        stat = s["stat"]
        rows.append({
            "season": season,
            "team": team,
            "g": stat.get("gamesPlayed"),
            "pa": stat.get("plateAppearances"),
            "ab": stat.get("atBats"),
            "r": stat.get("runs"),
            "h": stat.get("hits"),
            "2b": stat.get("doubles"),
            "3b": stat.get("triples"),
            "hr": stat.get("homeRuns"),
            "rbi": stat.get("rbi"),
            "bb": stat.get("baseOnBalls"),
            "so": stat.get("strikeOuts"),
            "sb": stat.get("stolenBases"),
            "avg": float(stat.get("avg", 0)),
            "obp": float(stat.get("obp", 0)),
            "slg": float(stat.get("slg", 0)),
            "ops": float(stat.get("ops", 0)),
            "babip": float(stat.get("babip", 0)) if stat.get("babip") not in (None, ".---") else None,
            "lob": stat.get("leftOnBase"),
            "gidp": stat.get("groundIntoDoublePlay"),
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    for season in (2026, 2025):
        df = team_hitting(season)
        df["r_per_g"] = df["r"] / df["g"]
        df["k_pct"] = df["so"] / df["pa"]
        df["bb_pct"] = df["bb"] / df["pa"]
        df["iso"] = df["slg"] - df["avg"]
        df["xbh_per_h"] = (df["2b"] + df["3b"] + df["hr"]) / df["h"]
        df = df.sort_values("r", ascending=True).reset_index(drop=True)
        df["r_rank"] = df["r"].rank(ascending=False, method="min").astype(int)
        df["rpg_rank"] = df["r_per_g"].rank(ascending=False, method="min").astype(int)
        df["ops_rank"] = df["ops"].rank(ascending=False, method="min").astype(int)
        df["wrc_proxy"] = df["ops"]  # placeholder; real wRC+ needs league context
        out = os.path.join(DATA, f"team_hitting_{season}.csv")
        df.to_csv(out, index=False)
        print(f"[{season}] wrote {out}  teams={len(df)}")
        print(df[["team", "g", "r", "r_per_g", "r_rank", "ops", "avg", "obp", "slg", "k_pct", "bb_pct", "iso"]].to_string())
        print()
        # highlight Mets
        mets = df[df["team"].str.contains("Mets")].iloc[0]
        print(f"  >>> NY METS {season}: R={mets['r']} ({mets['r_rank']}th of 30), R/G={mets['r_per_g']:.2f} (#{mets['rpg_rank']}), OPS={mets['ops']:.3f} (#{mets['ops_rank']})\n")
