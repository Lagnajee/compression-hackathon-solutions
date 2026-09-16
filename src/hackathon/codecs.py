"""Builders for the best zero-violation codec found for each challenge.

`solve.py` instantiates these and writes their `get_config()` to `configs/`;
`verify.py` rebuilds the codecs from those JSON configs only.
"""

import lzma

import numpy as np
from numcodecs import LZMA, FixedScaleOffset
from numcodecs.packbits import PackBits
from numcodecs_bitmap_index import BitmapIndexCodec
from numcodecs_combinators.framed import FramedCodecStack
from numcodecs_combinators.stack import CodecStack
from numcodecs_mask import MaskMetaCodec
from numcodecs_pw_ratio import PointwiseRatioErrorBoundedCodec
from numcodecs_replace import ReplaceFilterCodec
from numcodecs_safeguards import SafeguardedCodec
from numcodecs_tokenize import TokenizeCodec
from numcodecs_wasm_round import Round
from numcodecs_wasm_sperr import Sperr
from numcodecs_wasm_zstd import Zstd

LZMA_EXTREME = 9 | lzma.PRESET_EXTREME


def raw_lzma(*, delta: int | None, lc: int, lp: int, pb: int) -> LZMA:
    """Raw LZMA2 stream with an optional byte-delta pre-filter."""
    filters = [{"id": lzma.FILTER_DELTA, "dist": delta}] if delta else []
    filters.append({"id": lzma.FILTER_LZMA2, "preset": LZMA_EXTREME, "lc": lc, "lp": lp, "pb": pb})
    return LZMA(format=lzma.FORMAT_RAW, filters=filters)


def nan_missing_values() -> FramedCodecStack:
    """01: |error| <= 1 kg m-2 and NaNs preserved.

    Values are rounded to the nearest multiple of 2 in floating point (worst-case
    error exactly 1), which keeps NaNs as NaNs. The field then holds only ~40
    distinct values, so tokenization turns it into uint8 indices where NaN is
    just another token. A bitmap index then pulls the most frequent token (the
    NaN gaps) out into a bitmap, and a raw LZMA2 stream codes the rest. This
    beats storing a separate NaN bitmap up front (x39.76) and plain LZMA2 over
    the tokens (x42.80), because the swath gaps are predictable from their
    neighbours either way, but the bitmap keeps them out of the literal stream.
    """
    return FramedCodecStack(
        Round(precision=2.0),
        TokenizeCodec(),
        BitmapIndexCodec(max_bitmaps=1, cost_factor=1),
        raw_lzma(delta=None, lc=4, lp=0, pb=0),
    )


def nan_missing_values_bitmap() -> MaskMetaCodec:
    """01 runner-up (x39.76): NaN bitmap + integer grid + byte-delta LZMA2."""
    return MaskMetaCodec(
        mask=np.nan,
        codec=CodecStack(
            ReplaceFilterCodec(replacements={np.nan: 20.0}),
            FixedScaleOffset(offset=0, scale=0.5, dtype="<f4", astype="u1"),
            raw_lzma(delta=1, lc=4, lp=0, pb=0),
        ),
        bitmap_codec=CodecStack(PackBits(), LZMA(preset=LZMA_EXTREME)),
    )


def relative_error_bound() -> CodecStack:
    """02: |error| <= 1% of |value| (zeros exact).

    The pointwise-ratio meta-codec compresses log2|x| under the absolute bound
    log2(1.01). A fixed quantiser with a step just below 2*log2(1.01) turns the
    logs into int16 bins, a bitmap index lifts out the most frequent bin, and
    LZMA2 with a 2-byte delta filter exploits the spatial correlation between
    neighbouring bins. Running SPERR or SZ3 inside the ratio codec is worse
    here (x14-16): precipitation is noisy, so a looser setting breaks the bound
    at 7-23% of points and the safeguard corrections cost more than they save.
    """
    step = 2 * np.log2(1.01) * 0.9999
    return CodecStack(
        PointwiseRatioErrorBoundedCodec(
            eb_ratio=1.01,
            eb_abs_marker="$eb_abs",
            log_codec=CodecStack(
                FixedScaleOffset(offset=0, scale=1 / step, dtype="<f8", astype="<i2"),
                BitmapIndexCodec(max_bitmaps=1, cost_factor=1),
            ).get_config(),
            sign_codec=Zstd(level=19),
        ),
        raw_lzma(delta=2, lc=1, lp=1, pb=1),
    )


def spatial_gradient() -> CodecStack:
    """03: |error of (x[i-5] - x[i+5]) / 357.5| <= 1e-6 along periodic longitude.

    SPERR with a coarse quantisation step produces smooth errors; the stencil
    QoI safeguard encodes the notebook's exact finite-difference check and
    corrects the few points that would violate it. LZMA squeezes the result.
    """
    return CodecStack(
        SafeguardedCodec(
            codec=Sperr(mode="q", q=4.25e-4),
            safeguards=[
                {
                    "kind": "qoi_eb_stencil",
                    "qoi": "(X[I[0]-5] - X[I[0]+5]) / 357.5",
                    "neighbourhood": [{"axis": -1, "before": 5, "after": 5, "boundary": "wrap"}],
                    "type": "abs",
                    "eb": 1e-6,
                }
            ],
        ),
        LZMA(preset=LZMA_EXTREME),
    )


BEST = {
    "01-nan-missing-values": nan_missing_values,
    "02-relative-error-bound": relative_error_bound,
    "03-spatial-gradient": spatial_gradient,
}
