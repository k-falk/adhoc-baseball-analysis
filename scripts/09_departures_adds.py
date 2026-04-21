"""Identify which 2025 Mets hitters are no longer on the team, and new additions."""
import os
import pandas as pd
from lib import get_json

DATA = os.path.join(os.path.dirname(__file__), "..", "data")


def player_team_2026(player_id: int) -> str | None:
    try:
        data = get_json(
            f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats",
            params={"stats": "season", "group": "hitting", "season": 2026, "gameType": "R"},
        )
    except Exception:
        return "UNKNOWN"
    splits = []
    for s in data.get("stats", []):
        splits.extend(s.get("splits", []))
    if not splits:
        return None  # not active
    # last split (most recent team)
    teams = [sp.get("team", {}).get("name") for sp in splits if sp.get("team")]
    return teams[-1] if teams else None


if __name__ == "__main__":
    m25 = pd.read_csv(os.path.join(DATA, "mets_players_2025.csv"))
    m26 = pd.read_csv(os.path.join(DATA, "mets_players_2026.csv"))

    returnees = set(m25["player_id"]) & set(m26["player_id"])
    departed = set(m25["player_id"]) - set(m26["player_id"])
    new_adds = set(m26["player_id"]) - set(m25["player_id"])

    # departures with PA + where they are now
    dep_df = m25[m25["player_id"].isin(departed)].copy()
    dep_df["team_2026"] = dep_df["player_id"].apply(player_team_2026)
    dep_df = dep_df[["player", "pos", "pa", "hr", "rbi", "ops", "team_2026"]].sort_values("pa", ascending=False)

    add_df = m26[m26["player_id"].isin(new_adds)][["player", "pos", "pa", "hr", "rbi", "ops"]].sort_values("pa", ascending=False)

    dep_df.to_csv(os.path.join(DATA, "mets_departures.csv"), index=False)
    add_df.to_csv(os.path.join(DATA, "mets_additions.csv"), index=False)

    print("=" * 90)
    print("2025 Mets hitters NO LONGER with the Mets in 2026")
    print("=" * 90)
    print(dep_df.to_string(index=False))
    print(f"\nLost WAR-equivalent offense (2025 totals): PA={dep_df['pa'].sum()}  HR={dep_df['hr'].sum()}  RBI={dep_df['rbi'].sum()}")

    print("\n" + "=" * 90)
    print("NEW additions to Mets in 2026 (hitters only)")
    print("=" * 90)
    print(add_df.to_string(index=False))
