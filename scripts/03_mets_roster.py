"""Pull 2026 Mets hitter stats + 2025 comparison via MLB Stats API.

Uses the team roster endpoint (rosterType=fullSeason) and pulls per-player
season hitting stats so that bench players are included, not only leaders.
"""
import os, time
import pandas as pd
from lib import get_json

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
METS_ID = 121


def mets_roster(season: int) -> list[dict]:
    # fullSeason gives everyone who appeared or is on the 40-man for that year
    data = get_json(
        f"https://statsapi.mlb.com/api/v1/teams/{METS_ID}/roster",
        params={"rosterType": "fullSeason", "season": season},
    )
    return data.get("roster", [])


def player_hitting(player_id: int, season: int) -> dict | None:
    data = get_json(
        f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats",
        params={"stats": "season", "group": "hitting", "season": season, "gameType": "R"},
    )
    splits = []
    for s in data.get("stats", []):
        splits.extend(s.get("splits", []))
    # find split belonging to Mets (in case they were traded)
    mets_split = next((s for s in splits if s.get("team", {}).get("id") == METS_ID), None)
    if mets_split is None:
        return None
    return mets_split["stat"]


def collect(season: int) -> pd.DataFrame:
    roster = mets_roster(season)
    rows = []
    for r in roster:
        pos = r.get("position", {}).get("abbreviation", "")
        if pos == "P":
            continue  # skip pitchers from hitting view
        pid = r["person"]["id"]
        name = r["person"]["fullName"]
        try:
            st = player_hitting(pid, season)
        except Exception as e:
            print(f"  !! {name} {season}: {e}")
            st = None
        if not st:
            continue
        if int(st.get("plateAppearances", 0) or 0) == 0:
            continue
        rows.append({
            "season": season,
            "player_id": pid,
            "player": name,
            "pos": pos,
            "g": int(st.get("gamesPlayed", 0) or 0),
            "pa": int(st.get("plateAppearances", 0) or 0),
            "ab": int(st.get("atBats", 0) or 0),
            "r": int(st.get("runs", 0) or 0),
            "h": int(st.get("hits", 0) or 0),
            "2b": int(st.get("doubles", 0) or 0),
            "3b": int(st.get("triples", 0) or 0),
            "hr": int(st.get("homeRuns", 0) or 0),
            "rbi": int(st.get("rbi", 0) or 0),
            "bb": int(st.get("baseOnBalls", 0) or 0),
            "so": int(st.get("strikeOuts", 0) or 0),
            "hbp": int(st.get("hitByPitch", 0) or 0),
            "sb": int(st.get("stolenBases", 0) or 0),
            "cs": int(st.get("caughtStealing", 0) or 0),
            "sf": int(st.get("sacFlies", 0) or 0),
            "gidp": int(st.get("groundIntoDoublePlay", 0) or 0),
            "avg": float(st.get("avg", 0) or 0),
            "obp": float(st.get("obp", 0) or 0),
            "slg": float(st.get("slg", 0) or 0),
            "ops": float(st.get("ops", 0) or 0),
            "babip": float(st.get("babip", 0) or 0) if st.get("babip") not in (None, ".---") else None,
            "lob": int(st.get("leftOnBase", 0) or 0),
        })
        time.sleep(0.05)
    df = pd.DataFrame(rows)
    df["iso"] = df["slg"] - df["avg"]
    df["k_pct"] = df["so"] / df["pa"]
    df["bb_pct"] = df["bb"] / df["pa"]
    df["xbh"] = df["2b"] + df["3b"] + df["hr"]
    df = df.sort_values("pa", ascending=False).reset_index(drop=True)
    return df


if __name__ == "__main__":
    for season in (2026, 2025):
        df = collect(season)
        out = os.path.join(DATA, f"mets_players_{season}.csv")
        df.to_csv(out, index=False)
        print(f"[{season}] wrote {out}  rows={len(df)}")
        cols = ["player", "pos", "g", "pa", "h", "hr", "rbi", "bb", "so", "avg", "obp", "slg", "ops", "iso", "k_pct", "bb_pct", "babip"]
        print(df[cols].head(25).to_string())
        print()
