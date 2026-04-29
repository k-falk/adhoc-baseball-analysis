"""Identify 2027 and 2028 free-agent class candidates at 1B/2B/3B/DH, age <31.

For free-agent signings the team filter doesn't apply (Mets can sign anyone),
so we relax to all 30 teams. We also note current team for context.

Years-of-control logic:
  - 2027 FA class = contract/team-control runs through end of 2026 season
                   (i.e. ~1 year of control as of 2026-04-29)
  - 2028 FA class = contract/team-control runs through end of 2027 season
                   (~2 years of control)

Service-time proxy: 6 - years_since_debut. Refined with hand-curated
overrides for known extensions and short-term deals.
"""
import os
import pandas as pd

DATA = os.path.join(os.path.dirname(__file__), "..", "data")

# Hand-curated overrides (from public sources as of late 2025 / early 2026).
# Maps player_id -> (last_year_of_control, note).
# IMPORTANT: ALWAYS verify against Spotrac before acting.
OVERRIDES = {
    # Long-term extensions: NOT FAs in 2027/2028
    665487: (2039, "Vlad Jr.: 14yr/$500M ext through 2039"),
    646240: (2033, "Devers: 10yr/$313M ext"),
    687093: (2031, "Pasquantino: 7yr/$50M ext through 2031"),
    670541: (2029, "Yordan Alvarez: 6yr/$115M ext through 2028 + opt"),
    665487: (2039, "Vlad Jr."),
    600474: (2030, "Ozzie Albies: extended"),
    # Short-term deals (likely 2027 FA class)
    665161: (2026, "Yoán Moncada: 1yr LAA deal"),
    663697: (2026, "Jonathan India: arb-3, FA after 2026"),
    676612: (2026, "Luis Arraez: arb-3, FA after 2026"),
    641933: (2026, "Andrew Vaughn: arb, FA after 2026"),
    # FA after 2027 (2028 FA class) — known
    656333: (2027, "Isaac Paredes: arb path, FA after 2027"),
    665859: (2027, "Spencer Torkelson: arb path, FA after 2027"),
    668800: (2030, "Kazuma Okamoto: posting deal multi-yr"),
    700834: (2031, "Munetaka Murakami: posting deal"),
    665862: (2027, "Jazz Chisholm Jr: FA after 2027"),
    # 30+ in 2026 already excluded by age filter
}


def main():
    sav = pd.read_csv(os.path.join(DATA, "savant_batters_2026.csv"))
    info = pd.read_csv(os.path.join(DATA, "player_info_2026.csv"))
    rosters = pd.read_csv(os.path.join(DATA, "rosters_2026_dedup.csv"))
    four = pd.read_csv(os.path.join(DATA, "four_tool_2026.csv"))
    pull_air = pd.read_csv(os.path.join(DATA, "savant_pull_air_2026.csv"))

    sav["player"] = sav["last_name, first_name"].apply(
        lambda s: " ".join(reversed([p.strip() for p in str(s).split(",")])) if isinstance(s, str) else s
    )

    base = sav[["player_id", "player", "b_total_pa", "exit_velocity_avg",
                "iz_contact_percent", "z_swing_percent", "oz_swing_percent",
                "barrel_batted_rate", "hard_hit_percent", "woba", "xwoba", "xslg"]]
    base = base.merge(info[["player_id", "age", "primary_position", "bats", "mlb_debut", "yrs_since_debut", "est_yrs_to_fa"]], on="player_id", how="left")
    base = base.merge(rosters[["player_id", "team_abbr"]], on="player_id", how="left")
    base = base.merge(pull_air[["player_id", "pull_air_pct"]], on="player_id", how="left")
    base = base.merge(four[["player_id", "composite_z", "min_z", "rank_composite_z"]], on="player_id", how="left")

    base["swg_dec"] = (base["z_swing_percent"] + (100 - base["oz_swing_percent"])) / 2

    # contract_through: hand override else 2026 + est_yrs_to_fa rounded
    def ct(row):
        ov = OVERRIDES.get(int(row["player_id"]))
        if ov:
            return ov[0]
        if pd.notna(row["est_yrs_to_fa"]):
            return 2026 + round(row["est_yrs_to_fa"])
        return None

    def note(row):
        ov = OVERRIDES.get(int(row["player_id"]))
        return ov[1] if ov else "service-time proxy"

    base["contract_through"] = base.apply(ct, axis=1)
    base["contract_note"] = base.apply(note, axis=1)
    base["fa_year"] = base["contract_through"].apply(lambda y: int(y) + 1 if pd.notna(y) else None)

    # filters
    pos_ok = base["primary_position"].isin(["1B", "2B", "3B", "DH"])
    age_ok = base["age"] < 31
    pa_ok = base["b_total_pa"] >= 50

    fa_2027 = base[pos_ok & age_ok & pa_ok & (base["fa_year"] == 2027)].sort_values("composite_z", ascending=False)
    fa_2028 = base[pos_ok & age_ok & pa_ok & (base["fa_year"] == 2028)].sort_values("composite_z", ascending=False)

    cols = ["player", "primary_position", "age", "team_abbr", "b_total_pa",
            "exit_velocity_avg", "pull_air_pct", "iz_contact_percent", "swg_dec",
            "composite_z", "rank_composite_z", "woba", "xwoba", "fa_year", "contract_note"]

    print("=" * 110)
    print("2027 FREE AGENT CLASS  (contract / team control runs out at end of 2026)")
    print("Positions: 1B/2B/3B/DH; Age < 31; PA >= 50")
    print("=" * 110)
    print(fa_2027[cols].to_string(index=False))

    print("\n" + "=" * 110)
    print("2028 FREE AGENT CLASS  (contract / team control runs out at end of 2027)")
    print("Positions: 1B/2B/3B/DH; Age < 31; PA >= 50")
    print("=" * 110)
    print(fa_2028[cols].to_string(index=False))

    fa_2027.to_csv(os.path.join(DATA, "fa_2027_class.csv"), index=False)
    fa_2028.to_csv(os.path.join(DATA, "fa_2028_class.csv"), index=False)
    print("\nwrote data/fa_2027_class.csv and data/fa_2028_class.csv")


if __name__ == "__main__":
    main()
