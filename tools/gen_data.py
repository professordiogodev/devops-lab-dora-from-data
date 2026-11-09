#!/usr/bin/env python3
"""usage: gen_data.py OUTDIR SEED. Writes deployments.csv, incidents.csv, tickets.csv for 90 days."""
import csv, datetime as dt, os, random, sys
out, seed = sys.argv[1], int(sys.argv[2]); r = random.Random(seed)
os.makedirs(out, exist_ok=True)
start = dt.datetime(2026, 8, 1, 9, 0)
F = "%Y-%m-%d %H:%M"
dep, inc, tic = [], [], []
did = iid = tid = 0
day = 0
while day < 90:
    second_half = day >= 45
    per_week = 10 if second_half else 2
    p = per_week / 5.0 / 1.0                        # per weekday
    d = start + dt.timedelta(days=day)
    if d.weekday() < 5:
        n = 0
        x = r.random()
        while x < p and n < 4: n += 1; x = r.random() * 1.15 if n else x
        for _ in range(n):
            did += 1
            deploy = d + dt.timedelta(hours=r.randint(0, 7), minutes=r.randint(0, 59))
            lead = r.uniform(14, 44) if second_half else r.uniform(90, 260)
            commit = deploy - dt.timedelta(hours=lead)
            failed = r.random() < (0.08 if second_half else 0.18)
            dep.append((f"D{did:03d}", "clippy-api", commit.strftime(F), deploy.strftime(F), "failed" if failed else "success"))
            if failed:
                iid += 1
                restore = r.uniform(0.8, 6) if second_half else r.uniform(6, 40)
                inc.append((f"I{iid:03d}", f"D{did:03d}", deploy.strftime(F), (deploy + dt.timedelta(hours=restore)).strftime(F)))
    day += 1
for k in range(int(r.uniform(180, 220))):
    tid += 1
    created = start + dt.timedelta(days=r.uniform(0, 88), hours=r.uniform(0, 8))
    dev = r.uniform(8, 30); review = r.uniform(6, 20) if r.random() < 0.45 else r.uniform(40, 96); dpl = r.uniform(2, 22)
    s = created + dt.timedelta(hours=r.uniform(1, 30))
    rv = s + dt.timedelta(hours=dev); mg = rv + dt.timedelta(hours=review); dn = mg + dt.timedelta(hours=dpl)
    tic.append((f"T{tid:03d}", created.strftime(F), s.strftime(F), rv.strftime(F), mg.strftime(F), dn.strftime(F)))
def w(name, header, rows):
    with open(os.path.join(out, name), "w", newline="") as f:
        c = csv.writer(f); c.writerow(header); c.writerows(rows)
w("deployments.csv", ["id", "service", "commit_time", "deploy_time", "status"], dep)
w("incidents.csv", ["id", "deployment_id", "start", "end"], inc)
w("tickets.csv", ["id", "created", "work_started", "review_started", "merged", "deployed"], tic)
