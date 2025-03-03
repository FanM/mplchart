"""Triangle Pattern primitive"""

import warnings
import pandas as pd
from typing import List
from dataclasses import replace
from auto_chart_patterns.zigzag import Zigzag
from auto_chart_patterns.reversal_patterns import ReversalPatternProperties, ReversalPattern, find_reversal_patterns

from ..model import Primitive

def get_color(i) -> str:
    colors = ["darkred", "darkblue", "darkgreen", "darkorange"]
    return colors[i % len(colors)]

class Reversal(Primitive):
    """
    Reversal Pattern Primitive
    Used to plot reversal patterns

    Args:
        item (str) :  item to plot
        backcandles (int) :  number of periods to lookback
        forwardcandles (int) :  number of periods to lookforward
        pivot_limit (int) :  maximum number of pivots to consider
        scan_props (ReversalPatternProperties) :  scan properties
        show_pivots (bool) :  whether to show pivots
        axes (str) :  axes to plot on
        patterns (List[ReversalPattern]) :  patterns to plot
    """

    def __init__(
            self,
            item: str = None,
            *,
            backcandles: int = 5,
            forwardcandles: int = 5,
            pivot_limit: int = 55,
            scan_props: ReversalPatternProperties = None,
            show_pivots: bool = False,
            axes: str = None,
            patterns: List[ReversalPattern] = None
    ):
        self.item = item
        self.backcandles = backcandles
        self.forwardcandles = forwardcandles
        self.pivot_limit = pivot_limit
        self.show_pivots = show_pivots
        self.axes = axes
        self.patterns = patterns
        self.scan_props = ReversalPatternProperties()
        if scan_props is not None:
            self.scan_props = replace(self.scan_props, **scan_props.__dict__)

    def process(self, data):
        if self.item:
            data = getattr(data, self.item)
        return extract_chart_patterns(
            data,
            backcandles=self.backcandles,
            forwardcandles=self.forwardcandles,
            pivot_limit=self.pivot_limit,
            scan_props=self.scan_props
        )

    def plot_handler(self, data, chart, ax=None):
        if ax is None:
            ax = chart.get_axes()

        if not self.patterns:
            zigzag, patterns = self.process(data)

            px = [pivot.point.index for pivot in zigzag.zigzag_pivots]
            py = [pivot.point.price for pivot in zigzag.zigzag_pivots]
            if self.show_pivots:
                ax.scatter(px, py, color="purple", s=10 * 10, alpha=0.5, marker=".")
                for i, txt in enumerate(px):
                    ax.annotate(txt, (px[i], py[i]))
        else:
            patterns = self.patterns
            if self.show_pivots:
                warnings.warn("Cannot show pivots when direct plot is enabled!")

        kwargs = dict(
            linestyle="--",
            linewidth=1.5,
            alpha=0.5,
        )

        df = data.copy()
        # add row number as integer
        df['row_number'] = pd.RangeIndex(len(df))

        # For each pattern, plot line segments between its points
        for i, pattern in enumerate(patterns):
            # Use data.index to get the correct x positions
            line1_x = [df.loc[pattern.support_line.p1.time, 'row_number'],
                       df.loc[pattern.support_line.p2.time, 'row_number']]
            line1_y = [pattern.support_line.p1.price, pattern.support_line.p2.price]
            xp = [df.loc[pivot.point.time, 'row_number'] for pivot in pattern.pivots]
            yp = [pivot.point.price for pivot in pattern.pivots]

            color = get_color(i)
            ax.scatter(xp, yp, color=color, s=10 * 10, alpha=0.5, marker="o")
            if self.patterns:
                for i, txt in enumerate(xp):
                    ax.annotate(xp[i], (xp[i], yp[i]))

            ax.plot(line1_x, line1_y, color=color, **kwargs)
            sandle_point = pattern.pivots[2]
            text_x = df.loc[sandle_point.point.time, 'row_number']
            text_y = sandle_point.point.price
            if sandle_point.direction > 0:
                text_y *= 1.01
                xytext = (10, 40)  # Offset upward
                va = 'bottom'  # Align text to bottom of bbox
            else:
                text_y *= 0.99
                xytext = (10, -40)  # Offset downward
                va = 'top'  # Align text to top of bbox
            # Define box style for price action
            box_style = dict(
                boxstyle='round,pad=0.5',
                facecolor='white',
                alpha=0.7,
                edgecolor=color,
                linewidth=1
            )
            text = pattern.pattern_name
            if pattern.extra_props is not None and 'price_action' in pattern.extra_props:
                text += f"\naction: {pattern.extra_props['price_action']}" \
                        f"\nretrace: {pattern.extra_props['max_retrace_short_period']*100:.2f}%" \
                        f"\nmid profit: {pattern.extra_props['max_profit_mid_period']*100:.2f}%" \
                        f"\nlong profit: {pattern.extra_props['max_profit_long_period']*100:.2f}%"
            # Add callout box annotation
            ax.annotate(
                text,
                xy=(text_x, text_y),
                xytext=xytext,  # 10 points offset
                textcoords='offset points',
                bbox=box_style,
                color=color,
                ha='left',  # horizontal alignment
                va=va,  # vertical alignment
                arrowprops=dict(
                    arrowstyle='->',
                    connectionstyle='arc3,rad=0',
                    color=color
                )
            )


def extract_chart_patterns(prices, backcandles, forwardcandles, pivot_limit, scan_props):
    """
    extracts chart patterns.

    Args:
        backcandles (int) : refers to minimum number bars required before
        forwardcandles (int) : refers to minimum number bars required after
        pivot_limit (int) : maximum distance between two pivots
        scan_props (ReversalPatternProperties) : scan properties

    Return:
        A series of prices defined only at local peaks and equal to nan otherwize
    """

    zigzag = Zigzag(backcandles=backcandles, forwardcandles=forwardcandles, pivot_limit=pivot_limit, offset=0)
    zigzag.calculate(prices)

    # Initialize pattern storage
    patterns: List[ReversalPattern] = []

    # Find patterns
    for i in range(scan_props.offset, len(zigzag.zigzag_pivots)):
        find_reversal_patterns(zigzag, i, scan_props, patterns)

    return zigzag, patterns
