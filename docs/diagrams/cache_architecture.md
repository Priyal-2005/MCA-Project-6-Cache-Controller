# Direct-Mapped Cache Controller Architecture

## Configuration

- Cache capacity: 1 KB
- Block size: 16 bytes
- Cache lines: 64
- Words per block: 4
- Address width: 32 bits
- Mapping: Direct-mapped
- Write policy: Write-through
- Write miss policy: No-write-allocate

## Address Format

```text
| TAG (22 bits) | INDEX (6 bits) | OFFSET (4 bits) |
|    [31:10]    |     [9:4]     |      [3:0]      |
```

The offset selects one of four 32-bit words using bits [3:2].
Bits [1:0] select the byte within a word.

## Architecture Diagram

```mermaid
flowchart TD
    CPU["CPU / Processor"]
    REQ["Request Interface<br/>req, we, addr, wdata"]
    FSM["Cache Controller FSM<br/>IDLE - LOOKUP - REFILL<br/>WRITEMEM - DONE"]

    SPLIT["Address Decoder<br/>TAG [31:10]<br/>INDEX [9:4]<br/>OFFSET [3:0]"]

    CACHE["Cache Storage<br/>Data RAM: 64 x 4 words<br/>Tag RAM: 64 entries<br/>Valid Bits: 64"]

    CMP{"Valid bit AND<br/>Tag Match?"}

    HIT["Cache Hit<br/>Read selected word"]
    MISS{"Cache Miss<br/>Read or Write?"}

    REFILL["Read Miss<br/>Fetch 4 words from memory<br/>Fill cache block<br/>Update tag and valid bit"]

    WRITEH["Write Hit<br/>Update cache word<br/>Send write to memory"]

    WRITEM["Write Miss<br/>No allocation<br/>Send write directly to memory"]

    MEM["Main Memory<br/>4096 x 32-bit words<br/>Fixed latency: 4 cycles"]

    ACK["Memory ACK"]
    DONE["Request Complete<br/>done pulse"]
    CPUDATA["Return Read Data<br/>rdata"]

    CPU --> REQ
    REQ --> FSM
    FSM --> SPLIT
    SPLIT --> CACHE
    CACHE --> CMP

    CMP -->|Hit: Read| HIT
    HIT --> CPUDATA

    CMP -->|Miss| MISS
    MISS -->|Read| REFILL
    MISS -->|Write| WRITEM

    CMP -->|Hit: Write| WRITEH

    WRITEH --> MEM
    WRITEM --> MEM
    REFILL --> MEM

    MEM --> ACK
    ACK --> FSM
    REFILL --> CACHE
    WRITEH --> DONE
    WRITEM --> DONE
    HIT --> DONE
    DONE --> CPU
    CPUDATA --> CPU
```

## Write Policy

- Write hit: Update cache and main memory.
- Write miss: Write directly to main memory without allocating a cache block.
- Read miss: Fetch the complete four-word block into cache.

## Controller States

1. IDLE
2. LOOKUP
3. REFILL
4. WRITEMEM
5. DONE
