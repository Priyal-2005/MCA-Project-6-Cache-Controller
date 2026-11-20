`timescale 1ns/1ps
// tb_traffic.v - trace-driven memory-traffic testbench (write-allocate vs no-write-allocate)
//
// Counts the words moved between the cache and main memory (mem_reads / mem_writes)
// for the same trace under both write policies, so the traffic cost of the policy
// can be compared directly.
//
// Run (no-write-allocate, the default policy):
//   iverilog -g2012 -P tb_traffic.WA=0 -o sim_tr rtl/main_mem.v rtl/dm_cache.v tb/tb_traffic.v
//   vvp sim_tr +TRACE=traces/writes.trace
// Run (write-allocate):
//   iverilog -g2012 -P tb_traffic.WA=1 -o sim_tr rtl/main_mem.v rtl/dm_cache.v tb/tb_traffic.v
//   vvp sim_tr +TRACE=traces/writes.trace
//
// Prints one CSV row per run (see scripts/run_traffic.sh), so the runs can be
// concatenated straight into docs/results/write_policy_traffic.csv.
//
// Trace lines:  R <hex addr>   or   W <hex addr> <hex data>
module tb_traffic;
    parameter WA  = 0;             // WRITE_ALLOCATE passed down to the DUT
    parameter LAT = 4;             // main-memory latency, cycles per word

    reg clk = 0, rst = 1;
    always #5 clk = ~clk;

    reg req, we; reg [31:0] addr, wdata;
    wire [31:0] rdata; wire done, busy;
    wire mem_req, mem_we, mem_ack; wire [31:0] mem_addr, mem_wdata, mem_rdata;
    wire [31:0] hits, misses;
    wire [31:0] mem_reads, mem_writes;

    dm_cache #(.WRITE_ALLOCATE(WA)) dut(
        .clk(clk), .rst(rst), .req(req), .we(we), .addr(addr), .wdata(wdata),
        .rdata(rdata), .done(done), .busy(busy),
        .mem_req(mem_req), .mem_we(mem_we), .mem_addr(mem_addr),
        .mem_wdata(mem_wdata), .mem_rdata(mem_rdata), .mem_ack(mem_ack),
        .hits(hits), .misses(misses),
        .mem_reads(mem_reads), .mem_writes(mem_writes));

    main_mem #(.LAT(LAT)) mem(.clk(clk), .rst(rst), .req(mem_req), .we(mem_we),
        .addr(mem_addr), .wdata(mem_wdata), .rdata(mem_rdata), .ack(mem_ack));

    reg [31:0] ref_mem [0:4095];
    integer i, errors = 0, accesses = 0, reads = 0, writes = 0;
    integer total_cycles = 0, t0;

    task access(input w, input [31:0] a, input [31:0] d);
        begin
            @(negedge clk); req = 1; we = w; addr = a; wdata = d; t0 = $time;
            @(negedge clk); req = 0;
            wait (done); @(negedge clk);
            total_cycles = total_cycles + ($time - t0)/10;
            accesses = accesses + 1;
            if (w) begin
                writes = writes + 1;
                ref_mem[a[13:2]] = d;
            end else begin
                reads = reads + 1;
                if (rdata !== ref_mem[a[13:2]]) begin
                    errors = errors + 1;
                    $display("# ERROR addr=%h got=%h exp=%h", a, rdata, ref_mem[a[13:2]]);
                end
            end
        end
    endtask

    reg [1023:0] fname;
    reg [31:0] kind, a_in, d_in;
    integer fd, r;
    real hit_rate, miss_rate, avg_cycles;

    initial begin
        if (!$value$plusargs("TRACE=%s", fname)) begin
            $display("Usage: vvp sim_tr +TRACE=traces/<name>.trace");
            $finish;
        end
        fd = $fopen(fname, "r");
        if (fd == 0) begin $display("Cannot open trace file %0s", fname); $finish; end

        for (i = 0; i < 4096; i = i + 1) ref_mem[i] = i*3+1;
        req = 0; we = 0; addr = 0; wdata = 0;
        repeat (3) @(negedge clk); rst = 0;

        while (!$feof(fd)) begin
            r = $fscanf(fd, " %s %h", kind, a_in);
            if (r == 2) begin
                if (kind == "W") begin
                    r = $fscanf(fd, " %h", d_in);
                    access(1, a_in, d_in);
                end else access(0, a_in, 0);
            end
        end
        $fclose(fd);

        hit_rate   = (hits * 100.0) / (hits + misses);
        miss_rate  = 100.0 - hit_rate;
        avg_cycles = (total_cycles * 1.0) / accesses;

        // CSV row: trace,policy,accesses,reads,writes,hits,misses,hit_rate,
        //          mem_reads,mem_writes,mem_words_total,avg_cycles,data_check
        $display("CSV,%0s,%0s,%0d,%0d,%0d,%0d,%0d,%0.1f,%0d,%0d,%0d,%0.2f,%0s",
                 fname, WA ? "write-allocate" : "no-write-allocate",
                 accesses, reads, writes, hits, misses, hit_rate,
                 mem_reads, mem_writes, mem_reads + mem_writes, avg_cycles,
                 errors == 0 ? "PASS" : "FAIL");
        $finish;
    end
endmodule
