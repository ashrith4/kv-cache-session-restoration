# Week 1: Literature Review & Groundwork — Q3 (NVMe Contention Under Agent I/O)

 
**Focus:** Research Question 3 (Q3) — Impact of concurrent agent storage traffic on KV cache restore latency  

---

## 1. Problem Overview & Hypothesis

When an agent resumes on a node where other agents are actively reading and writing to the same local NVMe drive, KV cache restoration competes for device bandwidth and queue depth. While prefill recomputation stays strictly on the GPU and host memory, KV restore depends directly on storage responsiveness.

* **Core Question:** How severely does concurrent agent I/O degrade KV restore latency on a shared NVMe SSD, and how does that slowdown shift the token length at which restoring beats recomputing?
* **Working Hypothesis:** Latency degradation is driven by I/O pattern rather than raw throughput alone. Per byte written (`iostat`), small synchronous writes (`fsync` appends and `git` metadata operations) will inflate restore `p95` significantly more than large sequential transfers, narrowing the context-length window where exact restore wins over recomputation.
* **Validation Approach:** Refit Q1’s load-time parameters ($B_{\text{eff}}$, $\tau_{\text{obj}}$, $\tau_0$) under two background load intensities for a given I/O class, then test whether the refitted model accurately predicts restore time and the new break-even length at a third intensity.

---

## 2. Background & Reference Notes

| Source | Key Takeaway | How It Informs Q3 |
| :--- | :--- | :--- |
| **Kick-Off Deck** (*Krinkin, XINNOR / DIT*) | Maps long-session KV caches to local NVMe (7–14 GB/s) and highlights `blktrace` / `eBPF` for storage-stack visibility. | Establishes the local NVMe tier boundaries and kernel-level I/O tracing tools needed to observe contention. |
| **Trace Commons** (`agent-traces` dataset) | Analysis of 29 recorded agent sessions shows minimal logging traffic: ~104 B/s per session (~0.1 MB/s across 1,000 sessions). | Proves that passive session logging is negligible and will not bottleneck NVMe restore on its own. |
| **Cursor Blog** (*Lin, 2026 — Self-Driving Codebases*) | Multi-agent coding workflows generate heavy bursts ("many GB/s") of build artifact reads and writes, turning local disk into the primary bottleneck. | Motivates testing heavy tool/build traffic alongside metadata-heavy `git` workloads rather than log writes. |
| **IBM Redbooks MD260021** (*Leung et al., 2026*) | Benchmarks KV cache restoration on a shared parallel filesystem subjected to generic background network noise. | Represents the closest prior contention study, highlighting the gap for local NVMe contention from realistic agent I/O. |
| **py-kvcache & FlatCake** (`arXiv:2609.11744`, `arXiv:2610.38355`) | Quantifies idle NVMe restore-vs.-recompute crossover points and shows how SSD read stalls propagate into end-to-end TTFT. | Provides the idle baseline behavior and stage-level timing breakdown that Q3 measures degradation against. |
| **EfficientAgent** (`arXiv:2609.33762`) | Introduces the linear load-time formulation ($n \cdot \beta / B + \tau$) extended by Q1 to include object count $k(n) \cdot \tau_{\text{obj}}$. | Supplies the parametric structure whose parameters ($B_{\text{eff}}, \tau_{\text{obj}}, \tau_0$) Q3 refits under I/O load. |

---

## 3. Experimental Setup & Boundaries (Week 1 Decisions)

* **Workload Classes to Compare:**
  1. *Small Synchronous Writes:* `fsync`-heavy appends and `git` metadata operations (`status`, `add`, `commit`).
  2. *Large Sequential I/O:* Bulk build-artifact reads/writes.
* **Intensity Sweep:** Each I/O class will run at **three or more intensity levels** (2 levels used to refit Q1's parameters; 1+ held-out level used to test predictions).
* **Generator Strategy:** Begin with controllable synthetic I/O generators (`fio` + scripted `git` loops) to establish clean parameter fits, then transition to replayed agent traces from Project 3 if/when available.
* **Measurement & Isolation Rules:**
  * Enforce cold NVMe reads (`O_DIRECT` or KV working sets larger than host DRAM) so page-cache hits do not mask device contention.
  * Track device-level write bytes and queue utilization via `iostat` (supplemented by `blktrace`/`eBPF` if needed) alongside restore `p95` across independent runs.
  * Keep multi-session simultaneous restore storms and prefetching optimizations out of scope.
