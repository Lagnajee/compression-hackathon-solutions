"""Measure compression and decompression throughput for every exported ERA5 codec.

Each codec is rebuilt from `configs/era5/<leveltype>/<var>.json`, warmed up once,
then encoded and decoded `REPEATS` times. Throughput is the original (raw) size
divided by the median wall time, in GB/s, matching the leaderboard definition
"measured relative to the original size".

Results go to `results/era5_throughput.csv`, together with the machine and
number of concurrent workers, so the numbers can be put in context.

    uv run python scripts/throughput_era5.py [workers]
"""

import csv
import json
import os
import platform
import statistics
import sys
import time
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPEATS = 3


def measure(key: str) -> dict:
    import numcodecs.registry
    import numpy as np

    import hackathon  # noqa: F401, registers codecs
    from hackathon import era5

    leveltype, var = key.split("/")
    config = json.loads((ROOT / "configs" / "era5" / leveltype / f"{var}.json").read_text())
    codec = numcodecs.registry.get_codec(config)
    x = era5.field(leveltype, var)

    enc = codec.encode(x)
    codec.decode(enc)  # warm-up: JIT/wasm instantiation and caches

    enc_times, dec_times = [], []
    for _ in range(REPEATS):
        t = time.perf_counter()
        enc = codec.encode(x)
        enc_times.append(time.perf_counter() - t)
        t = time.perf_counter()
        codec.decode(enc)
        dec_times.append(time.perf_counter() - t)

    raw_gb = x.nbytes / 1e9
    return dict(
        key=key,
        raw_bytes=x.nbytes,
        compressed_bytes=int(np.array(enc).nbytes),
        encode_s=round(statistics.median(enc_times), 4),
        decode_s=round(statistics.median(dec_times), 4),
        compression_gb_per_s=round(raw_gb / statistics.median(enc_times), 5),
        decompression_gb_per_s=round(raw_gb / statistics.median(dec_times), 5),
    )


def main() -> None:
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    keys = sorted(json.loads((ROOT / "results" / "era5_expected.json").read_text()))
    rows = []
    with Pool(workers) as pool:
        for i, row in enumerate(pool.imap_unordered(measure, keys), 1):
            rows.append(row)
            if i % 20 == 0 or i == len(keys):
                print(f"{i}/{len(keys)} measured", flush=True)
    rows.sort(key=lambda r: r["key"])
    out = ROOT / "results" / "era5_throughput.csv"
    with out.open("w", newline="") as f:
        f.write(f"# machine: {platform.processor() or platform.machine()}, {os.cpu_count()} logical CPUs, "
                f"python {platform.python_version()}, {workers} concurrent workers, median of {REPEATS} runs after warm-up\n")
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
