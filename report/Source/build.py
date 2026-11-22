import os, subprocess, base64

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.dirname(SCRIPT_DIR)
FIGURES_DIR = os.path.join(SCRIPT_DIR, "figures")

def get_base64_image(filename):
    full_path = os.path.join(FIGURES_DIR, filename)
    if os.path.exists(full_path):
        with open(full_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
            ext = os.path.splitext(full_path)[1].replace(".", "").lower()
            if ext == "jpg": ext = "jpeg"
            return f"data:image/{ext};base64,{encoded}"
    else:
        print(f"Warning: Image not found: {full_path}")
        return ""

img_block_diag = get_base64_image("block_diagram.png")
img_fsm_diag = get_base64_image("fsm_diagram.png")
img_hit_miss = get_base64_image("hit_miss_comparison.png")
img_amat = get_base64_image("amat_comparison.png")
img_lat_sweep = get_base64_image("latency_sweep.png")
img_traffic = get_base64_image("memory_traffic_comparison.png")
img_res_comp = get_base64_image("resource_comparison.png")
img_wave_read = get_base64_image("read_miss_refill.png")
img_fault = get_base64_image("valid_check_removal_275_failures.png")

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Design and Performance Analysis of a Direct-Mapped Cache Controller Using Verilog</title>
<style>
  @page {
    size: letter;
    margin-top: 0.74in;
    margin-bottom: 0.74in;
    margin-left: 0.68in;
    margin-right: 0.68in;
  }
  * {
    box-sizing: border-box;
  }
  body {
    font-family: "Times New Roman", Times, Georgia, serif;
    font-size: 9.4pt;
    line-height: 1.21;
    color: #000;
    margin: 0;
    padding: 0;
  }

  /* Title Block */
  .header-block {
    text-align: center;
    margin-bottom: 11pt;
    padding-bottom: 2pt;
  }
  h1.paper-title {
    font-size: 18.2pt;
    font-weight: bold;
    margin: 0 0 7.5pt 0;
    line-height: 1.16;
    text-align: center;
  }
  .authors {
    font-size: 9.7pt;
    margin-bottom: 3.5pt;
    font-weight: bold;
    line-height: 1.26;
  }
  .affiliation {
    font-size: 8.9pt;
    margin-bottom: 2pt;
  }
  .course-team {
    font-size: 8.9pt;
    font-style: italic;
    margin-bottom: 10pt;
  }

  /* Abstract & Keywords */
  .abstract-box {
    margin: 0 0 6.5pt 0;
    text-align: justify;
    font-size: 8.8pt;
    line-height: 1.19;
  }
  .abstract-heading {
    font-weight: bold;
    font-style: italic;
  }
  .keywords-box {
    margin: 0 0 11pt 0;
    font-size: 8.8pt;
    line-height: 1.19;
    text-align: justify;
    padding-bottom: 6.5pt;
    border-bottom: 0.5pt solid #aaa;
  }
  .keywords-heading {
    font-weight: bold;
    font-style: italic;
  }

  /* Two Column Layout */
  .columns {
    column-count: 2;
    column-gap: 0.23in;
    text-align: justify;
  }

  /* Headings */
  h2.section-heading {
    font-size: 9.5pt;
    font-weight: bold;
    text-transform: uppercase;
    text-align: center;
    margin: 9.5pt 0 3.5pt 0;
    break-after: avoid;
    letter-spacing: 0.35px;
  }
  h3.subsection-heading {
    font-size: 9.3pt;
    font-weight: bold;
    font-style: italic;
    margin: 6.5pt 0 2.5pt 0;
    break-after: avoid;
  }
  p {
    margin: 0 0 4.6pt 0;
    text-indent: 1.15em;
  }
  p.no-indent {
    text-indent: 0;
  }

  /* Equations */
  .equation-table {
    width: 100%;
    margin: 3.5pt 0;
  }
  .equation-table td.eq-text {
    text-align: center;
    font-style: italic;
  }
  .equation-table td.eq-num {
    width: 25px;
    text-align: right;
    font-style: normal;
  }

  /* Tables */
  table.ieee-table {
    width: 100%;
    border-collapse: collapse;
    margin: 6.5pt 0 3.5pt 0;
    font-size: 7.4pt;
    line-height: 1.13;
    break-inside: avoid;
  }
  table.ieee-table caption {
    caption-side: top;
    text-align: center;
    font-weight: normal;
    margin-bottom: 3pt;
    font-size: 7.4pt;
  }
  table.ieee-table caption .table-num {
    text-transform: uppercase;
    font-weight: bold;
    display: block;
    margin-bottom: 1pt;
  }
  table.ieee-table th {
    border-top: 1.1pt solid #000;
    border-bottom: 0.5pt solid #000;
    padding: 2.6pt 1.8pt;
    font-weight: bold;
  }
  table.ieee-table td {
    padding: 2.4pt 1.8pt;
    border: none;
  }
  table.ieee-table tr.last-row td {
    border-bottom: 1.1pt solid #000;
  }

  /* Figures */
  .figure-container {
    margin: 7pt 0 4pt 0;
    text-align: center;
    break-inside: avoid;
  }
  .figure-container img {
    max-width: 100%;
    max-height: 1.88in;
    object-fit: contain;
    border: 0.5pt solid #ccc;
    border-radius: 1px;
    display: block;
    margin: 0 auto 2.5pt auto;
  }
  .figure-caption {
    font-size: 7.6pt;
    line-height: 1.15;
    text-align: justify;
    margin-top: 2.5pt;
  }
  .figure-caption strong {
    font-weight: bold;
  }

  .takeaway {
    font-style: italic;
    margin: 3.5pt 0 5.5pt 0;
    font-size: 8.9pt;
  }
  ul, ol {
    margin: 0 0 4.5pt 0;
    padding-left: 1.25em;
  }
  li {
    margin-bottom: 1.4pt;
  }
  .references {
    font-size: 7.4pt;
    line-height: 1.14;
    margin-top: 4pt;
  }
  .ref-item {
    padding-left: 1.45em;
    text-indent: -1.45em;
    margin-bottom: 2.6pt;
  }
  .sim-log-box {
    font-size: 6.9pt;
    background: #f8f9fa;
    border: 0.5pt solid #ccc;
    padding: 2.5pt 4pt;
    margin: 3pt 0;
    font-family: 'Courier New', Courier, monospace;
    line-height: 1.15;
    text-align: left;
    white-space: pre-wrap;
  }
</style>
</head>
<body>

<div class="header-block">
  <h1 class="paper-title">Design and Performance Analysis of a<br>Direct-Mapped Cache Controller Using Verilog</h1>
  <div class="authors">Priyal (2401010354), Anusha (2401010344), Kashika (2401010215),<br>Vaishnavi (2401010489), Sarthak (2401010420)</div>
  <div class="affiliation">Department of Computer Science and Engineering, Newton School of Technology</div>
  <div class="course-team">Modern Computer Architecture &mdash; Project 6 (Team T109)</div>
</div>

<div class="abstract-box">
  <span class="abstract-heading">Abstract&mdash;</span>Bridging the processor-memory performance gap requires efficient on-chip cache architectures. In this work, we present the design, functional verification, write-policy exploration, and FPGA physical implementation of a 1 KB direct-mapped cache controller authored in synthesizable Verilog HDL. The architecture features 64 cache lines, 16-byte blocks (4 words per block), a 5-state finite state machine (FSM), and a write-through memory policy operating alongside a fixed-latency main-memory model parameterized by access latency (LAT). Functional correctness is evaluated using self-checking directed testbenches, fault-injection tests, and eight synthetic and benchmark-derived memory traces. In the baseline configuration (LAT = 4), the cache achieves a 75.00% hit rate and 8.00-cycle Average Memory Access Time (AMAT) on sequential and matrix row-major traces, and a 99.50% hit rate with 3.10-cycle AMAT on temporal reuse traces. An optional write-allocate policy raises the hit rate on write-intensive read-back workloads from 71.05% to 84.21% without increasing total memory traffic (42 words), whereas pure streaming writes double external traffic from 512 to 1024 words and inflate latency from 8.00 to 13.00 cycles. Synthesis targeting the Lattice iCE40 HX8K FPGA demonstrates compact utilization (740 logic cells, 9% of device logic; 4 block RAMs, 12% of device memory) and achieves a post-route maximum frequency of 79.85 MHz, with critical path analysis confirming that 62.3% of cycle delay stems from routing interconnect rather than datapath logic.
</div>

<div class="keywords-box">
  <span class="keywords-heading">Keywords&mdash;</span>Cache memory, direct-mapped cache, Verilog HDL, write-through, write-allocate, memory traffic, AMAT, FPGA synthesis, Lattice iCE40.
</div>

<div class="columns">

  <h2 class="section-heading">I. Literature Review</h2>
  <p>On-chip memory hierarchies represent a fundamental architectural paradigm designed to bridge the widening performance divergence between processor execution speed and off-chip memory access latency, historically formalized as the &ldquo;memory wall&rdquo; [1], [2]. Since the early formalization of cache principles by Smith [3], modern memory hierarchies have relied upon temporal and spatial locality to maintain high instruction throughput and data availability.</p>

  <p>Cache design spaces are characterized by capacity, block granularity, placement mapping, and write policies. In his seminal survey, Smith [3] analyzed the fundamental tradeoffs between direct-mapped, set-associative, and fully associative organizations. Direct-mapped architectures, where each memory block maps to exactly one index location, provide the lowest hit latency and minimal hardware area overhead because they eliminate associative tag-matching arrays and multi-input multiplexers [2]. However, as highlighted by Jouppi [4], direct-mapped caches suffer from conflict misses when multiple active memory lines contend for identical index slots, an effect that can severely degrade IPC for non-unit-stride and matrix workloads. Jouppi demonstrated that augmenting direct-mapped structures with small victim caches or stream prefetch buffers could recoup much of the miss-rate penalty of associative caches while preserving direct-mapped cycle time [4].</p>

  <p>Write policies further govern interconnect traffic and coherence with backing storage. Hennessy and Patterson [1] classify write policies into write-through and write-back architectures. In write-through caching, every processor store synchronously updates both the resident cache line and backing main memory, ensuring immediate coherence at the cost of continuous bus traffic. Write-through systems typically deploy no-write-allocate on write misses to prevent bandwidth exhaustion from write-once streaming buffers, though write-allocate can reduce subsequent read-after-write miss penalties when local write reuse is prevalent [3].</p>

  <p>Recent developments in open-source electronic design automation (EDA) have catalyzed hardware verification and FPGA implementation on accessible platforms. Frameworks integrating the Yosys synthesis suite [5] and the nextpnr timing-driven place-and-route engine [6] provide vendor-neutral compilation targeting devices such as the Lattice iCE40 architecture [7]. Open-source flows facilitate cycle-accurate RTL verification, gate-level timing analysis, and detailed resource characterization without proprietary toolchain overhead. Building upon this body of literature, our work in Phase II focuses on the synthesizable Verilog implementation, trace-driven empirical characterization, write-policy traffic profiling, and open-source FPGA mapping of a 1 KB direct-mapped cache controller.</p>

  <h2 class="section-heading">II. Proposed Solution</h2>
  <h3 class="subsection-heading">A. Cache Architecture and Organization</h3>
  <p>The proposed cache system comprises a direct-mapped cache datapath and controller (<code>dm_cache.v</code>) interfacing directly to a processor request port on the host side and a synchronous main-memory model (<code>main_mem.v</code>) on the memory side, as illustrated in Fig. 1. The baseline configuration provides a 1 KB capacity partitioned into 64 cache lines. Each cache line holds a 16-byte block, organized as four 32-bit words (<code>WORDS=4</code>, set by <code>WORD_BITS=2</code>).</p>

  <div class="figure-container">
    <img src="{img_block_diag}" alt="Cache Architectural Block Diagram">
    <div class="figure-caption"><strong>Fig. 1.</strong> Architectural block diagram of the direct-mapped cache controller interfacing the processor request interface with main memory.</div>
  </div>

  <p>The architecture utilizes a 32-bit byte address decomposed deterministically according to parameter specifications:</p>
  <ul>
    <li><strong>Byte Offset (bits [1:0]):</strong> 2 bits selecting the byte within a 32-bit word (sub-word granularity).</li>
    <li><strong>Word Offset (bits [3:2]):</strong> 2 bits (<code>WORD_BITS=2</code>) indexing one of the four words residing in the 16-byte cache line.</li>
    <li><strong>Line Index (bits [9:4]):</strong> 6 bits (<code>INDEX_BITS=6</code>) addressing one of the 64 cache lines ($2^6 = 64$).</li>
    <li><strong>Tag (bits [31:10]):</strong> 22 bits (<code>TAG_BITS=22</code>) uniquely identifying the memory block mapping to that line ($32 - 6 - 2 - 2 = 22$).</li>
  </ul>

  <h3 class="subsection-heading">B. Controller Finite State Machine (FSM)</h3>
  <p>The controller coordinates cache lookups, tag matching, memory refills, and write-through operations via a 5-state Mealy/Moore synchronous FSM, depicted in Fig. 2:</p>
  <ol>
    <li><code>IDLE (3'b000)</code>: Default quiescent state. The controller samples the processor request signal (<code>req</code>). Upon request assertion, it latches address and write data, transitioning immediately to <code>LOOKUP</code>.</li>
    <li><code>LOOKUP (3'b001)</code>: Asserts <code>line_en</code> to read tag, valid, and data arrays at the indexed line. Tag comparison is evaluated:
      <table class="equation-table">
        <tr>
          <td class="eq-text">hit = valid[index] &amp;&amp; (tag_mem[index] == tag)</td>
          <td class="eq-num">(1)</td>
        </tr>
      </table>
      If <code>hit</code> is asserted on a read (<code>!we</code>), word multiplexing routes <code>data_mem[index][word_offset]</code> to <code>rdata</code>, hardware counter <code>hits</code> increments, and the FSM transitions to <code>DONE</code>. On a read miss (<code>!hit &amp;&amp; !we</code>), <code>misses</code> increments and the FSM transitions to <code>REFILL</code>. On a write request (<code>we</code>), the FSM transitions to <code>WRITEMEM</code> (or <code>REFILL</code> if <code>WRITE_ALLOCATE=1</code> and <code>!hit</code>).</li>
    <li><code>REFILL (3'b010)</code>: Handles 4-word burst memory refills on a read miss (or write-allocate miss). A 2-bit counter (<code>refill_word</code>) iterates through words 0 to 3. For each word, the controller asserts <code>mem_req</code> to address <code>{{tag, index, refill_word}}</code> and waits for <code>mem_ack</code>. Upon receiving each acknowledgment, data is loaded into <code>data_mem[index][refill_word]</code>. After word 3 completes, <code>tag_mem[index]</code> is updated with the request tag, <code>valid[index]</code> is set to 1, and the FSM advances to <code>DONE</code> (or <code>WRITEMEM</code> if write-allocate).</li>
    <li><code>WRITEMEM (3'b011)</code>: Executes synchronous write-through stores to backing memory. The controller asserts <code>mem_req</code> and <code>mem_we</code> with word address <code>addr[31:2]</code> and data <code>wdata</code>. If a write hit occurs, <code>data_mem[index][word_offset]</code> is updated in parallel. The FSM waits for <code>mem_ack</code>, increments <code>mem_writes</code>, and transitions to <code>DONE</code>.</li>
    <li><code>DONE (3'b100)</code>: Asserts the processor handshake signal <code>done=1</code> for exactly one clock cycle, signaling completion of the memory transaction. On the subsequent clock edge, the controller transitions unconditionally back to <code>IDLE</code>.</li>
  </ol>

  <div class="figure-container">
    <img src="{img_fsm_diag}" alt="Cache Controller FSM Diagram">
    <div class="figure-caption"><strong>Fig. 2.</strong> Finite State Machine (FSM) state transition diagram for cache controller sequencing across read, refill, and write paths.</div>
  </div>

  <h3 class="subsection-heading">C. Memory Interface and Timing Model</h3>
  <p>The backing main-memory model (<code>main_mem.v</code>) simulates off-chip memory response with synchronous handshake protocols (<code>mem_req</code>, <code>mem_we</code>, <code>mem_ack</code>). Memory access latency is parameterized by <code>LAT</code> (baseline LAT = 4 cycles). On assertion of <code>mem_req</code>, an internal cycle counter counts down from <code>LAT</code> to 0 before asserting <code>mem_ack</code> for one cycle.</p>

  <h2 class="section-heading">III. Experimental Results and Discussion</h2>
  <h3 class="subsection-heading">A. Workload Trace Hit and Miss Rates</h3>
  <p>The cache architecture was evaluated across eight benchmark and synthetic memory traces representing distinct spatial and temporal locality behaviors. Table I catalogs the empirical results under baseline parameters (1 KB capacity, 16 B block size, LAT = 4), and Fig. 3 displays hit and miss distributions.</p>

  <table class="ieee-table">
    <caption><span class="table-num">Table I</span>Cache Hit and Miss Rates across Workload Traces (1 KB, 16 B Block, LAT = 4)</caption>
    <thead>
      <tr>
        <th style="text-align:left;">Trace File</th>
        <th style="text-align:right;">Accesses</th>
        <th style="text-align:right;">Hits</th>
        <th style="text-align:right;">Misses</th>
        <th style="text-align:right;">Hit Rate</th>
        <th style="text-align:right;">Miss Rate</th>
        <th style="text-align:right;">Avg Cyc</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td style="text-align:left;">sequential</td>
        <td style="text-align:right;">64</td>
        <td style="text-align:right;">48</td>
        <td style="text-align:right;">16</td>
        <td style="text-align:right;">75.00%</td>
        <td style="text-align:right;">25.00%</td>
        <td style="text-align:right;">8.00</td>
      </tr>
      <tr>
        <td style="text-align:left;">repeated</td>
        <td style="text-align:right;">200</td>
        <td style="text-align:right;">199</td>
        <td style="text-align:right;">1</td>
        <td style="text-align:right;">99.50%</td>
        <td style="text-align:right;">0.50%</td>
        <td style="text-align:right;">3.10</td>
      </tr>
      <tr>
        <td style="text-align:left;">stride16</td>
        <td style="text-align:right;">64</td>
        <td style="text-align:right;">48</td>
        <td style="text-align:right;">16</td>
        <td style="text-align:right;">75.00%</td>
        <td style="text-align:right;">25.00%</td>
        <td style="text-align:right;">8.00</td>
      </tr>
      <tr>
        <td style="text-align:left;">stride1024</td>
        <td style="text-align:right;">64</td>
        <td style="text-align:right;">0</td>
        <td style="text-align:right;">64</td>
        <td style="text-align:right;">0.00%</td>
        <td style="text-align:right;">100.00%</td>
        <td style="text-align:right;">23.00</td>
      </tr>
      <tr>
        <td style="text-align:left;">random</td>
        <td style="text-align:right;">2000</td>
        <td style="text-align:right;">479</td>
        <td style="text-align:right;">1521</td>
        <td style="text-align:right;">23.95%</td>
        <td style="text-align:right;">76.05%</td>
        <td style="text-align:right;">18.21</td>
      </tr>
      <tr>
        <td style="text-align:left;">matrix_rowmajor</td>
        <td style="text-align:right;">64</td>
        <td style="text-align:right;">48</td>
        <td style="text-align:right;">16</td>
        <td style="text-align:right;">75.00%</td>
        <td style="text-align:right;">25.00%</td>
        <td style="text-align:right;">8.00</td>
      </tr>
      <tr>
        <td style="text-align:left;">matrix_colmajor</td>
        <td style="text-align:right;">64</td>
        <td style="text-align:right;">0</td>
        <td style="text-align:right;">64</td>
        <td style="text-align:right;">0.00%</td>
        <td style="text-align:right;">100.00%</td>
        <td style="text-align:right;">23.00</td>
      </tr>
      <tr class="last-row">
        <td style="text-align:left;">writes</td>
        <td style="text-align:right;">38</td>
        <td style="text-align:right;">27</td>
        <td style="text-align:right;">11</td>
        <td style="text-align:right;">71.05%</td>
        <td style="text-align:right;">28.95%</td>
        <td style="text-align:right;">8.53</td>
      </tr>
    </tbody>
  </table>

  <p>The benchmark results confirm foundational caching principles:</p>
  <ul>
    <li><strong>Sequential and Stride-16 Traces:</strong> Yield exactly 75.00% hit rate. Because each cache line holds 4 words, an initial access causes a compulsory miss that prefetches the remaining 3 adjacent words, which subsequently hit (3/4 = 75.00%).</li>
    <li><strong>Repeated Access Trace:</strong> Generates a 99.50% hit rate and 3.10-cycle average latency. After a single compulsory miss on the first access, all subsequent 199 accesses hit in cache lines, demonstrating near-ideal temporal locality exploitation.</li>
    <li><strong>Matrix Row-Major vs. Column-Major:</strong> Row-major traversal achieves 75.00% hit rate due to contiguous word access across rows. In contrast, column-major access exhibits 0.00% hit rate, as stride increments jump across lines, causing 100% compulsory misses.</li>
    <li><strong>Stride-1024 Trace:</strong> Produces 0.00% hit rate because consecutive accesses differ by 1024 bytes. Because the index field is bits [9:4], every address maps to the identical cache line index (<code>index=0</code>), creating severe conflict thrashing that evicts the resident line on every cycle.</li>
    <li><strong>Random Trace:</strong> With 2000 accesses distributed uniformly across address space, the exact hit rate is 479/2000 = 23.95% (rounded to 24.0% in summary charts). The measured miss rate of 1521/2000 = 76.05% reflects random line collisions across the 64 available lines.</li>
  </ul>

  <div class="figure-container">
    <img src="{img_hit_miss}" alt="Cache Hit and Miss Comparison Plot">
    <div class="figure-caption"><strong>Fig. 3.</strong> Cache hit and miss counts across the eight evaluation traces under baseline parameters (1 KB, 16 B Block, LAT = 4).</div>
  </div>

  <p class="takeaway"><em>Takeaway:</em> Cache efficiency is fundamentally governed by memory access patterns: contiguous spatial layouts yield 75% hit rates via multi-word refills, whereas large strides cause line thrashing and collapse hit rates to 0%.</p>

  <h3 class="subsection-heading">B. Average Memory Access Time (AMAT)</h3>
  <p>AMAT quantifies memory hierarchy performance and is calculated using:</p>
  <table class="equation-table">
    <tr>
      <td class="eq-text">AMAT = Hit Time + (Miss Rate &times; Miss Penalty)</td>
      <td class="eq-num">(2)</td>
    </tr>
  </table>
  <p>In the simulated architecture with LAT = 4, timing measurements establish:</p>
  <ul>
    <li><strong>Hit Time:</strong> 3 clock cycles (<code>IDLE &rarr; LOOKUP &rarr; DONE &rarr; IDLE</code>).</li>
    <li><strong>Miss Penalty:</strong> 20 clock cycles. A read miss refills 4 words, each requiring LAT + 1 = 5 cycles (4 latency cycles plus 1 handshake cycle), totaling 4 &times; 5 = 20 cycles. Total miss latency is 3 + 20 = 23 cycles.</li>
  </ul>
  <p>Substituting these verified parameters yields the baseline evaluation formula:</p>
  <table class="equation-table">
    <tr>
      <td class="eq-text">AMAT = 3 + (Miss Rate &times; 20)</td>
      <td class="eq-num">(3)</td>
    </tr>
  </table>
  <p>For sequential access (Miss Rate = 0.25): AMAT = 3 + (0.25 &times; 20) = 8.00 cycles, matching cycle-accurate simulation. For repeated access (Miss Rate = 0.005): AMAT = 3 + (0.005 &times; 20) = 3.10 cycles.</p>

  <p>It is critical to distinguish theoretical read AMAT from measured write latency. The standard formula assumes read-dominant access where a miss incurs a full 20-cycle block refill. For the write workload (<code>writes.trace</code>: 20 reads, 18 writes, 28.95% miss rate), applying the read AMAT equation would yield 3 + (0.2895 &times; 20) = 8.79 cycles. However, cycle-accurate simulation in <code>tb_trace.v</code> measures an average access latency of exactly <strong>8.53 clock cycles</strong>.</p>
  
  <p>This exact measurement is traceable directly to the cycle accumulation in <code>tb_trace.v</code> (totaling 324 cycles over 38 accesses): (1) 6 read misses &times; 23 cycles = 138; (2) 14 read hits &times; 3 cycles = 42; (3) 13 write hits &times; 8 cycles = 104; and (4) 5 write misses &times; 8 cycles = 40. Summing these yields exactly 324 cycles (324 / 38 = 8.5263 &approx; 8.53 cycles). Under the default no-write-allocate policy, write misses do not refill a 4-word block; instead, they post a single word directly to memory via <code>WRITEMEM</code>, completing in only 8 cycles (3 lookup + LAT memory write + 1 handshake = 8). Consequently, the measured 8.53-cycle latency accurately accounts for write-through execution paths. Fig. 4 illustrates AMAT values across workloads.</p>
  
  <div class="sim-log-box"><strong>Verification Log (<code>tb_trace.v</code> execution on <code>writes.trace</code>):</strong>
Trace: traces/writes.trace | WRITE_ALLOCATE=0 | LAT=4
accesses=38 hits=27 misses=11 | hit_rate=71.1% miss_rate=28.9%
avg_cycles_per_access=8.53  AMAT(formula)=8.79  no_cache_baseline=4
Accumulated cycles: 6*23 + 14*3 + 13*8 + 5*8 = 324 cycles / 38 accesses = 8.5263 cycles
DATA CHECK PASSED</div>

  <div class="figure-container">
    <img src="{img_amat}" alt="AMAT Comparison Plot">
    <div class="figure-caption"><strong>Fig. 4.</strong> Average Memory Access Time (AMAT) in clock cycles across benchmark workloads (LAT = 4).</div>
  </div>

  <p class="takeaway"><em>Takeaway:</em> AMAT scales linearly with read miss penalty (20 cycles at LAT = 4), while write-containing workloads require measured cycle accounting due to single-word write-through timing.</p>

  <h3 class="subsection-heading">C. Cache versus No-Cache Comparison</h3>
  <p>In a system without cache, the processor accesses main memory directly, incurring LAT cycles per operation. Table II evaluates average access cycles between the cache-enabled design and the no-cache baseline across memory latencies from LAT = 4 to LAT = 100.</p>

  <table class="ieee-table">
    <caption><span class="table-num">Table II</span>Average Access Latency (Cycles): Cache vs. No-Cache Across Latencies</caption>
    <thead>
      <tr>
        <th style="text-align:left;">Trace File</th>
        <th style="text-align:left;">Configuration</th>
        <th style="text-align:right;">LAT 4</th>
        <th style="text-align:right;">LAT 20</th>
        <th style="text-align:right;">LAT 100</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td style="text-align:left;">sequential</td>
        <td style="text-align:left;">Cache / None</td>
        <td style="text-align:right;">8.00 / 4</td>
        <td style="text-align:right;">24.00 / 20</td>
        <td style="text-align:right;">104.00 / 100</td>
      </tr>
      <tr>
        <td style="text-align:left;">random</td>
        <td style="text-align:left;">Cache / None</td>
        <td style="text-align:right;">18.21 / 4</td>
        <td style="text-align:right;">66.88 / 20</td>
        <td style="text-align:right;">310.24 / 100</td>
      </tr>
      <tr>
        <td style="text-align:left;">repeated</td>
        <td style="text-align:left;">Cache / None</td>
        <td style="text-align:right;">3.10 / 4</td>
        <td style="text-align:right;">3.42 / 20</td>
        <td style="text-align:right;">5.02 / 100</td>
      </tr>
      <tr>
        <td style="text-align:left;">matrix_rowmajor</td>
        <td style="text-align:left;">Cache / None</td>
        <td style="text-align:right;">8.00 / 4</td>
        <td style="text-align:right;">24.00 / 20</td>
        <td style="text-align:right;">104.00 / 100</td>
      </tr>
      <tr class="last-row">
        <td style="text-align:left;">matrix_colmajor</td>
        <td style="text-align:left;">Cache / None</td>
        <td style="text-align:right;">23.00 / 4</td>
        <td style="text-align:right;">87.00 / 20</td>
        <td style="text-align:right;">407.00 / 100</td>
      </tr>
    </tbody>
  </table>

  <p>The comparison reveals critical performance crossover points:</p>
  <ul>
    <li>At low memory latency (LAT = 4), cache overhead (3 lookup cycles + 4-word refill) causes sequential access to require 8.00 cycles versus 4 cycles without cache. However, on repeated accesses, the cache wins (3.10 cycles vs. 4 cycles).</li>
    <li>As memory latency scales to LAT = 20 and LAT = 100, the benefit of caching becomes dramatic for high-hit-rate workloads: repeated access remains at 5.02 cycles at LAT = 100, achieving a <strong>19.9&times; speedup</strong> over the 100-cycle un-cached baseline.</li>
    <li>Conversely, for thrashing workloads like <code>matrix_colmajor</code> (0% hit rate), caching degrades performance across all latencies because every access incurs a 4-word block refill penalty ($3 + 4 \times (\text{LAT}+1)$ cycles).</li>
  </ul>

  <p class="takeaway"><em>Takeaway:</em> Cache controllers deliver massive speedups (up to 20&times;) when temporal locality is high and memory latency is long, but degrade throughput when conflict misses dominate and burst memory interfaces are absent.</p>

  <h3 class="subsection-heading">D. Latency Sensitivity Sweep (LAT = 2, 4, 8)</h3>
  <p>To quantify the sensitivity of access latency to memory delay, <code>tb_lat_sweep.v</code> evaluated directed test cases across memory latencies LAT &isin; (2, 4, 8). Table III records measured cycles per access.</p>

  <table class="ieee-table">
    <caption><span class="table-num">Table III</span>Measured Latencies from <code>tb_lat_sweep.v</code> across LAT &isin; (2, 4, 8)</caption>
    <thead>
      <tr>
        <th style="text-align:left;">Test Case</th>
        <th style="text-align:right;">LAT = 2</th>
        <th style="text-align:right;">LAT = 4</th>
        <th style="text-align:right;">LAT = 8</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td style="text-align:left;">T1_cold_miss (1 access)</td>
        <td style="text-align:right;">15.0</td>
        <td style="text-align:right;">23.0</td>
        <td style="text-align:right;">39.0</td>
      </tr>
      <tr>
        <td style="text-align:left;">T2_repeated (128 accesses)</td>
        <td style="text-align:right;">3.3</td>
        <td style="text-align:right;">3.6</td>
        <td style="text-align:right;">4.1</td>
      </tr>
      <tr>
        <td style="text-align:left;">T3_seq_burst (64 accesses)</td>
        <td style="text-align:right;">6.0</td>
        <td style="text-align:right;">8.0</td>
        <td style="text-align:right;">12.0</td>
      </tr>
      <tr>
        <td style="text-align:left;">T4_conflict_thrash (64 accesses)</td>
        <td style="text-align:right;">15.0</td>
        <td style="text-align:right;">23.0</td>
        <td style="text-align:right;">39.0</td>
      </tr>
      <tr>
        <td style="text-align:left;">T5_write_through (16 accesses)</td>
        <td style="text-align:right;">5.0</td>
        <td style="text-align:right;">7.0</td>
        <td style="text-align:right;">11.0</td>
      </tr>
      <tr class="last-row">
        <td style="text-align:left;">T6_full_line_fill (64 accesses)</td>
        <td style="text-align:right;">15.0</td>
        <td style="text-align:right;">23.0</td>
        <td style="text-align:right;">39.0</td>
      </tr>
    </tbody>
  </table>

  <p>In <code>tb_lat_sweep.v</code>, the T2 repeated test issues 128 accesses (8 loops of 16 words). The first 16 words generate 4 compulsory misses, followed by 124 hits, producing a 96.88% hit rate (124/128). The average access times scale gracefully from 3.3 cycles at LAT = 2, to 3.6 cycles at LAT = 4, and 4.1 cycles at LAT = 8. Conversely, test T6 (full line fill, 64 compulsory misses) incurs full block refills on every access, scaling sharply from 15.0 cycles (LAT = 2) to 23.0 cycles (LAT = 4) and 39.0 cycles (LAT = 8).</p>

  <p class="takeaway"><em>Takeaway:</em> Controlled parameter sweeping in <code>tb_lat_sweep.v</code> verifies that miss penalty scales as $4 \times (\text{LAT}+1)$, validating hardware refill timing across memory latency regimes.</p>

  <h3 class="subsection-heading">E. Latency Sweep (LAT = 4 to 100)</h3>
  <p>The broader latency sweep evaluated system performance under memory latencies spanning two orders of magnitude: LAT &isin; (4, 10, 20, 50, 100) using <code>tb_trace.v</code>, charted in Fig. 5. For repeated access, cycles per access increase minimally: 3.10 cycles at LAT = 4, 3.22 at LAT = 10, 3.42 at LAT = 20, 4.02 at LAT = 50, and 5.02 at LAT = 100. Because miss rate is merely 0.50%, 99.50% of accesses complete in 3 cycles regardless of memory delay. Conversely, for matrix column-major (100% miss rate), cycles per access equal $3 + 4 \times (\text{LAT}+1)$: 23.0 at LAT = 4, 47.0 at LAT = 10, 87.0 at LAT = 20, 207.0 at LAT = 50, and 407.0 at LAT = 100.</p>

  <div class="figure-container">
    <img src="{img_lat_sweep}" alt="Latency Sweep Plot">
    <div class="figure-caption"><strong>Fig. 5.</strong> Latency sweep comparing access cycles across memory latency parameters from LAT = 4 to LAT = 100.</div>
  </div>

  <p class="takeaway"><em>Takeaway:</em> High cache hit rates effectively decouple processor execution speed from backing memory latency, while low hit rates expose processor throughput directly to off-chip delays.</p>

  <h3 class="subsection-heading">F. Write-Policy Traffic Comparison</h3>
  <p>The controller implements write-through caching, with no-write-allocate as the default policy and write-allocate selectable via <code>WRITE_ALLOCATE</code>. Hardware counters <code>mem_reads</code> and <code>mem_writes</code> record the total 32-bit words transferred across the memory bus. Table IV summarizes comparative results from <code>tb_traffic.v</code>, and Fig. 6 depicts the traffic comparison.</p>

  <table class="ieee-table">
    <caption><span class="table-num">Table IV</span>Memory Traffic and Performance Comparison between Write Policies</caption>
    <thead>
      <tr>
        <th style="text-align:left;">Trace</th>
        <th style="text-align:left;">Policy</th>
        <th style="text-align:right;">Hit Rate</th>
        <th style="text-align:right;">Reads</th>
        <th style="text-align:right;">Writes</th>
        <th style="text-align:right;">Total</th>
        <th style="text-align:right;">Avg Cyc</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td style="text-align:left;">writes</td>
        <td style="text-align:left;">No-Alloc</td>
        <td style="text-align:right;">71.05%</td>
        <td style="text-align:right;">24</td>
        <td style="text-align:right;">18</td>
        <td style="text-align:right;">42</td>
        <td style="text-align:right;">8.53</td>
      </tr>
      <tr>
        <td style="text-align:left;">writes</td>
        <td style="text-align:left;">Allocate</td>
        <td style="text-align:right;">84.21%</td>
        <td style="text-align:right;">24</td>
        <td style="text-align:right;">18</td>
        <td style="text-align:right;">42</td>
        <td style="text-align:right;">8.53</td>
      </tr>
      <tr>
        <td style="text-align:left;">write_stream</td>
        <td style="text-align:left;">No-Alloc</td>
        <td style="text-align:right;">0.00%</td>
        <td style="text-align:right;">0</td>
        <td style="text-align:right;">512</td>
        <td style="text-align:right;">512</td>
        <td style="text-align:right;">8.00</td>
      </tr>
      <tr class="last-row">
        <td style="text-align:left;">write_stream</td>
        <td style="text-align:left;">Allocate</td>
        <td style="text-align:right;">75.00%</td>
        <td style="text-align:right;">512</td>
        <td style="text-align:right;">512</td>
        <td style="text-align:right;">1024</td>
        <td style="text-align:right;">13.00</td>
      </tr>
    </tbody>
  </table>

  <div class="figure-container">
    <img src="{img_traffic}" alt="Memory Traffic Comparison Plot">
    <div class="figure-caption"><strong>Fig. 6.</strong> Memory traffic comparison (words transferred) between write-allocate and no-write-allocate policies on writes and write_stream traces.</div>
  </div>

  <p>For the eight read-only traces, both policies yield identical hit rates and traffic counts, confirming that <code>WRITE_ALLOCATE</code> affects only the write-miss datapath. For <code>writes.trace</code> (20 reads, 18 writes with immediate read-back), write-allocate increases hit rate from 71.05% to 84.21% (hits increase from 27 to 32) with identical total memory traffic (42 words: 24 reads, 18 writes) and identical average latency (8.53 cycles). In contrast, on <code>write_stream.trace</code> (512 sequential writes without subsequent reads), write-allocate incurs an unnecessary 4-word refill for every write miss, doubling memory traffic from 512 to 1024 words and increasing average cycle latency from 8.00 to 13.00 cycles.</p>

  <p class="takeaway"><em>Takeaway:</em> Write-allocate improves hit rate without traffic penalty when written lines experience subsequent read reuse, but doubles bus traffic and increases latency on write-once streaming workloads.</p>

  <h3 class="subsection-heading">G. Synthesis Results and Flow Distinction</h3>
  <p>Physical implementation was conducted for the Lattice iCE40 HX8K FPGA (CT256 package) using the open-source Yosys (version 0.71) and nextpnr-ice40 (version 0.11.1) toolchain. It is critical to distinguish the three sequential stages of synthesis reporting: generic elaboration, technology mapping, and place-and-route timing. Table V presents metrics across both 1 KB and 512 B configurations, and Fig. 7 charts resource utilization.</p>

  <table class="ieee-table">
    <caption><span class="table-num">Table V</span>Multi-Stage FPGA Synthesis and Timing Results on Lattice iCE40 HX8K</caption>
    <thead>
      <tr>
        <th style="text-align:left;">Synthesis Flow Stage / Metric</th>
        <th style="text-align:right;">1 KB Cache</th>
        <th style="text-align:right;">512 B Cache</th>
        <th style="text-align:right;">Device Capacity</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td style="text-align:left;"><strong>Stage 1: Generic Elaboration</strong></td>
        <td style="text-align:right;"></td>
        <td style="text-align:right;"></td>
        <td style="text-align:right;"></td>
      </tr>
      <tr>
        <td style="text-align:left;">&nbsp;&nbsp;Elaborated Cells / FFs</td>
        <td style="text-align:right;">30,922 / 9,935</td>
        <td style="text-align:right;">15,735 / 5,038</td>
        <td style="text-align:right;">N/A (Generic)</td>
      </tr>
      <tr>
        <td style="text-align:left;"><strong>Stage 2: Technology Mapping</strong></td>
        <td style="text-align:right;"></td>
        <td style="text-align:right;"></td>
        <td style="text-align:right;"></td>
      </tr>
      <tr>
        <td style="text-align:left;">&nbsp;&nbsp;Logic Cells (LUT4 + Carry)</td>
        <td style="text-align:right;">740 (9.6%)</td>
        <td style="text-align:right;">677 (8.8%)</td>
        <td style="text-align:right;">7,680 LCs</td>
      </tr>
      <tr>
        <td style="text-align:left;">&nbsp;&nbsp;Mapped Flip-Flops (SB_DFF)</td>
        <td style="text-align:right;">383 (5.0%)</td>
        <td style="text-align:right;">379 (4.9%)</td>
        <td style="text-align:right;">7,680 FFs</td>
      </tr>
      <tr>
        <td style="text-align:left;">&nbsp;&nbsp;Block RAMs (SB_RAM40_4K)</td>
        <td style="text-align:right;">4 (12.5%)</td>
        <td style="text-align:right;">4 (12.5%)</td>
        <td style="text-align:right;">32 BRAMs</td>
      </tr>
      <tr>
        <td style="text-align:left;"><strong>Stage 3: Place-and-Route Timing</strong></td>
        <td style="text-align:right;"></td>
        <td style="text-align:right;"></td>
        <td style="text-align:right;"></td>
      </tr>
      <tr>
        <td style="text-align:left;">&nbsp;&nbsp;Max Operating Frequency (Fmax)</td>
        <td style="text-align:right;">79.85 MHz</td>
        <td style="text-align:right;">82.35 MHz</td>
        <td style="text-align:right;">N/A</td>
      </tr>
      <tr>
        <td style="text-align:left;">&nbsp;&nbsp;Critical Path Delay (Total)</td>
        <td style="text-align:right;">12.52 ns</td>
        <td style="text-align:right;">12.14 ns</td>
        <td style="text-align:right;">N/A</td>
      </tr>
      <tr class="last-row">
        <td style="text-align:left;">&nbsp;&nbsp;Routing Delay Proportion</td>
        <td style="text-align:right;">7.80 ns (62.3%)</td>
        <td style="text-align:right;">7.45 ns (61.4%)</td>
        <td style="text-align:right;">N/A</td>
      </tr>
    </tbody>
  </table>

  <div class="figure-container">
    <img src="{img_res_comp}" alt="FPGA Resource Comparison">
    <div class="figure-caption"><strong>Fig. 7.</strong> FPGA resource utilization comparison between 1 KB and 512 B configurations on the Lattice iCE40 HX8K FPGA.</div>
  </div>

  <p>The generic cell counts (30,922 cells, 9,935 FFs for 1 KB) represent unmapped flip-flop expansion of memory arrays and do not reflect physical FPGA cost. Technology mapping infers four embedded BRAM primitives (2 for 32-bit data RAM, 2 for 22/23-bit tag RAM). BRAM consumption is identical between 1 KB and 512 B configurations because memory count is dictated by data and tag bit-widths rather than depth. The 383 mapped flip-flops in the 1 KB design include 128 FFs dedicated to four 32-bit statistics counters (<code>hits</code>, <code>misses</code>, <code>mem_reads</code>, <code>mem_writes</code>), which would be omitted in a production embedded core.</p>

  <p>Critical-path timing analysis reveals an operating frequency of 79.85 MHz (Fmax). The critical path spans 12.52 ns: BRAM clock-to-output requires 2.15 ns, seven levels of LUT4 logic require 2.47 ns, setup requires 0.10 ns, and routing interconnect contributes 7.80 ns (62.3% of total path delay). Logic-only delay equates to a theoretical 210 MHz, demonstrating that physical routing congestion on the target FPGA dominates timing.</p>

  <p class="takeaway"><em>Takeaway:</em> The cache controller synthesizes into 740 logic cells (9%) and 4 BRAMs (12%) on an iCE40 HX8K FPGA, achieving 79.85 MHz with routing interconnect accounting for over 62% of cycle delay.</p>

  <h3 class="subsection-heading">H. Verification Summary and Robustness</h3>
  <p>Hardware verification was performed using a layered methodology across six comprehensive verification activities:</p>
  <ol>
    <li><strong>Directed Testbench (<code>tb_dm_cache.v</code>):</strong> Evaluated cold start misses, sequential reads, repeated hits, conflict thrashing, write-hit data coherence, write-miss bypass, pseudo-random reads, and full 64-line residency, completing with zero errors (<code>ALL TESTS PASSED</code>).</li>
    <li><strong>Write-Allocate Testbench (<code>tb_write_allocate.v</code>):</strong> Validated refill-before-write sequencing (<code>REFILL &rarr; WRITEMEM &rarr; DONE</code>) on write misses, reporting <code>ALL WRITE-ALLOCATE TESTS PASSED</code>.</li>
    <li><strong>Memory Latency Sweeps (<code>tb_lat_sweep.v</code>):</strong> Executed directed tests under LAT &isin; (2, 4, 8), passing all checks.</li>
    <li><strong>Write Traffic and Coherence (<code>tb_traffic.v</code>):</strong> Executed all 9 trace files under both write policies against a reference memory array; all 18 runs reported <code>DATA CHECK PASSED</code>.</li>
    <li><strong>Fault-Injection Testing:</strong> To verify testbench observability, the valid-bit check in line 47 of <code>rtl/dm_cache.v</code> was artificially disabled. The testbench immediately flagged the initial post-reset read as invalid and captured 275 cumulative verification errors (Fig. 9) before the condition was restored.</li>
    <li><strong>Gate-Level Netlist Simulation:</strong> Post-synthesis netlists for both 1 KB and 512 B configurations were simulated with Lattice iCE40 cell models, achieving 9/9 trace passes with correct data verified against the reference memory array.</li>
  </ol>

  <div class="figure-container">
    <img src="{img_wave_read}" alt="Read Miss Refill Waveform">
    <div class="figure-caption"><strong>Fig. 8.</strong> Annotated simulation waveform of a read miss and 4-word refill sequence: controller transitions IDLE &rarr; LOOKUP &rarr; REFILL &rarr; DONE, retrieving four 32-bit words with handshake.</div>
  </div>

  <div class="figure-container">
    <img src="{img_fault}" alt="Fault Injection Failure Spike">
    <div class="figure-caption"><strong>Fig. 9.</strong> Fault-injection simulation: deliberate removal of the valid-bit check condition triggers 275 errors in the verification suite, demonstrating testbench coverage.</div>
  </div>

  <p class="takeaway"><em>Takeaway:</em> Comprehensive testbench suites, gate-level simulations, and deliberate fault injection confirming 275 caught errors verify the functional correctness and robustness of the controller.</p>

  <h2 class="section-heading">IV. Individual Contributions</h2>
  <p>Project responsibilities and verifiable Phase II contributions for Team T109 are cataloged in Table VI.</p>

  <table class="ieee-table">
    <caption><span class="table-num">Table VI</span>Team T109 Individual Contributions and Phase II Ownership</caption>
    <thead>
      <tr>
        <th style="text-align:left;">Name</th>
        <th style="text-align:left;">Role in Phase II</th>
        <th style="text-align:left;">Files / Work Owned</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td style="text-align:left;">Priyal</td>
        <td style="text-align:left;">Datapath &amp; Perf. Lead</td>
        <td style="text-align:left;"><code>rtl/dm_cache.v</code> datapath, parameter sweep curation</td>
      </tr>
      <tr>
        <td style="text-align:left;">Anusha</td>
        <td style="text-align:left;">Controller &amp; Synth. Lead</td>
        <td style="text-align:left;"><code>docs/synthesis/synthesis.md</code>, <code>syn_wrap.v</code>, <code>scripts/run_synth.sh</code>, <code>tb_traffic.v</code>, <code>run_traffic.sh</code></td>
      </tr>
      <tr>
        <td style="text-align:left;">Kashika</td>
        <td style="text-align:left;">Verification Lead</td>
        <td style="text-align:left;"><code>tb_dm_cache.v</code>, <code>tb_write_allocate.v</code>, <code>tb_lat_sweep.v</code>, fault-injection, <code>verification_summary.md</code></td>
      </tr>
      <tr>
        <td style="text-align:left;">Vaishnavi</td>
        <td style="text-align:left;">Traces &amp; Plots Lead</td>
        <td style="text-align:left;"><code>traces/*.trace</code>, <code>scripts/trace_gen.py</code>, Plot scripts (<code>plot_*.py</code>), <code>docs/results/plots/</code></td>
      </tr>
      <tr class="last-row">
        <td style="text-align:left;">Sarthak</td>
        <td style="text-align:left;">Report &amp; Demo Lead</td>
        <td style="text-align:left;">IEEE technical report (<code>report/*.tex</code>), PDF generation, <code>viva_prep.md</code>, results integration, demo preparation</td>
      </tr>
    </tbody>
  </table>

  <h2 class="section-heading">V. Conclusion</h2>
  <p>Experimental evaluation of the 1 KB direct-mapped cache controller demonstrates a 75.00% hit rate and 8.00-cycle AMAT on sequential access, reaching 99.50% hit rate and 3.10-cycle AMAT under high temporal locality. Investigation of write policies establishes that while write-allocate enhances hit rate from 71.05% to 84.21% on write-and-read-back sequences, it doubles bus traffic on streaming writes from 512 to 1024 words. On the Lattice iCE40 HX8K FPGA, the design achieves 79.85 MHz post-routing frequency while occupying only 740 logic cells (9%) and 4 block RAMs (12%), with post-synthesis gate-level simulations confirming 9/9 trace passes with correct functional data.</p>

  <p>The current implementation has three primary design limitations: (1) the controller is non-pipelined and blocking, handling only a single CPU request at a time; (2) the memory interface relies on a fixed-latency model without multi-word burst transfer capabilities, preventing spatial prefetching advantages from being realized in cycle counts; and (3) the baseline write policy is write-through with no-write-allocate, requiring off-chip memory transactions on every store operation unless the optional <code>WRITE_ALLOCATE</code> mode is enabled.</p>

  <p>Future architectural enhancements for Phase III include implementing a non-blocking controller with hit-under-miss capability to support pipelined processors, designing a burst-mode SDRAM/DDR interface to exploit memory row buffers, incorporating a write-back policy with dirty bits to eliminate redundant write traffic, and implementing 2-way and 4-way set associativity with pseudo-LRU replacement to resolve the conflict misses observed in column-major and large-stride workloads.</p>

  <h2 class="section-heading">References</h2>
  <div class="references">
    <div class="ref-item">[1] J. L. Hennessy and D. A. Patterson, <em>Computer Architecture: A Quantitative Approach</em>, 6th ed. Cambridge, MA: Morgan Kaufmann, 2017.</div>
    <div class="ref-item">[2] D. A. Patterson and J. L. Hennessy, <em>Computer Organization and Design: The Hardware/Software Interface</em>, 5th ed. Waltham, MA: Morgan Kaufmann, 2014.</div>
    <div class="ref-item">[3] A. J. Smith, &ldquo;Cache Memories,&rdquo; <em>ACM Computing Surveys</em>, vol. 14, no. 3, pp. 473&ndash;530, Sep. 1982.</div>
    <div class="ref-item">[4] N. P. Jouppi, &ldquo;Improving direct-mapped cache performance by the addition of a small fully-associative cache and prefetch buffers,&rdquo; in <em>Proc. 17th Annu. Int. Symp. Comput. Archit. (ISCA)</em>, 1990, pp. 364&ndash;373.</div>
    <div class="ref-item">[5] C. Wolf, &ldquo;Yosys Open SYnthesis Suite,&rdquo; 2016. [Online]. Available: https://yosyshq.net/yosys/</div>
    <div class="ref-item">[6] D. Shah, E. Hung, C. Wolf, S. Bazanski, D. Gisselquist, and M. Milanovic, &ldquo;nextpnr: a portable framework for FPGA place and route,&rdquo; in <em>Proc. IEEE 27th Annu. Int. Symp. Field-Program. Custom Comput. Mach. (FCCM)</em>, 2019, pp. 1&ndash;4.</div>
    <div class="ref-item">[7] Lattice Semiconductor, &ldquo;iCE40 LP/HX Family Data Sheet,&rdquo; FPGA-DS-02029 (formerly DS1040), Rev. 3.5, Sep. 2018. [Online]. Available: https://www.latticesemi.com/</div>
  </div>

</div>

</body>
</html>
"""

html_path = os.path.join(SCRIPT_DIR, "report.html")
pdf_path = os.path.join(REPORT_DIR, "MCA_Project6_Report.pdf")

for img_var in ["img_block_diag", "img_fsm_diag", "img_hit_miss", "img_amat", "img_lat_sweep", "img_traffic", "img_res_comp", "img_wave_read", "img_fault"]:
    html_content = html_content.replace("{" + img_var + "}", globals()[img_var])

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

chrome_cmd = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "--headless",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={pdf_path}",
    f"file://{html_path}"
]

print(f"Compiling publication PDF to {pdf_path}...")
res = subprocess.run(chrome_cmd, capture_output=True, text=True)
if os.path.exists(pdf_path):
    print("PDF generated successfully! Size:", os.path.getsize(pdf_path), "bytes")
else:
    print("Error: PDF was not generated. stderr:", res.stderr)
