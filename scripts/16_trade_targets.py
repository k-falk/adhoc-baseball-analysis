"""Build a Mets trade-target board.

Filters:
  - Position primary in {1B, 2B, 3B, DH}
  - Age < 31 (as of 2026-04-29)
  - On an underperforming team (W% < .500 AND run diff < 0)
  - Min 50 PA in 2026 (qualified for our four-tool composite)
"""
import os
import pandas as pd

DATA = os.path.join(os.path.dirname(__file__), "..", "data")


def main():
    sav = pd.read_csv(os.path.join(DATA, "savant_batters_2026.csv"))
    info = pd.read_csv(os.path.join(DATA, "player_info_2026.csv"))
    rosters = pd.read_csv(os.path.join(DATA, "rosters_2026_dedup.csv"))
    standings = pd.read_csv(os.path.join(DATA, "standings_2026.csv"))
    four = pd.read_csv(os.path.join(DATA, "four_tool_2026.csv"))
    pull_air = pd.read_csv(os.path.join(DATA, "savant_pull_air_2026.csv"))

    # underperforming teams: under .500 and negative run diff
    standings["under"] = (standings["pct"] < 0.500) & (standings["diff"] < 0)
    # exclude the Mets themselves
    standings.loc[standings["team"] == "Mets", "under"] = False
    # show what we picked
    print("Underperforming target teams (W% < .500 AND run diff < 0):")
    print(standings[standings["under"]][["team", "w", "l", "pct", "rs", "ra", "diff"]].to_string(index=False))

    target_team_ids = set(standings.loc[standings["under"], "team_id"])

    # build merged candidate table
    name_col = "last_name, first_name"
    sav["player"] = sav[name_col].apply(
        lambda s: " ".join(reversed([p.strip() for p in str(s).split(",")])) if isinstance(s, str) else s
    )
    base = sav[["player_id", "player", "b_total_pa", "exit_velocity_avg",
                "iz_contact_percent", "z_swing_percent", "oz_swing_percent",
                "barrel_batted_rate", "hard_hit_percent", "woba", "xwoba", "xslg"]]
    base = base.merge(info[["player_id", "age", "primary_position", "bats", "mlb_debut"]], on="player_id", how="left")
    base = base.merge(rosters[["player_id", "team", "team_id", "team_abbr"]], on="player_id", how="left")
    base = base.merge(pull_air[["player_id", "pull_air_pct", "bb_count"]], on="player_id", how="left")
    base = base.merge(four[["player_id", "composite_z", "min_z", "rank_composite_z",
                            "z_ev", "z_pullair", "z_izcon", "z_swgdec"]], on="player_id", how="left")

    # 4-tool ingredients (already in base)
    base["swg_dec"] = (base["z_swing_percent"] + (100 - base["oz_swing_percent"])) / 2

    # filter
    base["pos_match"] = base["primary_position"].isin(["1B", "2B", "3B", "DH"])
    base["age_ok"] = base["age"] < 31
    base["pa_ok"] = base["b_total_pa"] >= 50
    base["team_ok"] = base["team_id"].isin(target_team_ids)
    candidates = base[base["pos_match"] & base["age_ok"] & base["pa_ok"] & base["team_ok"]].copy()

    print(f"\n{len(candidates)} candidates pass filter (pos=1B/2B/3B/DH, age<31, PA>=50, team underperforming)")
    show = ["player", "primary_position", "age", "team_abbr", "b_total_pa",
            "exit_velocity_avg", "pull_air_pct", "iz_contact_percent", "swg_dec",
            "composite_z", "rank_composite_z", "woba", "xwoba"]
    candidates = candidates.sort_values("composite_z", ascending=False)
    print(candidates[show].to_string(index=False))
    candidates.to_csv(os.path.join(DATA, "trade_candidates_2026.csv"), index=False)
    print("\nwrote data/trade_candidates_2026.csv")


if __name__ == "__main__":
    main()
