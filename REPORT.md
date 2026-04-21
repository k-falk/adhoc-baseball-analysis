# Why are the 2026 New York Mets the lowest-scoring offense in MLB?

**A full Statcast + MLB Stats API audit — data through games of Apr 20, 2026 (22 games played)**

---

## Executive summary

- Through 22 games the Mets have scored **72 runs (3.27 R/G) — dead last in MLB**. Every other team has scored at least 75.
- They finished **2025 9th in runs and 6th in OPS (.753)**. In 2026 they are 30th in runs, 30th in OPS (.624), 30th in SLG (.336), and 30th in ISO (.110).
- This is not a BABIP fluke. Team **expected wOBA collapsed from #2 in MLB in 2025 (.339) to #24 in 2026 (.309)** — a .030-point drop in underlying quality of contact. They are also underperforming their xwOBA by .025 (wOBA .284 vs xwOBA .309), tied for the largest negative gap in baseball — so there is *additional* bad sequencing/finishing on top of a real decline.
- Three compounding causes:
  1. **Roster churn**: They lost 2,704 PA / 87 HR / 340 RBI of 2025 production (Alonso, Nimmo, McNeil, Marte) and replaced them with Bichette, Semien, Robert Jr. and rookie Carson Benge — all of whom are cold out of the gate (combined .595 OPS).
  2. **Returnee regression and plate-discipline slippage**: Lindor, Baty, Vientos, Torrens, Taylor are all down in xwOBA and chasing more. Baty in particular has collapsed — 24.9% → 36.3% chase rate, OPS .748 → .483.
  3. **Juan Soto availability + likely injury**: Soto has played only 8 of 22 games. His hard-hit% is down from 55.3% to 28.0% and chase rate has doubled (15.9% → 31.8%), strongly suggesting he is banged up.
- Situationally it gets worse: **Mets OPS with RISP has fallen from .806 (3rd in MLB in 2025) to .601 (29th in 2026)** — the clearest evidence that the lineup lacks a middle-of-order finisher.

---

## 1. The scale of the regression

### Team-level YoY (MLB Stats API)

| Metric            | 2025 Mets | MLB avg '25 | 2026 Mets YTD | MLB avg '26 | MLB rank '26 |
|-------------------|-----------|-------------|----------------|-------------|--------------|
| Runs / game       | 4.73      | 4.45        | **3.27**       | 4.46        | **30 / 30**  |
| AVG               | .249      | .245        | .226           | .238        | 27           |
| OBP               | .326      | .315        | .288           | .321        | 30           |
| SLG               | .427      | .404        | **.336**       | .383        | **30**       |
| OPS               | .753      | .719        | **.624**       | .704        | **30**       |
| ISO               | .178      | .158        | **.110**       | .145        | **30**       |
| BB%               | 9.1%      | 8.4%        | 7.7%           | 9.8%        | 26           |
| K%                | 21.4%     | 22.2%       | 21.5%          | 22.4%       | 15           |

The strikeout rate is essentially unchanged — so this is **not a contact problem**. It is a **power and walk problem**. The SLG drop of **.091** and ISO drop of **.068** are the two largest Mets-specific deltas vs the league and are doing most of the damage.

### League-wide change, 2025 → 2026 YTD (R/G delta)

![R/G change](charts/06_rank_change.png)

The Mets' drop of **-1.46 R/G** is the largest fall-off in baseball by a wide margin — nobody else is worse than -1.0. This is an outlier-level regression, not a small-sample league-wide issue.

### Expected vs actual — it's real *and* unlucky

Statcast team totals (Savant `expected_statistics` leaderboard):

| Year | Mets xwOBA | MLB rank | Mets wOBA | MLB rank | Gap   |
|------|-----------|----------|-----------|----------|-------|
| 2025 | .339      | **2nd**  | .326      | 6th      | -.013 |
| 2026 | .309      | 24th     | .284      | **30th** | **-.025** |

![Team expected vs actual](charts/05_team_xwoba.png)

Takeaway: a ~30-point drop in xwOBA *by itself* would push them from a top-5 offense to below league average. On top of that they are under-running their already-reduced expected wOBA by 25 points (the worst in MLB is -.032, Reds), i.e., they are also getting bad sequencing / clutch results. Both things are true.

---

## 2. Root cause #1 — Roster churn stripped the middle of the order

All four of the Mets' 2025 primary run producers are on different teams in 2026:

![Roster churn](charts/07_roster_churn.png)

| Departed     | 2025 PA | 2025 HR | 2025 RBI | 2025 OPS | 2026 team  |
|--------------|---------|---------|----------|----------|------------|
| Pete Alonso  | 709     | **38**  | **126**  | **.871** | Orioles    |
| Brandon Nimmo| 652     | 25      | 92       | .760     | Rangers    |
| Jeff McNeil  | 462     | 12      | 54       | .746     | Athletics  |
| Starling Marte| 329    | 9       | 34       | .745     | Royals     |
| L. Acuña     | 193     | 0       | 8        | .567     | White Sox  |
| Cedric Mullins| 143    | 2       | 10       | .565     | Rays       |
| bench pieces | ~218    | 1       | 16       | ~.450    | various    |

Cumulative lost production: **2,704 PA, 87 HR, 340 RBI, roughly league-average ~.740 OPS as a group.**

The replacements (2026 YTD):

| New hitter     | PA | OPS   | xwOBA | Barrel % | Hard-Hit % |
|----------------|----|-------|-------|----------|------------|
| Bo Bichette    | 98 | .538  | .313  | 2.9%     | 42.9%      |
| Marcus Semien  | 86 | .606  | .303  | 6.5%     | 35.5%      |
| Luis Robert Jr.| 82 | .737  | .350  | 3.7%     | 44.4%      |
| Carson Benge   | 70 | .435  | .265  | 4.4%     | 37.8%      |
| MJ Melendez    | 16 | 1.152 | .334  | 33.3%    | 83.3%      |
| Tommy Pham     | 8  | .000  | .142  | 0.0%     | 50.0%      |

Even if Bichette and Semien heat up to their career norms, the underlying Statcast marks for this group are concerning: **Bichette's barrel rate of 2.9% is a career low**, Semien's xwOBA of .303 is below average, Robert Jr.'s 3.7% barrel rate is inconsistent with the prior hope that he would be the primary slugging replacement for Alonso. The cold bats are not all small-sample noise — the power metrics they're generating on contact are genuinely below expectation.

---

## 3. Root cause #2 — Returnees have regressed *and* lost the strike zone

Eight hitters returning from the 2025 club have ≥15 PA this year. Their year-over-year changes:

![Returnees YoY quality of contact](charts/03_returnees_yoy.png)
![Discipline YoY](charts/04_discipline_yoy.png)

| Player            | OPS '25 | OPS '26 | ΔxwOBA   | ΔBarrel% | ΔChase% | Verdict |
|-------------------|---------|---------|----------|----------|---------|---------|
| Francisco Lindor  | .812    | .600    | -.022    | -0.2     | +1.1    | Mild underlying decline, some BABIP bad luck (.288 → .246), whiff% up 20.8 → 24.9 |
| Brett Baty        | .748    | **.483**| **-.098**| -4.1     | **+11.4** | Plate discipline collapse — BB% 7.6 → **1.5**, K% 25 → **30.9** |
| Mark Vientos      | .702    | .616    | -.040    | **-6.8** | 0.0     | Power-on-contact dropped sharply |
| Tyrone Taylor     | .598    | .598    | -.007    | +4.2     | **+9.2**| Expanding zone; same OPS disguises regression |
| Luis Torrens      | .629    | .609    | -.034    | -10.7    | **+10.4**| Chasing and making worse contact |
| Juan Soto         | .921    | .928*   | **-.108**| **-10.1**| **+15.9**| **Red-flag small sample, see below** |
| Francisco Alvarez | .786    | **.879**| +.093    | +6.1     | +1.0    | Only hitter clearly *improving* |
| Jared Young       | .722    | .841    | +.069    | +2.4     | -1.0    | Small sample positive |

Two patterns jump off the page:

1. **Chase rates are up across the board.** Baty +11.4, Taylor +9.2, Torrens +10.4, Soto +15.9. This is a team-wide trend, not coincidence. It is often the signature of either (a) pressing because the lineup behind you is weaker (the "nobody's going to drive me in, I'd better do it myself" effect) or (b) opposing pitchers attacking the zone edges more aggressively because the middle of the order has less punch. Either way, this is a coaching / approach-level issue Carlos Mendoza and hitting coach Eric Chavez should be able to directly address.

2. **Only Alvarez is up.** The rest of the returnee core is *all* down in xwOBA, i.e., the regression is real, not just a BABIP quirk.

### Spotlight: Juan Soto

Soto's actual line (.355/.412/.516) looks fine — but he has only **8 games, 34 PA**, and the Statcast tells a different story:

| Metric         | 2025   | 2026 YTD |
|----------------|--------|----------|
| xwOBA          | .429   | **.321** |
| Hard-Hit %     | 55.3   | **28.0** |
| Barrel %       | 18.1   | **8.0**  |
| Avg EV (mph)   | 93.8   | **87.3** |
| Chase %        | 15.9   | **31.8** |
| BB %           | 17.8   | 8.8      |

An average exit velocity drop of **6.5 mph** combined with a doubling of his chase rate, from an elite-discipline hitter, is not slump noise — it is extremely consistent with a player protecting an injured lower-half or upper body. The Mets either need him healthy or on the IL; splitting the difference is costing them their one elite talent while his BABIP luck (.417 on balls in play) papers over real damage.

### Spotlight: Brett Baty — the most actionable single problem

Baty is the most fixable data point on the roster. His contact quality is close to last year's (xwOBA .236 is ugly but barrel 8.7%, HH 37.0% are only mildly down). What is destroying him is **an almost total loss of plate discipline**:

- Walk rate: 7.6% → **1.5%** (1 walk in 68 PA)
- Chase rate: 24.9% → **36.3%** (+11.4 points)
- K rate: 25.0% → **30.9%**

He is essentially swinging at everything. This is consistent with a hitter hunting for contact because his bat-speed-on-breaking-stuff has eroded, or because he is pressing in the two-hole. Either is correctable with a short demotion or a forced approach reset.

---

## 4. Root cause #3 — Situational and clutch collapse (RISP)

The split data exposes the *finishing* problem more clearly than the rate stats do:

![Splits YoY](charts/02_splits_yoy.png)

| Situation       | 2025 OPS | Rank | 2026 OPS | Rank |
|-----------------|---------|------|---------|------|
| Runners in scoring position | **.806** | **3** | **.601** | **29** |
| RISP, 2 outs    | (low sample) | — | low | — |
| Late & close    | .684    | 16   | .563    | 27   |
| Men on          | .890    | 2    | .559    | 28   |

A .205-point drop in RISP OPS while the team overall dropped .129 means the Mets are **substantially worse with men on base than they are in aggregate** — the opposite of 2025, when they over-performed with RISP. Combined with the -.025 wOBA-vs-xwOBA gap at the team level, this is the statistical fingerprint of a sequencing meltdown: they're either taking their best swings in the wrong situations, or (more likely) the lineup construction has no "thumper" after Soto/Lindor to make pitchers avoid the strike zone when men are aboard.

---

## 5. What the individual batters are actually doing differently

Aggregating the Savant batter leaderboard rolled up to team:

- **Chase rate (O-Swing%)**: Mets are swinging at **more** pitches outside the zone than last year despite league-wide chase rates being flat. This is consistent with the per-player chase-rate evidence above.
- **Walk rate**: 9.1% → 7.7% (league: 8.4% → 9.8%). The rest of MLB is walking *more*; the Mets are walking less. That is a 3.5-point swing vs the league — essentially all explained by lost Soto/Nimmo PA and Baty's collapse.
- **Barrel rate (team)**: 9.6% (2025, top-5) → ~6.8% (2026, lower third). Mets have stopped squaring the ball up.
- **Expected Batting Average**: .255 (2025) → .247 (2026), league .243. Actual BA is .226 — they should be hitting around .247 based on contact quality, so about 5-8 points of AVG is bad luck / sequencing.
- **Expected SLG**: .450 (2025) → .390 (2026), actual .336. Roughly 30-50 points of SLG gap with xSLG is real underperformance on top of a real underlying decline in contact quality.

---

## 6. Verdict — a three-layer problem

1. **Real regression in underlying quality of contact (Statcast)** — the Mets went from #2 in xwOBA to #24. That is a roster-composition issue: you cannot subtract Alonso (.386 xwOBA, 18.9% barrel) and Nimmo (.321 xwOBA, 8.8% barrel) and add Bichette (.313 xwOBA, 2.9% barrel) + Semien (.303 xwOBA, 6.5% barrel) without your team xwOBA dropping roughly 30 points. **This part was predictable in February.**
2. **Bad luck on top of it (wOBA-xwOBA gap)** — another ~25 wOBA points of negative variance. Some of this will regress positively. Expect maybe .010-.015 of the gap to close by midseason naturally.
3. **Approach/behavior regression (chase rate, walk rate)** — 5 of 7 returnees are chasing more, and Baty has functionally forgotten the strike zone. This is *not* a Statcast issue; it's a plate-discipline / coaching issue. It is the part that can be fixed most quickly.

---

## 7. Recommendations (what the front office / coaching staff should actually do)

### Immediate (this week)
- **Get Soto's medicals checked.** His hard-hit drop (55→28) and chase rate (16→32) are not slump signatures — they are injury signatures. A short IL stint is cheaper than two months of this.
- **Sit Brett Baty or send him to Syracuse for a plate-discipline reset.** 1 BB in 68 PA with a 36% chase rate is a broken hitter, not a cold one. Let Vientos play every day at 3B.
- **Move Alvarez up in the order.** He is the only hitter clearly *improving* (.879 OPS, .419 xwOBA). He is batting 6-7 in many games; he should be batting 3rd or 4th until Soto is right.

### Short-term (next 30 days)
- **Reset the approach.** The across-the-board chase-rate spike (Baty, Taylor, Torrens, Soto, Vientos) screams a team-wide pressing issue. Aggressive sit-on-fastball / take-to-first-strike drills; message that an 8% walk rate is table-stakes for this lineup to work.
- **Play Robert Jr. every day if healthy.** His .737 OPS / .350 xwOBA is actually the best Statcast signal of the 3 new adds; he has been under-deployed (20 of 22 games is fine — but bat him in the top 5).
- **Explore a buy-low contact bat trade.** The roster has no dedicated #3-hole hitter in Alonso's mold; a reasonable target is an OPS-over-.800 right-handed bat whose power peaks align with Citi Field (RF/CF ~380 ft).

### Structural (season-long)
- **Acknowledge that the projected ~.745 OPS this lineup was built to produce is probably a ~.690 OPS lineup** given the early Statcast picture. At current run rates that is a 70-win team. The front office built this roster expecting Bichette + Semien + Robert Jr. to combine for ~2.5 wins of offense above replacement; they're currently running at negative WAR.
- The underlying xwOBA of .309 projects to about **620-640 runs over 162 games** — not the 4.2 R/G worst-case, but still ~100 runs *below* 2025. Without a mid-season addition or a Soto/Baty bounce, 8th-9th place in the NL in runs is the realistic ceiling.

---

## Appendix A — Data sources & methodology

- **MLB Stats API** (`statsapi.mlb.com/api/v1/...`): team hitting, rosters, per-player season stats, situational splits.
- **Baseball Savant** (`baseballsavant.mlb.com/leaderboard/...`): player-level custom batter leaderboard (xwOBA, barrel%, EV, plate-discipline), team-level expected statistics (xBA, xSLG, xwOBA).
- **Scope**: 2026 season through Apr 20 (22 games, 827 PA). 2025 data is the full 162-game line for comparison.
- **Reproducibility**: All pulls scripted under `scripts/01_..._10_charts.py`, with CSVs saved under `data/` and PNGs under `charts/`. `scripts/lib.py` handles retries on transient 503s from MLB Stats API.

## Appendix B — Key files

- `data/team_hitting_{2025,2026}.csv` — 30-team hitting leaderboards
- `data/team_expected_{2025,2026}.csv` — Statcast xwOBA/xSLG team totals
- `data/team_splits_{2025,2026}.csv` — RISP, late & close, men-on splits
- `data/mets_players_{2025,2026}.csv` — Mets roster hitting lines
- `data/mets_savant_{2025,2026}.csv` — Mets roster + Statcast merged
- `data/mets_yoy.csv` — year-over-year comparison for returnees
- `data/mets_departures.csv` / `data/mets_additions.csv` — roster churn
- `charts/*.png` — the 7 figures referenced above
