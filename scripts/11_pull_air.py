"""Pull 2026 Statcast events to compute Pulled-Air% per batter.

Pulled-Air% = (pulled FB + pulled LD) / total batted balls.
We classify pull by spray angle from hc_x/hc_y plus batter stand.
"""
import os, math
import pandas as pd
import pybaseball as pb

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
pb.cache.enable()


def spray_angle(hc_x, hc_y):
    # Statcast hit coords: home plate ~ (125.42, 198.27); decreasing y = into the field.
    # Returns angle in degrees: 0 = CF, negative = LF (3B side), positive = RF (1B side).
    if pd.isna(hc_x) or pd.isna(hc_y):
        return float("nan")
    return math.degrees(math.atan2(hc_x - 125.42, 198.27 - hc_y))


def pull_class(stand: str, sa: float) -> str:
    if pd.isna(sa) or stand not in ("L", "R"):
        return "unknown"
    # RHB pulls to LF (negative angle); LHB pulls to RF (positive angle).
    if stand == "R":
        if sa < -15:
            return "pull"
        if sa > 15:
            return "oppo"
        return "center"
    else:  # L
        if sa > 15:
            return "pull"
        if sa < -15:
            return "oppo"
        return "center"


def fetch_statcast_events(start: str, end: str) -> pd.DataFrame:
    df = pb.statcast(start_dt=start, end_dt=end)
    return df


if __name__ == "__main__":
    # 2026 to date — split into chunks to avoid timeout
    print("Fetching 2026 statcast events...")
    df = fetch_statcast_events("2026-03-26", "2026-04-20")
    print(f"  rows={len(df)}")

    # Keep only batted balls
    bb = df[df["type"] == "X"].copy()  # ball in play
    print(f"  batted balls={len(bb)}")

    bb["spray_angle"] = bb.apply(lambda r: spray_angle(r["hc_x"], r["hc_y"]), axis=1)
    bb["pull_class"] = bb.apply(lambda r: pull_class(r["stand"], r["spray_angle"]), axis=1)
    bb["air_class"] = bb["bb_type"].map(
        {"fly_ball": "air", "line_drive": "air", "popup": "air", "ground_ball": "ground"}
    ).fillna("other")

    bb["is_pull_air"] = ((bb["pull_class"] == "pull") & (bb["bb_type"].isin(["fly_ball", "line_drive"]))).astype(int)
    bb["is_pull_fb"] = ((bb["pull_class"] == "pull") & (bb["bb_type"] == "fly_ball")).astype(int)
    bb["is_air"] = bb["bb_type"].isin(["fly_ball", "line_drive"]).astype(int)
    bb["is_pull"] = (bb["pull_class"] == "pull").astype(int)

    agg = bb.groupby("batter").agg(
        bb_count=("type", "size"),
        air=("is_air", "sum"),
        pull_air=("is_pull_air", "sum"),
        pull_fb=("is_pull_fb", "sum"),
        pull=("is_pull", "sum"),
        fly_ball=("bb_type", lambda s: (s == "fly_ball").sum()),
        line_drive=("bb_type", lambda s: (s == "line_drive").sum()),
        ground=("bb_type", lambda s: (s == "ground_ball").sum()),
        avg_ev=("launch_speed", "mean"),
        avg_la=("launch_angle", "mean"),
    ).reset_index()
    agg = agg.rename(columns={"batter": "player_id"})
    agg["pull_air_pct"] = 100 * agg["pull_air"] / agg["bb_count"]
    agg["pull_fb_pct"] = 100 * agg["pull_fb"] / agg["bb_count"]
    agg["pull_pct"] = 100 * agg["pull"] / agg["bb_count"]
    agg["air_pct"] = 100 * agg["air"] / agg["bb_count"]

    out = os.path.join(DATA, "savant_pull_air_2026.csv")
    agg.sort_values("bb_count", ascending=False).to_csv(out, index=False)
    print(f"wrote {out}  rows={len(agg)}")
    print(agg.sort_values("pull_air_pct", ascending=False).head(20).to_string())
