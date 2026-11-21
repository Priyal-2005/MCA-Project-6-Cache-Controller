
# Verification Summary – Phase II

## 1. Testbench Verification

The following testbenches were executed successfully:

| Testbench | Purpose | Result |
|---|---|---|
| tb_dm_cache | Cache read/write operations, hit/miss, reset and corner cases | PASS |
| tb_write_allocate | Write-allocate functionality | PASS |
| tb_lat_sweep (LAT=2) | Cache verification with memory latency 2 | PASS |
| tb_lat_sweep (LAT=4) | Cache verification with memory latency 4 | PASS |
| tb_lat_sweep (LAT=8) | Cache verification with memory latency 8 | PASS |
| tb_traffic | Memory traffic (`mem_reads`, `mem_writes`) per write policy, with a data check against a reference memory | PASS (9 traces x 2 policies, all data checks passed) |

## 2. Trace-Based Verification

All 8 trace files were executed in both write modes.

- Write Allocate OFF: 8/8 traces passed.
- Write Allocate ON: 8/8 traces passed.
- All traces reported DATA CHECK PASSED.

Trace files:
- matrix_colmajor.trace
- matrix_rowmajor.trace
- random.trace
- repeated.trace
- sequential.trace
- stride1024.trace
- stride16.trace
- writes.trace

## 3. Fault Injection

The valid-bit hit check was deliberately removed to introduce a fault.

The testbench detected 275 errors, confirming that the verification environment catches this fault.

The original valid-bit hit condition was restored:

`wire hit = valid_ram[idx] && (tag_ram[idx] == tag);`

## 4. Waveform Verification

A write-miss with write-allocate was inspected in the waveform.

The state sequence REFILL → WRITEMEM → DONE was observed, confirming that the cache line is refilled before the pending write is completed.

## 5. Final Result

All assigned Phase II regression tests passed.

- Anusha's post-synthesis verification: 9/9 traces passed in both configurations.
- Anusha's write-policy traffic testbench (`tb_traffic`): all 9 traces (the 8 shared traces plus `write_stream`) passed the data check under both write policies.
- Both write modes passed all 8 trace tests.
- Deliberate fault-injection test detected 275 errors.
