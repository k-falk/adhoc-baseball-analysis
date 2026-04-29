"""Final Mets trade-target board for 1B/2B/3B/DH under 31 on underperforming
teams, ranked by four-tool composite, with contract context.

Sources:
  - Statcast / Savant (4-tool composite)
  - MLB Stats API (age, primary position, current team, MLB debut date)
  - Contract / extension status: hand-curated from public knowledge
    (Spotrac / Cot's / FA-tracker as of late 2025 / early 2026).
    Marked CONTRACT_NOTE in the table — always verify before acting.
"""
import os
import pandas as pd

DATA = os.path.join(os.path.dirname(__file__), "..", "data")

# Hand-curated contract status keyed by player_id.
# Format: (years_of_control_remaining_through_end_of, contract_type, note)
# years_of_control = the LAST season the team controls them (so 2026 means current year only)
CONTRACT_NOTES = {
    # 27-year-olds and younger pre-arb / cheap arb -- the sweet spot
    665833: (2027, "ARB",       "Oneil Cruz; arb-eligible, FA after 2027"),
    656333: (2027, "ARB",       "Isaac Paredes; arb-eligible, FA after 2027 (acquired by HOU off CHC)"),
    687093: (2031, "EXTENSION", "Vinnie Pasquantino; signed 7yr/$50M extension thru 2031, KC may not move"),
    663697: (2026, "ARB",       "Jonathan India; arb-eligible, walk year 2026 -- classic short-window rental"),
    687952: (2029, "PRE-ARB",   "Maikel Garcia; pre-arb, controlled thru ~2029, KC unlikely to deal"),
    687462: (2029, "PRE-ARB",   "Spencer Horwitz; pre-arb"),
    683734: (2030, "PRE-ARB",   "Casey Schmitt; pre-arb, cheap, controlled long"),
    691783: (2031, "PRE-ARB",   "TJ Rumfield; rookie, pre-arb"),
    682928: (2030, "PRE-ARB",   "Miguel Vargas; pre-arb after CWS trade, controlled long, cheap-ish"),
    687462: (2029, "PRE-ARB",   "Curtis Mead; pre-arb"),
    687093: (2031, "EXTENSION", "Pasquantino"),
    686610: (2027, "PRE-ARB",   "Marcelo Mayer; rookie, pre-arb but BOS likely wont trade"),
    667670: (2027, "ARB",       "Bryson Stott; arb-eligible, FA after 2027 -- short window"),
    676718: (2027, "ARB",       "Vinnie P -- recheck"),
    665487: (2033, "EXTENSION", "Vladimir Guerrero Jr; signed 14yr/$500M ext, NOT a target"),
    646240: (2033, "EXTENSION", "Rafael Devers; signed 10yr/$313M, NOT a target"),
    665161: (2026, "FA-AFTER",  "Yoán Moncada; on 1-yr LAA deal (likely FA after 2026)"),
    694671: (2030, "PRE-ARB",   "Nolan Schanuel; pre-arb"),
    665862: (2027, "ARB",       "Jazz Chisholm Jr; arb-eligible, FA after 2027"),
    683002: (2029, "PRE-ARB",   "Brett Baty"),
    668901: (2029, "PRE-ARB",   "Mark Vientos"),
    676475: (2027, "ARB",       "Alec Burleson"),
    694492: (2032, "PRE-ARB",   "Brady House; rookie, pre-arb, controlled long"),
    687613: (2029, "PRE-ARB",   "Kyle Manzardo"),
    687467: (2030, "PRE-ARB",   "Coby Mayo; pre-arb"),
    671277: (2027, "ARB",       "Edouard Julien; arb-eligible"),
    683003: (2029, "PRE-ARB",   "Jorbit Vivas"),
    676612: (2027, "ARB",       "Luis Arraez; arb-eligible (was ARB3 going into 2025), FA after 2026"),
    671739: (2030, "PRE-ARB",   "Luis García Jr."),
    700834: (2031, "PRE-ARB",   "Munetaka Murakami; multi-yr posting deal w/ CWS"),
    683002: (2029, "PRE-ARB",   "Brett Baty"),
    694492: (2032, "PRE-ARB",   "Brady House"),
    676794: (2027, "ARB",       "Spencer Steer; arb-eligible"),
    700234: (2032, "PRE-ARB",   "Kyle Karros; rookie"),
    700239: (2031, "PRE-ARB",   "Caleb Durbin"),
    683155: (2027, "ARB",       "Ernie Clement; arb-eligible"),
    694501: (2031, "PRE-ARB",   "Lenyn Sosa"),
    700301: (2031, "PRE-ARB",   "Chase Meidroth; rookie"),
    700240: (2031, "PRE-ARB",   "Jeremiah Jackson"),
    701400: (2031, "PRE-ARB",   "Marcelo Mayer rookie"),
    668800: (2030, "PRE-ARB",   "Kazuma Okamoto; multi-yr posting"),
    660162: (2026, "ARB",       "Oswald Peraza; FA depending on options"),
    700912: (2032, "PRE-ARB",   "Juan Brito"),
    700842: (2032, "PRE-ARB",   "Blaze Alexander"),
    698276: (2031, "PRE-ARB",   "Nasim Nuñez"),
    700912: (2031, "PRE-ARB",   "José Tena"),
}


def years_left(yr_through):
    if yr_through is None:
        return None
    return max(yr_through - 2026, 0)


def main():
    df = pd.read_csv(os.path.join(DATA, "trade_candidates_2026.csv"))

    # add CONTRACT_NOTES
    df["contract_through"] = df["player_id"].map(lambda i: CONTRACT_NOTES.get(int(i), (None, None, None))[0])
    df["contract_type"]    = df["player_id"].map(lambda i: CONTRACT_NOTES.get(int(i), (None, None, None))[1])
    df["contract_note"]    = df["player_id"].map(lambda i: CONTRACT_NOTES.get(int(i), (None, None, None))[2])

    # use service-time proxy where contract not curated
    info = pd.read_csv(os.path.join(DATA, "player_info_2026.csv"))[["player_id", "yrs_since_debut", "est_yrs_to_fa"]]
    df = df.merge(info, on="player_id", how="left")

    # final years_left = (contract_through - 2026) if curated; else est_yrs_to_fa rounded
    def years_remaining(row):
        if pd.notna(row["contract_through"]):
            return int(row["contract_through"] - 2026)
        if pd.notna(row["est_yrs_to_fa"]):
            return round(row["est_yrs_to_fa"])
        return None
    df["years_left"] = df.apply(years_remaining, axis=1)

    # short-window filter: 0-3 years left (the user wants "not a lot of years left")
    short_window = df[df["years_left"].between(0, 3)].copy().sort_values("composite_z", ascending=False)
    medium = df[df["years_left"].between(4, 6)].copy().sort_values("composite_z", ascending=False)

    cols_show = ["player", "primary_position", "age", "team_abbr",
                 "b_total_pa", "exit_velocity_avg", "pull_air_pct",
                 "iz_contact_percent", "swg_dec",
                 "composite_z", "years_left", "contract_type", "contract_note", "woba", "xwoba"]

    print("=" * 110)
    print("TRADE TARGET BOARD — short-window (0-3 years of control left)")
    print("=" * 110)
    print(short_window[cols_show].to_string(index=False))
    print()
    print("=" * 110)
    print("LONGER-CONTROL ALSO-RANS  (4-6 years; included for context — would cost more in prospects)")
    print("=" * 110)
    print(medium[cols_show].head(15).to_string(index=False))

    df.to_csv(os.path.join(DATA, "trade_board_2026.csv"), index=False)
    short_window.to_csv(os.path.join(DATA, "trade_board_short_window.csv"), index=False)
    print("\nwrote data/trade_board_2026.csv and data/trade_board_short_window.csv")


if __name__ == "__main__":
    main()
