from dataclasses import dataclass, field

@dataclass
class GlobalStyle:
    """
    Config that spans style-elements for all figures generated.
    """

    label_size:     float = 8
    tick_size:      float = 7
    title_size:     float = 9
    legend_size:    float = 8

    suptitle_size:  float = 10
    suptitle_fontweight: str = 'bold'

    tick_width:     float = 0.8
    spine_width:    float = 0.8

    tag_args: dict = field(
        default_factory=lambda: {
            "x": -0.06,
            "y": 1.05,
            "fontsize": 16,
            "fontweight": "bold",
            "va": "bottom",
            "ha": "right",
        }
    )