# Synthesis: resource utilisation and maximum frequency

Owner: Anusha (Controller, Memory Interface & Synthesis Lead)
Design under synthesis: `rtl/dm_cache.v` (direct-mapped, write-through cache controller)
Reproduce everything below with: `bash scripts/run_synth.sh`

## Headline numbers

| Configuration | Logic cells (iCE40 HX8K) | Block RAM | Maximum frequency |
|---|---|---|---|
| 1 KB, 64 lines, 16 B blocks (default) | 740 / 7680 (9%) | 4 / 32 (12%) | **79.85 MHz** |
| 512 B, 32 lines, 16 B blocks | 662 / 7680 (8%) | 4 / 32 (12%) | **79.90 MHz** |

The synthesised netlist was also simulated at gate level and passed the data check on all
nine traces, so these numbers belong to a design that is verified after synthesis, not only
before it.

## Tool flow

Vivado was not available on the machine used, so the whole flow is open-source and runs on
macOS. Three stages, all driven by `scripts/run_synth.sh`:

| Stage | Tool | What it gives |
|---|---|---|
| 1. Generic synthesis | Yosys 0.71 `synth` | Vendor-independent cell count |
| 2. Technology mapping | Yosys 0.71 `synth_ice40` | Real FPGA primitives, block RAM inference |
| 3. Place and route | nextpnr-ice40 0.11.1 | Device utilisation and maximum clock frequency |

Target device for stages 2 and 3: Lattice iCE40 HX8K, package CT256 (7680 logic cells,
32 block RAMs of 4 Kbit, 206 I/O pins).

Install:

```bash
brew install yosys nextpnr-ice40 icestorm icarus-verilog
```

## 1. Resource utilisation

### Generic synthesis (no memory primitives)

```bash
yosys -p "read_verilog rtl/dm_cache.v; synth -top dm_cache; stat"
```

| Configuration | Total cells | of which flip-flops |
|---|---|---|
| 1 KB | 30 922 | 9 935 |
| 512 B | 15 652 | 5 134 |

**These numbers must not be read as the cost of the design.** The generic Yosys flow has no
memory primitives, so it implements the cache arrays as individual flip-flops plus the
multiplexer trees needed to address them. The flip-flop count is simply the storage in bits:

| Array | 1 KB | 512 B |
|---|---|---|
| `data_ram` (lines x 4 words x 32 bits) | 8 192 | 4 096 |
| `tag_ram` (lines x tag bits) | 64 x 22 = 1 408 | 32 x 23 = 736 |
| `valid_ram` (1 bit per line) | 64 | 32 |
| Total storage bits | 9 664 | 4 864 |
| Flip-flops reported by generic synthesis | 9 935 | 5 134 |

The difference in each column (271 and 270 flip-flops) is everything that is not array
storage: the FSM state register, the latched request (`l_addr`, `l_wdata`, `l_we`), the
refill counter `cnt`, `pending_write`, the memory-side output registers, and the four 32-bit
statistics counters. The per-group breakdown is in the next section. That state is what the
controller really costs; the rest is memory that any real target maps into dedicated RAM.

### Technology-mapped synthesis (iCE40)

```bash
yosys -p "read_verilog rtl/dm_cache.v; synth_ice40 -top dm_cache; stat"
```

| Configuration | LUT4 | Carry | Flip-flops | Block RAM (SB_RAM40_4K) |
|---|---|---|---|---|
| 1 KB | 491 | 155 | 383 | 4 |
| 512 B | 412 | 154 | 352 | 4 |

With real primitives available the arrays are inferred as block RAM and the flip-flop count
falls from 9 935 to 383, a factor of 26. Counted from the netlist by the signal each
flip-flop drives:

| Group | Flip-flops | What |
|---|---|---|
| Statistics counters | 128 | `hits`, `misses`, `mem_reads`, `mem_writes`, 32 bits each |
| Memory-side outputs | 64 | `mem_addr`, `mem_wdata` |
| Latched request | 63 | `l_addr` (30 surviving bits, of which 6 are `idx`), `l_wdata` (32), `l_we` |
| `valid_ram` | 64 | one bit per line, kept in flip-flops because it is cleared in a single cycle on reset, which a block RAM cannot do |
| Block RAM read-data registers | ~52 | 31 on `data_ram`, 21 on `tag_ram` |
| FSM and control | 9 | `state` (3), `cnt` (2), `done`, `mem_req`, `mem_we`, `pending_write` |

These groups account for about 380 of the 383; the small remainder is signals the mapping
splits across groups, and the read-data register count is approximate for the same reason.

The block RAM read-data registers are worth noting: the RTL reads both arrays
combinationally, but `SB_RAM40_4K` has a synchronous read port, so the mapping adds
registers on the read data. They are a cost of mapping an asynchronous-read description
onto a synchronous memory primitive, not of the cache logic itself.

So of the 383, roughly 128 are statistics counters that a production cache would not carry,
about 52 are that mapping artefact, and the remaining ~200 are the cache's real state: the
latched request, the memory-side output registers, the valid bits and the FSM.

Why the arrays map cleanly: the cache reads `tag_ram[idx]` and `data_ram[{idx, word}]`
combinationally, but `idx` and `word` are both slices of `l_addr`, which is a register loaded
in `IDLE`. Yosys can therefore absorb that address register into the block RAM's synchronous
read port without changing behaviour, which is why no extra latency appears and why the
post-synthesis simulation (section 3) matches the RTL cycle for cycle.

### Why block RAM usage does not fall with cache size

Both configurations use 4 block RAMs even though the 512 B cache stores half as much. On
iCE40 an `SB_RAM40_4K` in the mode the tool selected (`READ_MODE = WRITE_MODE = 0`) is
**256 words x 16 bits**. Both arrays are wider than 16 bits, so each needs two block RAMs
side by side to make up its width:

| Array | Width | Depth (1 KB) | Depth (512 B) | Block RAMs |
|---|---|---|---|---|
| `data_ram` | 32 bits | 256 | 128 | 2 (width split 16 + 16) |
| `tag_ram` | 22 / 23 bits | 64 | 32 | 2 (width split) |

The block RAM count is limited by **width**, not by depth. Halving the number of lines halves
the depth used inside each block RAM but does not reduce how many are needed, so the count
stays at 4. The saving from the smaller cache shows up in the logic instead: 491 to 412 LUT4
and 740 to 662 placed logic cells, because the index decode, the address arithmetic and the
tag comparator all get one bit narrower.

### Placed and routed utilisation

| Resource | 1 KB | 512 B | Available |
|---|---|---|---|
| Logic cells (ICESTORM_LC) | 740 (9%) | 662 (8%) | 7 680 |
| Block RAM (ICESTORM_RAM) | 4 (12%) | 4 (12%) | 32 |
| I/O (SB_IO) | 6 (2%) | 6 (2%) | 206 |
| Global buffers (SB_GB) | 3 | 3 | 8 |

The design is small: a 1 KB cache controller occupies under a tenth of a mid-range iCE40.

## 2. Maximum frequency

```
Max frequency for clock 'clk': 79.85 MHz   (1 KB configuration)
Max frequency for clock 'clk': 79.90 MHz   (512 B configuration)
```

Reported by nextpnr-ice40 after routing, with a 100 MHz constraint requested so that the tool
reports how far it falls short. Full logs in `logs/nextpnr_1KB.log` and
`logs/nextpnr_512B.log`; the annotated path is in `critical_path_1KB.txt`.

**Quote the post-routing figure, not the post-placement one.** Each nextpnr log contains two
`Max frequency` lines: an estimate made after placement, before routing delays are known,
and the real figure after routing. The post-placement estimate is not reliably optimistic or
pessimistic — it is simply made with incomplete information, and it lands on either side:

| Configuration | After placement | After routing (quote this) |
|---|---|---|
| 1 KB | 88.83 MHz | **79.85 MHz** |
| 512 B | 78.61 MHz | **79.90 MHz** |

For 1 KB the estimate is 11% high; for 512 B it is 1.6% low. The routed number is the one
that counts, and it is the one in the tables above and in `resource_utilization.csv`. In the
logs the routed line is always the last one, printed as a `Warning:` because it misses the
100 MHz constraint we deliberately asked for.

### The critical path is the hit path

The 1 KB critical path is 12.52 ns (1 / 12.52 ns = 79.9 MHz), and it runs exactly where the
architecture says the limit should be:

| Segment | Delay | What it is |
|---|---|---|
| Block RAM clock-to-output | 2.15 ns | reading the stored tag, `tag_ram[idx]` |
| 7 levels of LUT4 | 2.47 ns | 22-bit tag comparator and the `hit` / FSM next-state logic |
| Routing (8 hops) | 7.80 ns | wiring between those cells |
| Setup | 0.10 ns | at the clock enable of the `mem_addr` register |
| **Total** | **12.52 ns** | |

Start point: `u_cache.tag_ram.0.0_RAM.RDATA_6` (a tag bit leaving block RAM).
End point: the clock enable of the `mem_addr` register, which is control logic.

So the limiting path is **tag RAM read, then tag compare, then control decision** — the hit
path. That is the fundamental reason this design cannot be clocked arbitrarily fast: deciding
hit or miss in a single cycle means a memory read, a 22-bit equality compare and the FSM
branch must all complete inside one clock period. The refill and write-through paths are not
critical, because they only count words and increment an address while waiting on `mem_ack`.

The 512 B configuration is marginally faster (79.90 vs 79.85 MHz, a 0.05% difference, which
is placement noise rather than a real effect). This is itself the expected result: the tag
comparator grows by one bit when the index shrinks by one bit, so the hit path is almost the
same length in both. Cache size changes area, not clock speed, in this design.

### Routing dominates

Of the 12.52 ns, 4.73 ns is logic and 7.79 ns is routing — routing is 62% of the period. That
is characteristic of a small, routing-limited FPGA fabric. On a device with faster
interconnect, or in an ASIC flow, the same logic depth would allow a substantially higher
clock; the 4.73 ns logic-only path corresponds to roughly 210 MHz. The 79.85 MHz figure
should therefore be quoted as *the maximum frequency of this design on an iCE40 HX8K*, not as
a property of the architecture.

### A harness is needed to measure timing

`dm_cache` has 329 port bits: two 32-bit CPU buses, three 32-bit memory-side buses and four
32-bit statistics counters. No iCE40 package has that many pins (the largest, CT256, has
206), so the module cannot be placed as a chip on its own. In a real system this is not a
problem, because the cache is an internal block between the CPU and the memory controller and
none of these signals are chip pins.

For the timing run only, `syn_wrap.v` instantiates the cache with 6 pins: wide inputs are
driven from a shift register fed by one pin, and every output is observed through a two-stage
registered XOR tree. Nothing inside the cache can then be constant-folded or removed as
dangling, and the observation logic is kept short enough (one XOR reduction per bus,
registered, then combined) that it does not become the critical path — confirmed by the
critical path above, which lies entirely inside `u_cache`.

Resource numbers in section 1 come from `dm_cache` synthesised on its own, never from the
harness, so the harness does not inflate or deflate the area figures.

## 3. Post-synthesis verification

A resource count only means something if the netlist still works. `scripts/run_synth.sh`
writes the iCE40 netlist, compiles it against the Lattice cell simulation models and reruns
the trace testbench on it:

```bash
iverilog -g2012 -o sim_post \
  $(dirname $(command -v yosys))/../share/yosys/ice40/cells_sim.v \
  netlist.v rtl/main_mem.v tb/tb_trace.v
```

Result, both configurations: **9 / 9 traces pass the data check**, with hit, miss and
cycle counts identical to the RTL simulation. Logs in `logs/postsynth_sim_1KB.log` and
`logs/postsynth_sim_512B.log`.

This matters for two reasons. It confirms the block RAM inference described above did not
change behaviour, and it confirms the arrays are genuinely synthesisable rather than
simulation-only constructs.

## 4. Limits of this measurement

State these in the report; they are honest limits, not defects.

1. **Device-specific frequency.** 79.85 MHz is for an iCE40 HX8K. A different FPGA or an ASIC
   library would give a different number from the same RTL. Routing contributes 62% of the
   critical path here, so a device with better interconnect would be noticeably faster.
2. **No vendor comparison.** Vivado was not available, so there is no Xilinx utilisation or
   timing report to compare against. The open-source flow reports the same two quantities the
   project asks for (utilisation and maximum frequency) on a real device model.
3. **Statistics counters are included.** The four 32-bit counters (`hits`, `misses`,
   `mem_reads`, `mem_writes`) are measurement infrastructure, not part of a production cache.
   They account for 128 of the 383 flip-flops, so a deployed version would be about a third
   smaller in flip-flops.
4. **Timing is measured through a harness.** Necessary because of the pin count; the critical
   path report confirms the reported path is inside the cache, so the figure is meaningful.
5. **`valid_ram` stays in flip-flops.** It is cleared in one cycle on reset, which block RAM
   cannot do. For a much larger cache this would become the dominant flip-flop cost and would
   need a different invalidation scheme, such as a generation counter.
6. **Single clock domain, no I/O timing.** The CPU and memory interfaces are synchronous to
   the same clock, so no cross-domain analysis was required.

## Files

| File | Contents |
|---|---|
| `resource_utilization.csv` | all numbers above, machine-readable (for plotting) |
| `critical_path_1KB.txt` | annotated critical path, default configuration |
| `syn_wrap.v` | pin-count harness used for the timing run only |
| `logs/yosys_generic_*.log` | generic synthesis logs |
| `logs/yosys_ice40_*.log` | technology-mapped synthesis logs |
| `logs/nextpnr_*.log` | place-and-route logs, utilisation and frequency |
| `logs/postsynth_sim_*.log` | gate-level simulation of the netlist on all nine traces |
