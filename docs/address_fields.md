# Address-field derivation (default configuration)

Configuration: 1 KB cache, 16-byte blocks, 32-bit byte addresses, direct-mapped.

| Step | Calculation | Result |
|---|---|---|
| Block offset bits | block = 16 B, log2(16) | 4 bits (2 select the word in the block, 2 select the byte in the word) |
| Words per block | 16 B / 4 B | 4 words (WORD_BITS = 2) |
| Number of lines | 1024 B / 16 B | 64 lines |
| Index bits | log2(64) | 6 bits (INDEX_BITS = 6) |
| Tag bits | 32 - 6 - 4 | 22 bits |

Address layout: `[31:10]` tag (22) | `[9:4]` index (6) | `[3:0]` offset (4)

Example: address 0x00000500 = binary ...0101 0000 0000
- offset = bits [3:0] = 0x0
- index = bits [9:4] = 0x50 & 0x3F = 16 (0x10)
- tag = bits [31:10] = 0x1
Address 0x00000100 has index 16 and tag 0, so it collides with 0x500 (same index, different tag). That is the conflict-miss case in the testbench.

Two addresses exactly 1 KB apart always share an index, because the index and offset together use 10 bits (2^10 = 1024).

## Other configurations (only WORD_BITS and INDEX_BITS change)

| Cache | Block | Lines | Offset | Index | Tag |
|---|---|---|---|---|---|
| 1 KB | 16 B | 64 | 4 | 6 | 22 |
| 512 B | 16 B | 32 | 4 | 5 | 23 |
| 1 KB | 32 B | 32 | 5 | 5 | 22 |
| 256 B | 8 B | 32 | 3 | 5 | 24 |
| 2 KB | 16 B | 128 | 4 | 7 | 21 |

All of these were simulated by changing only the two parameters, and every run passed the data check.
