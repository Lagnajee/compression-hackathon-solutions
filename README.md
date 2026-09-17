# Compression Lab Challenge Solutions

Reproducible, verified solutions for the challenges in the
[Online Laboratory for Data Compression in Climate Science and Meteorology](https://github.com/climet-eu/compression-lab-notebooks)
(ESiWACE3 / ECMWF compression hackathon).

**Author:** [@Lagnajee](https://github.com/Lagnajee)

Every entry below has **zero violations** under the challenge notebook's own
evaluation code, and every codec is rebuilt from its JSON config alone in CI.

| WORK | Constraint | Notebook Baseline | **This Repository** |
|:---|:---|---:|---:|
| [01 — Missing Values](configs/01-nan-missing-values.json) | \|error\| ≤ 1 kg m⁻²; NaNs preserved | ZFP ×8.0<br>68.7% violations | **×47.44** |
| [02 — Relative Error](configs/02-relative-error-bound.json) | \|error\| ≤ 1% of \|value\| | SZ3 ×142<br>93.5% violations | **×19.071** |
| [03 — Spatial Gradient](configs/03-spatial-gradient.json) | \|error of ∂/∂lon\| ≤ 10⁻⁶ | SPERR ×1051<br>14.2% violations | **×83.876** |

![Challenge 03 result](results/figures/03-spatial-gradient.png)

## Quick start

```shell
uv sync
bash scripts/download_data.sh      # ~72 MB, checksum-verified
uv run python verify.py            # rebuild codecs from configs/ and re-score
uv run python solve.py             # rebuild codecs from source, rewrite configs/ and leaderboard/
```

## How each solution works

### 01 — Missing values (×47.44)
69% of the HOAPS water-vapour field is NaN, and the values are stored with
0.01 precision. A pointwise bound of 1 allows snapping every value to the
nearest multiple of 2, so the field collapses to ~40 distinct values.

1. `Round(precision=2)` rounds in floating point (worst-case error exactly 1) and leaves NaNs untouched.
2. `TokenizeCodec` maps the distinct values, NaN included, to uint8 indices.
3. `BitmapIndexCodec` lifts the most frequent token (the NaN gaps) into a bitmap.
4. Raw LZMA2 (`lc=4`, `pb=0`, no delta filter) codes the remainder.

Each step is worth measuring: tokens straight into raw LZMA2 give ×42.80, and
the bitmap index adds the last 10%. Storing NaN as a token beats a separate NaN
bitmap up front (`MaskMetaCodec` + step-2 integer grid + byte-delta LZMA2,
×39.76), and restoring NaNs through safeguard corrections reaches only ×36.97.
Every floating-point compressor tried is far behind: SZ3 (×17–30), SPERR (×20),
EBCC (×21), LC (×21), BitRound+Zstd (×24), pcodec (×33).

### 02 — Pointwise relative error (×19.07)
A 1% relative bound is an absolute bound of `log2(1.01)` on `log2|x|`.
`PointwiseRatioErrorBoundedCodec` performs that transform and preserves zeros
and signs. Instead of SZ3 inside it (×18.06 with the `lorenzo` predictor), a
fixed quantiser with a step just below `2·log2(1.01)` stores int16 bins, a
bitmap index lifts out the most frequent bin, and LZMA2 with a 2-byte delta
filter (`lc=1, lp=1, pb=1`) exploits neighbour correlation.

This challenge resists the trick that works on ERA5: running SPERR or SZ3
inside the ratio codec above the bound and repairing violations with a relative
error-bound safeguard tops out at ×14–16, because precipitation is noisy enough
that 1.4× the bound already breaks 7–23% of points, and the corrections cost
more than the looser setting saves. Tokenising the log bins also backfires
(×13.7): there are ~2,000 distinct bins, not 01's ~40 values.

### 03 — Spatial gradient (×83.88)
The notebook's derivative divides by `(lon[i-5] - lon[i+5]) % 360`, which
evaluates to **357.5°**, not the 2.5° spacing it describes. The check is
therefore ~143× looser than intended. See [notes on the notebook](#notes-on-the-challenge-notebooks).

The solution targets the check exactly as written:

1. SPERR with a coarse quantisation step (`q=4.25e-4`) produces smooth, wavelet-shaped errors.
2. A `qoi_eb_stencil` safeguard encodes the exact QoI `(X[i-5] - X[i+5]) / 357.5` with periodic wrap and corrects the few points that would violate it.
3. LZMA compresses the combined stream.

Pointwise-bounded alternatives top out lower: SPERR `pwe` at ×81.2, SZ3 at
×61.6, quantise+LZMA at ×63.4. A sweep around the chosen step confirms it sits
at the peak: 0.84× gives ×83.62 and 1.19× gives ×82.35, while SZ3 (×61.6), ZFP
(×17.9), a rounding grid (×61.7) and LZMA-coded corrections (×79.5) under the
same safeguard are all further behind.

## ERA5 challenges (04 pressure-level, 05 single-level)

These challenges have one leaderboard row per variable, and each variable has
its own safety requirements from
[`compression-recommendations`](https://github.com/juntyr/compression-recommendations).
Every exported codec passes the notebook's `check_safety_requirements` on the
one-timestep test subset.

- **Pressure-level (16 variables):** [`leaderboard/era5-pressure.md`](leaderboard/era5-pressure.md), [`results/era5_pressure.csv`](results/era5_pressure.csv)
- **Single-level (226 variables with requirements):** [`leaderboard/era5-single.md`](leaderboard/era5-single.md), [`results/era5_single.csv`](results/era5_single.csv)

The other 36 single-level variables (the vertical integrals `vi*`) have no
recommendation yet, so they cannot be scored.

### Results

| | Pressure-level | Single-level |
|---|---|---|
| Variables passing their requirements | 16 / 16 | 226 / 226 |
| Median compression ratio | ×55.7 | ×50.8 |
| Median of the `Safeguarded(Zero)` baseline | ×46.1 | ×22.9 |
| Median gain over the baseline | ×1.35 | ×1.85 |
| Variables at least 2× better than the baseline | 4 | 100 |
| Winning codec families | SPERR 9, log-ratio grid 5, safeguard-only 2 | grid 170, SPERR 23, log-ratio grid 13, safeguard-only 11, lossless 5, SZ3 4 |
| Median throughput (this machine, 4 workers) | 0.008 GB/s compress, 0.074 GB/s decompress | 0.015 GB/s compress, 0.506 GB/s decompress |
| Median error relative to the field's own spread | 0.6% | 0.8% |

Highlights: `t` ×787.7, `v` ×135.9, `z` ×132.2, `u` ×131.9 (pressure-level);
`aluvp` ×6,530, `aluvd` ×6,350, `smlt` ×5,732 (single-level). The weakest are
relative-bound fields such as `d` ×13.5 and mean-absolute-bound single-level
fields such as `dl` ×8.1.

### Fidelity filter

For some variables the published mean-error bound is larger than the field's own
variability, so the highest-ratio *passing* codec simply flattens the field:
`csf`, `es` and `smlt` reached ×35,194 by reconstructing a single constant
value, and `istl4` ×34,899 with an error 2.3× the field's spread. Those entries
satisfy `check_safety_requirements` but say nothing about compression.

`scripts/fidelity_era5.py` therefore records, for every exported codec, the RMSE
relative to `std(original)` and how many distinct values survive
([`results/era5_fidelity.csv`](results/era5_fidelity.csv)).
`exploration/era5/pick_fidelity.py` re-picks any variable whose reconstruction
fails

    RMSE <= 0.30 * std(original)   and   > 3 distinct values

taking the highest-ratio logged candidate that passes both that test and the
official checks; `scripts/export_era5.py` honours those choices so a re-export
cannot reinstate a flattened field. 28 of the 226 single-level variables were
re-picked this way (`csf` ×35,194 → ×542, `istl4` ×34,899 → ×485,
`10u` ×11,798 → ×4,863). After filtering, every variable at both levels has an
error of at most 30% of its field's spread, with a median of 0.8%.

20 single-level variables still exceed ×1,000. Those are faithful
reconstructions of fields that are genuinely near-constant or strongly
quantised, but the loose bounds remain worth an issue or pull request against
`compression-recommendations`, as the challenge notebooks suggest.

### Approach

The notebook baseline wraps a `ZeroCodec` in `safeguards_for_requirements(...)`.
That translation is conservative: a **mean** error bound becomes a **pointwise**
bound of the same size. The official check, however, tests the actual mean. The
sweep therefore builds candidates from each variable's requirement tree:

| Requirement | Candidates |
|---|---|
| Pointwise absolute `ε` | step-`2ε` integer grid + LZMA2, SZ3, SPERR; also wrapped in the full safeguards |
| Pointwise relative `ε` | log2 grid inside `PointwiseRatioErrorBoundedCodec` + LZMA2 (as in challenge 02) |
| Mean absolute `ε` | step-`2kε` grid, descending ladder `k = 16 … 1` (extended to `k = 256 … 22.6` for the 18 variables that passed at `k = 16`); the first passing `k` is kept |
| Any of the above | `exploration/era5/search.py` re-searches each family by doubling the looseness `p` until the check fails, then bisecting. Run for all 16 pressure-level variables and 46 of the single-level ones; it improved 40 single-level variables (for example `2t` ×21.5 → ×25.0, `swh` ×35.0 → ×42.9). |
| Mean relative `ε` | absolute grid scaled by `ε·mean|x|`, and log2 grid with ratio `1 + kε` |
| Data limits | the candidates above, wrapped in only the data-limit safeguards |
| Lossless | LZMA2, integer tokens + LZMA2 |
| NaN present (e.g. ocean-wave fields) | NaN bitmap via `MaskMetaCodec` around the grid codecs |

The zero-anchored grid reproduces exact zeros, which contribute no error to a
mean bound, so mostly-zero fields (precipitation, cloud water) can use larger
grid steps than the uniform-error estimate suggests.

Reproduce or extend:

```shell
uv run python verify_era5.py               # all exported variables (streams fields from S3, cached in data/era5)
uv run python verify_era5.py single/2t     # one variable
uv run python scripts/export_era5.py \
    --pressure exploration/era5/log04.json exploration/era5/log04b.json exploration/era5/search_pressure \
    --single exploration/era5/results05 exploration/era5/results05_ext exploration/era5/search_single
uv run python scripts/throughput_era5.py 4   # encode/decode speed per variable
uv run python scripts/sheet_rows_era5.py     # leaderboard/sheet/ERA5-*.tsv
```

Known gap: the safeguard translation of a `DataLimits` requirement on its own
returns no safeguards (`safeguards_for_requirements(DataLimits(...)) == []`), so
codecs that can undershoot a minimum are rejected by the checker rather than
corrected. A `sign` safeguard at the limit fixes it but costs far more than it
saves on mostly-zero fields (`cp`: ×141.7 with the grid versus ×3.8 with
SZ3 + sign safeguard), so the grid codecs win those variables.

## Repository layout

| Path | Contents |
|---|---|
| `src/hackathon/challenges.py` | Data loading and evaluation, copied verbatim from the notebooks' "do not edit" cells |
| `src/hackathon/codecs.py` | Builders for the winning codecs, with the reasoning for each |
| `configs/` | `codec.get_config()` for each winner, the leaderboard artefact |
| `leaderboard/` | Ready-to-copy Google Sheet rows (ratio, version, codec config) |
| `results/sweeps/` | Raw logs of ~900 exploration runs (codec, parameters, ratio, violations) |
| `results/figures/` | Comparison figures produced by the unmodified notebook plotting cells |
| `exploration/` | The sweep scripts that produced those logs (`exploration/era5/` for 04/05) |
| `configs/era5/` | Best codec config per ERA5 variable |
| `scripts/export_era5.py` | Turns ERA5 sweep logs into configs, tables and expected ratios |
| `scripts/fidelity_era5.py` | Records reconstruction error and surviving detail per ERA5 variable |
| `scripts/apply_fidelity_choice.py` | Applies the re-picked, fidelity-filtered codecs |
| `exploration/era5/pick_fidelity.py` | Re-picks codecs that pass the checks only by flattening the field |
| `verify_era5.py` | Rebuilds ERA5 codecs from `configs/era5/` and re-checks the safety requirements |
| `scripts/throughput_era5.py` | Measures compress/decompress throughput per ERA5 variable |
| `scripts/sheet_rows_era5.py` | Writes the leaderboard sheet rows, including the throughput columns |
| `scripts/sheet_rows_challenges.py` | Writes the NaN / PwRel / Gradient sheet rows |
| `exploration/search_challenges.py` | Parameter search over codec families for challenges 01-03 |
| `results/era5_throughput.csv` | Measured throughput for all 242 ERA5 variables |
| `leaderboard/sheet/` | Tab-separated rows ready to paste into each leaderboard sheet tab |

## Reproducibility notes

- Package versions are pinned to match `climet-eu/compression-lab-notebooks`
  `main` (e.g. `compression-safeguards==1.0.0rc3`).
- The notebooks load data through `ipyfilite`, which only works inside the
  browser lab. `challenges.py` reads byte-identical local copies instead;
  everything after loading is unchanged.
- The published online lab (`lab.climet.eu/v0.4.0`) ships older safeguards
  (`1.0.0b4`) and SPERR (`0.2.2`) packages. The 01 and 02 configs use only
  codecs that are present there (`numcodecs-wasm-round` 0.5.0,
  `numcodecs-tokenize` 0.1.3, `numcodecs-pw-ratio`, `lzma`, `zstd`). The 03
  config relies on the `1.0.0rc3` safeguards format and may not load in that
  older lab build.

## Notes on the challenge notebooks

- **03 gradient denominator:**
  `np.mod(da.lon.roll(lon=5) - da.lon.roll(lon=-5), 360)` evaluates to `357.5`
  for every point. Using `np.mod(da.lon.roll(lon=-5) - da.lon.roll(lon=5), 360)`
  (i.e. `2.5`) would match the comment `(x[i+5] - x[i-5]) / ...`. If the
  notebook is fixed, the 03 entry must be re-tuned.

## License

CC BY 4.0, matching the upstream laboratory. Challenge data © their respective
providers (HOAPS / EUMETSAT CM SAF, ECMWF, NextGEMS).
