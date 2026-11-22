# Report Source Package — Modern Computer Architecture (Project 6)
## Team T109 | Verilog Direct-Mapped Cache Controller Phase II Report

This directory contains the complete source code, datasets, figures, and build scripts required to compile the IEEE-formatted technical report:
`MCA_Project6_Report.pdf` (located at `../MCA_Project6_Report.pdf`).

---

### Directory Contents

- **`MCA_Project6_Report.tex`**: Complete IEEE conference report source written with `IEEEtran` document class. Contains all mathematical formulations, tables, experimental evaluations, and citations.
- **`references.bib`**: BibTeX bibliography database containing all 7 IEEE citations ([1] through [7]).
- **`figures/`**: High-resolution image assets embedded in the report:
  - `block_diagram.png`: Architectural block diagram of the cache controller and memory interface (Fig. 1).
  - `fsm_diagram.png`: 5-state synchronous FSM state transition diagram (Fig. 2).
  - `hit_miss_comparison.png`: Cache hit/miss counts across 8 evaluation traces (Fig. 3).
  - `amat_comparison.png`: Average Memory Access Time (AMAT) across workloads (Fig. 4).
  - `latency_sweep.png`: Latency sweep curves from LAT = 4 to LAT = 100 (Fig. 5).
  - `memory_traffic_comparison.png`: Word bus traffic comparison across write policies (Fig. 6).
  - `resource_comparison.png`: Lattice iCE40 FPGA resource utilization comparison (Fig. 7).
  - `read_miss_refill.png`: Annotated simulation waveform showing 4-word refill sequence (Fig. 8).
  - `valid_check_removal_275_failures.png`: Fault-injection simulation plot confirming 275 caught errors (Fig. 9).
- **`data/`**: Machine-readable CSV experimental datasets generated from testbenches:
  - `results_table.csv`: 8 benchmark and synthetic traces hit/miss/AMAT results (Table I).
  - `lat_sweep.csv`: Cache vs. no-cache latency comparisons across memory delays (Table II).
  - `lat_2_4_8_sweep.csv`: Parameter sweep results across LAT in {2, 4, 8} (Table III).
  - `write_policy_traffic.csv`: Memory bus traffic words across write policies (Table IV).
  - `resource_utilization.csv`: Multi-stage FPGA synthesis and timing metrics (Table V).
- **`IEEEtran.cls`**: IEEE conference document class used by the `.tex` file.

---

### How to Compile the Report

The PDF `../MCA_Project6_Report.pdf` is built from `MCA_Project6_Report.tex` with LaTeX. From this `Source/` directory:
```bash
latexmk -pdf MCA_Project6_Report.tex
cp MCA_Project6_Report.pdf ..
```
(or run `pdflatex MCA_Project6_Report.tex` twice). The reference list is written inside the `.tex` file, so BibTeX is not needed. If you change a number in the report, change it in the `.tex` and rebuild; do not edit the PDF directly.
