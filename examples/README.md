# Examples

These examples are deliberately explicit finite grammars, not PDFs traced by
hand. Each motif declares its pulli and gates, then invokes \KolamRender.

| Source | Start here for |
| --- | --- |
| 01-minimal-loop.tex | the smallest crossed seed and default closed gates |
| 02-hourglass.tex | a compact one-stroke decorative motif |
| 03-braided-ladder.tex | a one-stroke Drop-Fan motif |
| 04-diamond-weave.tex | a 21-pulli multi-stroke weave |
| 05-one-stroke-21.tex | the 21-pulli one-stroke hero motif |
| 07-nine-row-diamond.tex | a 41-pulli 1–3–5–7–9–7–5–3–1 diamond weave |
| 06-gallery.tex | the labelled contact sheet |

## Build from the package root

~~~sh
make examples
make check
~~~

The local .latexmkrc adds ../tex/ to the TeX search path for latexmk when an
example is built from this directory. For a direct pdflatex invocation, supply
the path yourself:

~~~sh
cd examples
TEXINPUTS=../tex: pdflatex 05-one-stroke-21.tex
~~~

The examples use the public kolam grid style, the exact-tangent preset, and
only the documented commands. Their corresponding PDFs are intentional vector
assets in the public package.
