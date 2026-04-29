# Mets 2026 Offense Audit

Ad-hoc analysis of why the New York Mets have MLB's lowest-scoring offense in 2026, using public Baseball Savant (Statcast) and MLB Stats API data.

See **[REPORT.md](REPORT.md)** for the full write-up.

## Reproduce

```bash
pip install pybaseball pandas requests matplotlib seaborn

python3 scripts/02_team_offense.py       # team hitting, both seasons
python3 scripts/03_mets_roster.py        # Mets player-level hitting
python3 scripts/04_savant_batters.py     # Statcast batter leaderboard
python3 scripts/05_mets_savant_merge.py  # merge + YoY
python3 scripts/06_team_savant.py        # savant batter data by year
python3 scripts/07_team_statcast.py      # team xwOBA/xSLG
python3 scripts/08_situational.py        # RISP and other splits
python3 scripts/09_departures_adds.py    # roster churn
python3 scripts/10_charts.py             # generate audit charts
python3 scripts/11_pull_air.py           # compute Pulled-Air% from events
python3 scripts/12_four_tool.py          # 4-D composite + viz
```

Outputs: `data/*.csv` and `charts/*.png`.

## Key findings

- Mets 2026 YTD: 72 R in 22 G (3.27 R/G) — **30th of 30**. 2025: 9th.
- Underlying xwOBA dropped from **2nd in MLB (.339) to 24th (.309)** — real, not luck.
- Further -.025 gap between wOBA and xwOBA — worst in MLB, extra bad sequencing.
- Lost 2,704 PA / 87 HR / 340 RBI in Alonso, Nimmo, McNeil, Marte departures.
- Bichette / Semien / Robert Jr. / Benge replacements combined for .595 OPS.
- RISP OPS .806 → .601 (rank 3rd → 29th) — lineup has no finisher.
- Team-wide chase rate spike (Baty +11.4pts, Soto +15.9pts) — plate-discipline regression.
- Juan Soto 8 games with EV down 6.5 mph — likely playing hurt.
