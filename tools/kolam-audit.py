#!/usr/bin/env python3
r"""Audit a direct coordinate declaration made with kolam-tikz.

The script reconstructs the eight-port graph specified by \KolamPulli and
\Kolam{Open,Closed}Gate declarations.  It is deliberately small and depends
only on Python's standard library.

Examples:
  python3 tools/kolam-audit.py examples/05-one-stroke-21.tex --require-one
  python3 tools/kolam-audit.py examples/03-braided-ladder.tex --drop-fan
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

POINT = tuple[int, int]
EDGE = tuple[POINT, POINT]
PORT = tuple[POINT, str]
ADJACENCY = dict[PORT, list[PORT]]

# Match exactly the coordinate spelling accepted by the TeX grammar: canonical
# decimal integers, with no leading plus sign, leading zero, or negative zero.
INTEGER = r"(?:0|[1-9]\d*|-[1-9]\d*)"
PULLI = re.compile(
    rf"\\KolamPulli\s*\{{\s*({INTEGER})\s*\}}\s*\{{\s*({INTEGER})\s*\}}"
)
PULLI_COMMAND = re.compile(r"\\KolamPulli\b")
GATE = re.compile(
    rf"\\KolamGate\s*\{{\s*({INTEGER})\s*\}}\s*\{{\s*({INTEGER})\s*\}}"
    rf"\s*\{{\s*({INTEGER})\s*\}}\s*\{{\s*({INTEGER})\s*\}}"
    r"\s*\{\s*(open|closed)\s*\}",
)
OPEN_GATE = re.compile(
    rf"\\KolamOpenGate\s*\{{\s*({INTEGER})\s*\}}\s*\{{\s*({INTEGER})\s*\}}"
    rf"\s*\{{\s*({INTEGER})\s*\}}\s*\{{\s*({INTEGER})\s*\}}"
)
CLOSED_GATE = re.compile(
    rf"\\KolamClosedGate\s*\{{\s*({INTEGER})\s*\}}\s*\{{\s*({INTEGER})\s*\}}"
    rf"\s*\{{\s*({INTEGER})\s*\}}\s*\{{\s*({INTEGER})\s*\}}"
)
GATE_COMMAND = re.compile(r"\\Kolam(?:Open|Closed)?Gate\b")

THREE_FIVE = {
    (-1, 2), (0, 2), (1, 2),
    (-2, 1), (-1, 1), (0, 1), (1, 1), (2, 1),
    (-2, 0), (-1, 0), (0, 0), (1, 0), (2, 0),
    (-2, -1), (-1, -1), (0, -1), (1, -1), (2, -1),
    (-1, -2), (0, -2), (1, -2),
}
PORTS = ("Nne", "Ene", "Ese", "Sse", "Ssw", "Wsw", "Wnw", "Nnw")
PERMANENT = (("Nne", "Ene"), ("Ese", "Sse"),
             ("Ssw", "Wsw"), ("Wnw", "Nnw"))
CAP = {"N": ("Nne", "Nnw"), "E": ("Ese", "Ene"),
       "S": ("Sse", "Ssw"), "W": ("Wnw", "Wsw")}


class AuditError(ValueError):
    """Raised for a malformed grammar declaration."""


def strip_comments(text: str) -> str:
    return "\n".join(line.split("%", 1)[0] for line in text.splitlines())


def key(a: POINT, b: POINT) -> EDGE:
    return tuple(sorted((a, b)))  # type: ignore[return-value]


def add_gate(dots: set[POINT], gates: dict[EDGE, str],
             x: str, y: str, u: str, v: str, state: str) -> None:
    a, b = (int(x), int(y)), (int(u), int(v))
    if a not in dots or b not in dots:
        raise AuditError(f"gate {a}--{b} has an undeclared endpoint")
    if abs(a[0] - b[0]) + abs(a[1] - b[1]) != 1:
        raise AuditError(f"gate {a}--{b} is not a cardinal unit edge")
    edge = key(a, b)
    if edge in gates:
        raise AuditError(f"gate {a}--{b} is declared twice")
    gates[edge] = state


def parse(path: Path) -> tuple[set[POINT], dict[EDGE, str]]:
    text = strip_comments(path.read_text())
    pulli_matches = PULLI.findall(text)
    if len(PULLI_COMMAND.findall(text)) != len(pulli_matches):
        raise AuditError("malformed \\KolamPulli declaration")
    dots: set[POINT] = set()
    for x, y in pulli_matches:
        point = int(x), int(y)
        if point in dots:
            raise AuditError(f"pulli {point} is declared twice")
        dots.add(point)
    if r"\KolamThreeFiveFiveFiveThree" in text:
        overlap = dots & THREE_FIVE
        if overlap:
            raise AuditError(f"helper duplicates explicit pulli: {sorted(overlap)}")
        dots |= THREE_FIVE
    if not dots:
        raise AuditError("no direct \\KolamPulli declaration found")

    gates: dict[EDGE, str] = {}
    generic_matches = GATE.findall(text)
    open_matches = OPEN_GATE.findall(text)
    closed_matches = CLOSED_GATE.findall(text)
    parsed_gate_count = len(generic_matches) + len(open_matches) + len(closed_matches)
    if len(GATE_COMMAND.findall(text)) != parsed_gate_count:
        raise AuditError("malformed gate declaration")

    for x, y, u, v, state in generic_matches:
        add_gate(dots, gates, x, y, u, v, state)
    for x, y, u, v in open_matches:
        add_gate(dots, gates, x, y, u, v, "open")
    for x, y, u, v in closed_matches:
        add_gate(dots, gates, x, y, u, v, "closed")
    return dots, gates


def induced_edges(dots: set[POINT]) -> set[EDGE]:
    return {key(p, (p[0] + dx, p[1] + dy))
            for p in dots for dx, dy in ((1, 0), (0, 1))
            if (p[0] + dx, p[1] + dy) in dots}


def join(adjacency: ADJACENCY, a: PORT, b: PORT) -> None:
    if a == b:
        raise AuditError(f"self-pairing at {a}")
    adjacency[a].append(b)
    adjacency[b].append(a)


def cap(adjacency: ADJACENCY, point: POINT, side: str) -> None:
    a, b = CAP[side]
    join(adjacency, (point, a), (point, b))


def audit(dots: set[POINT], declared: dict[EDGE, str]) -> dict[str, object]:
    host = induced_edges(dots)
    unknown = set(declared) - host
    if unknown:
        raise AuditError(f"non-host gate(s): {sorted(unknown)}")
    state = {edge: declared.get(edge, "closed") for edge in host}
    adjacency: ADJACENCY = defaultdict(list)

    for point in dots:
        for a, b in PERMANENT:
            join(adjacency, (point, a), (point, b))
        x, y = point
        for side, neighbor in {
            "N": (x, y + 1), "E": (x + 1, y),
            "S": (x, y - 1), "W": (x - 1, y),
        }.items():
            if neighbor not in dots:
                cap(adjacency, point, side)

    degree = {point: 0 for point in dots}
    for edge, gate_state in state.items():
        (x, y), (u, v) = edge
        if x == u:
            bottom, top = ((x, y), (u, v)) if y < v else ((u, v), (x, y))
            if gate_state == "open":
                join(adjacency, (top, "Sse"), (bottom, "Nnw"))
                join(adjacency, (top, "Ssw"), (bottom, "Nne"))
                degree[top] += 1
                degree[bottom] += 1
            else:
                cap(adjacency, bottom, "N")
                cap(adjacency, top, "S")
        else:
            left, right = ((x, y), (u, v)) if x < u else ((u, v), (x, y))
            if gate_state == "open":
                join(adjacency, (left, "Ene"), (right, "Wsw"))
                join(adjacency, (left, "Ese"), (right, "Wnw"))
                degree[left] += 1
                degree[right] += 1
            else:
                cap(adjacency, left, "E")
                cap(adjacency, right, "W")

    ports = {(point, port) for point in dots for port in PORTS}
    missing = ports - set(adjacency)
    bad = {port: peers for port, peers in adjacency.items() if len(peers) != 2}
    if missing or bad:
        raise AuditError(f"unpaired ports: {sorted(missing)}; non-2-regular: {bad}")

    components: list[set[tuple[POINT, str]]] = []
    unseen = set(ports)
    while unseen:
        component = {unseen.pop()}
        todo = list(component)
        while todo:
            current = todo.pop()
            for nxt in adjacency[current]:
                if nxt not in component:
                    component.add(nxt)
                    unseen.discard(nxt)
                    todo.append(nxt)
        components.append(component)
    components.sort(key=lambda component: (len(component), sorted(component)))
    return {
        "dots": len(dots), "host_gates": len(host),
        "open_gates": sum(value == "open" for value in state.values()),
        "implicit_closed": len(host) - len(declared),
        "components": len(components),
        "sizes": [len(component) for component in components],
        "degree": degree,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--require-one", action="store_true",
                        help="require exactly one closed port-graph component")
    parser.add_argument("--drop-fan", action="store_true",
                        help="require every pulli to have open degree one or three")
    args = parser.parse_args(argv)
    try:
        dots, gates = parse(args.source)
        report = audit(dots, gates)
        if args.require_one and report["components"] != 1:
            raise AuditError(f"expected one stroke, found {report['components']}")
        if args.drop_fan:
            bad = {p: d for p, d in report["degree"].items() if d not in (1, 3)}
            if bad:
                raise AuditError(f"not Drop--Fan; open degrees {bad}")
    except (OSError, AuditError) as error:
        print(f"kolam audit: {error}", file=sys.stderr)
        return 1
    print(f"{args.source}: {report['dots']} pulli, {report['host_gates']} induced gates "
          f"({report['open_gates']} open; {report['implicit_closed']} implicit closed)")
    print(f"  {report['components']} closed stroke(s): {report['sizes']}")
    print(f"  open degrees: {dict(sorted(report['degree'].items()))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
