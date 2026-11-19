# Q1 Sprint Plan (24-Week Schedule, Milestones, and Friday Reporting Protocol)

## 1. Governance and Weekly Sprint Protocol

- **Duration and Cadence:** 24-week project horizon with one tracked GitHub issue per week and a recurring Friday supervisor review[cite: 8].
- **Friday Check-In Format:** Prior to each Friday session, the weekly issue is updated with:
  1. Completed work and quantitative/empirical results[cite: 8],
  2. Impediments and technical questions[cite: 8],
  3. Concrete plan and next issue for the following week[cite: 8].
- **Validation Standard:** Fit $T(n) = n \cdot \frac{\beta}{B_{\text{eff}}} + k(n) \cdot \tau_{\text{obj}} + \tau_0$ on the main model, inspect stage breakdowns and residuals, and evaluate predictive accuracy (restore times and break-even behavior) on a second model with a different KV size per token ($\beta$).

---

## 2. 24-Week Execution Plan for Q1

| Week | Sprint Block | Primary Q1 Milestone / Deliverable |
| :--- | :--- | :--- |
| **Week 1** | Phase 1: Foundation & Setup | Complete Q1 literature synthesis, kick-off alignment, research gap analysis, and Q1 sprint plan; close Issue #1. |
| **Week 2** | Phase 1: Foundation & Setup | Record system and local NVMe specifications, run baseline `fio` read benchmarks, and document $\beta$ (KV bytes/token) for two candidate models. |
| **Week 3** | Phase 1: Foundation & Setup | Pin exact versions of one inference engine and one KV cache layer; verify configurations for the main and second models. |
| **Week 4** | Phase 1: Foundation & Setup | Define the fixed grid of token lengths $n$ and vary object counts $k(n)$ independently of byte volume. |
| **Week 5** | Phase 2: Harness & Cold Storage | Enforce cold reads (direct I/O or KV payload exceeding RAM); verify GDS (`allow_compat_mode: false`) and NVMe-oF status. |
| **Week 6** | Phase 2: Harness & Cold Storage | Implement the stage-by-stage timing harness measuring from resume request to first output token. |
| **Week 7** | Phase 2: Harness & Cold Storage | Validate harness repeatability across multiple restores per point (for p95) and independent runs (for spread). |
| **Week 8** | Phase 3: Main Model & Fitting | Measure first-token recompute latency $f(n)$ across the length grid on the main model. |
| **Week 9** | Phase 3: Main Model & Fitting | Collect cold exact-restore timings and stage breakdowns across lengths and object counts on the main model. |
| **Week 10** | Phase 3: Main Model & Fitting | Fit $T(n) = n \cdot \frac{\beta}{B_{\text{eff}}} + k(n) \cdot \tau_{\text{obj}} + \tau_0$ on the main model and compute parameter confidence intervals. |
| **Week 11** | Phase 3: Main Model & Fitting | Audit residuals against $n$ and object/chunk size beyond run-to-run spread; map parameters to execution stages. |
| **Week 12** | Phase 3: Main Model & Fitting | Conduct mid-project Q1 review; summarize main-model fit and stage attribution; align with Raghav and Madhav. |
| **Week 13** | Phase 4: Cross-Model Validation | Measure first-token recompute curve $f(n)$ across the length grid on the second model. |
| **Week 14** | Phase 4: Cross-Model Validation | Collect cold exact-restore measurements on the second model across the test grid. |
| **Week 15** | Phase 4: Cross-Model Validation | Predict second-model restore times and break-even lengths (including direction or no crossover) from the main-model fit. |
| **Week 16** | Phase 4: Cross-Model Validation | Evaluate prediction errors against pre-fixed tolerances and isolate stage-level causes of any discrepancies. |
| **Week 17** | Phase 5: Storage Paths & Integration | Measure GDS path (if available with `allow_compat_mode: false`) and compare against CPU staging path. |
| **Week 18** | Phase 5: Storage Paths & Integration | Measure NVMe-oF remote target path (if available) and fit cost model parameters on the remote target. |
| **Week 19** | Phase 5: Storage Paths & Integration | Deliver clean restore harness outputs, stage timings, and parameter artifacts needed by Q2 and Q3. |
| **Week 20** | Phase 5: Storage Paths & Integration | Re-verify pinned versions, cold-read compliance, and run-to-run stability across Q1 experimental runs. |
| **Week 21** | Phase 6: Finalization & Reporting | Finalize confidence intervals for $B_{\text{eff}}$, $\tau_{\text{obj}}$, $\tau_0$, p95 latencies, and break-even lengths. |
| **Week 22** | Phase 6: Finalization & Reporting | Draft the complete Q1 methodology, mathematical model, stage attribution, and result figures. |
| **Week 23** | Phase 6: Finalization & Reporting | Conduct peer review with Raghav and Madhav; audit scripts, configs, and reproducibility instructions. |
| **Week 24** | Phase 6: Finalization & Reporting | Complete final Q1 sign-off, close remaining Q1 issues, and freeze final deliverables. |
