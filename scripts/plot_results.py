
import csv
import re
from pathlib import Path
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "docs" / "results"
OUT = RESULTS / "plots"
OUT.mkdir(parents=True, exist_ok=True)


def read_csv(filename):
    with open(RESULTS / filename, newline="") as f:
        return list(csv.DictReader(f))


def save_plot(filename):
    plt.tight_layout()
    plt.savefig(OUT / filename, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Created: {filename}")


# 1. Hit rate and miss rate comparison
data = read_csv("results_table.csv")

traces = [r["trace"] for r in data]
hits = [float(r["hit_rate_pct"]) for r in data]
misses = [float(r["miss_rate_pct"]) for r in data]

plt.figure(figsize=(11, 5))
plt.bar(traces, hits, label="Hit Rate")
plt.bar(traces, misses, bottom=hits, label="Miss Rate")

plt.ylabel("Percentage (%)")
plt.title("Cache Hit and Miss Rate Comparison")
plt.xticks(rotation=35, ha="right")
plt.ylim(0, 100)
plt.legend()

save_plot("hit_miss_comparison.png")


# 2. AMAT comparison
amat_key = next(
    k for k in data[0]
    if "avg_cycles_per_access" in k
)

plt.figure(figsize=(10, 5))
plt.bar(traces, [float(r[amat_key]) for r in data])

plt.ylabel("Average Cycles per Access")
plt.title("AMAT Comparison Across Traces")
plt.xticks(rotation=35, ha="right")

save_plot("amat_comparison.png")


# 3. Cache configuration sweep
sweep = read_csv("sweep.csv")

block_sizes = sorted({
    int(r["block_bytes"]) for r in sweep
})

plt.figure(figsize=(9, 5))

for block in block_sizes:
    subset = sorted(
        [r for r in sweep if int(r["block_bytes"]) == block],
        key=lambda r: int(r["cache_bytes"])
    )

    plt.plot(
        [int(r["cache_bytes"]) / 1024 for r in subset],
        [float(r["hit_rate_pct"]) for r in subset],
        marker="o",
        label=f"Block size {block} bytes"
    )

plt.xlabel("Cache Size (KB)")
plt.ylabel("Hit Rate (%)")
plt.title("Cache Configuration Sweep")
plt.legend()

save_plot("cache_sweep.png")


# 4. Memory latency sweep
latency = read_csv("lat_sweep.csv")

first = latency[0]

plt.figure(figsize=(11, 6))

for prefix in ("cache", "nocache"):

    columns = [
        c for c in first
        if c.startswith(prefix + "_LAT")
    ]

    columns.sort(
        key=lambda c: int(re.search(r"(\d+)$", c).group(1))
    )

    for row in latency:

        values = [float(row[c]) for c in columns]

        x = [
            int(re.search(r"(\d+)$", c).group(1))
            for c in columns
        ]

        plt.plot(
            x,
            values,
            marker="o",
            label=f"{row['trace']} ({prefix})"
        )

plt.xlabel("Memory Latency (Cycles)")
plt.ylabel("Average Cycles per Access")
plt.title("Memory Latency Impact")
plt.legend(fontsize=7)

save_plot("latency_sweep.png")


print("\nAll plots generated successfully!")
print(f"Output folder: {OUT}")
