"""Measure compression and decompression throughput for challenges 01-03.

Each codec is rebuilt from `configs/<challenge>.json`, warmed up once, then
encoded and decoded `REPEATS` times. Throughput is the original (raw) size over
the median wall time, in GB/s, matching the leaderboard's definition
"measured relative to the original size".

    uv run python scripts/throughput_challenges.py
"""

import csv
import json
import os
import platform
import statistics
import time
from pathlib import Path

import numcodecs.registry
import numpy as np

import hackathon  # noqa: F401, registers codecs
from hackathon.challenges import CHALLENGES, ROOT

REPEATS = 3


def main() -> None:
    rows = []
    for key, challenge in CHALLENGES.items():
        codec = numcodecs.registry.get_codec(json.loads((ROOT / "configs" / f"{key}.json").read_text()))
        da = challenge.load()
        x = da.values
        enc = codec.encode(x)
        codec.decode(enc, out=np.empty(x.shape, dtype=x.dtype)) if key.startswith("01") else codec.decode(enc)

        enc_times, dec_times = [], []
        for _ in range(REPEATS):
            t = time.perf_counter()
            enc = codec.encode(x)
            enc_times.append(time.perf_counter() - t)
            t = time.perf_counter()
            codec.decode(enc, out=np.empty(x.shape, dtype=x.dtype)) if key.startswith("01") else codec.decode(enc)
            dec_times.append(time.perf_counter() - t)

        raw_gb = x.nbytes / 1e9
        rows.append(dict(
            challenge=key,
            raw_bytes=x.nbytes,
            compressed_bytes=int(np.array(enc).nbytes),
            encode_s=round(statistics.median(enc_times), 4),
            decode_s=round(statistics.median(dec_times), 4),
            compression_gb_per_s=round(raw_gb / statistics.median(enc_times), 5),
            decompression_gb_per_s=round(raw_gb / statistics.median(dec_times), 5),
        ))
        print(f"{key}: {rows[-1]['compression_gb_per_s']} GB/s compress, {rows[-1]['decompression_gb_per_s']} GB/s decompress", flush=True)

    out = ROOT / "results" / "challenges_throughput.csv"
    with out.open("w", newline="") as f:
        f.write(f"# machine: {platform.processor() or platform.machine()}, {os.cpu_count()} logical CPUs, "
                f"python {platform.python_version()}, single process, median of {REPEATS} runs after warm-up\n")
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
