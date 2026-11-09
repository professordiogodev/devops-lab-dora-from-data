#!/usr/bin/env python3
"""Compares your dora.py with an independent reference. Run: python3 verify.py"""
import os, subprocess, sys, tempfile
passed = failed = 0
def check(desc, ok):
    global passed, failed
    print(("PASS  " if ok else "FAIL  ") + desc)
    if ok: passed += 1
    else: failed += 1

def parse(text):
    d = {}
    for line in text.strip().splitlines():
        p = line.split()
        if len(p) == 2: d[p[0]] = p[1]
    return d
def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return r.returncode, r.stdout, r.stderr
def same(want, got):
    bad = []
    for k, v in want.items():
        g = got.get(k)
        try: ok = g is not None and abs(float(g) - float(v)) <= 0.11
        except ValueError: ok = g == v
        if not ok: bad.append(f"{k}: expected {v}, got {g}")
    return bad

check("dora.py exists", os.path.exists("dora.py"))
if not os.path.exists("dora.py"):
    print("1 check(s) failed"); sys.exit(1)
tmp = tempfile.mkdtemp()
subprocess.run([sys.executable, "tools/gen_data.py", tmp, "777"], check=True)
cases = [("your data, whole 90 days", "data", "all"), ("your data, first 45 days", "data", "first"), ("your data, last 45 days", "data", "second"),
         ("a different dataset (no hard-coding), whole period", tmp, "all"), ("a different dataset, last 45 days", tmp, "second")]
for name, d, part in cases:
    _, want_txt, _ = run([sys.executable, "tools/expected.py", d, part])
    rc, got_txt, err = run([sys.executable, "dora.py", d, part])
    bad = same(parse(want_txt), parse(got_txt))
    check(f"{name}: all 13 output lines correct" + (f"  -> {bad[0]}" if bad else ""), rc == 0 and not bad)
rc, out, _ = run([sys.executable, "dora.py"])
check("running with no arguments uses ./data and the whole period", rc == 0 and not same(parse(run([sys.executable, "tools/expected.py", "data", "all"])[1]), parse(out)))
rc, _, err = run([sys.executable, "dora.py", "/nonexistent"])
check("a missing data folder gives a non-zero exit code and a message", rc != 0 and err.strip() != "")
print()
print(f"ALL CHECKS PASSED ({passed}/{passed})" if failed == 0 else f"{failed} check(s) failed, {passed} passed")
sys.exit(1 if failed else 0)
