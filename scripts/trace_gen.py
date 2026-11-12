# trace_gen.py - writes memory-access traces. Format: one access per line, "R 00000400" or "W 00000400 DEADBEEF"
import random
random.seed(1)
MEM_BYTES = 16 * 1024          # testbench memory window

def write(name, accesses):
    with open(f"traces/{name}.trace", "w") as f:
        for kind, addr in accesses:
            f.write(f"{kind} {addr:08X}\n")

# 1. sequential: walk 2 KB of words (512 reads)
write("sequential", [("R", a) for a in range(0, 2048, 4)])
# 2. random over a window 4x the cache size
write("random", [("R", random.randrange(0, 4096, 4)) for _ in range(2000)])
# 3. repeated / looping: same 16 words, 50 times (temporal locality)
write("repeated", [("R", 0x400 + 4 * (i % 16)) for i in range(800)])
# 4. stride: 16 B stride (one access per block) vs 1 KB stride (every access hits the same index)
write("stride16",   [("R", (i * 16)   % MEM_BYTES) for i in range(1000)])
write("stride1024", [("R", (i * 1024) % MEM_BYTES) for i in range(1000)])
# 5. matrix 32x32 of 4-byte ints: row-major vs column-major traversal
N = 32
write("matrix_rowmajor", [("R", (r * N + c) * 4) for r in range(N) for c in range(N)])
write("matrix_colmajor", [("R", (r * N + c) * 4) for c in range(N) for r in range(N)])
# 6. writes: exercises write hit, write miss (no allocate) and read-back. Format: "W addr data"
with open("traces/writes.trace", "w") as f:
    f.write("R 00000100\nW 00000100 DEADBEEF\nR 00000100\n")
    f.write("W 00000900 CAFEF00D\nR 00000900\nR 00000900\n")
    for i in range(16):
        f.write(f"W {0x400 + 4*i:08X} {0x1000 + i:08X}\nR {0x400 + 4*i:08X}\n")