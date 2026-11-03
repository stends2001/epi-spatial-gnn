from dataclasses import dataclass, field

@dataclass
class FigStyle:
    """
    Config that spans style-elements for a single figure.
    """
    figsize:        tuple = (3.5, 3.0)
    dpi:            int = 300
    suptitle:       str | None = None
    num_subfigures: int = 1

    suptitle_args: dict = field(
        default_factory=lambda: {
            "ha": "left",
            "x": 0.02,
        }
    )