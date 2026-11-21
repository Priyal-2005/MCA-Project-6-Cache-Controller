# MCA Project 6: Direct-Mapped Cache Controller

A direct-mapped cache controller written in Verilog, with a main-memory model, a self-checking testbench and trace-driven performance analysis (hit rate, miss rate, AMAT). Phase II adds synthesis (resource use and maximum frequency on an iCE40 FPGA), a write-allocate versus no-write-allocate memory-traffic study and a verification summary.

Course: Modern Computer Architecture, Newton School of Technology

## Team

| Member | Enrollment Number | Role |
|---|---|---|
| Priyal | 2401010354 | Cache Datapath, Performance & Repo Lead |
| Anusha | 2401010344 | Controller, Memory Interface & Synthesis Lead |
| Kashika | 2401010215 | Verification Lead |
| Vaishnavi | 2401010489 | Traces & Plots Lead |
| Sarthak | 2401010420 | Report & Demo Lead |

## Cache parameters

| Parameter | Value |
|---|---|
| Cache size | 1 KB |
| Block size | 16 bytes (4 words) |
| Address width | 32 bits |
| Lines | 64 |
| Address split | `[31:10]` tag (22) / `[9:4]` index (6) / `[3:0]` offset (4) |
| Write policy | Write-through. No-write-allocate by default; the `WRITE_ALLOCATE` parameter switches the controller to write-allocate |
| Memory latency | 4 cycles per word (parameter `LAT`) |

The controller FSM is `IDLE -> LOOKUP -> (REFILL | WRITEMEM) -> DONE`. A `busy` output is high while a request is being processed.
The controller keeps `hits` and `misses` counters, and `mem_reads` and `mem_writes` counters that count the words read from and written to main memory (used to compare the memory traffic of the two write policies).
Cache size and block size are set by the `INDEX_BITS` and `WORD_BITS` parameters in `rtl/dm_cache.v`.

## Repository Structure

```
MCA-Project-6-Cache-Controller/
  README.md                 project idea, team, how to run, video link, report link
  .gitignore
  rtl/
    dm_cache.v              cache datapath + FSM
    main_mem.v              main-memory model + handshake
  tb/
    tb_dm_cache.v           self-checking directed testbench
    tb_trace.v              trace-driven testbench
    tb_write_allocate.v     tests for the write-allocate mode
    tb_lat_sweep.v          same directed tests, used for the LAT 2 / 4 / 8 experiment
    tb_traffic.v            trace-driven memory-traffic count per write policy
  traces/
    sequential.trace  random.trace  repeated.trace  stride16.trace
    stride1024.trace  matrix_rowmajor.trace  matrix_colmajor.trace
    writes.trace
  scripts/
    trace_gen.py            trace generator
    run_all.sh              runs every trace and prints the summary
    plot_results.py         generates the plots in docs/results/plots/ from the CSV files
    run_traffic.sh          write-allocate vs no-write-allocate traffic comparison
    run_synth.sh            Yosys + nextpnr synthesis flow (resources, maximum frequency)
    plot_memory_traffic.py  memory-traffic plot
    plot_resource_utilization.py  resource comparison chart
  docs/
    address_fields.md       tag / index / offset working
    verification_summary.md Phase II verification results
    diagrams/               block_diagram.png, cache_architecture.md, fsm.md (FSM description and diagram)
    waveforms/              annotated hit / miss / conflict screenshots
    synthesis/              synthesis.md, resource_utilization.csv, logs/, screenshots, syn_wrap.v (timing harness)
    results/                results tables, sweep CSVs, analysis.md, test screenshots
      plots/                hit/miss rate, AMAT, cache size sweep, latency sweep, memory traffic
    (results/ also holds write_policy_traffic.csv and write_policy_traffic.md)
  report/
    MCA_Project6_Report.pdf IEEE report (Phase I now, final in Phase II)
    source/                 Word or LaTeX source
```

## How to run

Requires [Icarus Verilog](https://steveicarus.github.io/iverilog/) and optionally GTKWave (or the Surfer / WaveTrace extension in VS Code, if GTKWave is not available).

```bash
brew install icarus-verilog
```

Run the self-checking testbench (expect `ALL TESTS PASSED`):

```bash
iverilog -g2012 -o sim rtl/main_mem.v rtl/dm_cache.v tb/tb_dm_cache.v
vvp sim
```

View the waveform:

```bash
gtkwave dm_cache.vcd
```

Without GTKWave, open `dm_cache.vcd` in Surfer or WaveTrace. The stored tag and valid bit of the indexed line are visible as `dbg_stored_tag` and `dbg_valid`.

Run the write-allocate tests (expect `ALL WRITE-ALLOCATE TESTS PASSED`):

```bash
iverilog -g2012 -o sim_wa rtl/main_mem.v rtl/dm_cache.v tb/tb_write_allocate.v
vvp sim_wa
```

Run the memory-latency experiment (change `LAT` to 2, 4 or 8; results are in `docs/results/lat_2_4_8_sweep.csv`):

```bash
iverilog -g2012 -P tb_dm_cache.LAT=8 -o sim_lat rtl/main_mem.v rtl/dm_cache.v tb/tb_lat_sweep.v
vvp sim_lat
```

Generate the traces:

```bash
mkdir -p traces
python3 scripts/trace_gen.py
```

Run a trace:

```bash
iverilog -g2012 -o sim_trace rtl/main_mem.v rtl/dm_cache.v tb/tb_trace.v
vvp sim_trace +TRACE=traces/random.trace
```

Run all traces:

```bash
bash scripts/run_all.sh
```

Generate the plots (needs `matplotlib`; reads the CSV files in `docs/results/`):

```bash
pip3 install matplotlib
python3 scripts/plot_results.py
```

Run the write-allocate versus no-write-allocate memory-traffic comparison (writes `docs/results/write_policy_traffic.csv`):

```bash
bash scripts/run_traffic.sh
```

Run a trace with write-allocate switched on:

```bash
iverilog -g2012 -P tb_trace.WRITE_ALLOCATE=1 -o sim_trace rtl/main_mem.v rtl/dm_cache.v tb/tb_trace.v
vvp sim_trace +TRACE=traces/writes.trace
```

Synthesis (Yosys + nextpnr-ice40 for a Lattice iCE40 HX8K; Vivado was not available). It writes the logs, `resource_utilization.csv` and the post-synthesis simulation results to `docs/synthesis/`:

```bash
brew install yosys nextpnr-ice40 icestorm
bash scripts/run_synth.sh
```

The generic cell count alone (this is not the real cost, see `docs/synthesis/synthesis.md`):

```bash
yosys -p "read_verilog rtl/dm_cache.v; synth -top dm_cache; stat"
```

Generate the memory-traffic plot and the resource comparison chart:

```bash
python3 scripts/plot_memory_traffic.py
python3 scripts/plot_resource_utilization.py
```

## Verification

`tb/tb_dm_cache.v` is self-checking: every read is compared with a reference memory (`ref_mem`) and the run ends with `ALL TESTS PASSED` or an error count. It has seven test groups:

1. First access after reset (cold miss, tag RAM starts at 0 so a missing valid check is caught)
2. Repeated reads (hits)
3. Conflict misses (same index, different tag)
4. Write hit and read-back
5. Write miss with no-allocate (the write must not fill a line)
6. Pseudo-random reads
7. Fill all 64 cache lines

The testbench also checks that `busy` is high while a request is processed and low when it completes. The write-allocate mode has its own testbench, `tb/tb_write_allocate.v`. `tb/tb_trace.v` takes a `WRITE_ALLOCATE` parameter, and `tb/tb_traffic.v` counts memory traffic per write policy. Every trace passes the data check under both write policies. After synthesis, the iCE40 netlist was simulated against the trace testbench and passes on all nine traces (the eight shared traces plus `write_stream`) for both the 1 KB and the 512 B configuration. The full list of tests and results is in `docs/verification_summary.md`.

Fault injection: removing the valid-bit check from `dm_cache.v` makes the testbench fail (275 errors, first at the first access after reset), so the tests do detect that bug. Screenshots are in `docs/results/`:

- `Directed test cases PASS.png`, `baseline_all_tests_passed.png`: all tests passing
- `valid_check_removal_first_access_error.png`, `valid_check_removal_275_failures.png`: the injected bug being caught

Annotated waveforms are in `docs/waveforms/`: `read_miss_refill.png`, `Read Hit Waveform_ Immediate Cache Success.png`, `Conflict Miss Waveform Annotation.png`, and `WriteMiss_with_WriteAllocate.png` (write miss with write-allocate: REFILL, then WRITEMEM, then DONE). The signals `dbg_stored_tag` and `dbg_valid` in `dm_cache.v` show the tag and valid bit of the indexed line in the waveform.

## Results

Measured with Icarus Verilog, 1 KB / 16 B blocks / LAT = 4. A hit takes 3 cycles and a read miss 23 cycles (miss penalty 20). Every trace passed the data check.

| Trace | Hit rate | AMAT (cycles) |
|---|---|---|
| sequential | 75.0% | 8.00 |
| random | 23.9% | 18.21 |
| repeated | 99.5% | 3.10 |
| stride16 | 0.0% | 23.00 |
| stride1024 | 0.0% | 23.00 |
| matrix_rowmajor | 75.0% | 8.00 |
| matrix_colmajor | 0.0% | 23.00 |
| writes | 71.1% | 8.53 |

A no-cache access costs LAT = 4 cycles, so at LAT 4 the cache only pays off on the repeated trace. Details, the no-cache baseline, the LAT sweep and the cache/block size sweep are in `docs/results/analysis.md` and the CSV files in `docs/results/`. Plots are in `docs/results/plots/`: hit and miss rate per trace, AMAT per trace, the cache size and block size sweep (random trace), the latency sweep with and without a cache, and the memory traffic of the two write policies. The resource comparison chart for synthesis is `docs/synthesis/resource_comparison.png`. All results in the table above use the default no-write-allocate policy.

Note on two different "repeated" results: the trace `repeated.trace` (800 accesses, 99.5% hits, 3.10 cycles) and test T2 in `tb/tb_lat_sweep.v` (128 accesses, 96% hits, 3.6 cycles at LAT 4) are different workloads, so their numbers differ. The LAT 2/4/8 experiment in `docs/results/lat_2_4_8_sweep.csv` comes from the six tests in `tb_lat_sweep.v`, not from the trace files.

### Write policy: memory traffic

1 KB cache, 16 B blocks, LAT 4. `mem_reads` and `mem_writes` count the words moved between the cache and main memory. Data: `docs/results/write_policy_traffic.csv`, write-up: `docs/results/write_policy_traffic.md`, plot: `docs/results/plots/memory_traffic_comparison.png`.

| Trace | Policy | Hit rate | `mem_reads` | `mem_writes` | Total words | Avg cycles |
|---|---|---|---|---|---|---|
| `writes` | no-write-allocate | 71.1% | 24 | 18 | 42 | 8.53 |
| `writes` | write-allocate | 84.2% | 24 | 18 | 42 | 8.53 |
| `write_stream` | no-write-allocate | 0.0% | 0 | 512 | 512 | 8.00 |
| `write_stream` | write-allocate | 75.0% | 512 | 512 | 1024 | 13.00 |

The eight read-only traces give identical results under both policies. Write-allocate raises the hit rate when the written blocks are used again (`writes`), but it doubles the memory traffic when data is written once and never read (`write_stream`). The AMAT formula (3 + miss rate x 20) only holds for read-dominated traces: use the measured average for traces with writes (for `write_stream` it is 8.00 cycles, not 23.00).

### Synthesis (Lattice iCE40 HX8K, Yosys + nextpnr-ice40)

| Configuration | Logic cells | LUT4 | Flip-flops | Block RAM | Maximum frequency |
|---|---|---|---|---|---|
| 1 KB, 64 lines (default) | 740 / 7680 (9%) | 491 | 383 | 4 / 32 (12%) | 79.85 MHz |
| 512 B, 32 lines | 662 / 7680 (8%) | 412 | 352 | 4 / 32 (12%) | 79.90 MHz |

The maximum frequency is the post-routing figure from nextpnr-ice40 and is specific to this device. The critical path (12.52 ns for 1 KB) is the hit path: tag RAM read, 22-bit tag compare, then the control decision, and 62% of it is routing delay. The generic Yosys flow gives 30,922 cells and 9,935 flip-flops for 1 KB, but that only reflects the cache arrays being flattened into flip-flops because the generic flow has no memory primitives: it is not the cost of the design. The synthesised netlist passes the trace testbench at gate level on all nine traces. Details, limits and the reproduce steps: `docs/synthesis/synthesis.md`.

## Links

- Phase I video: https://drive.google.com/file/d/1DD9B_PW0EQaov7HUue0Nbp39FaIN0b6A/view?usp=sharing
- IEEE report: `report/MCA_Project6_Report.pdf`
