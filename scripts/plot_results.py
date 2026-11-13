
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


# --------------------------------------------------
# 3. CACHE CONFIGURATION SWEEP
# FIX: Plot only random trace to avoid mixing
# random and matrix_colmajor results.
# --------------------------------------------------

sweep = read_csv("sweep.csv")

block_sizes = sorted({
    int(r["block_bytes"]) for r in sweep
})

plt.figure(figsize=(9, 5))

for block in block_sizes:

    subset = sorted(
        [
            r for r in sweep
            if r["trace"] == "random"
            and int(r["block_bytes"]) == block
        ],
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
plt.title("Cache Configuration Sweep — Random Trace")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.5)

save_plot("cache_sweep.png")


# --------------------------------------------------
# 4. MEMORY LATENCY SWEEP
# FIX: One no-cache line instead of repeating
# identical no-cache lines for every trace.
# --------------------------------------------------

latency = read_csv("lat_sweep.csv")
first = latency[0]

plt.figure(figsize=(11, 6))

# Cache lines: one for each trace
cache_columns = [
    c for c in first
    if c.startswith("cache_LAT")
]

cache_columns.sort(
    key=lambda c: int(re.search(r"(\d+)$", c).group(1))
)

cache_x = [
    int(re.search(r"(\d+)$", c).group(1))
    for c in cache_columns
]

for row in latency:

    cache_values = [
        float(row[c]) for c in cache_columns
    ]

    plt.plot(
        cache_x,
        cache_values,
        marker="o",
        label=f"{row['trace']} (cache)"
    )


# One shared no-cache line
nocache_columns = [
    c for c in first
    if c.startswith("nocache_LAT")
]

nocache_columns.sort(
    key=lambda c: int(re.search(r"(\d+)$", c).group(1))
)

nocache_x = [
    int(re.search(r"(\d+)$", c).group(1))
    for c in nocache_columns
]

nocache_values = [
    float(first[c]) for c in nocache_columns
]

plt.plot(
    nocache_x,
    nocache_values,
    linestyle="--",
    linewidth=2,
    color="black",
    label="No cache"
)

plt.xlabel("Memory Latency (Cycles)")
plt.ylabel("Average Cycles per Access")
plt.title("Memory Latency Impact")
plt.legend(fontsize=8)
plt.grid(True, linestyle="--", alpha=0.5)

save_plot("latency_sweep.png")


# --------------------------------------------------
# 5. ADDITIONAL CHARTS REQUESTED BY PRIYAL
# --------------------------------------------------


# 5A and 5B. Separate cache sweep charts

def make_trace_sweep_chart(trace_name, output_filename, takeaway):

    fig, ax = plt.subplots(figsize=(9, 5.5))

    for block in (8, 16, 32):

        subset = sorted(
            [
                r for r in sweep
                if r["trace"] == trace_name
                and int(r["block_bytes"]) == block
            ],
            key=lambda r: int(r["cache_bytes"])
        )

        ax.plot(
            [int(r["cache_bytes"]) for r in subset],
            [float(r["hit_rate_pct"]) for r in subset],
            marker="o",
            linewidth=2,
            label=f"{block} B block"
        )

    ax.set_xlabel("Cache Size")
    ax.set_ylabel("Hit Rate (%)")
    ax.set_title(f"Hit Rate vs Cache Size — {trace_name}")
    ax.set_xticks([256, 512, 1024, 2048])
    ax.set_xticklabels(["256 B", "512 B", "1 KB", "2 KB"])
    ax.set_ylim(0, 100)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend()

    fig.subplots_adjust(bottom=0.23)
    fig.text(
        0.5, 0.06,
        takeaway,
        ha="center",
        fontsize=9,
        wrap=True
    )

    save_docs_plot(output_filename)


make_trace_sweep_chart(
    "random",
    "random_cache_sweep.png",
    "Random access hit rates vary with cache capacity and block size."
)

make_trace_sweep_chart(
    "matrix_colmajor",
    "matrix_colmajor_cache_sweep.png",
    "Column-major access shows a 0% hit rate across the tested configurations."
)


# 5C. Hit rate comparison for all 8 traces
# Baseline results: 1 KB cache / 16 B block

fig, ax = plt.subplots(figsize=(11, 5.5))

traces = [r["trace"] for r in data]
hit_rates = [float(r["hit_rate_pct"]) for r in data]

bars = ax.bar(traces, hit_rates)

ax.set_xlabel("Memory Access Trace")
ax.set_ylabel("Hit Rate (%)")
ax.set_title("Hit Rate Across All 8 Traces (1 KB Cache / 16 B Block)")
ax.set_ylim(0, 110)
ax.tick_params(axis="x", rotation=35)
ax.grid(axis="y", linestyle="--", alpha=0.5)

for bar, rate in zip(bars, hit_rates):

    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 1,
        f"{rate:.1f}%",
        ha="center",
        fontsize=8
    )

fig.subplots_adjust(bottom=0.32)

fig.text(
    0.5, 0.025,
    "The chart highlights how different memory access patterns affect cache hit rate.",
    ha="center",
    fontsize=9,
    wrap=True
)

save_docs_plot("trace_hit_rates.png")


# --------------------------------------------------
# FINISHED
# --------------------------------------------------

print("\nAll plots generated successfully!")
print(f"Existing plots folder: {OUT}")
print(f"Additional charts folder: {DOCS}")
