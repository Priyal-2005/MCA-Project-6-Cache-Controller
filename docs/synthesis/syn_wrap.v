// syn_wrap.v - thin synthesis harness, used ONLY for the nextpnr place-and-route
// timing run that produces the maximum-frequency figure.
//
// Why a harness is needed: dm_cache has 329 port bits (two 32-bit CPU buses, three
// 32-bit memory buses and four 32-bit statistics counters). No iCE40 package has that
// many I/O pins (the largest, HX8K CT256, has 206), so dm_cache cannot be placed as a
// top-level chip on its own. In a real system the cache is an internal block between
// the CPU and the memory controller, and none of these signals are chip pins anyway.
//
// The harness keeps the pin count at 6 while making sure nothing inside the cache can
// be optimised away:
//   * every wide input is driven from a shift register fed by a pin, so no input can be
//     constant-folded;
//   * every output is observed through a two-stage registered XOR tree, so no output is
//     dangling and no logic driving it can be removed.
// The XOR reduction is registered per bus and then combined in a second clocked stage,
// so the observation logic itself stays far shorter than the cache's own hit path and
// does not become the reported critical path.
//
// Resource-utilisation numbers in docs/synthesis/synthesis.md are taken from dm_cache
// synthesised on its own, NOT from this harness.
module syn_wrap #(
    parameter WORD_BITS  = 2,
    parameter INDEX_BITS = 6
) (
    input  wire clk,
    input  wire rst,
    input  wire req,
    input  wire we,
    input  wire din,
    output wire dout
);
    // Shift register supplying the wide inputs.
    reg [31:0] shreg;
    always @(posedge clk) begin
        if (rst) shreg <= 32'h0000_0001;
        else     shreg <= {shreg[30:0], din};
    end

    wire [31:0] rdata, mem_addr, mem_wdata;
    wire [31:0] hits, misses, mem_reads, mem_writes;
    wire        done, busy, mem_req, mem_we;

    dm_cache #(
        .WORD_BITS(WORD_BITS),
        .INDEX_BITS(INDEX_BITS)
    ) u_cache (
        .clk(clk), .rst(rst),
        .req(req), .we(we),
        .addr(shreg), .wdata(shreg),
        .rdata(rdata), .done(done), .busy(busy),
        .mem_req(mem_req), .mem_we(mem_we),
        .mem_addr(mem_addr), .mem_wdata(mem_wdata),
        .mem_rdata(shreg), .mem_ack(shreg[0]),
        .hits(hits), .misses(misses),
        .mem_reads(mem_reads), .mem_writes(mem_writes)
    );

    // Stage 1: one registered parity bit per observed bus / control signal.
    reg [10:0] obs1;
    always @(posedge clk) begin
        obs1 <= { ^rdata, ^mem_addr, ^mem_wdata, ^hits, ^misses, ^mem_reads,
                  ^mem_writes, done, busy, mem_req, mem_we };
    end

    // Stage 2: combine the parity bits.
    reg obs2;
    always @(posedge clk) obs2 <= ^obs1;

    assign dout = obs2;
endmodule
