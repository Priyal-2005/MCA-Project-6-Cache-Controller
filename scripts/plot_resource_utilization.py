import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
CSV_FILE = ROOT / "docs" / "synthesis" / "resource_utilization.csv"
OUTPUT = ROOT / "docs" / "synthesis" / "resource_comparison.png"

with open(CSV_FILE, newline="") as f:
    data = list(csv.DictReader(f))

configs = [row["config"] for row in data]

fig, axes = plt.subplots(2, 2, figsize=(13, 9))
x = np.arange(len(configs))
width = 0.35

def comparison(ax, metrics, labels, title, ylabel):
    for i, (metric, label) in enumerate(zip(metrics, labels)):
        values = [float(row[metric]) for row in data]
        bars = ax.bar(
            x + (i - (len(metrics) - 1) / 2) * width,
            values,
            width,
            label=label
        )
        ax.bar_label(bars, padding=3, fmt="%.2f" if metric == "fmax_mhz" else "%.0f")

    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xticks(x)
    ax.set_xticklabels(configs)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

comparison(
    axes[0, 0],
    ["generic_cells", "generic_ffs"],
    ["Generic Cells", "Generic Flip-Flops"],
    "Generic Synthesis Resources",
    "Cell Count"
)

comparison(
    axes[0, 1],
    ["ice40_lut4", "ice40_carry", "ice40_ffs"],
    ["LUT4", "Carry Cells", "Flip-Flops"],
    "ICE40 Technology-Mapped Resources",
    "Resource Count"
)

comparison(
    axes[1, 0],
    ["pnr_logic_pct", "pnr_bram_pct"],
    ["Logic Utilization", "BRAM Utilization"],
    "Place-and-Route Device Utilization",
    "Utilization (%)"
)

comparison(
    axes[1, 1],
    ["fmax_mhz"],
    ["Maximum Frequency"],
    "Maximum Operating Frequency",
    "Frequency (MHz)"
)

fig.suptitle(
    "Resource Utilization Comparison: 1KB vs 512B Cache",
    fontsize=15
)

fig.tight_layout()
fig.savefig(OUTPUT, dpi=300, bbox_inches="tight")
plt.close(fig)

print(f"Created: {OUTPUT}")
print(
    "Takeaway: The 1KB cache uses more logic resources, "
    "while both configurations use the same BRAM utilization "
    "and achieve nearly identical maximum frequencies."
)
