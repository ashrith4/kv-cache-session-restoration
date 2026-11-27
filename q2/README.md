# Q2 KV Cache Session Restoration Simulator

A small Python prototype for the Q2 research question:
**Exact restore vs. summary-based compaction vs. observation masking.**

## Important limitation
This is a **synthetic simulation**. It does not measure an actual LLM, GPU, NVMe,
or KV cache. The configurable assumptions are illustrative and must be replaced
with measurements from the team's shared testbed before drawing research conclusions.

## Requirements
- Python 3.9+
- matplotlib

## Run
```bash
python3 -m pip install -r requirements.txt
python3 q2_simulator.py
```

Outputs are written to `results/`:
- `q2_simulation_results.csv`
- `01_session_cache_size.png`
- `02_restore_latency.png`
- `03_cumulative_cost.png`
- `04_k_star.png`

## What the prototype demonstrates
1. KV-cache size grows with session length.
2. Restore latency is modeled as fixed overhead + payload transfer.
3. Summary/masking restore less context and therefore have lower modeled initial latency.
4. Cumulative post-resume cost includes a simplified penalty for context not reused.
5. `k*` is the first turn at which the masking cumulative curve exceeds exact restore.

## Next research step
Replace synthetic parameters with measured values:
- KV bytes/token from the selected model and engine
- Effective restore bandwidth and fixed restore overhead from Q1
- Prefix-cache reuse rates measured from the actual agent/session replay
- Per-turn recomputation cost measured on the selected model
- Quality scores from actual benchmark runs

Do not present simulation graphs as experimental measurements.
