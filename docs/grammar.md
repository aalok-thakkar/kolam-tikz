# Formal grammar and semantics

kolam-tikz formalizes a narrow, coordinate-first vocabulary for drawing pulli
kolam motifs. It is a drawing grammar, not a definition of the broader living
practice of kolam.

## Coordinate language

A kolam program is a pair

$$
K=(D,\sigma),
\qquad
D\subset\mathbb Z^2,
\qquad
\sigma:E_D\to\{\mathsf{open},\mathsf{closed}\},
$$

where the induced cardinal gate graph is

$$
E_D=\bigl\{\{p,q\}:p,q\in D,\ \lVert p-q\rVert_1=1\bigr\}.
$$

In other words, the terminals are integer pulli coordinates and a gate can
connect only immediate north, east, south, or west neighbors. The source
language represents $D$ by \KolamPulli{x}{y} declarations and represents
nondefault values of $\sigma$ by gate commands. Every induced gate omitted
from the source is closed.

~~~tex
\begin{kolam}
  \KolamPulli{-1}{2}
  \KolamPulli{0}{2}
  \KolamPulli{1}{2}
  \KolamOpenGate{-1}{2}{0}{2}
  \KolamClosedGate{0}{2}{1}{2}
  \KolamRender
\end{kolam}
~~~

Coordinates must be canonical decimal integer literals (for example `-2`, `0`,
or `3`; not `+3`, `03`, or `-0`). Duplicate pulli, duplicate
undirected gates, undeclared gate endpoints, non-cardinal gates, and unknown
gate states are package errors.

The generic declaration

~~~tex
\KolamGate{x}{y}{u}{v}{open}
~~~

is equivalent to the corresponding open or closed shorthand. The package
accepts declarations inside TikZ \foreach loops; the shipped examples remain
explicit because the standalone auditor intentionally does not interpret
arbitrary TeX.

## Port graph and strokes

Every pulli has eight ports: two on each cardinal side. Four permanent circular
corner arcs pair adjacent side ports around the pulli. A gate supplies the
remaining pairing:

- A closed gate caps the two ports on each endpoint locally.
- An open gate cross-pairs the two lanes across the gap.

Each port has one local-arc incidence and one gate-or-cap incidence. The
resulting port graph is therefore 2-regular; its connected components are
exactly the visible closed strokes.

This is the key distinction between the grammar and a hand-drawn collection of
curves: an apparent X is a geometric crossing of two tracks, not a graph
vertex or a join. Connectivity is determined only by the port pairings.

A one-stroke motif is a program whose port graph has one connected component.
tools/kolam-audit.py reconstructs this graph independently of TikZ for
explicit declarations.

## Smooth tangent geometry

Use the package's unit grid:

~~~tex
\begin{tikzpicture}[kolam grid]
~~~

Let the unit-grid turn radius be $r$, with $0 < r < 1/2$. The
tangent-port angle is

$$
\alpha=\arcsin(2r).
$$

The default turn radius=exact sets

$$
r_*=\frac{1}{2\sqrt2},
\qquad
\alpha=45^\circ.
$$

The renderer assigns the 45-degree angle exactly rather than relying on a
floating-point inverse sine. The short intervening corner arcs then have zero
sweep and adjacent tracks are exactly collinear in the TikZ construction.

To resize a motif, apply a uniform scale=<factor> to the picture or an
enclosing scope. Do not change x and y independently: TikZ stores arc radii
as physical dimensions, while pulli coordinates use the current grid basis.
Nonuniform scaling also turns the local circles into ellipses.

## Decorative and Drop-Fan vocabularies

The general coordinate/gate grammar permits arbitrary open degrees from zero
through four. It therefore describes decorative motifs beyond the restricted
Drop-Fan family defined below.

For the optional Drop-Fan sublanguage, define the open degree

$$
d_\sigma(p)=\bigl|\{pq\in E_D:\sigma(pq)=\mathsf{open}\}\bigr|.
$$

Calling \KolamAssertDropFan requires

$$
d_\sigma(p)\in\{1,3\}
$$

for every pulli. The TeX command checks the local degree condition while
compiling. The Python auditor can additionally require a one-stroke port
graph.

## What source files guarantee

Every motif declaration specifies:

1. the pulli coordinates;
2. every nondefault gate state; and
3. the rendering style.

There are no auxiliary route fragments, invisible joins, or manually placed
stroke repairs. A reviewer can inspect the finite grammar first and then view
its rendered ornament.
