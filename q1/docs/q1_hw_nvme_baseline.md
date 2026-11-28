# Week 2 Results: Laptop Hardware, Storage Baseline, and Candidate Model $\beta$

> **Note:** Captured on local laptop hardware (`Ashrith`, Arch Linux) for Week 2 while awaiting dedicated testbed resources (expected around the end of Week 3). Will be re-baselined on the target testbed once provisioned[cite: 1].

## 1. System and Storage Specifications
* **Host:** `Ashrith`
* **OS & Kernel:** Arch Linux (rolling), Linux `7.1.5-arch1-2`
* **CPU:** AMD Ryzen 7 5800H with Radeon Graphics (16 logical CPUs, 1 NUMA node)
* **System RAM & Swap:** 14 GiB RAM (10 GiB available at capture), 4.0 GiB swap (`zram0`)
* **NVMe Drive (`nvme0n1`):** `KINGSTON OM8PDP3256B-AA1` (238.5 GiB, `nvme`; partitions `p1` FAT32, `p2`, `p3` `aceros` NTFS, `p4` NTFS had no active mountpoint at capture time)
* **Secondary Drive (`sda`):** `ST1000LM049-2GH172` (931.5 GiB, `sata`, rotational)[cite: 1, 3]

## 2. Direct-Read Baseline Results
* **Benchmark Tool & Settings:** `dd` direct read (`iflag=direct`, `bs=1M`, `count=1024`, `1073741824` bytes / `1.0 GiB`) after `fio` was skipped due to `pacman` upgrade/library mismatch (`libcrypto.so.4`)
* **Measured Throughput:** `83.0 MB/s` in `12.9345 s`
* **Raw Log:** `results/week02_fio/dd_read_1m.txt`
* **Note for Q1:** This gives a quick local baseline on the current path; Q1's cost model will measure effective software-path bandwidth $B_{\text{eff}}$ on the target testbed's local NVMe (or NVMe-oF) during restore[cite: 1].

## 3. Candidate Models and KV Bytes per Token ($\beta$)
* **Main Model Candidate (Model A):**
  * Model & dtype: *(e.g., Qwen2.5-7B BF16)*
  * Parameters ($n_{\text{layers}}$, $n_{\text{kv\_heads}}$, $d_{\text{head}}$, bytes/element):
  * Calculated $\beta$ (bytes/token):
* **Second Model Candidate (Model B):**
  * Model & dtype: *(e.g., model with distinct KV footprint)*
  * Parameters ($n_{\text{layers}}$, $n_{\text{kv\_heads}}$, $d_{\text{head}}$, bytes/element):
  * Calculated $\beta$ (bytes/token):[cite: 1, 6]