// main_mem.v - word-addressed main memory with fixed access latency
module main_mem #(parameter LAT = 4, parameter DEPTH = 4096) (
    input  wire        clk, rst,
    input  wire        req, we,
    input  wire [31:0] addr,        // word address
    input  wire [31:0] wdata,
    output reg  [31:0] rdata,
    output reg         ack
);
    reg [31:0] mem [0:DEPTH-1];
    reg [7:0]  cnt;
    integer i;
    initial for (i = 0; i < DEPTH; i = i + 1) mem[i] = i * 3 + 1;   // known pattern
    always @(posedge clk) begin
        if (rst) begin cnt <= 0; ack <= 0; end
        else begin
            ack <= 0;
            if (req && !ack) begin
                if (cnt == LAT-1) begin
                    cnt <= 0; ack <= 1;
                    if (we) mem[addr[11:0]] <= wdata;
                    else    rdata <= mem[addr[11:0]];
                end else cnt <= cnt + 1;
            end
        end
    end
endmodule