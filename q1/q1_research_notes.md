# Week 1: Q1 Research Notes, Kick-Off Context, and Reference Analysis

## 1. Research Scope and Alignment with Kick-Off Context

This document establishes the foundational literature and systems context for **Research Question 1 (Q1)**—formulating and validating a cost model for exact Key-Value (KV) cache restoration from storage—within the broader kick-off framework *"Does data storage matter for agent AI workloads?"* (XINNOR / Deggendorf Institute of Technology, Kirill Krinkin).

In the kick-off taxonomy of agent state tiers, session context corresponds to the attention KV cache of long sessions, scaling with context length and the number of sessions kept restorable. Across storage tiers—GPU HBM (~100 GB/GPU, TB/s), Host DRAM (~1 TB PCIe, tens of GB/s), Local NVMe (7–14 GB/s per SSD, tens of TB), and Network Storage (200–400 Gb/s, PB shared)—exact restoration from persistent storage competes against recomputing prefill from scratch.

For Q1 specifically, the objective is to evaluate whether exact restore time from a storage tier can be predicted from a concise set of measured parameters and to identify which execution stage governs each parameter:

$$T(n) = n \cdot \frac{\beta}{B_{\text{eff}}} + k(n) \cdot \tau_{\text{obj}} + \tau_0$$

where $n$ denotes token length, $\beta$ denotes KV bytes per token, $B_{\text{eff}}$ denotes effective software-path bandwidth, $k(n)$ denotes the number of storage objects, $\tau_{\text{obj}}$ denotes per-object cost, and $\tau_0$ denotes fixed per-restore overhead.

---

## 2. Reference Sources and Relevance to Q1

### A. Kick-Off Framework & Session Context References

1. **Kick-Off Presentation: *Does data storage matter for agent AI workloads?* (Krinkin, XINNOR / Deggendorf Institute of Technology)**.
   - **Summary & Findings:** Classifies agent state into long-term agent memory, session context (active and persisted KV cache), and self-improvement artifacts across GPU HBM, host DRAM, local NVMe, and network storage tiers. Topic `02 LONG-SESSION CONTEXT` frames returning to a long session after minutes or days and comparing KV reload, prefill recomputation, and compression across axes such as context length, reuse fraction, KV bytes per token, and model architectures (e.g., GQA vs. MLA).
   - **Relevance to Q1:** Grounds Q1 within the course/project scope on long-session KV restoration, storage-tier trade-offs, and model KV-footprint variation ($\beta$).

2. **LMCache (`arXiv:2510.09665`) & vLLM Tiered KV Offloading (`vllm.ai` blog, Sep 2026)**.
   - **Summary & Findings:** LMCache provides an inference-engine cache layer (compatible with engines such as vLLM) with a data plane and control plane for extracting, offloading, and retrieving KV caches across memory and storage tiers (such as CPU memory, local disk, and remote/object storage). Tiered KV offloading architectures examine moving KV blocks across storage hierarchies to reduce Time-to-First-Token (TTFT) and recompute overhead.
   - **Relevance to Q1:** Serves as a primary reference architecture for selecting a pinned cache/offloading layer and separating storage retrieval, transfer, and engine execution stages.

### B. Q1 Modeling, Bandwidth, Granularity, and Crossover References

3. **Kanichai et al. (2026), *Building py-kvcache: A Performance Characterization of External KV Caching for vLLM with NVMe SSDs* (`arXiv:2609.11744`)**
   - **Summary & Findings:** Evaluates external NVMe KV caching on 3B and 4B models across H100 PCIe and RTX 4000 Ada GPUs. Reports that the bandwidth required for restore to break even against recompute decreases from 23.2 GB/s at 1K tokens to 3.5 GB/s at 80K tokens, with no measured drive beating recompute below approximately 8K tokens on those testbeds.
   - **Relevance to Q1:** Establishes empirical break-even bandwidth scaling with context length and illustrates regimes where restore gains advantage as sequence length increases.

4. **Huang et al. (2026), *FlatCake: A Flat KVCache Storage Architecture for LLM Serving* (`arXiv:2610.38355`)**
   - **Summary & Findings:** Demonstrates an opposite regime on 8 B200 GPUs from 16K to 128K tokens, where restore is slower than recompute (e.g., ~11 s restore vs. ~8.1 s recompute at 128K tokens, with ~4.4 s attributable to SSD I/O and the remainder to CPU control, host-to-device copy, and GPU stall). Also shows non-linear recompute throughput $f(n)$, declining from ~27K to ~16K tokens/s between 8K and 128K tokens.
   - **Relevance to Q1:** Motivates stage-level latency decomposition (storage read, host/device transfer, CPU control, and compute/stall) and independent measurement of non-linear first-token recompute time $f(n)$.

5. **Shi et al. (2026), *Range: Decoupling KV-Cache Reuse Granularity from Storage Work* (`arXiv:2610.21241`)**
   - **Summary & Findings:** Shows that for a fixed 6 GiB payload, TTFT increases from 2.124 s with 192 storage objects to 3.012 s with 6,144 storage objects.
   - **Relevance to Q1:** Demonstrates that object count $k(n)$ independently affects restore latency beyond total byte volume, motivating our experimental design to vary object count separately from payload bytes so $B_{\text{eff}}$ and $\tau_{\text{obj}}$ remain identifiable.

6. **Shao et al. (2026), *EfficientAgent: What Makes KV Cache Offloading Work for Concurrent Agents?* (`arXiv:2609.33762`)**
   - **Summary & Findings:** Models load time on host DRAM using a linear-plus-intercept form $n \cdot \beta / B + \tau$.
   - **Relevance to Q1:** Provides the baseline structural form for load-time modeling that Q1 extends to NVMe (and optionally NVMe-oF) with an explicit object-count term $k(n) \cdot \tau_{\text{obj}}$ and software-path effective bandwidth $B_{\text{eff}}$.

7. **Najafizadeh et al. (HotStorage 2026), *LLM KV-cache: To Restore or To Recompute, That Is the Question***
   - **Summary & Findings:** Models restore/recompute crossover conditions and hybrid restore-plus-recompute execution.
   - **Relevance to Q1:** Clarifies prior art boundaries (so crossover existence and hybrid read/recompute splits are not claimed as novel) and anchors Q1's evaluation of predicted break-even lengths against measured $f(n)$.

---

## 3. Research Gap and Methodological Boundaries for Q1

- **Identified Gap:** Prior literature either models host-DRAM load times, characterizes hardware-specific restore-versus-recompute outcomes, or demonstrates object-granularity sensitivity without fitting a unified NVMe/NVMe-oF cost model $T(n) = n \cdot \frac{\beta}{B_{\text{eff}}} + k(n) \cdot \tau_{\text{obj}} + \tau_0$, attributing parameters to distinct execution stages, and validating cross-model predictive accuracy (including break-even length, direction, or absence of crossover) on a second model with a different $\beta$.
- **Scope & Constraints:** Local NVMe is required; GPU Direct Storage (`cuFile`, with `allow_compat_mode: false` to prevent silent host-memory fallback) and NVMe-oF are evaluated if available without making Q1 dependent on them. Cold reads must bypass the OS page cache (via direct I/O or KV sets exceeding RAM), and predictions fitted on a main model must be tested against a second model within pre-specified tolerances.
