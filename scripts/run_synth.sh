#!/bin/bash
# run_synth.sh - synthesis flow for dm_cache: resource utilisation and maximum frequency.
#
# Run from the repo root:  bash scripts/run_synth.sh
#
# Three steps per configuration (1 KB default and 512 B):
#   1. Yosys generic synthesis   - vendor-independent cell count. The generic flow has no
#                                  memory primitives, so it flattens the cache arrays into
#                                  flip-flops; reported to show why that number is not the
#                                  real cost of the design.
#   2. Yosys iCE40 synthesis     - technology mapping to real FPGA primitives, where the
#                                  arrays are inferred as block RAM (SB_RAM40_4K).
#   3. nextpnr-ice40 place/route - device utilisation and the maximum clock frequency,
#                                  via the syn_wrap harness (see docs/synthesis/syn_wrap.v).
#
# Also runs a post-synthesis gate-level simulation of the iCE40 netlist against the
# trace testbench, so the synthesised netlist is verified and not just counted.
#
# Needs: yosys, nextpnr-ice40, iverilog
#   brew install yosys nextpnr-ice40 icarus-verilog

set -e

OUTDIR=docs/synthesis
LOGDIR=$OUTDIR/logs
CSV=$OUTDIR/resource_utilization.csv
CELLS_SIM=$(dirname "$(command -v yosys)")/../share/yosys/ice40/cells_sim.v
DEVICE_ARGS="--hx8k --package ct256"
# Same trace set as scripts/run_traffic.sh: the eight shared traces plus the write-streaming
# trace used for the write-policy study. Both are committed, so this set is the same in any
# clean clone and the post-synthesis log is reproducible.
TRACE_SET="traces/*.trace docs/results/write_stream.trace"

mkdir -p "$LOGDIR"
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

echo "config,cache_bytes,index_bits,lines,tag_bits,generic_cells,generic_ffs,ice40_lut4,ice40_carry,ice40_ffs,ice40_bram,pnr_logic_cells,pnr_logic_pct,pnr_bram,pnr_bram_pct,fmax_mhz" > "$CSV"

# cell_count <stat.json> <regex>  -> total cells of the matching types in the top module
cell_count () {
  python3 -c '
import json, re, sys
types = json.load(open(sys.argv[1]))["design"]["num_cells_by_type"]
pat = re.compile(sys.argv[2])
print(sum(n for t, n in types.items() if pat.search(t)))
' "$1" "$2"
}

# strip_timing <file>
# Remove the wall-clock timings and log hashes the tools print. They change on every run
# even though every synthesis result is identical, which would otherwise leave a dirty
# working tree for anyone who reruns the flow. Engineering numbers are untouched: delays
# are printed as "2.15" or "7.80 ns" and never with an "s" suffix, so normalising the
# "0.15s" style durations cannot touch a timing result.
strip_timing () {
  python3 -c '
import re, sys
path = sys.argv[1]
drop = re.compile(r"^(End of script\.|Time spent:)")
subs = [
    (re.compile(r"\b[0-9]+\.[0-9]+s\b"), "-s"),
    (re.compile(r"\|\s*[0-9]+\.[0-9]{2}\s+[0-9]+\.[0-9]{2}\|\s*$"), "| - -|"),
]
out = []
for line in open(path, errors="replace"):
    if drop.match(line):
        continue
    for pat, rep in subs:
        line = pat.sub(rep, line)
    out.append(line)
open(path, "w").writelines(out)
' "$1"
}

# trim_log <full log> <output> <title>
# Yosys writes a few hundred kilobytes per run, almost all of it ABC internals. Keep only
# the statistics and check sections, which are the parts worth committing and reviewing.
trim_log () {
  {
    echo "$3"
    echo "Tool: $(yosys -V)"
    echo "Trimmed from the full Yosys log: statistics and check sections only."
    echo "Regenerate the full log with scripts/run_synth.sh (see the yosys -l argument)."
    echo
    python3 -c '
import re, sys
header = re.compile(r"^[0-9]+(\.[0-9]+)*\.\s+(.*)$")
wanted = ("Printing statistics", "Executing CHECK pass")
keep = False
for line in open(sys.argv[1], errors="replace"):
    m = header.match(line)
    if m:
        keep = any(w in m.group(2) for w in wanted)
    if keep:
        sys.stdout.write(line)
' "$1"
  } > "$2"
  strip_timing "$2"
}

stat_field () {
  python3 -c '
import json, sys
print(json.load(open(sys.argv[1]))["design"][sys.argv[2]])
' "$1" "$2"
}

synth_config () {
  local label=$1 index_bits=$2
  local lines=$((1 << index_bits))
  local bytes=$((lines * 4 * 4))                 # lines x 4 words x 4 bytes
  local tag_bits=$((32 - index_bits - 4))

  echo "=============================================================="
  echo " Configuration: $label  (INDEX_BITS=$index_bits, $lines lines, $bytes B)"
  echo "=============================================================="

  # --- 1. generic synthesis -------------------------------------------------
  yosys -q -l "$WORK/yosys_generic_${label}.full.log" -p "
    read_verilog rtl/dm_cache.v
    chparam -set INDEX_BITS $index_bits dm_cache
    synth -top dm_cache
    stat
    tee -q -o $WORK/gen_${label}.json stat -json
  "
  trim_log "$WORK/yosys_generic_${label}.full.log" "$LOGDIR/yosys_generic_${label}.log" \
           "Yosys generic synthesis (synth), INDEX_BITS=$index_bits"
  local gen_cells gen_ffs
  gen_cells=$(stat_field "$WORK/gen_${label}.json" num_cells)
  gen_ffs=$(cell_count   "$WORK/gen_${label}.json" 'DFF')

  # --- 2. iCE40 technology mapping -----------------------------------------
  yosys -q -l "$WORK/yosys_ice40_${label}.full.log" -p "
    read_verilog rtl/dm_cache.v
    chparam -set INDEX_BITS $index_bits dm_cache
    synth_ice40 -top dm_cache
    stat
    tee -q -o $WORK/ice_${label}.json stat -json
    write_verilog -noattr $WORK/net_${label}.v
  "
  trim_log "$WORK/yosys_ice40_${label}.full.log" "$LOGDIR/yosys_ice40_${label}.log" \
           "Yosys iCE40 synthesis (synth_ice40), INDEX_BITS=$index_bits"
  local ice_lut ice_carry ice_ff ice_bram
  ice_lut=$(cell_count   "$WORK/ice_${label}.json" '^SB_LUT4$')
  ice_carry=$(cell_count "$WORK/ice_${label}.json" '^SB_CARRY$')
  ice_ff=$(cell_count    "$WORK/ice_${label}.json" '^SB_DFF')
  ice_bram=$(cell_count  "$WORK/ice_${label}.json" '^SB_RAM40_4K$')

  # --- 2b. post-synthesis gate-level simulation ----------------------------
  echo "--- post-synthesis gate-level simulation ($label) ---"
  iverilog -g2012 -o "$WORK/sim_post_${label}" \
    "$CELLS_SIM" "$WORK/net_${label}.v" rtl/main_mem.v tb/tb_trace.v
  {
    echo "Post-synthesis gate-level simulation of the iCE40 netlist ($label)"
    echo "Netlist: yosys synth_ice40, simulated with the iCE40 cell models."
    echo
    for t in $TRACE_SET; do
      vvp "$WORK/sim_post_${label}" +TRACE="$t" | grep -E "^Trace|accesses=|hit_rate|DATA"
      echo
    done
  } > "$LOGDIR/postsynth_sim_${label}.log"
  local n_traces n_pass
  n_traces=$(echo $TRACE_SET | wc -w | tr -d ' ')
  n_pass=$(grep -c "DATA CHECK PASSED" "$LOGDIR/postsynth_sim_${label}.log" || true)
  echo "    netlist data check: $n_pass / $n_traces traces passed"
  if [ "$n_pass" != "$n_traces" ]; then
    echo "    ERROR: post-synthesis simulation did not pass on every trace" >&2
    exit 1
  fi

  # --- 3. place and route for timing ---------------------------------------
  yosys -q -p "
    read_verilog rtl/dm_cache.v docs/synthesis/syn_wrap.v
    chparam -set INDEX_BITS $index_bits syn_wrap
    synth_ice40 -top syn_wrap -json $WORK/wrap_${label}.json
  "
  nextpnr-ice40 $DEVICE_ARGS --json "$WORK/wrap_${label}.json" \
    --freq 100 --timing-allow-fail --seed 1 \
    > "$LOGDIR/nextpnr_${label}.log" 2>&1
  strip_timing "$LOGDIR/nextpnr_${label}.log"

  local pnr_lc pnr_lc_pct pnr_bram pnr_bram_pct fmax
  pnr_lc=$(grep       "ICESTORM_LC:"  "$LOGDIR/nextpnr_${label}.log" | awk '{print $3}' | cut -d/ -f1)
  pnr_lc_pct=$(grep   "ICESTORM_LC:"  "$LOGDIR/nextpnr_${label}.log" | awk '{print $NF}' | tr -d '%')
  pnr_bram=$(grep     "ICESTORM_RAM:" "$LOGDIR/nextpnr_${label}.log" | awk '{print $3}' | cut -d/ -f1)
  pnr_bram_pct=$(grep "ICESTORM_RAM:" "$LOGDIR/nextpnr_${label}.log" | awk '{print $NF}' | tr -d '%')
  fmax=$(grep "Max frequency for clock" "$LOGDIR/nextpnr_${label}.log" | tail -1 | awk '{print $7}')

  echo "$label,$bytes,$index_bits,$lines,$tag_bits,$gen_cells,$gen_ffs,$ice_lut,$ice_carry,$ice_ff,$ice_bram,$pnr_lc,$pnr_lc_pct,$pnr_bram,$pnr_bram_pct,$fmax" >> "$CSV"

  echo "    generic: $gen_cells cells, of which $gen_ffs flip-flops"
  echo "    iCE40:   $ice_lut LUT4, $ice_carry carry, $ice_ff FFs, $ice_bram BRAM"
  echo "    P&R:     $pnr_lc LCs ($pnr_lc_pct%), $pnr_bram BRAM ($pnr_bram_pct%), fmax = $fmax MHz"
  echo
}

synth_config 1KB  6
synth_config 512B 5

# Critical-path extract for the default configuration, for the report.
{
  echo "Critical path, 1 KB configuration, iCE40 HX8K CT256, nextpnr-ice40 (seed 1)."
  echo "Harness: docs/synthesis/syn_wrap.v. Generated by scripts/run_synth.sh."
  echo
  sed -n '/Critical path report/,$p' "$LOGDIR/nextpnr_1KB.log"
} > "$OUTDIR/critical_path_1KB.txt"

echo "Wrote $CSV"
column -s, -t < "$CSV"
