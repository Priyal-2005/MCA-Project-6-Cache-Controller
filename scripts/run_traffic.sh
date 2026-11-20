#!/bin/bash
# run_traffic.sh - write-allocate vs no-write-allocate memory-traffic comparison.
#
# Runs every trace under both write policies and writes the CSV to
# docs/results/write_policy_traffic.csv.
#
# Run from the repo root:  bash scripts/run_traffic.sh
#
# Trace set: the eight shared traces in traces/, plus docs/results/write_stream.trace.
#
# write_stream is kept in docs/results/ rather than traces/ on purpose. It exists only for
# this write-policy study, not for the general performance measurements, so keeping it out
# of traces/ leaves scripts/run_all.sh and the shared results tables reporting the same
# eight traces as before. It is regenerated below on every run, so it stays reproducible
# without modifying scripts/trace_gen.py.
#
# Why it is needed: on the eight shared traces the write policy changes nothing measurable.
# writes.trace reads back every address it writes, so the refill that write-allocate performs
# on a write miss would have happened anyway on the following read - traffic and cycle count
# come out identical under both policies and only the hit rate moves. write_stream writes
# 2 KB once and never reads it, which is the case where write-allocate's refills are pure
# overhead, so the cost side of the trade-off becomes measurable.
set -e

OUT=docs/results/write_policy_traffic.csv
STREAM=docs/results/write_stream.trace
TMPDIR_LOCAL=$(mktemp -d)
trap 'rm -rf "$TMPDIR_LOCAL"' EXIT

# Regenerate the write-streaming trace: 512 sequential word writes over 2 KB, no read-back.
python3 -c '
import sys
with open(sys.argv[1], "w") as f:
    for i in range(512):
        f.write("W %08X %08X\n" % (4 * i, 0x2000 + i))
' "$STREAM"

echo "trace,policy,accesses,reads,writes,hits,misses,hit_rate_pct,mem_reads,mem_writes,mem_words_total,avg_cycles_per_access,data_check" > "$OUT"

for wa in 0 1; do
  iverilog -g2012 -P tb_traffic.WA=$wa -o "$TMPDIR_LOCAL/sim_tr" \
    rtl/main_mem.v rtl/dm_cache.v tb/tb_traffic.v
  for t in traces/*.trace "$STREAM"; do
    name=$(basename "$t" .trace)
    vvp "$TMPDIR_LOCAL/sim_tr" +TRACE="$t" \
      | grep '^CSV,' \
      | sed -e 's/^CSV,//' -e "s|^[^,]*,|$name,|" >> "$OUT"
  done
done

echo "Wrote $OUT"
column -s, -t < "$OUT"
