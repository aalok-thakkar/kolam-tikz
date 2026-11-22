# API reference

Use declarations inside one non-nested kolam environment for each independent
motif. Place that environment inside a TikZ picture using the package's unit
grid style.

~~~tex
\begin{tikzpicture}[kolam grid]
  \begin{kolam}
    % setup and declarations
    \KolamRender
  \end{kolam}
\end{tikzpicture}
~~~

## Setup

~~~tex
\KolamSetup{
  turn radius=exact,
  line width=1.15pt,
  dot size=4.1pt
}
~~~

\KolamSetup accepts the following keys.

| Key | Default | Meaning |
| --- | --- | --- |
| turn radius=exact | exact | Uses $r=1/(2\sqrt2)$ and an exact 45-degree port angle. |
| radius=<number> | 0.353553390593 | A custom unit-grid radius, strictly between 0 and .5. Setting it leaves exact mode. |
| line width=<dimension> | 1.15pt | Strand width. |
| dot size=<dimension> | 4.10pt | Pulli diameter. |
| dot fill=<color> | black | Pulli fill. |
| background=<color> | white | Pulli outline color. |

An out-of-range radius raises a package error and falls back to the exact
preset. The public constant \KolamExactRadius expands to the exact-preset
radius. Ordinary code should use \KolamSetup rather than the lower-level
\KolamRecompute command.

The exact-tangent guarantee assumes the kolam grid style, equivalent to
x=1cm,y=1cm. Resize a complete motif with a uniform TikZ scale=<factor>.
Changing x or y independently desynchronizes physical arc radii from the
coordinate grid.

## Pulli

~~~tex
\KolamPulli{x}{y}
\KolamThreeFiveFiveFiveThree
~~~

\KolamPulli{x}{y} declares one pulli at an integer coordinate. Both arguments
must be canonical decimal integer literals (such as `-2`, `0`, or `3`).
Declarations can be placed inside TikZ
\foreach loops.

\KolamThreeFiveFiveFiveThree declares the centered 3-5-5-5-3 field, where the
numbers are the row lengths from top to bottom:

~~~text
(-1,2) (0,2) (1,2)
(-2,1) (-1,1) (0,1) (1,1) (2,1)
(-2,0) (-1,0) (0,0) (1,0) (2,0)
(-2,-1) (-1,-1) (0,-1) (1,-1) (2,-1)
(-1,-2) (0,-2) (1,-2)
~~~

## Gates

~~~tex
\KolamGate{x}{y}{u}{v}{open}
\KolamOpenGate{x}{y}{u}{v}
\KolamClosedGate{x}{y}{u}{v}
~~~

All forms name the same undirected gate from (x,y) to (u,v). The four
coordinates must be integer literals, the endpoints must have been declared,
and their Manhattan distance must be one. The generic form accepts exactly the
states open and closed.

Every unlisted induced gate is closed. An explicit closed declaration is useful
when documenting an intentional local choice. A malformed declaration raises a
package error and is not stored.

## Rendering and validation

~~~tex
\KolamAssertDropFan  % optional: every open degree is 1 or 3
\KolamRender
~~~

\KolamRender draws permanent local corner arcs, then open-gate tracks, then
pulli. It requires at least one declared pulli.

\KolamAssertDropFan checks the optional local restriction that every pulli has
one or three open incident gates. It does not establish one-stroke
connectivity; use the independent auditor for that:

~~~sh
python3 tools/kolam-audit.py examples/03-braided-ladder.tex --drop-fan --require-one
~~~

## Styles and advanced extension point

The package exposes three TikZ styles:

| Style | Use |
| --- | --- |
| kolam grid | The intended x=1cm,y=1cm coordinate grid. |
| kolam strand | The default rendered strand appearance. |
| kolam dot | The default pulli appearance. |

\KolamPort{x}{y}{angle} is a low-level tangent-port coordinate for expert
extensions. Most motifs should use the declarative pulli and gate commands
only, so that they remain completely auditable.

## Multiple motifs

Use one kolam environment per declaration set. Separate environments may share
a TikZ picture through ordinary scopes:

~~~tex
\begin{tikzpicture}[kolam grid]
  \begin{scope}[shift={(-3,0)}]
    \begin{kolam}
      % first motif
      \KolamRender
    \end{kolam}
  \end{scope}
  \begin{scope}[shift={(3,0)}]
    \begin{kolam}
      % second motif
      \KolamRender
    \end{kolam}
  \end{scope}
\end{tikzpicture}
~~~

Do not nest kolam environments.
