"""
Q2 KV Cache Session Restoration Simulator
---------------------------------------
Synthetic prototype for comparing:
1. Exact KV cache restoration
2. Summary-based compaction
3. Observation masking

IMPORTANT:
This is a simulation, not a real LLM/NVMe benchmark. Replace the configurable
assumptions with measurements from the shared testbed when available.
"""

import argparse
import csv
import math
import os
from dataclasses import dataclass
from typing import List, Dict

import matplotlib.pyplot as plt


@dataclass
class Config:
    session_lengths: List[int]
    bytes_per_token: float = 65536       # illustrative KV size: 64 KiB/token
    effective_restore_gbps: float = 3.0  # illustrative effective path bandwidth
    fixed_restore_ms: float = 120.0
    summary_ratio: float = 0.20           # summary retains 20% of original tokens
    summary_write_ms: float = 250.0       # cost paid during pause
    masking_ratio: float = 0.35            # masked context retains 35%
    recompute_ms_per_1k_tokens: float = 80.0
    prefix_reuse_exact: float = 0.95
    prefix_reuse_summary: float = 0.65
    prefix_reuse_masking: float = 0.45
    turns_after_resume: int = 12
    tokens_added_per_turn: int = 800
    quality_exact: float = 1.00
    quality_summary: float = 0.88
    quality_masking: float = 0.94


def kv_size_gib(tokens: int, bytes_per_token: float) -> float:
    return tokens * bytes_per_token / (1024 ** 3)


def exact_restore_ms(tokens: int, cfg: Config) -> float:
    payload_gib = kv_size_gib(tokens, cfg.bytes_per_token)
    # GiB / GB/s approximately seconds; convert to milliseconds.
    io_ms = payload_gib / cfg.effective_restore_gbps * 1000
    return cfg.fixed_restore_ms + io_ms


def compact_restore_ms(tokens: int, ratio: float, cfg: Config) -> float:
    compact_tokens = max(1, int(tokens * ratio))
    return exact_restore_ms(compact_tokens, cfg)


def turn_cost_ms(tokens: int, prefix_reuse: float, cfg: Config) -> float:
    """Illustrative per-turn recompute cost for the context not reused."""
    reused_tokens = tokens * prefix_reuse
    recomputed_tokens = max(0, tokens - reused_tokens)
    return (recomputed_tokens / 1000) * cfg.recompute_ms_per_1k_tokens


def cumulative_after_resume(tokens: int, strategy: str, cfg: Config) -> List[float]:
    if strategy == "exact":
        initial = exact_restore_ms(tokens, cfg)
        reuse = cfg.prefix_reuse_exact
        context_ratio = 1.0
    elif strategy == "summary":
        initial = compact_restore_ms(tokens, cfg.summary_ratio, cfg)
        reuse = cfg.prefix_reuse_summary
        context_ratio = cfg.summary_ratio
    elif strategy == "masking":
        initial = compact_restore_ms(tokens, cfg.masking_ratio, cfg)
        reuse = cfg.prefix_reuse_masking
        context_ratio = cfg.masking_ratio
    else:
        raise ValueError(strategy)

    cumulative = initial
    results = [cumulative]
    for turn in range(1, cfg.turns_after_resume + 1):
        context_tokens = int(tokens * context_ratio + turn * cfg.tokens_added_per_turn)
        cumulative += turn_cost_ms(context_tokens, reuse, cfg)
        results.append(cumulative)
    return results


def estimate_k_star(tokens: int, cfg: Config) -> int:
    exact_curve = cumulative_after_resume(tokens, "exact", cfg)
    masking_curve = cumulative_after_resume(tokens, "masking", cfg)
    for k, (mask_t, exact_t) in enumerate(zip(masking_curve, exact_curve)):
        if mask_t > exact_t:
            return k
    return -1


def generate_results(cfg: Config) -> List[Dict]:
    rows = []
    for tokens in cfg.session_lengths:
        rows.append({
            "session_tokens": tokens,
            "kv_cache_gib": round(kv_size_gib(tokens, cfg.bytes_per_token), 4),
            "exact_restore_ms": round(exact_restore_ms(tokens, cfg), 3),
            "summary_restore_ms": round(compact_restore_ms(tokens, cfg.summary_ratio, cfg), 3),
            "masking_restore_ms": round(compact_restore_ms(tokens, cfg.masking_ratio, cfg), 3),
            "summary_quality_score": cfg.quality_summary,
            "masking_quality_score": cfg.quality_masking,
            "exact_quality_score": cfg.quality_exact,
            "estimated_k_star": estimate_k_star(tokens, cfg),
        })
    return rows


def save_csv(rows: List[Dict], path: str):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_cache_size(cfg: Config, outdir: str):
    lengths = cfg.session_lengths
    sizes = [kv_size_gib(n, cfg.bytes_per_token) for n in lengths]
    plt.figure()
    plt.plot(lengths, sizes, marker="o")
    plt.xlabel("Session length (tokens)")
    plt.ylabel("Estimated KV cache size (GiB)")
    plt.title("Session Length vs. Estimated KV Cache Size")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, "01_session_cache_size.png"), dpi=160)
    plt.close()


def plot_restore_latency(cfg: Config, outdir: str):
    lengths = cfg.session_lengths
    exact = [exact_restore_ms(n, cfg) for n in lengths]
    summary = [compact_restore_ms(n, cfg.summary_ratio, cfg) for n in lengths]
    masking = [compact_restore_ms(n, cfg.masking_ratio, cfg) for n in lengths]
    plt.figure()
    plt.plot(lengths, exact, marker="o", label="Exact restore")
    plt.plot(lengths, summary, marker="s", label="Summary compaction")
    plt.plot(lengths, masking, marker="^", label="Observation masking")
    plt.xlabel("Session length (tokens)")
    plt.ylabel("Illustrative resume latency (ms)")
    plt.title("Resume Latency Comparison")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, "02_restore_latency.png"), dpi=160)
    plt.close()


def plot_cumulative_cost(cfg: Config, outdir: str):
    selected = cfg.session_lengths[len(cfg.session_lengths)//2]
    curves = {
        "Exact restore": cumulative_after_resume(selected, "exact", cfg),
        "Summary compaction": cumulative_after_resume(selected, "summary", cfg),
        "Observation masking": cumulative_after_resume(selected, "masking", cfg),
    }
    plt.figure()
    for name, curve in curves.items():
        plt.plot(range(len(curve)), curve, marker=".", label=name)
    plt.xlabel("Turns after resume")
    plt.ylabel("Cumulative illustrative time (ms)")
    plt.title(f"Cumulative Cost After Resume ({selected:,}-token session)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, "03_cumulative_cost.png"), dpi=160)
    plt.close()


def plot_kstar(cfg: Config, outdir: str):
    lengths = cfg.session_lengths
    kstars = [estimate_k_star(n, cfg) for n in lengths]
    plt.figure()
    plt.plot(lengths, kstars, marker="o")
    plt.xlabel("Session length (tokens)")
    plt.ylabel("Estimated crossover turn k*")
    plt.title("Predicted Masking vs. Exact Restore Crossover")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, "04_k_star.png"), dpi=160)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="results", help="Output directory")
    args = parser.parse_args()
    os.makedirs(args.out, exist_ok=True)

    cfg = Config(session_lengths=[2048, 4096, 8192, 16384, 32768, 65536])
    rows = generate_results(cfg)
    save_csv(rows, os.path.join(args.out, "q2_simulation_results.csv"))

    plot_cache_size(cfg, args.out)
    plot_restore_latency(cfg, args.out)
    plot_cumulative_cost(cfg, args.out)
    plot_kstar(cfg, args.out)

    print("Simulation complete.")
    print(f"Results and graphs saved to: {os.path.abspath(args.out)}")
    print("\nEstimated k* by session length:")
    for row in rows:
        print(f"{row['session_tokens']:>7,} tokens: k* = {row['estimated_k_star']}")


if __name__ == "__main__":
    main()
