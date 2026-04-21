"""Pull team situational splits (RISP, 2-out RISP, close/late) for Mets + league."""
import os
import pandas as pd
from lib import get_json

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
METS_ID = 121


def split_stats(season: int, split_code: str) -> pd.DataFrame:
    """For a given situational split, get all 30 teams."""
    data = get_json(
        "https://statsapi.mlb.com/api/v1/teams/stats",
        params={
            "season": season, "sportId": 1,
            "stats": "statSplits", "group": "hitting",
            "sitCodes": split_code,
        },
    )
    rows = []
    for section in data.get("stats", []):
        split_name = section.get("type", {}).get("displayName", "")
        for s in section.get("splits", []):
            st = s["stat"]
            rows.append({
                "season": season,
                "split": split_code,
                "team": s["team"]["name"],
                "pa": int(st.get("plateAppearances", 0) or 0),
                "ab": int(st.get("atBats", 0) or 0),
                "h": int(st.get("hits", 0) or 0),
                "hr": int(st.get("homeRuns", 0) or 0),
                "bb": int(st.get("baseOnBalls", 0) or 0),
                "so": int(st.get("strikeOuts", 0) or 0),
                "rbi": int(st.get("rbi", 0) or 0),
                "avg": float(st.get("avg", 0) or 0),
                "obp": float(st.get("obp", 0) or 0),
                "slg": float(st.get("slg", 0) or 0),
                "ops": float(st.get("ops", 0) or 0),
            })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    # Common sit codes: risp = runners in scoring position
    #                   r10 = RISP 2 out, lc = late & close
    splits = {
        "risp": "Runners in scoring position",
        "r10": "RISP with 2 outs",
        "lc": "Late & close",
        "b1": "Bases empty",
        "b2": "Men on",
    }
    for season in (2026, 2025):
        all_rows = []
        for code in splits:
            try:
                df = split_stats(season, code)
                all_rows.append(df)
            except Exception as e:
                print(f"  !! {season} {code}: {e}")
        combined = pd.concat(all_rows, ignore_index=True) if all_rows else pd.DataFrame()
        out = os.path.join(DATA, f"team_splits_{season}.csv")
        combined.to_csv(out, index=False)
        print(f"[{season}] wrote {out} rows={len(combined)}")
        for code in splits:
            sub = combined[combined["split"] == code].copy()
            if sub.empty:
                continue
            sub["ops_rank"] = sub["ops"].rank(ascending=False, method="min").astype(int)
            mets = sub[sub["team"].str.contains("Mets")]
            if len(mets):
                m = mets.iloc[0]
                print(f"  {splits[code]:<30s} Mets PA={m['pa']} AVG={m['avg']:.3f} OPS={m['ops']:.3f} RBI={m['rbi']} rank={int(m['ops_rank'])}/30")
        print()
