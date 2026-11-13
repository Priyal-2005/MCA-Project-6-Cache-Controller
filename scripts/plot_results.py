
import csv
import re
from pathlib import Path
import matplotlib.pyplot as plt


# --------------------------------------------------
# PATHS AND HELPERS
# --------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "docs" / "results"
OUT = RESULTS / "plots"
DOCS = ROOT / "docs"

OUT.mkdir(parents=True, exist_ok=True)


def read_csv(filename):
    with open(RESULTS / filename, newline="") as f:
        return list(csv.DictReader(f))


def save_plot(filename):
    plt.tight_layout()
    plt.savefig(OUT / filename, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Created: {OUT / filename}")


def save_docs_plot(filename):
    plt.savefig(DOCS / filename, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Created: {DOCS / filename}")


# --------------------------------------------------
# 1. HIT RATE AND MISS RATE COMPARISON
# --------------------------------------------------

data = read_csv("results_table.csv")

traces = [r["trace"] for r in data]
hits = [float(r["hit_rate_pct"]) for r in data]
misses = [float(r["miss_rate_pct"]) for r in data]

plt.figure(figsize=(11, 5))
plt.bar(traces, hits, label="Hit Rate")
plt.bar(traces, misses, bottom=hits, label="Miss Rate")

plt.xlabel("Memory Access Trace")
plt.ylabel("Percentage (%)")
plt.title("Cache Hit and Miss Rate Comparison")
plt.xticks(rotation=35, ha="right")
plt.ylim(0, 100)
plt.legend()

save_plot("hit_miss_comparison.png")


# --------------------------------------------------
# 2. AMAT COMPARISON
# --------------------------------------------------

amat_key = next(
    k for k in data[0]
    if "avg_cycles_per_access" in k
)

plt.figure(figsize=(10, 5))
plt.bar(traces, [float(r[amat_key]) for r in data])

plt.xlabel("Memory Access Trace")
plt.ylabel("Average Cycles per Access")
plt.title("AMAT Comparison Across Traces")
plt.xticks(rotation=35, ha="right")

save_plot("amat_comparison.png")



# 3. Cache configuration sweep
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
PLOTS_DIR = ROOT / "docs" / "results" / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

# Read sweep data
sweep_file = next(ROOT.rglob("sweep.csv"))
sweep_df = pd.read_csv(sweep_file)

# IMPORTANT: Only use random trace for this plot
random_df = sweep_df[sweep_df["trace"] == "random"].copy()

plt.figure(figsize=(9, 5))

for block_size in sorted(random_df["block_bytes"].unique()):
    subset = random_df[random_df["block_bytes"] == block_size].sort_values("cache_bytes")

    cache_kb = subset["cache_bytes"] / 1024

    plt.plot(
        cache_kb,
        subset["hit_rate_pct"],
        marker="o",
        label=f"Block size: {block_size} bytes"
    )

plt.xlabel("Cache Size (KB)")
plt.ylabel("Hit Rate (%)")
plt.title("Cache Size Sweep — Random Trace")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(PLOTS_DIR / "cache_sweep.png", dpi=300)
plt.close()


# 4. Memory latency sweep
lat_file = next(ROOT.rglob("lat_sweep.csv"))
lat_df = pd.read_csv(lat_file)

# Identify cache and no-cache latency columns
cache_cols = sorted(
    [c for c in lat_df.columns if c.startswith("cache_LAT")],
    key=lambda c: int(c.replace("cache_LAT", ""))
)

nocache_cols = sorted(
    [c for c in lat_df.columns if c.startswith("nocache_LAT")],
    key=lambda c: int(c.replace("nocache_LAT", ""))
)

latencies = [int(c.replace("cache_LAT", "")) for c in cache_cols]

plt.figure(figsize=(9, 5))

# One solid cache line for each trace
for _, row in lat_df.iterrows():
    plt.plot(
        latencies,
        [row[c] for c in cache_cols],
        marker="o",
        label=f"{row['trace']} (cache)"
    )

# One dashed no-cache line (same values across traces)
if nocache_cols:
    first_row = lat_df.iloc[0]
    plt.plot(
        latencies,
        [first_row[c] for c in nocache_cols],
        marker="o",
        linestyle="--",
        linewidth=2,
        label="No cache"
    )

plt.xlabel("Main Memory Latency (Cycles)")
plt.ylabel("Average Cycles per Access")
plt.title("Performance vs Memory Latency")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(PLOTS_DIR / "latency_sweep.png", dpi=300)
plt.close()

print("Updated cache_sweep.png and latency_sweep.png successfully.")
