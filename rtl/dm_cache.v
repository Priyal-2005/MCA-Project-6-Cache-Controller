// dm_cache.v - direct-mapped, write-through / no-write-allocate cache controller
// Default: 1 KB, 16-byte blocks, 32-bit byte addresses -> offset=4, index=6, tag=22
module dm_cache #(
    parameter WORD_BITS = 2,       // Words per block = 4
    parameter INDEX_BITS = 6,      // Cache lines = 64
    parameter WRITE_ALLOCATE = 0  // 0: No-write-allocate, 1: Write-allocate
)
(
    input  wire        clk, rst,
    // CPU side
    input  wire        req, we,
    input  wire [31:0] addr,         // byte address
    input  wire [31:0] wdata,
    output wire [31:0] rdata,
    output reg         done,         // 1-cycle completion pulse
    output wire        busy,         // high while controller is processing
    // memory side
    output reg         mem_req, mem_we,
    output reg  [31:0] mem_addr,     // word address
    output reg  [31:0] mem_wdata,
    input  wire [31:0] mem_rdata,
    input  wire        mem_ack,
    // statistics
    output reg  [31:0] hits, misses,
    output reg  [31:0] mem_reads, mem_writes
);
    localparam WORDS = 1 << WORD_BITS;
    localparam LINES = 1 << INDEX_BITS;
    localparam OFF_BITS = WORD_BITS + 2;
    localparam TAG_BITS = 32 - INDEX_BITS - OFF_BITS;

    localparam IDLE=0, LOOKUP=1, REFILL=2, WRITEMEM=3, DONE=4;
    reg [2:0] state;
    assign busy = (state != IDLE);

    reg [31:0]         data_ram [0:LINES*WORDS-1];
    reg [TAG_BITS-1:0] tag_ram  [0:LINES-1];
    reg [LINES-1:0]    valid_ram;

    reg [31:0] l_addr, l_wdata; reg l_we;
    reg [WORD_BITS-1:0] cnt;
    reg pending_write;

    wire [WORD_BITS-1:0]  word = l_addr[OFF_BITS-1:2];
    wire [INDEX_BITS-1:0] idx  = l_addr[OFF_BITS+INDEX_BITS-1:OFF_BITS];
    wire [TAG_BITS-1:0]   tag  = l_addr[31:OFF_BITS+INDEX_BITS];
    wire hit = valid_ram[idx] && (tag_ram[idx] == tag);

    // Debug wires for waveforms: the tag and valid bit stored in the indexed line
    wire [TAG_BITS-1:0] dbg_stored_tag = tag_ram[idx];
    wire                dbg_valid      = valid_ram[idx];

    assign rdata = data_ram[{idx, word}];

    always @(posedge clk) begin
        if (rst) begin
            state <= IDLE;
            valid_ram <= 0;
            hits <= 0;
            misses <= 0;
            mem_reads <= 0;
            mem_writes <= 0;
            done <= 0;
            mem_req <= 0;
            mem_we <= 0;
            cnt <= 0;
            pending_write <= 0;
        end else begin
            done <= 0;
            case (state)
            IDLE: if (req) begin
                l_addr <= addr; l_wdata <= wdata; l_we <= we; state <= LOOKUP;
            end
            LOOKUP: begin
                if (hit) begin
                    hits <= hits + 1;
                    if (l_we) begin
                        data_ram[{idx, word}] <= l_wdata;   // update cache...
                        mem_req <= 1; mem_we <= 1;          // ...and write through
                        mem_addr <= l_addr[31:2]; mem_wdata <= l_wdata;
                        state <= WRITEMEM;
                    end else state <= DONE;
                end else begin
                    misses <= misses + 1;
                    if (l_we && !WRITE_ALLOCATE) begin
                        // Write miss: no-write-allocate
                        pending_write <= 0;
                        mem_req <= 1;
                        mem_we <= 1;
                        mem_addr <= l_addr[31:2];
                        mem_wdata <= l_wdata;
                        state <= WRITEMEM;
                    end else begin
                        // Read miss OR write miss with write-allocate
                        pending_write <= l_we;
                        cnt <= 0;
                        mem_req <= 1;
                        mem_we <= 0;
                        mem_addr <= {l_addr[31:OFF_BITS], {WORD_BITS{1'b0}}};
                        state <= REFILL;
                    end
                end
            end
            REFILL: if (mem_ack) begin
                mem_reads <= mem_reads + 1;
                data_ram[{idx, cnt}] <= mem_rdata;

                if (cnt == WORDS-1) begin
                    mem_req <= 0;
                    valid_ram[idx] <= 1;
                    tag_ram[idx] <= tag;

                    if (pending_write) begin
                        data_ram[{idx, word}] <= l_wdata;

                        mem_req <= 1;
                        mem_we <= 1;
                        mem_addr <= l_addr[31:2];
                        mem_wdata <= l_wdata;

                        state <= WRITEMEM;
                    end else begin
                        state <= DONE;
                    end
                end else begin
                    cnt <= cnt + 1;
                    mem_addr <= mem_addr + 1;
                end
            end
            WRITEMEM: if (mem_ack) begin
                mem_writes <= mem_writes + 1;
                mem_req <= 0;
                mem_we <= 0;
                state <= DONE;
            end
            DONE: begin done <= 1; state <= IDLE; end
            endcase
        end
    end
endmodule