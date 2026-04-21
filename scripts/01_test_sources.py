"""Probe data sources for 2026 MLB data availability."""
import json
import sys
import requests
import pandas as pd

print("=" * 80)
print("PROBING DATA SOURCES (date: 2026-04-21)")
print("=" * 80)

# 1) MLB Stats API — team hitting, standings
print("\n[1] MLB Stats API: team hitting stats for 2026...")
url = "https://statsapi.mlb.com/api/v1/teams/stats"
params = {"season": 2026, "sportId": 1, "stats": "season", "group": "hitting"}
try:
    r = requests.get(url, params=params, timeout=30)
    data = r.json()
    splits = data.get("stats", [{}])[0].get("splits", [])
    print(f"  -> {len(splits)} teams returned")
    if splits:
        print(f"  -> sample keys: {list(splits[0]['stat'].keys())[:12]}")
        print(f"  -> sample team: {splits[0]['team']['name']} games={splits[0]['stat'].get('gamesPlayed')}")
except Exception as e:
    print(f"  !! error: {e}")

# 2) MLB Stats API — standings
print("\n[2] MLB Stats API: standings 2026...")
url = "https://statsapi.mlb.com/api/v1/standings"
params = {"leagueId": "103,104", "season": 2026, "standingsTypes": "regularSeason"}
try:
    r = requests.get(url, params=params, timeout=30)
    data = r.json()
    recs = data.get("records", [])
    print(f"  -> {len(recs)} divisions")
    mets_found = False
    for rec in recs:
        for tr in rec.get("teamRecords", []):
            if "Mets" in tr["team"]["name"]:
                mets_found = True
                print(f"  -> METS: W={tr['wins']} L={tr['losses']} pct={tr['winningPercentage']} rs={tr.get('runsScored','?')} ra={tr.get('runsAllowed','?')} gb={tr.get('gamesBack','?')}")
    if not mets_found:
        print("  !! Mets not found")
except Exception as e:
    print(f"  !! error: {e}")

# 3) Baseball Savant — statcast leaderboard CSV
print("\n[3] Baseball Savant: statcast leaderboard 2026...")
savant_url = ("https://baseballsavant.mlb.com/leaderboard/custom"
              "?year=2026&type=batter&filter=&sort=1&sortDir=desc&min=1&selections=b_total_pa,b_ab,b_total_hits,b_home_run,b_k_percent,b_bb_percent,xba,xslg,xwoba,exit_velocity_avg,launch_angle_avg,barrel_batted_rate&chart=false&x=b_total_pa&y=b_total_pa&r=no&chartType=beeswarm&csv=true")
try:
    r = requests.get(savant_url, timeout=60)
    print(f"  -> status={r.status_code} bytes={len(r.content)}")
    # read as CSV
    from io import StringIO
    df = pd.read_csv(StringIO(r.text))
    print(f"  -> rows={len(df)} cols={list(df.columns)[:8]}")
    print(df.head(2).to_string())
except Exception as e:
    print(f"  !! error: {e}")

# 4) pybaseball statcast (event-level) sample
print("\n[4] pybaseball statcast: 1 day of events in 2026...")
try:
    import pybaseball
    pybaseball.cache.enable()
    df = pybaseball.statcast(start_dt="2026-04-15", end_dt="2026-04-15")
    print(f"  -> rows={len(df)} cols={len(df.columns)}")
    if len(df):
        print(f"  -> teams seen: {sorted(pd.unique(df[['home_team','away_team']].values.ravel()))[:20]}")
except Exception as e:
    print(f"  !! error: {e}")
