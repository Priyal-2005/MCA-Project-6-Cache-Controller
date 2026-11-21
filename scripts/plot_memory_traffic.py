
import csv
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
CSV_FILE = ROOT / "docs" / "results" / "write_policy_traffic.csv"
OUT_DIR = ROOT / "docs" / "results" / "plots"

OUT_DIR.mkdir(parents=True, exist_ok=True)

with open(CSV_FILE, newline="") as f:
    data = list(csv.DictReader(f))

traces = ["writes", "write_stream"]
policies = ["no-write-allocate", "write-allocate"]

metrics = [
    ("mem_reads", "Main Memory Reads"),
    ("mem_writes", "Main Memory Writes")
]

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
x = np.arange(len(traces))
width = 0.35

for ax, (metric, title) in zip(axes, metrics):
    for i, policy in enumerate(policies):
        values = []
        for trace in traces:
            row = next(
                r for r in data
                if r["trace"] == trace and r["policy"] == policy
            )
            values.append(int(row[metric]))

        bars = ax.bar(
            x + (i - 0.5) * width,
            values,
            width,
            label=policy
        )
        ax.bar_label(bars, padding=3)

    ax.set_title(title)
    ax.set_ylabel("Memory Words")
    ax.set_xticks(x)
    ax.set_xticklabels(traces)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

fig.suptitle("Memory Traffic: Write-Allocate vs No-Write-Allocate")
fig.tight_layout()

output = OUT_DIR / "memory_traffic_comparison.png"
fig.savefig(output, dpi=300, bbox_inches="tight")
plt.close(fig)

print(f"Created: {output}")
print(
    "Takeaway: Write-allocate increases traffic for write_stream, "
    "while writes has identical total traffic under both policies."
)

