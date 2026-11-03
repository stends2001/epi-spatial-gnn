from __future__ import annotations
from matplotlib.figure import Figure 
from matplotlib.axes import Axes

from . import FigStyle, AxStyle, GlobalStyle

def apply_axstyle(ax : Axes,
                  axstyle: AxStyle,
                  globalstyle : GlobalStyle) -> None:

    # titles / labels
    ax.set_xlabel(axstyle.label_x, fontsize=globalstyle.label_size)
    ax.set_ylabel(axstyle.label_y, fontsize=globalstyle.label_size)
    ax.set_title(axstyle.title,    fontsize=globalstyle.title_size, loc="left")

    if axstyle.tag:
        ax.text(s=axstyle.tag, transform=ax.transAxes, **globalstyle.tag_args)

    if axstyle.lims_x:
        ax.set_xlim(axstyle.lims_x[0], axstyle.lims_x[1])

    if axstyle.lims_y:
        ax.set_ylim(axstyle.lims_y[0], axstyle.lims_y[1])            

    # ticks
    if not axstyle.ticks_x:
        ax.set_xticks([])
    else:
        if not axstyle.ticks_x_labels:
            ax.tick_params(axis="x", labelbottom=False)
        ax.tick_params(axis="x", labelsize=globalstyle.tick_size, **axstyle.ticks_x_args)

    if not axstyle.ticks_y:
        ax.set_yticks([])
    else:
        if not axstyle.ticks_y_labels:
            ax.tick_params(axis="y", labelleft=False)  # was labelbottom (bug)
        ax.tick_params(axis="y", labelsize=globalstyle.tick_size, **axstyle.ticks_y_args)

    # tick + spine width (global default, overridable per-axes)
    tick_width = axstyle.tick_width if axstyle.tick_width is not None else globalstyle.tick_width
    spine_width = axstyle.spine_width if axstyle.spine_width is not None else globalstyle.spine_width
    ax.tick_params(width=tick_width)
    for spine in ax.spines.values():
        spine.set_linewidth(spine_width)

    # spines (the box around the plot)
    if isinstance(axstyle.spines, bool):
        if not axstyle.spines:
            for spine in ax.spines.values():
                spine.set_visible(False)
    else:
        for side, visible in axstyle.spines.items():
            if side in ax.spines:
                ax.spines[side].set_visible(visible)

    # grid
    ax.grid(axstyle.show_grid)

    # legend
    existing_legend = ax.get_legend()

    if not axstyle.legend:
        if existing_legend is not None:
            existing_legend.remove()
    
    else:
        handles, labels = ax.get_legend_handles_labels()

        if axstyle.legend_labels:
            labels = [axstyle.legend_labels.get(l, l) for l in labels]

        legend_kwargs = {"fontsize": globalstyle.legend_size, **axstyle.legend_args}

        if handles:
            # legend alread exists by seaborn, adjusted here.
            ax.legend(handles, labels, **legend_kwargs)

        elif existing_legend is not None:
            # Legend was built manually from handles with no `label`.
            for text in existing_legend.get_texts():
                if axstyle.legend_labels:
                    text.set_text(axstyle.legend_labels.get(text.get_text(), text.get_text()))
                text.set_fontsize(legend_kwargs["fontsize"])

    if axstyle.spines is not False:
        if axstyle.spine_align_tick:
            x0 = ax.get_xticks()[0]
            ax.spines["left"].set_position(("data", x0))            


def apply_figstyle(fig : Figure,
                   figstyle : FigStyle,
                   globalstyle: GlobalStyle) -> None:
    """ 
    Apply the style onto a fig, using FigStyle and GlobalStyle.
    """
    
    if figstyle.figsize:
        fig.set_size_inches(*figstyle.figsize)
    if figstyle.dpi:
        fig.set_dpi(figstyle.dpi)
    if figstyle.suptitle:
        fig.suptitle(figstyle.suptitle, 
                     fontsize = globalstyle.suptitle_size, 
                     fontweight = globalstyle.suptitle_fontweight, 
                     **figstyle.suptitle_args)

def apply_styles(
    fig:        Figure,
    ax:         Axes | list[Axes],
    figstyle:    FigStyle,
    axstyle:     AxStyle | list[AxStyle],
    globalstyle: GlobalStyle,
):
    """Apply titles, labels, tags, ticks, legends, and global styling.

    NOTE: this only sets cosmetic properties. It does not touch axes
    *positions* -- do that afterwards with align_axes_to_reference(), once
    all labels/legends are in and the layout engine has had a chance to
    compute a first pass.
    """

    # make iterable lists of not yet lists.
    axes      = [ax]      if isinstance(ax, Axes)         else list(ax)
    axstyles  = [axstyle] if isinstance(axstyle, AxStyle) else list(axstyle)

    if len(axes) != len(axstyles):
        raise ValueError("len of ax and ax_cfg need to be the same!")

    # --- figure-level style -------------------------------------------------
    apply_figstyle(fig, figstyle, globalstyle)

    # --- per-axes style ------------------------------------------------------
    for ax, axstyle in zip(axes, axstyles):
        apply_axstyle(ax, axstyle, globalstyle)
       
    return fig, axes
 
