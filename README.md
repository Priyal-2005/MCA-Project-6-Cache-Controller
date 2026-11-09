# MCA Project 6: Direct-Mapped Cache Controller

A direct-mapped cache controller written in Verilog, with a main-memory model, a self-checking testbench, trace-driven performance analysis (hit rate, miss rate, AMAT) and synthesis results.

Course: Modern Computer Architecture, Newton School of Technology

## Team

| Member | Enrollment Number | Role |
|---|---|---|
| Priyal | 2401010354 | Cache Datapath, Performance & Repo Lead |
| Anusha | 240 | Controller, Memory Interface & Synthesis Lead |
| Kashika | 240 | Verification Lead |
| Vaishnavi | 240 | Traces & Plots Lead |
| Sarthak | 240 | Report & Demo Lead |

## Cache parameters

| Parameter | Value |
|---|---|
| Cache size | 1 KB |
| Block size | 16 bytes (4 words) |
| Address width | 32 bits |
| Lines | 64 |
| Address split | `[31:10]` tag (22) / `[9:4]` index (6) / `[3:0]` offset (4) |
| Write policy | Write-through, no-write-allocate (write-allocate variant planned) |
| Memory latency | 4 cycles per word (parameter `LAT`) |

The controller FSM is `IDLE -> LOOKUP -> (REFILL | WRITEMEM) -> DONE`.
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
  traces/
    sequential.trace  random.trace  repeated.trace  stride16.trace
    stride1024.trace  matrix_rowmajor.trace  matrix_colmajor.trace
  scripts/
    trace_gen.py            trace generator
  docs/
    diagrams/               block diagram, FSM diagram, topology
    waveforms/              annotated hit / miss / conflict screenshots
    synthesis/              Vivado or Yosys reports and screenshots
    results/                results tables, sweep CSV, plots
  report/
    MCA_Project6_Report.pdf IEEE report (Phase I now, final in Phase II)
    source/                 Word or LaTeX source
```

## How to run

Requires [Icarus Verilog](https://steveicarus.github.io/iverilog/) and optionally GTKWave.

```bash
brew install icarus-verilog
brew install --cask gtkwave
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

Generate the traces:

```bash
mkdir -p traces
python3 scripts/trace_gen.py
```

Run a trace (once `tb/tb_trace.v` is complete):

```bash
iverilog -g2012 -o sim_trace rtl/main_mem.v rtl/dm_cache.v tb/tb_trace.v
vvp sim_trace +TRACE=traces/random.trace
```

Synthesis (resource count with Yosys; Vivado for utilization and timing):

```bash
yosys -p "read_verilog rtl/dm_cache.v; synth -top dm_cache; stat"
```

## Results

To be added: hit and miss rates per trace, AMAT, comparison with a no-cache baseline, parameter sweep, synthesis numbers.

## Links

- Phase I video: _to be added_
- IEEE report: `report/MCA_Project6_Report.pdf` (to be added)
