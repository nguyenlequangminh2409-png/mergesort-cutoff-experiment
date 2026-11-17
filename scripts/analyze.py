"""Summarize per-dataset medians and geometric-mean speedups; Python 3 stdlib."""
import csv
import math
import statistics
import sys
from collections import defaultdict

if len(sys.argv) != 2:
    raise SystemExit("Usage: python analyze.py measurements.csv")

samples = defaultdict(list)
with open(sys.argv[1], newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        samples[(row["dataset"], row["kind"], int(row["n"]), int(row["cutoff"]))].append(int(row["elapsed_ns"]))

medians = {key: statistics.median(values) for key, values in samples.items()}
cases = sorted({(d, kind, n) for d, kind, n, k in medians})
cutoffs = sorted({k for d, kind, n, k in medians})
if 7 not in cutoffs:
    raise SystemExit("Include cutoff 7 as a reference")
for d, kind, n in cases:
    if any((d, kind, n, k) not in medians for k in cutoffs):
        raise SystemExit(f"Missing cutoff for {d}")

print("Each value is a median over timed rounds. Relative speed is baseline k=7 / candidate (>1 means faster).")
print("cutoff,cases,geomean_speedup_vs_7,wins_vs_7,mean_median_ms")
ranking = []
for k in cutoffs:
    speedups = [medians[d, kind, n, 7] / medians[d, kind, n, k] for d, kind, n in cases]
    gm = math.exp(statistics.mean(map(math.log, speedups)))
    mean_ms = statistics.mean(medians[d, kind, n, k] / 1e6 for d, kind, n in cases)
    wins = sum(x > 1 for x in speedups)
    print(f"{k},{len(cases)},{gm:.4f},{wins},{mean_ms:.3f}")
    ranking.append((gm, k))
print(f"Best measured aggregate: k={max(ranking)[1]} (differences around 1–3% merit another run).")
print("Best k by n/kind (median across seeds; descriptive only):")
for n, kind in sorted({(n, kind) for d, kind, n in cases}):
    ks = [(statistics.median(medians[d, kind, size, k] for d, kd, size in cases if kd == kind and size == n), k)
          for k in cutoffs]
    value, best = min(ks)
    print(f"n={n:>6} {kind:>10}: k={best:>2} median={value / 1e6:.3f} ms")
