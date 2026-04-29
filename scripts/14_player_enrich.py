"""Enrich the 2026 batter universe with team, age, and primary position
from the MLB Stats API people endpoint.
"""
import os, time
import pandas as pd
from datetime import date
from lib import get_json

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
TODAY = date(2026, 4, 29)


def people_lookup(player_ids: list[int]) -> pd.DataFrame:
    """Batch /people endpoint up to ~100 ids per call."""
    rows = []
    for i in range(0, len(player_ids), 100):
        batch = player_ids[i:i + 100]
        ids = ",".join(str(x) for x in batch)
        try:
            data = get_json(f"https://statsapi.mlb.com/api/v1/people", params={"personIds": ids})
        except Exception as e:
            print(f"  !! batch {i}: {e}")
            continue
        for p in data.get("people", []):
            bdate = p.get("birthDate")
            age = None
            if bdate:
                bd = date.fromisoformat(bdate)
                age = (TODAY - bd).days / 365.25
            current_team = (p.get("currentTeam") or {}).get("name")
            current_team_id = (p.get("currentTeam") or {}).get("id")
            primary_pos = (p.get("primaryPosition") or {}).get("abbreviation", "")
            rows.append({
                "player_id": p["id"],
                "full_name": p.get("fullName"),
                "birth_date": bdate,
                "age": round(age, 2) if age is not None else None,
                "primary_position": primary_pos,
                "current_team": current_team,
                "current_team_id": current_team_id,
                "bats": p.get("batSide", {}).get("code"),
                "throws": p.get("pitchHand", {}).get("code"),
                "mlb_debut": p.get("mlbDebutDate"),
            })
        time.sleep(0.2)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    sav = pd.read_csv(os.path.join(DATA, "savant_batters_2026.csv"))
    ids = sav["player_id"].dropna().astype(int).unique().tolist()
    print(f"looking up {len(ids)} players...")
    info = people_lookup(ids)
    info.to_csv(os.path.join(DATA, "player_info_2026.csv"), index=False)
    print(f"wrote data/player_info_2026.csv  rows={len(info)}")
    print(info.head(15).to_string(index=False))
