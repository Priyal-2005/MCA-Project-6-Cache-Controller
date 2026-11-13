
`timescale 1ns/1ps

module tb_write_allocate;

    localparam LAT = 4;

    reg clk = 0, rst = 1;
    always #5 clk = ~clk;

    reg req, we;
    reg [31:0] addr, wdata;

    wire [31:0] rdata;
    wire done, busy;

    wire mem_req, mem_we, mem_ack;
    wire [31:0] mem_addr, mem_wdata, mem_rdata;

    wire [31:0] hits, misses;
    wire [31:0] mem_reads, mem_writes;

    dm_cache #(.WRITE_ALLOCATE(1)) dut (
        .clk(clk), .rst(rst),
        .req(req), .we(we),
        .addr(addr), .wdata(wdata),
        .rdata(rdata), .done(done), .busy(busy),
        .mem_req(mem_req), .mem_we(mem_we),
        .mem_addr(mem_addr), .mem_wdata(mem_wdata),
        .mem_rdata(mem_rdata), .mem_ack(mem_ack),
        .hits(hits), .misses(misses),
        .mem_reads(mem_reads), .mem_writes(mem_writes)
    );

    main_mem #(.LAT(LAT)) mem (
        .clk(clk), .rst(rst),
        .req(mem_req), .we(mem_we),
        .addr(mem_addr), .wdata(mem_wdata),
        .rdata(mem_rdata), .ack(mem_ack)
    );

    integer errors = 0;

    task access(input w, input [31:0] a, input [31:0] d);
        begin
            @(negedge clk);
            req = 1;
            we = w;
            addr = a;
            wdata = d;

            @(negedge clk);
            req = 0;

            wait(done);
            #1;

            @(negedge clk);
        end
    endtask

    initial begin
        req = 0;
        we = 0;
        addr = 0;
        wdata = 0;

        repeat(3) @(negedge clk);
        rst = 0;

        // Test 1: Write miss should allocate the block.
        $display("\nTEST 1: WRITE MISS WITH WRITE-ALLOCATE");

        access(1, 32'h00000024, 32'hDEADBEEF);

        if (misses !== 1) begin
            errors = errors + 1;
            $display("ERROR: Expected one miss, got %0d", misses);
        end else begin
            $display("PASS: Write miss detected");
        end

        if (dut.valid_ram[2] !== 1'b1) begin
            errors = errors + 1;
            $display("ERROR: Cache line was not allocated");
        end else begin
            $display("PASS: Cache line allocated");
        end

        if (dut.data_ram[9] !== 32'hDEADBEEF) begin
            errors = errors + 1;
            $display("ERROR: Cache word not updated correctly");
        end else begin
            $display("PASS: Requested cache word updated");
        end

        if (mem.mem[9] !== 32'hDEADBEEF) begin
            errors = errors + 1;
            $display("ERROR: Main memory was not updated");
        end else begin
            $display("PASS: Main memory updated (write-through)");
        end
        // Check memory traffic for write-allocate miss
        if (mem_reads !== 4) begin
            errors = errors + 1;
            $display("ERROR: Expected 4 memory reads, got %0d", mem_reads);
        end else begin
            $display("PASS: 4 memory reads counted during block refill");
        end

        if (mem_writes !== 1) begin
            errors = errors + 1;
            $display("ERROR: Expected 1 memory write, got %0d", mem_writes);
        end else begin
            $display("PASS: 1 memory write counted during write-through");
        end
        // Test 1B: Other words in the refilled block must be preserved.
        $display("\nTEST 1B: PRESERVE OTHER WORDS AFTER REFILL");

        if (dut.data_ram[8] !== 32'd25) begin
            errors = errors + 1;
            $display("ERROR: Word 0 was not preserved: %h", dut.data_ram[8]);
        end else begin
            $display("PASS: Word 0 preserved");
        end

        if (dut.data_ram[10] !== 32'd31) begin
            errors = errors + 1;
            $display("ERROR: Word 2 was not preserved: %h", dut.data_ram[10]);
        end else begin
            $display("PASS: Word 2 preserved");
        end

        if (dut.data_ram[11] !== 32'd34) begin
            errors = errors + 1;
            $display("ERROR: Word 3 was not preserved: %h", dut.data_ram[11]);
        end else begin
            $display("PASS: Word 3 preserved");
        end

        // Test 2: Reading the same address should now be a hit.
        $display("\nTEST 2: READ AFTER WRITE-ALLOCATE");

        access(0, 32'h00000024, 0);

        if (hits !== 1) begin
            errors = errors + 1;
            $display("ERROR: Expected a cache hit, got %0d", hits);
        end else begin
            $display("PASS: Following read is a cache hit");
        end

        if (rdata !== 32'hDEADBEEF) begin
            errors = errors + 1;
            $display("ERROR: Read-back data incorrect: %h", rdata);
        end else begin
            $display("PASS: Read-back returned DEADBEEF");
        end

        // Test 3: Write-allocate at all four word offsets.
        $display("\nTEST 3: ALL FOUR WORD OFFSETS");

        access(1, 32'h00000040, 32'hAABBCC00);
        if (dut.data_ram[16] !== 32'hAABBCC00) begin
            errors = errors + 1;
            $display("ERROR: Offset 0 write failed");
        end else
            $display("PASS: Offset 0 write");

        access(1, 32'h00000044, 32'hAABBCC11);
        if (dut.data_ram[17] !== 32'hAABBCC11) begin
            errors = errors + 1;
            $display("ERROR: Offset 1 write failed");
        end else
            $display("PASS: Offset 1 write");

        access(1, 32'h00000048, 32'hAABBCC22);
        if (dut.data_ram[18] !== 32'hAABBCC22) begin
            errors = errors + 1;
            $display("ERROR: Offset 2 write failed");
        end else
            $display("PASS: Offset 2 write");

        access(1, 32'h0000004C, 32'hAABBCC33);
        if (dut.data_ram[19] !== 32'hAABBCC33) begin
            errors = errors + 1;
            $display("ERROR: Offset 3 write failed");
        end else
            $display("PASS: Offset 3 write");

        $display("\n==============================");
        if (errors == 0)
            $display("ALL WRITE-ALLOCATE TESTS PASSED");
        else
            $display("WRITE-ALLOCATE TESTS FAILED: %0d errors", errors);
        $display("==============================");

        $finish;
    end

endmodule
