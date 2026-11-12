
`timescale 1ns/1ps

module tb_dm_cache;

    localparam LAT = 4;

    reg clk = 0, rst = 1;
    always #5 clk = ~clk;

    reg req, we;
    reg [31:0] addr, wdata;

    wire [31:0] rdata;
    wire done;

    wire mem_req, mem_we, mem_ack;
    wire [31:0] mem_addr, mem_wdata, mem_rdata;

    wire [31:0] hits, misses;

    dm_cache dut(
        .clk(clk), .rst(rst),
        .req(req), .we(we),
        .addr(addr), .wdata(wdata),
        .rdata(rdata), .done(done),
        .mem_req(mem_req), .mem_we(mem_we),
        .mem_addr(mem_addr), .mem_wdata(mem_wdata),
        .mem_rdata(mem_rdata), .mem_ack(mem_ack),
        .hits(hits), .misses(misses)
    );

    main_mem #(.LAT(LAT)) mem(
        .clk(clk), .rst(rst),
        .req(mem_req), .we(mem_we),
        .addr(mem_addr), .wdata(mem_wdata),
        .rdata(mem_rdata), .ack(mem_ack)
    );

    reg [31:0] ref_mem [0:4095];

    integer i, errors = 0;
    integer accesses = 0, total_cycles = 0, t0;
    integer h0 = 0, m0 = 0, a0 = 0, c0 = 0;

    integer k, r;
    integer h_before, m_before;
    integer fill_start_hits, fill_start_misses;

    // ------------------------------------------------
    // Access task: performs read/write and checks data
    // ------------------------------------------------
    task access(input w, input [31:0] a, input [31:0] d);
        begin
            @(negedge clk);
            req = 1;
            we = w;
            addr = a;
            wdata = d;
            t0 = $time;

            @(negedge clk);
            req = 0;

            wait (done);
            @(negedge clk);

            total_cycles = total_cycles + ($time - t0)/10;
            accesses = accesses + 1;

            if (w)
                ref_mem[a[13:2]] = d;
            else if (rdata !== ref_mem[a[13:2]]) begin
                errors = errors + 1;
                $display("ERROR addr=%h got=%h exp=%h",
                         a, rdata, ref_mem[a[13:2]]);
            end
        end
    endtask

    // ------------------------------------------------
    // Report task
    // ------------------------------------------------
    task report(input [255:0] name);
        integer dh, dm, da, dc;
        begin
            dh = hits - h0;
            dm = misses - m0;
            da = accesses - a0;
            dc = total_cycles - c0;

            $display("%0s: accesses=%0d hits=%0d misses=%0d hit_rate=%0d%% miss_rate=%0d%% avg_cycles/access=%0d.%0d",
                     name, da, dh, dm,
                     (dh*100)/(dh+dm),
                     (dm*100)/(dh+dm),
                     dc/da, ((dc*10)/da)%10);

            h0 = hits;
            m0 = misses;
            a0 = accesses;
            c0 = total_cycles;
        end
    endtask

    initial begin

        $dumpfile("dm_cache.vcd");
        $dumpvars(0, tb_dm_cache);

        for (i = 0; i < 4096; i = i + 1)
            ref_mem[i] = i*3+1;

        req = 0;
        we = 0;
        addr = 0;
        wdata = 0;

        repeat (3) @(negedge clk);
        rst = 0;

        // ================================================
        // TEST 1: Sequential reads + first access after reset
        // ================================================

        $display("\n--- TEST 1: FIRST ACCESS AFTER RESET ---");

        access(0, 32'h00000000, 0);

        if (misses !== 32'd1 || hits !== 32'd0) begin
            errors = errors + 1;
            $display("ERROR: First access after reset should MISS. hits=%0d misses=%0d",
                     hits, misses);
        end else
            $display("PASS: First access after reset is a MISS");

        // Original sequential test
        for (k = 1; k < 256; k = k + 1)
            access(0, k*4, 0);

        report("T1 sequential");

        // ================================================
        // TEST 2: Repeated reads
        // ================================================

        for (r = 0; r < 8; r = r + 1)
            for (k = 0; k < 16; k = k + 1)
                access(0, 32'h400 + k*4, 0);

        report("T2 repeated");

        // ================================================
        // TEST 3: Conflict misses
        // ================================================

        for (r = 0; r < 8; r = r + 1) begin
            access(0, 32'h100, 0);
            access(0, 32'h500, 0);
        end

        report("T3 conflict");

        // ================================================
        // TEST 4: Write hit + read-back
        // ================================================

        $display("\n--- TEST 4: WRITE HIT AND READ-BACK ---");

        // Address 0x200 was loaded by the sequential test.
        h_before = hits;
        m_before = misses;

        access(1, 32'h200, 32'hDEADBEEF);

        if (hits != h_before + 1 || misses != m_before) begin
            errors = errors + 1;
            $display("ERROR: Write hit was not detected correctly");
        end else
            $display("PASS: Write hit detected");

        // Read back the value written above.
        h_before = hits;
        m_before = misses;

        access(0, 32'h200, 0);

        if (rdata !== 32'hDEADBEEF ||
            hits != h_before + 1 ||
            misses != m_before) begin
            errors = errors + 1;
            $display("ERROR: Write-hit read-back verification failed");
        end else
            $display("PASS: Write-hit read-back returned DEADBEEF");

        // ================================================
        // TEST 5: Write miss must NOT allocate
        // ================================================

        $display("\n--- TEST 5: WRITE MISS NO-ALLOCATE ---");

        // 0x900 conflicts with the previously loaded 0x100/0x500 index.
        h_before = hits;
        m_before = misses;

        access(1, 32'h900, 32'hCAFEF00D);

        if (misses != m_before + 1 || hits != h_before) begin
            errors = errors + 1;
            $display("ERROR: Write miss was not detected correctly");
        end else
            $display("PASS: Write miss detected");

        // Next read must miss because write miss did not allocate.
        h_before = hits;
        m_before = misses;

        access(0, 32'h900, 0);

        if (misses != m_before + 1 || hits != h_before) begin
            errors = errors + 1;
            $display("ERROR: Write miss incorrectly allocated a cache line");
        end else
            $display("PASS: Following read misses - no allocation confirmed");

        report("T4 write policy");

        // ================================================
        // TEST 6: Pseudo-random reads
        // ================================================

        for (k = 0; k < 400; k = k + 1)
            access(0, ($random & 32'h0FFC), 0);

        report("T5 random");

        // ================================================
        // TEST 7: Fill all 64 cache lines
        // ================================================

        $display("\n--- TEST 7: ALL 64 CACHE LINES ---");

        fill_start_hits = hits;
        fill_start_misses = misses;

        // Same tag, all 64 different cache indices.
        for (k = 0; k < 64; k = k + 1)
            access(0, 32'h00002000 + k*16, 0);

        if ((misses - fill_start_misses) == 64 &&
            (hits - fill_start_hits) == 0) begin
            $display("PASS: All 64 cache lines filled successfully");
        end else begin
            errors = errors + 1;
            $display("ERROR: Expected 64 misses and 0 hits. Actual misses=%0d hits=%0d",
                     misses - fill_start_misses,
                     hits - fill_start_hits);
        end

        report("T6 full line fill");

        // ================================================
        // FINAL RESULT
        // ================================================

        $display("\n================================");

        if (errors == 0)
            $display("ALL TESTS PASSED");
        else
            $display("%0d FAILURES", errors);

        $display("Total errors = %0d", errors);
        $display("================================");

        $finish;

    end

endmodule
