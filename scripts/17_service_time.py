"""Estimate years of MLB service for each candidate by counting full seasons
since MLB debut. Used as a rough proxy for years of team control remaining.

Note: MLB Stats API does NOT expose actual service-time days. This is a coarse
proxy. Players become free agents after 6 years of service time.
"""
import os
import pandas as pd
from datetime import date

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
TODAY = date(2026, 4, 29)


def main():
    info = pd.read_csv(os.path.join(DATA, "player_info_2026.csv"))
    info["mlb_debut_date"] = pd.to_datetime(info["mlb_debut"], errors="coerce").dt.date
    def years_since(d):
        if pd.isna(d) or d is None:
            return None
        return round((TODAY - d).days / 365.25, 2)
    info["yrs_since_debut"] = info["mlb_debut_date"].apply(years_since)
    info["est_yrs_to_fa"] = (6 - info["yrs_since_debut"]).clip(lower=0).round(1)
    info.to_csv(os.path.join(DATA, "player_info_2026.csv"), index=False)
    print(info[["full_name", "primary_position", "age", "mlb_debut", "yrs_since_debut", "est_yrs_to_fa"]].head(15).to_string(index=False))


if __name__ == "__main__":
    main()
