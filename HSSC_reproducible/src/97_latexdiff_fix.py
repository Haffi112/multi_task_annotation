"""Make a latexdiff output compile: natbib for deleted citations, no active quotes, unsplit URLs.

Usage: latexdiff OLD NEW | python src/97_latexdiff_fix.py > diff.tex
"""
import sys
s = sys.stdin.read()
pre, body = s.split("\\begin{document}", 1)
pre = pre.replace("\\documentclass[11pt]{article}",
                  "\\documentclass[11pt]{article}\n\\usepackage[round]{natbib} %DIF PREAMBLE: deleted text may use natbib commands", 1)
pre = pre.replace('\\usepackage{csquotes}\\MakeOuterQuote{"}', '\\usepackage{csquotes} %DIF PREAMBLE: active quotes disabled, they break the change markup', 1)
import re
# latexdiff splits percent-encoded characters in \url{...} (it reads % as a comment); put the URL back together.
body = re.sub(r"\\url\{\\DIFadd\{([^{}%]*)%DIF > ([^{}]*)\}\s*\}", lambda m: "\\url{" + m.group(1) + "%" + m.group(2) + "}", body)
sys.stdout.write(pre + "\\begin{document}" + body)
