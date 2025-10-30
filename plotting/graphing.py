from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence, Tuple

try:  
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError as exc:  # pragma: no cover
    plt = None
    _MATPLOTLIB_ERROR = exc
else:
    _MATPLOTLIB_ERROR = None


@dataclass(frozen=True)
class ThoughtNode:
    """Lightweight carrier for thought graph nodes."""

    id: str
    depth: int
    label: str
    branch_label: str
    probability: float
    potential_increment: float
    cumulative_potential: float
    is_final: bool = False
    regrets: bool = False


def _compute_layout(nodes: Sequence[ThoughtNode]) -> dict[str, Tuple[float, float]]:
    levels: dict[int, list[ThoughtNode]] = {}
    for node in nodes:
        levels.setdefault(node.depth, []).append(node)

    positions: dict[str, Tuple[float, float]] = {}
    for depth in sorted(levels.keys()):
        depth_nodes = levels[depth]
        count = len(depth_nodes)
        width = max(count - 1, 1)
        for index, node in enumerate(depth_nodes):
            x_pos = index - width / 2.0
            positions[node.id] = (x_pos, -float(depth))
    return positions


def render_thought_graph(
    nodes: Sequence[ThoughtNode],
    edges: Sequence[Tuple[str, str]],
    output_path: Path,
) -> Path:
    """
    Render the thought process as a PNG image.

    Parameters
    ----------
    nodes:
        Nodes to render, ordered by traversal sequence.
    edges:
        Directed edges represented as (parent_id, child_id) tuples.
    output_path:
        Destination path for the PNG file.
    """
    if _MATPLOTLIB_ERROR is not None: 
        raise RuntimeError("matplotlib is required to render thought graphs") from _MATPLOTLIB_ERROR
    if not nodes:
        raise ValueError("No nodes provided for thought graph rendering.")

    positions = _compute_layout(nodes)
    depth_levels = {node.depth for node in nodes}
    depth_count = len(depth_levels)
    max_width = max(len([n for n in nodes if n.depth == depth]) for depth in depth_levels) or 1

    fig_width = max(6.0, max_width * 3.0)
    fig_height = max(4.0, depth_count * 2.5)

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.set_axis_off()

    for parent_id, child_id in edges:
        parent_pos = positions.get(parent_id)
        child_pos = positions.get(child_id)
        if parent_pos is None or child_pos is None:
            continue
        ax.plot(
            (parent_pos[0], child_pos[0]),
            (parent_pos[1], child_pos[1]),
            color="#94a3b8",
            linewidth=1.6,
            zorder=1,
        )

    for node in nodes:
        x_pos, y_pos = positions[node.id]
        if node.regrets:
            face_color = "#f8d7da"
        elif node.is_final:
            face_color = "#d4edda"
        else:
            face_color = "#e0ecff"

        text_lines = [
            node.branch_label,
            node.label,
            f"Prob: {node.probability:.2f}",
            f"ΔPot: {node.potential_increment:+.2f}",
            f"Cumulative: {node.cumulative_potential:.2f}",
        ]
        text = "\n".join(filter(None, text_lines))

        ax.text(
            x_pos,
            y_pos,
            text,
            ha="center",
            va="center",
            fontsize=9,
            zorder=2,
            bbox=dict(boxstyle="round,pad=0.4", fc=face_color, ec="#475569", linewidth=0.8),
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return output_path
