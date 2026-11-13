
# Cache Controller Finite State Machine (FSM)

## 1. Overview

The cache controller uses a five-state Finite State Machine (FSM) to manage CPU requests, cache lookups, memory refills and write operations.

The five states are:

1. IDLE
2. LOOKUP
3. REFILL
4. WRITEMEM
5. DONE

## 2. FSM State Diagram

```mermaid
stateDiagram-v2
    [*] --> IDLE

    IDLE --> LOOKUP: CPU request

    LOOKUP --> DONE: Read hit
    LOOKUP --> REFILL: Read miss
    LOOKUP --> WRITEMEM: Write hit
    LOOKUP --> WRITEMEM: Write miss, no-write-allocate
    LOOKUP --> REFILL: Write miss, write-allocate

    REFILL --> REFILL: mem_ack, more words
    REFILL --> DONE: Read miss, final word
    REFILL --> WRITEMEM: Write miss, write-allocate, final word

    WRITEMEM --> DONE: mem_ack

    DONE --> IDLE: Request completed
```


## 3. State Descriptions

| State | Function |
|---|---|
| IDLE | Waits for a CPU request and captures the request details. |
| LOOKUP | Checks the valid bit and stored tag to identify a cache hit or miss. |
| REFILL | Fetches four words from main memory on a read miss or a write miss when write-allocate is enabled. For a write-allocate miss, the controller writes the requested word after completing the refill. |
| WRITEMEM | Sends write requests to main memory and waits for acknowledgement. |
| DONE | Generates a completion pulse and returns to IDLE. |

## 4. Control Signal Outputs

| State | mem_req | mem_we | done |
|---|---:|---:|---:|
| IDLE | 0 | 0 | 0 |
| LOOKUP | 0 | 0 | 0 |
| REFILL | 1 | 0 | 0 |
| WRITEMEM | 1 | 1 | 0 |
| DONE | 0 | 0 | 1 |

Note: The table represents the intended control-signal behaviour during each state. The memory request and write-enable signals are controlled by the FSM and maintained until the corresponding memory operation is acknowledged.

## 5. Memory Interface Handshake

The controller communicates with main memory using a request-acknowledgement handshake.

- mem_req initiates a memory operation.
- mem_we indicates whether the operation is a write.
- mem_ack indicates that the memory operation has completed.

During a read miss, the REFILL state receives four words from main memory. The memory address increments after each acknowledgement.

During a write miss with write-allocate enabled, the controller first refills the complete cache block. After receiving the final word, it updates the requested cache word and initiates a write to main memory. The WRITEMEM state waits for the memory acknowledgement before completing the CPU request.

Once the refill is complete, the controller updates the valid bit and tag.

## 6. Write Policy

The cache controller supports two write-miss policies while maintaining a write-through policy:

- **Write-through:** Every write updates main memory.
- **No-write-allocate:** A write miss updates main memory without loading the block into the cache.
- **Write-allocate:** A write miss first loads the complete block into the cache and then updates the requested word in both the cache and main memory.

The baseline configuration uses no-write-allocate. Write-allocate can be enabled through the WRITE_ALLOCATE parameter.

## 7. Conclusion

The five-state FSM coordinates cache lookup, memory communication, block refill and request completion. It ensures that CPU requests are handled in the correct sequence while maintaining communication with main memory.
