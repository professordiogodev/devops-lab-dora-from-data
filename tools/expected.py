#!/usr/bin/env python3
"""Independent reference implementation. usage: expected.py DATA_DIR [first|second|all]"""
import csv, datetime as dt, statistics as st, sys
d = sys.argv[1]; part = sys.argv[2] if len(sys.argv) > 2 else "all"
F = "%Y-%m-%d %H:%M"; P = lambda s: dt.datetime.strptime(s, F)
deps = list(csv.DictReader(open(f"{d}/deployments.csv"))); incs = list(csv.DictReader(open(f"{d}/incidents.csv"))); tics = list(csv.DictReader(open(f"{d}/tickets.csv")))
t0 = dt.datetime(2026, 8, 1, 0, 0); cut = t0 + dt.timedelta(days=45); end = t0 + dt.timedelta(days=90)
lo, hi = {"all": (t0, end), "first": (t0, cut), "second": (cut, end)}[part]
deps = [x for x in deps if lo <= P(x["deploy_time"]) < hi]
ids = {x["id"] for x in deps}
incs = [x for x in incs if x["deployment_id"] in ids]
tics = [x for x in tics if lo <= P(x["deployed"]) < hi]
weeks = (hi - lo).days / 7.0
df = len(deps) / weeks
lt = st.median([(P(x["deploy_time"]) - P(x["commit_time"])).total_seconds() / 3600 for x in deps])
cfr = 100.0 * sum(1 for x in deps if x["status"] == "failed") / len(deps)
ttr = st.median([(P(x["end"]) - P(x["start"])).total_seconds() / 3600 for x in incs]) if incs else 0.0
def level_df(v): return "elite" if v >= 7 else "high" if v >= 1 else "medium" if v >= 0.25 else "low"
def level_lt(v): return "elite" if v < 24 else "high" if v < 168 else "medium" if v < 720 else "low"
def level_cfr(v): return "elite" if v <= 5 else "high" if v <= 10 else "medium" if v <= 15 else "low"
def level_ttr(v): return "elite" if v < 1 else "high" if v < 24 else "medium" if v < 168 else "low"
order = ["elite", "high", "medium", "low"]
levels = [level_df(df), level_lt(lt), level_cfr(cfr), level_ttr(ttr)]
overall = max(levels, key=order.index)
dev = st.median([(P(x["review_started"]) - P(x["work_started"])).total_seconds() / 3600 for x in tics])
rev = st.median([(P(x["merged"]) - P(x["review_started"])).total_seconds() / 3600 for x in tics])
dpl = st.median([(P(x["deployed"]) - P(x["merged"])).total_seconds() / 3600 for x in tics])
bott = max([("dev", dev), ("review", rev), ("deploy", dpl)], key=lambda kv: kv[1])[0]
print(f"deployments_per_week {df:.1f}")
print(f"lead_time_hours_median {lt:.1f}")
print(f"change_failure_rate_pct {cfr:.1f}")
print(f"time_to_restore_hours_median {ttr:.1f}")
print(f"level_deployment_frequency {levels[0]}")
print(f"level_lead_time {levels[1]}")
print(f"level_change_failure_rate {levels[2]}")
print(f"level_time_to_restore {levels[3]}")
print(f"overall_level {overall}")
print(f"stage_median_hours_dev {dev:.1f}")
print(f"stage_median_hours_review {rev:.1f}")
print(f"stage_median_hours_deploy {dpl:.1f}")
print(f"bottleneck {bott}")
