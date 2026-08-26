#!/usr/bin/env bash
# Rebuild every asset in assets/ from a source video.
# Usage: scripts/build-assets.sh path/to/source.mp4
set -euo pipefail

SRC="${1:?usage: scripts/build-assets.sh path/to/source.mp4}"
OUT="$(cd "$(dirname "$0")/.." && pwd)/assets"
mkdir -p "$OUT"

# Segments kept from the source (seconds). Everything else is a black transition.
# Find them yourself on another source with:
#   ffmpeg -i "$SRC" -vf "blackdetect=d=0.3:pix_th=0.06" -f null -
GRADE="eq=brightness=0.06:contrast=1.10:saturation=1.10,unsharp=5:5:0.7"

ffmpeg -v error -y -i "$SRC" -filter_complex "\
[0:v]trim=0.95:3.28,setpts=PTS-STARTPTS[a];\
[0:v]trim=4.92:7.20,setpts=PTS-STARTPTS[b];\
[0:v]trim=8.38:10.87,setpts=PTS-STARTPTS[c];\
[0:v]trim=12.10:14.58,setpts=PTS-STARTPTS[d];\
[0:v]trim=15.56:27.88,setpts=PTS-STARTPTS[e];\
[a][b][c][d][e]concat=n=5:v=1:a=0,fps=20,scale=1920:1080:flags=lanczos,${GRADE}[v]" \
  -map "[v]" -an \
  -c:v libx264 -crf 22 -g 10 -preset slow -pix_fmt yuv420p -movflags +faststart \
  "$OUT/storm-reveal.mp4"

STILL="eq=brightness=0.05:contrast=1.08:saturation=1.10,unsharp=5:5:0.6"
still() { # still <timestamp> <width> <quality> <name>
  ffmpeg -v error -y -ss "$1" -i "$SRC" -frames:v 1 -vf "${STILL},scale=$2:-2" -q:v "$3" "$OUT/$4"
}
still 26.5 1920 82 hero.webp
still 1.6  1400 80 detail-01.webp
still 6.8  1400 80 detail-02.webp
still 19.5 1400 80 detail-03.webp
still 26.5 1200 80 og-preview.webp

ls -lh "$OUT"
