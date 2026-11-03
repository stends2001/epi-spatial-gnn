from dataclasses import dataclass, field

@dataclass
class AxStyle:
    """ 
    Config that spans style-elements for a single axes.
    """
    # labels / titles
    title:          str | None = None
    label_x:        str | None = None
    label_y:        str | None = None
    tag:            str | None = None

    # x-axis
    ticks_x:        bool = True
    ticks_x_labels: bool = True
    ticks_x_args:   dict = field(default_factory=dict)
    lims_x:         list[float] | None = None

    # y-axis
    ticks_y:        bool = True
    ticks_y_labels: bool = True
    ticks_y_args:   dict = field(default_factory=dict)
    lims_y:         list[float] | None = None

    # legend
    legend:         bool = False
    legend_args:    dict = field(default_factory=dict)
    legend_labels:  dict[str, str] | None = None

    # grid
    show_grid:      bool = False
    spines:         bool | dict[str, bool] = True
    spine_align_tick: bool = False

    # per-axes overrides of the global defaults (None -> use global)
    tick_width:     float | None = None
    spine_width:    float | None = None