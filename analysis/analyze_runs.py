"""Audit two student-code runs and reproduce their median-based cutoff table.

From the project root: python analysis/analyze_runs.py
Uses Python standard library for the audit and tables; matplotlib only for the plot.
"""

import csv
import hashlib
import math
import re
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNS = (ROOT / "results" / "run1", ROOT / "results" / "run2")
CUTOFFS = (0, 4, 6, 7, 8, 9, 10, 11, 12, 14, 16, 20)
ROUNDS = 7
PATTERN = re.compile(r"(random|sorted|reverse|few_values)_n(\d+)_s(\d+)\.txt")


def geometric_mean(values):
    return math.exp(statistics.mean(math.log(value) for value in values))


def load_run(folder):
    source = (folder / "StudentMergeSort.java").read_bytes()
    assert source == (ROOT / "src" / "StudentMergeSort.java").read_bytes(), folder
    source_hash = hashlib.sha256(source).hexdigest().upper()
    assert source_hash in (folder / "environment.txt").read_text(encoding="utf-8-sig")
    assert "PASS sorted + stable: 43230 cases" in (folder / "check.log").read_text(encoding="utf-16")
    log = (folder / "console.log").read_text(encoding="utf-16")
    assert log.count("Done: ") == 24 and "Saved " in log

    listed = list(csv.DictReader((folder / "data_sha256.csv").open(encoding="utf-8-sig")))
    assert len(listed) == 24
    assert len({row["dataset"] for row in listed}) == 24
    for row in listed:
        assert hashlib.sha256((ROOT / "data" / row["dataset"]).read_bytes()).hexdigest().upper() == row["sha256"].upper()

    with (folder / "measurements.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 24 * len(CUTOFFS) * ROUNDS
    times = defaultdict(list)
    by_round = defaultdict(dict)
    seen = set()
    for row in rows:
        dataset = row["dataset"]
        match = PATTERN.fullmatch(dataset)
        assert match is not None
        assert (match[1], int(match[2]), int(match[3])) == (row["kind"], int(row["n"]), int(row["seed"]))
        cutoff, round_number, duration = int(row["cutoff"]), int(row["round"]), int(row["elapsed_ns"])
        key = (dataset, cutoff, round_number)
        assert key not in seen and cutoff in CUTOFFS and 0 <= round_number < ROUNDS and duration > 0
        seen.add(key)
        times[dataset, cutoff].append(duration)
        by_round[dataset, round_number][cutoff] = duration
    datasets = sorted({dataset for dataset, _ in times})
    assert len(datasets) == 24 and len(times) == 24 * len(CUTOFFS)
    assert set(datasets) == {row["dataset"] for row in listed}
    assert all(len(values) == ROUNDS for values in times.values())
    assert len(by_round) == 24 * ROUNDS and all(len(values) == len(CUTOFFS) for values in by_round.values())
    median = {key: statistics.median(values) for key, values in times.items()}
    ratios = {k: geometric_mean(median[d, 7] / median[d, k] for d in datasets) for k in CUTOFFS}
    paired = {k: geometric_mean(by_round[d, r][7] / by_round[d, r][k] for d in datasets for r in range(ROUNDS)) for k in CUTOFFS}
    spikes = sum(value > 2 * median[key] for key, values in times.items() for value in values)
    return datasets, median, ratios, paired, spikes


def write_csv(path, header, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def main():
    runs = [load_run(folder) for folder in RUNS]
    assert runs[0][0] == runs[1][0]
    summary = []
    for k in CUTOFFS:
        a, b = (run[2][k] for run in runs)
        summary.append((k, f"{(a-1)*100:.4f}", f"{(b-1)*100:.4f}", f"{(math.sqrt(a*b)-1)*100:.4f}",
                        sum(runs[0][1][d, k] < runs[0][1][d, 7] for d in runs[0][0]),
                        sum(runs[1][1][d, k] < runs[1][1][d, 7] for d in runs[1][0])))
    write_csv(ROOT / "analysis" / "summary.csv", ("cutoff", "run1_pct", "run2_pct", "combined_pct", "run1_wins", "run2_wins"), summary)
    by_kind = []
    for kind in ("random", "sorted", "reverse", "few_values"):
        ds = [d for d in runs[0][0] if d.startswith(kind + "_")]
        for k in CUTOFFS:
            values = [geometric_mean(run[1][d, 7] / run[1][d, k] for d in ds) for run in runs]
            by_kind.append((kind, k, f"{(values[0]-1)*100:.4f}", f"{(values[1]-1)*100:.4f}"))
    write_csv(ROOT / "analysis" / "by_kind.csv", ("kind", "cutoff", "run1_pct", "run2_pct"), by_kind)
    lines = ["PASS: two sessions each have 24 datasets x 12 cutoffs x 7 rounds; no missing or duplicate rows.",
             "Student source, 24 dataset SHA-256 hashes, 43,230-case check logs, and completion logs verified.",
             f"Spikes over 2x own dataset/cutoff median: {runs[0][4]} and {runs[1][4]} / 2016.",
             f"k=10 vs 7 by dataset medians: {(runs[0][2][10]-1)*100:+.2f}% and {(runs[1][2][10]-1)*100:+.2f}%.",
             f"k=10 vs 7 by per-round pairing (sensitivity check): {(runs[0][3][10]-1)*100:+.2f}% and {(runs[1][3][10]-1)*100:+.2f}%.",
             "The different summary signs in run 1 and the between-run timing drift preclude a precise optimum claim."]
    (ROOT / "analysis" / "audit.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))

    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib missing: numeric audit is complete; plot skipped")
        return
    plt.rcParams["font.family"] = "DejaVu Sans"
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    selected = [k for k in CUTOFFS if 6 <= k <= 16]
    for i, run in enumerate(runs, 1):
        ax.plot(selected, [(run[2][k] - 1) * 100 for k in selected], color="black",
                linestyle="-" if i == 1 else "--", marker="o" if i == 1 else "s", label=f"Phiên {i}")
    ax.axhline(0, color="0.5", linewidth=1)
    ax.set_xticks(selected)
    ax.set_xlabel("Cutoff k (số phần tử)")
    ax.set_ylabel("Chênh lệch tốc độ so với k=7 (%)")
    ax.set_title("Mergesort: hai phiên đo độc lập")
    ax.legend(frameon=False)
    ax.grid(axis="y", color="0.85")
    fig.tight_layout()
    fig.savefig(ROOT / "analysis" / "cutoff_two_runs.png", dpi=180, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main()
