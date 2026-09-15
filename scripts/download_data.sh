#!/usr/bin/env bash
# Download the challenge datasets (01-03) from the ESiWACE S3 bucket and verify
# them against known checksums. ERA5 data (04/05) is streamed on demand.
set -euo pipefail

BASE_URL="https://object-store.os-api.cci1.ecmwf.int/esiwacebucket"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA="${HACKATHON_DATA:-$ROOT/data}"
mkdir -p "$DATA"

declare -A FILES=(
    [hoaps.nc]="HOAPS/HOAPS_2020-08_6-hourly.nc"
    [tp.nc]="hplp/hplp_sfc_regridded_tp_025deg_steps_228_240.nc"
    [hus.nc]="NextGEMS_EW3_ICON_ngc4008/NextGEMS_regridded_hus_025deg_steps_44_45.nc"
)

for name in "${!FILES[@]}"; do
    if [[ -f "$DATA/$name" ]]; then
        echo "exists: $name"
    else
        echo "downloading: $name"
        curl -fL --retry 3 -o "$DATA/$name.part" "$BASE_URL/${FILES[$name]}"
        mv "$DATA/$name.part" "$DATA/$name"
    fi
done

(cd "$DATA" && sha256sum -c "$ROOT/scripts/SHA256SUMS")
