from __future__ import annotations
from matplotlib.figure import Figure 
from pathlib import Path
from typing import TYPE_CHECKING 

if TYPE_CHECKING:
    from .style import FigStyle

def save_figure(fig: Figure, dir: Path, filename: str, figstyle: FigStyle):
    """based on dir and name save .eps, .svg and .pdf"""

    fig.savefig(dir / f"{filename}.eps", bbox_inches="tight", dpi = figstyle.dpi)
    fig.savefig(dir / f"{filename}.svg", bbox_inches="tight")
    fig.savefig(dir / f"{filename}.pdf", bbox_inches="tight")