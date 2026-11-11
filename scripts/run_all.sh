#!/bin/bash
# Run from the repo root:  bash scripts/run_all.sh
set -e
iverilog -g2012 -o sim_trace rtl/main_mem.v rtl/dm_cache.v tb/tb_trace.v
for t in traces/*.trace; do
  vvp sim_trace +TRACE=$t | grep -E "^Trace|accesses=|hit_rate|avg_cycles|DATA"
  echo
done