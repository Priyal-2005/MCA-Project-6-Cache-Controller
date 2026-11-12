`timescale 1ns/1ps
module tb_dm_cache;
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
    integer h0 = 0, m0 = 0, a0 = 0, c0 = 0;

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

    task report(input [255:0] name);
        integer dh, dm, da, dc;
        begin
            dh = hits - h0; dm = misses - m0; da = accesses - a0; dc = total_cycles - c0;
            $display("%0s: accesses=%0d hits=%0d misses=%0d hit_rate=%0d%% miss_rate=%0d%% avg_cycles/access=%0d.%0d",
                     name, da, dh, dm, (dh*100)/(dh+dm), (dm*100)/(dh+dm), dc/da, ((dc*10)/da)%10);
            h0 = hits; m0 = misses; a0 = accesses; c0 = total_cycles;
        end
    endtask

    integer k, r;
    initial begin
        $dumpfile("dm_cache.vcd"); $dumpvars(0, tb_dm_cache);
        for (i = 0; i < 4096; i = i + 1) ref_mem[i] = i*3+1;
        req = 0; we = 0; addr = 0; wdata = 0;
        repeat (3) @(negedge clk); rst = 0;

        // Test 1: sequential reads (spatial locality: 1 miss + 3 hits per block)
        for (k = 0; k < 256; k = k + 1) access(0, k*4, 0);
        report("T1 sequential   ");
        // Test 2: repeated reads of same 16 words (temporal locality, fits in cache)
        for (r = 0; r < 8; r = r + 1) for (k = 0; k < 16; k = k + 1) access(0, 32'h400 + k*4, 0);
        report("T2 repeated     ");
        // Test 3: conflict misses - two addresses 1KB apart map to same index
        for (r = 0; r < 8; r = r + 1) begin access(0, 32'h100, 0); access(0, 32'h500, 0); end
        report("T3 conflict     ");
        // Test 4: write hit, read-back; write miss (no allocate), read-back
        access(0, 32'h200, 0); access(1, 32'h200, 32'hDEADBEEF); access(0, 32'h200, 0);
        access(1, 32'h900, 32'hCAFEF00D); access(0, 32'h900, 0);
        report("T4 read/write   ");
        // Test 5: pseudo-random
        for (k = 0; k < 400; k = k + 1) access(0, ($random & 32'h0FFC), 0);
        report("T5 random       ");

        if (errors == 0) $display("ALL TESTS PASSED"); else $display("%0d FAILURES", errors);
        $finish;
    end
endmodule