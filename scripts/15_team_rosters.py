"""Pull each team's 2026 active+full-season roster to map player_id -> team."""
import os, time
import pandas as pd
from lib import get_json

DATA = os.path.join(os.path.dirname(__file__), "..", "data")


def all_team_rosters(season: int = 2026) -> pd.DataFrame:
    teams_data = get_json("https://statsapi.mlb.com/api/v1/teams",
                          params={"sportId": 1, "activeStatus": "ACTIVE", "season": season})
    rows = []
    for t in teams_data.get("teams", []):
        tid = t["id"]; tname = t["name"]; tabbr = t.get("abbreviation")
        try:
            r = get_json(f"https://statsapi.mlb.com/api/v1/teams/{tid}/roster",
                         params={"rosterType": "fullSeason", "season": season})
        except Exception as e:
            print(f"  !! {tname}: {e}")
            continue
        for player in r.get("roster", []):
            rows.append({
                "player_id": player["person"]["id"],
                "full_name": player["person"]["fullName"],
                "team": tname,
                "team_id": tid,
                "team_abbr": tabbr,
                "roster_pos": player.get("position", {}).get("abbreviation"),
                "status": player.get("status", {}).get("description"),
            })
        time.sleep(0.05)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = all_team_rosters(2026)
    df.to_csv(os.path.join(DATA, "rosters_2026.csv"), index=False)
    print(f"wrote rosters_2026.csv  rows={len(df)}")
    # if a player is on >1 roster (traded), keep most recent (last team in list iteration)
    df_dedup = df.drop_duplicates("player_id", keep="last")
    df_dedup.to_csv(os.path.join(DATA, "rosters_2026_dedup.csv"), index=False)
    print(f"  unique players: {len(df_dedup)}")
