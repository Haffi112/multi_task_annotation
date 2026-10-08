#!/usr/bin/env bash
# Regenerate the two change-tracked versions of the manuscript in the Overleaf clone.
#   diff.tex                main_CCR.tex (earlier manuscript) -> main_HSSC.tex
#   diff_HSSC_revision.tex  main_HSSC.tex before the statistical revision (git ref $BASE) -> main_HSSC.tex
# Usage: src/97_make_diffs.sh [BASE]   (default BASE: bc433ea, the Overleaf commit before the revision)
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
OL="$HERE/../6aa2a6597c4ec877dc07dd96"
BASE="${1:-bc433ea}"
TMP="$(mktemp -d)"
cd "$OL"
git show "$BASE:main_HSSC.tex" > "$TMP/main_HSSC_before_revision.tex"
latexdiff --disable-citation-markup main_CCR.tex main_HSSC.tex | python3 -I "$HERE/src/97_latexdiff_fix.py" > diff.tex
latexdiff --disable-citation-markup "$TMP/main_HSSC_before_revision.tex" main_HSSC.tex \
  | python3 -I "$HERE/src/97_latexdiff_fix.py" \
  | sed "s|^%DIF DEL .*main_HSSC_before_revision.tex|%DIF DEL main_HSSC.tex at Overleaf commit $BASE (before the statistical revision)|" > diff_HSSC_revision.tex
rm -rf "$TMP"
echo "wrote $OL/diff.tex and $OL/diff_HSSC_revision.tex"
