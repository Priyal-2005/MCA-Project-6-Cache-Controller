# MCA Project 6: Direct-Mapped Cache Controller

A direct-mapped cache controller written in Verilog, with a main-memory model, a self-checking testbench, trace-driven performance analysis (hit rate, miss rate, AMAT) and synthesis results.

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
  traces/
    sequential.trace  random.trace  repeated.trace  stride16.trace
    stride1024.trace  matrix_rowmajor.trace  matrix_colmajor.trace
    writes.trace
  scripts/
    trace_gen.py            trace generator
    run_all.sh              runs every trace and prints the summary
    plot_results.py         generates the plots in docs/results/plots/ from the CSV files
  docs/
    address_fields.md       tag / index / offset working
    diagrams/               block_diagram.png, cache_architecture.md, fsm.md (FSM description and diagram)
    waveforms/              annotated hit / miss / conflict screenshots
    synthesis/              Vivado or Yosys reports and screenshots
    results/                results tables, sweep CSVs, analysis.md, test screenshots
      plots/                hit/miss rate, AMAT, cache size sweep, latency sweep
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

Synthesis (resource count with Yosys; Vivado for utilization and timing):

```bash
yosys -p "read_verilog rtl/dm_cache.v; synth -top dm_cache; stat"
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

The testbench also checks that `busy` is high while a request is processed and low when it completes. The write-allocate mode has its own testbench, `tb/tb_write_allocate.v`.

Fault injection: removing the valid-bit check from `dm_cache.v` makes the testbench fail (275 errors, first at the first access after reset), so the tests do detect that bug. Screenshots are in `docs/results/`:

- `Directed test cases PASS.png`, `baseline_all_tests_passed.png`: all tests passing
- `valid_check_removal_first_access_error.png`, `valid_check_removal_275_failures.png`: the injected bug being caught

Annotated waveforms are in `docs/waveforms/`: `read_miss_refill.png`, `Read Hit Waveform_ Immediate Cache Success.png`, `Conflict Miss Waveform Annotation.png`. The signals `dbg_stored_tag` and `dbg_valid` in `dm_cache.v` show the tag and valid bit of the indexed line in the waveform.

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

A no-cache access costs LAT = 4 cycles, so at LAT 4 the cache only pays off on the repeated trace. Details, the no-cache baseline, the LAT sweep and the cache/block size sweep are in `docs/results/analysis.md` and the CSV files in `docs/results/`. Plots are in `docs/results/plots/`: hit and miss rate per trace, AMAT per trace, the cache size and block size sweep (random trace), and the latency sweep with and without a cache. All results above use the default no-write-allocate policy.

Still to be added: synthesis numbers.

## Links

- Phase I video: _to be added_
- IEEE report: `report/MCA_Project6_Report.pdf` (to be added)
