`timescale 1ns/1ps
// tb_trace.v - trace-driven testbench
// Run: vvp sim_trace +TRACE=traces/random.trace
// Trace lines:  R <hex addr>   or   W <hex addr> <hex data>
module tb_trace;
    localparam LAT = 4;
    reg clk = 0, rst = 1;
    always #5 clk = ~clk;

    reg req, we; reg [31:0] addr, wdata;
    wire [31:0] rdata; wire done;
    wire mem_req, mem_we, mem_ack; wire [31:0] mem_addr, mem_wdata, mem_rdata;
    wire [31:0] hits, misses;

    dm_cache dut(.clk(clk), .rst(rst), .req(req), .we(we), .addr(addr), .wdata(wdata),
                 .rdata(rdata), .done(done), .mem_req(mem_req), .mem_we(mem_we),
                 .mem_addr(mem_addr), .mem_wdata(mem_wdata), .mem_rdata(mem_rdata),
                 .mem_ack(mem_ack), .hits(hits), .misses(misses));
    main_mem #(.LAT(LAT)) mem(.clk(clk), .rst(rst), .req(mem_req), .we(mem_we), .addr(mem_addr),
                 .wdata(mem_wdata), .rdata(mem_rdata), .ack(mem_ack));

    reg [31:0] ref_mem [0:4095];
    integer i, errors = 0, accesses = 0, total_cycles = 0, t0;

    task access(input w, input [31:0] a, input [31:0] d);
        begin
            @(negedge clk); req = 1; we = w; addr = a; wdata = d; t0 = $time;
            @(negedge clk); req = 0;
            wait (done); @(negedge clk);
            total_cycles = total_cycles + ($time - t0)/10;
            accesses = accesses + 1;
            if (w) ref_mem[a[13:2]] = d;
            else if (rdata !== ref_mem[a[13:2]]) begin
                errors = errors + 1;
                $display("ERROR addr=%h got=%h exp=%h", a, rdata, ref_mem[a[13:2]]);
            end
        end
    endtask

    reg [1023:0] fname;
    reg [31:0] kind, a_in, d_in;
    integer fd, r;
    real hit_rate, miss_rate, avg_cycles, hit_time, penalty, amat;

    initial begin
        if (!$value$plusargs("TRACE=%s", fname)) begin
            $display("Usage: vvp sim_trace +TRACE=traces/<name>.trace");
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
        // measured in the reference run (LAT=4): hit = 3 cycles, miss penalty = 20 cycles
        hit_time = 3.0; penalty = 20.0;
        amat = hit_time + (miss_rate / 100.0) * penalty;

        $display("Trace: %0s", fname);
        $display("accesses=%0d hits=%0d misses=%0d", accesses, hits, misses);
        $display("hit_rate=%0.1f%% miss_rate=%0.1f%%", hit_rate, miss_rate);
        $display("avg_cycles_per_access=%0.2f  AMAT(formula)=%0.2f  no_cache_baseline=%0d",
                 avg_cycles, amat, 3 + 20);
        if (errors == 0) $display("DATA CHECK PASSED"); else $display("%0d DATA ERRORS", errors);
        $finish;
    end
endmodule
