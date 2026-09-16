"""Reproducible solutions for the compression lab challenges."""

# importing these modules registers their codec ids with numcodecs, which is
# needed to rebuild codecs from their JSON configs
import numcodecs_bitmap_index  # noqa: F401
import numcodecs_combinators.best  # noqa: F401
import numcodecs_combinators.framed  # noqa: F401
import numcodecs_combinators.stack  # noqa: F401
import numcodecs_mask  # noqa: F401
import numcodecs_pw_ratio  # noqa: F401
import numcodecs_replace  # noqa: F401
import numcodecs_safeguards  # noqa: F401
import numcodecs_tokenize  # noqa: F401
import numcodecs_wasm_round  # noqa: F401
import numcodecs_wasm_sperr  # noqa: F401
import numcodecs_wasm_sz3  # noqa: F401
import numcodecs_wasm_zstd  # noqa: F401
import numcodecs_zero  # noqa: F401
