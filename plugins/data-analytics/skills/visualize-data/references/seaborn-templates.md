# Seaborn Templates

Use this when implementing static charts in Python. Seaborn owns marks;
Matplotlib owns layout, axes, annotations, and export.

## How To Use This File

1. Choose the family from `../SKILL.md` `Chart Selection`.
2. Pick the lightest variant below that answers the question.
3. Apply shared style before chart-specific tweaks.
4. Export SVG and PNG.
5. Inspect in the final notebook, report, dashboard, or slide.

## Canonical Family Map

- `Tables & Scorecards`: HTML layer, not Seaborn.
- `Trend`: Trend Line, Highlighted Multi-Series Trend, Stacked Area,
  Overlapping Area, Small Multiples.
- `Comparison & Ranking`: Grouped Column Bars, Ranked Horizontal Bars,
  Diverging Horizontal Bars, Dot Reference Comparison, Concentration / Pareto.
- `Composition`: Stacked Horizontal Bars, Pie Chart.
- `Distribution`: Histogram / KDE, Grouped Distribution Comparison.
- `Relationship`: Scatter, Bubble Chart, Scatter / Density.
- `Uncertainty & Benchmark`: Ordered Line & Dot, Faceted Dot & Interval,
  Experiment Lift With Confidence Intervals.
- `Matrix & Cohort`: Heatmap.
- `Decomposition & Progression`: Funnel Stage Bars, Waterfall Bridge.

## Shared Style Guidance

Use this section for every chart. The recipes name form; this section owns visual decisions.

### Build Sequence

Use this order:

1. `Format`: family and delivery surface.
2. `Structure`: title, subtitle, axes, labels, annotations, removals.
3. `Colors`: smallest readable set of palette roots.

If the chart feels busy, revisit `Format` or `Structure`; do not add colors,
heavier strokes, or extra decoration.

### Palette

Choose a palette policy before plotting. Use only approved roots, explicit maps, neutrals, and shades. Never use default categorical colors for shipped charts.

Policy classes:

- `Single-root preferred`: one non-neutral root plus shades and neutrals. Use for simple trends, ranks, distributions, relationships,
  heatmaps, intervals, experiment lift, and comparable small multiples.
- `Hard two-root cap`: at most two non-neutral roots plus neutrals. Use for binary, signed, focal-vs-context, benchmark, Pareto, overlapping area,
  highlighted trend, ordered line-dot, and waterfall charts.
- `Relaxed multi-category`: up to five approved roots when category identity matters. Use for pie, stacked bars/area, grouped bars, and stage bars.
  With more than five categories, group to top-N plus Other or change form.

Shades and neutral comparator fills do not count as roots. Separate series with tone, open fill, marker fill, line style, direct labels, ordering, or faceting.
Do not ship visually identical fills for adjacent or overlapping marks.
Use each selected root's `base` tone, the middle swatch of the five-color row,
as the default non-neutral mark color for shipped charts. Use `dark` for keylines, outlines, labels, or reference strokes; use `light`, `xlight`, or `open` for supporting fills.

| Family | XLight | Light | Base | Mid | Dark |
|---|---|---|---|---|---|
| Blue | `#EAF1FE` | `#CEDFFE` | `#A3BEFA` | `#5477C4` | `#2E4780` |
| Gold | `#FFF4C2` | `#FFEA8F` | `#FFE15B` | `#B8A037` | `#736422` |
| Orange | `#FFEDDE` | `#FFBDA1` | `#F0986E` | `#CC6F47` | `#804126` |
| Olive | `#D8ECBD` | `#BEEB96` | `#A3D576` | `#71B436` | `#386411` |
| Pink | `#FCDAD6` | `#F5BACC` | `#F390CA` | `#BD569B` | `#8A3A6F` |

- Use `Blue` for general product or KPI charts.
- Use `Gold` for model/eval examples with no subject color.
- Use `Orange`, `Olive`, or `Pink` when the subject or report points there.
- Calls with `hue`, grouped marks, multiple lines, `stackplot`, `pie`, grouped distributions, or colormaps must pass explicit palette/color maps.
- Prefer `base` for primary fills, lines, dots, and legend swatches. Treat `mid` as an exception for cases that need extra contrast.
- For positive/negative states, use dark vs open/light fills, signed labels,
  and zero-line context; use green/red only for documented domain semantics.

### Semantic Tokens

| Token | Value | Use |
|---|---:|---|
| `surface` | `#FCFCFD` | page or figure background |
| `panel` | `#FFFFFF` | chart panel and axes background |
| `ink` | `#1F2430` | titles, primary labels, reference lines |
| `muted` | `#6F768A` | subtitles, notes, secondary ticks |
| `grid` | `#E6E8F0` | quiet grid lines and dotted plot areas |
| `axis` | `#D7DBE7` | visible left/bottom axis bars |

Use dark-neutral calibration, benchmark, reference, and ideal lines.

Neutral comparator fills:

| Token | Value | Use |
|---|---:|---|
| `neutral_xlight` | `#F4F5F7` | open comparator fills |
| `neutral_light` | `#E2E5EA` | secondary comparator fills |
| `neutral_base` | `#C5CAD3` | dense comparator fills or disabled states |
| `neutral_mid` | `#7A828F` | comparator outlines and labels |
| `neutral_dark` | `#464C55` | high-contrast comparator keylines |

### Typography And Naming

- Use a sans stack for titles, subtitles, axis titles, legends, and notes.
- Use a mono stack for numeric tick labels, direct value labels, benchmark labels, and compact callouts.
- Every shipped chart must have a visible title and subtitle.
- Use sentence case for short takeaway titles.
- Put metric scope in subtitles: unit, denominator, date range, cohort, filters,
  confidence level, or benchmark.
- Use title case for short axis labels.
- Use sentence case for subtitles, notes, and analytical questions.
- Preserve model names exactly: `GPT-4o`, `o3-mini`, `o1`, `o1-mini`, `Sora`.
- Do not shrink type to fix layout. Widen, wrap, facet, or split.

### Labels, Legends, And Callouts

- Align title, subtitle, and top legend to the same left edge.
- Prefer direct labels when they reduce lookup.
- Use a compact top legend when direct labels collide.
- Keep value labels near marks with a clear gutter.
- Put pie labels outside. If labels collide, use a right-side list.
- Use callouts sparingly; anchor them to data points.

### Axes, Grids, And Plot Area

- Use one stroke width per chart; do not encode emphasis with thickness.
- Web/static chart default: `1px` visual stroke.
- Deck export default: `1.5px` visual stroke.
- Keep keylines on filled marks and shapes.
- Do not use gradients inside chart marks.
- Use white or near-white backgrounds unless the whole artifact is dark.
- For line, area, and line-dot charts, keep left and bottom axis bars visible.
- Use dotted plot areas only for line, area, or line-dot charts.
- For bar charts, keep grid lines quiet and only on the value axis.
- For datetime x-axes, use `format_date_axis(ax)` after plotting so tick labels stay concise and do not overlap.

### Mark Styling

- Bars: filled marks with keylines; sort unless order matters; use horizontal bars for long labels.
- Use the root `base` tone for primary fills and line marks. Use `dark` as the keyline or high-contrast reference stroke, not as the default fill.
- Diverging bars: reserve separate zones for category labels, negative value labels, zero line, positive bars, and positive value labels.
- Lines: use declared roots, line style, tone, or labels; remove extra guides.
- Line-dot and interval charts: make dots and whiskers primary; keep connector lines quiet; use dark-neutral benchmark lines.
- Bubbles: area-encode size only when the third metric materially changes the interpretation; include a compact size legend.
- Areas: keep boundary lines above fills, but do not outline the sides or bottom of filled area polygons.
- Pie charts: sort slices, use outside labels, avoid tiny inside labels, and keep labels readable.
- Heatmaps: use a declared sequential scale; annotate only readable cells.

### Layout And Export

- Reserve header space for title and subtitle plus label gutters before plotting.
- Use `add_chart_header(fig, ax, title, subtitle)` for every shipped static chart. Do not mix `ax.set_title(...)` with separate subtitle text.
- Use an 8-column footprint for most standalone HTML charts; widen to 10 or 12 for long labels, dense series, or annotations. Treat 6 columns as the minimum.
- Stack side-by-side charts on mobile; do not invent off-grid widths.
- For shipped branded web outputs, inspect light and dark variants.
- Never compress a chart into a narrow card if labels clip.
- Inspect the exported PNG and final embedded context, not only the raw SVG.

## Minimal Implementation Skeleton

Adapt this skeleton.

```python
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import numpy as np
import seaborn as sns
import textwrap
from matplotlib.patches import Patch

FONT_FAMILY = ["Aptos", "Inter", "Segoe UI", "DejaVu Sans", "Arial", "sans-serif"]
MONO_FONT_FAMILY = ["SF Mono", "Menlo", "Consolas", "DejaVu Sans Mono", "monospace"]

TOKENS = {
    "surface": "#FCFCFD",
    "panel": "#FFFFFF",
    "ink": "#1F2430",
    "muted": "#6F768A",
    "grid": "#E6E8F0",
    "axis": "#D7DBE7",
}

NEUTRAL_MARKS = {
    "open": TOKENS["panel"],
    "xlight": "#F4F5F7",
    "light": "#E2E5EA",
    "base": "#C5CAD3",
    "mid": "#7A828F",
    "dark": "#464C55",
}

COLOR_FAMILIES = {
    "blue": {
        "open": TOKENS["panel"],
        "xlight": "#EAF1FE",
        "light": "#CEDFFE",
        "base": "#A3BEFA",
        "mid": "#5477C4",
        "dark": "#2E4780",
    },
    "gold": {
        "open": TOKENS["panel"],
        "xlight": "#FFF4C2",
        "light": "#FFEA8F",
        "base": "#FFE15B",
        "mid": "#B8A037",
        "dark": "#736422",
    },
    "orange": {
        "open": TOKENS["panel"],
        "xlight": "#FFEDDE",
        "light": "#FFBDA1",
        "base": "#F0986E",
        "mid": "#CC6F47",
        "dark": "#804126",
    },
    "olive": {
        "open": TOKENS["panel"],
        "xlight": "#D8ECBD",
        "light": "#BEEB96",
        "base": "#A3D576",
        "mid": "#71B436",
        "dark": "#386411",
    },
    "pink": {
        "open": TOKENS["panel"],
        "xlight": "#FCDAD6",
        "light": "#F5BACC",
        "base": "#F390CA",
        "mid": "#BD569B",
        "dark": "#8A3A6F",
    },
}

def palette_from_family(labels, family, tones=("base", "light", "xlight", "open", "base")):
    """Return an explicit palette map from one declared palette root."""
    labels = list(labels)
    tone_list = list(tones)
    return {
        label: family[tone_list[i % len(tone_list)]]
        for i, label in enumerate(labels)
    }


def add_chart_header(fig, ax, title, subtitle, *, title_width=78, subtitle_width=112) -> None:
    """Add a wrapped figure-level title/subtitle and reserve plot space."""
    title = str(title).strip()
    subtitle = str(subtitle).strip()
    if not title or not subtitle:
        raise ValueError("Every shipped chart needs a non-empty title and subtitle.")

    title = textwrap.fill(title, width=title_width, break_long_words=False)
    subtitle = textwrap.fill(subtitle, width=subtitle_width, break_long_words=False)
    title_lines = title.count("\n") + 1
    subtitle_lines = subtitle.count("\n") + 1

    ax.set_title("")
    fig.subplots_adjust(top=max(0.62, 0.86 - 0.045 * (title_lines - 1) - 0.032 * (subtitle_lines - 1)))

    left = ax.get_position().x0
    fig.text(left, 0.985, title, ha="left", va="top", fontsize=13, fontweight="semibold", color=TOKENS["ink"], linespacing=1.08)
    fig.text(left, 0.93 - 0.045 * (title_lines - 1), subtitle, ha="left", va="top", fontsize=9, color=TOKENS["muted"], linespacing=1.18)
    sns.despine(ax=ax)


def format_date_axis(ax, *, max_ticks=6) -> None:
    """Keep time axes readable by limiting ticks and using concise labels."""
    locator = mdates.AutoDateLocator(minticks=3, maxticks=max_ticks)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
    ax.tick_params(axis="x", labelrotation=0)


def use_chart_theme() -> None:
    sns.set_theme(
        style="whitegrid",
        rc={
            "figure.facecolor": TOKENS["surface"],
            "figure.edgecolor": "none",
            "savefig.facecolor": "none",
            "savefig.edgecolor": "none",
            "axes.facecolor": TOKENS["panel"],
            "axes.edgecolor": TOKENS["axis"],
            "axes.labelcolor": TOKENS["ink"],
            "axes.grid": True,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "grid.color": TOKENS["grid"],
            "grid.linewidth": 0.8,
            "font.family": "sans-serif",
            "font.sans-serif": FONT_FAMILY,
            "font.monospace": MONO_FONT_FAMILY,
            "patch.linewidth": 1.0,
        },
    )
```

## Visualization Templates

Each template inherits shared style. Snippets assume `fig`, `ax`, `family`,
`title`, `subtitle`, and labels exist; adapt names and sizing. Finish every shipped chart with `add_chart_header(fig, ax, title, subtitle)`. For FacetGrid or multi-axis charts, pass the figure and first primary axis.

### Trend Line

- Use: continuous metric over ordered x.
- Data: sorted x, y.
- Snippet:
```python
plot_df = df.sort_values(x_col)
sns.lineplot(data=plot_df, x=x_col, y=y_col, ax=ax, color=family["base"], linewidth=1.0)
if np.issubdtype(plot_df[x_col].dtype, np.datetime64):
    format_date_axis(ax)
add_chart_header(fig, ax, title, subtitle)
```

### Highlighted Multi-Series Trend

- Use: focal series with peer context.
- Data: x, y, series, focal flag.
- Snippet:
```python
peer_families = [NEUTRAL_MARKS, COLOR_FAMILIES["gold"], NEUTRAL_MARKS]
for i, (series, part) in enumerate(df.loc[~df[focal_col]].groupby(series_col)):
    peer_family = peer_families[i % len(peer_families)]
    sns.lineplot(data=part, x=x_col, y=y_col, ax=ax, color=peer_family["base"], linewidth=1.0, linestyle=["--", ":", "-."][i % 3], label=series)
focal_label = str(df.loc[df[focal_col], series_col].drop_duplicates().iloc[0])
sns.lineplot(data=df.loc[df[focal_col]], x=x_col, y=y_col, ax=ax, color=family["base"], linewidth=1.0, label=focal_label)
if np.issubdtype(df[x_col].dtype, np.datetime64):
    format_date_axis(ax)
ax.legend(loc="lower left", bbox_to_anchor=(0, 1.02), frameon=False, ncol=min(df[series_col].nunique(), 4), borderaxespad=0)
add_chart_header(fig, ax, title, subtitle)
```

### Stacked Area

- Use: additive composition over time.
- Data: x plus additive components, or long data pivoted wide.
- Snippet:
```python
wide = df.pivot(index=x_col, columns=segment_col, values=value_col).fillna(0).sort_index()
family_cycle = [COLOR_FAMILIES[name] for name in ["blue", "gold", "olive", "pink", "orange"]]
area_families = [family_cycle[i % len(family_cycle)] for i in range(wide.shape[1])]
fills = [area_families[i]["base"] for i in range(wide.shape[1])]
areas = ax.stackplot(wide.index, wide.T.to_numpy(), labels=list(wide.columns), colors=fills, linewidth=0)
lower = np.zeros(len(wide), dtype=float)
for area, values, area_family in zip(areas, wide.T.to_numpy(), area_families):
    area.set_edgecolor("none")
    area.set_linewidth(0)
    upper = lower + values
    lower = upper
cumulative = wide.T.to_numpy().cumsum(axis=0)
for boundary, area_family in zip(cumulative, area_families):
    ax.plot(wide.index, boundary, color=area_family["dark"], linewidth=1.0, zorder=3.2)
ax.legend(loc="lower left", bbox_to_anchor=(0, 1.02), frameon=False, ncol=min(wide.shape[1], 4), borderaxespad=0)
add_chart_header(fig, ax, title, subtitle)
```

### Overlapping Area

- Use: overlapping continuous envelopes.
- Data: x plus 2-3 y series.
- Snippet:
```python
if not 2 <= len(y_cols) <= 3:
    raise ValueError("Overlapping area expects two or three y series.")
area_styles = [
    # Draw rear envelopes first and the low/base envelope last.
    (str(y_cols[1]), y_cols[1], COLOR_FAMILIES["olive"]["base"], COLOR_FAMILIES["olive"]["dark"], COLOR_FAMILIES["olive"]["base"], "-", 0.36, 1.1),
]
if len(y_cols) == 3:
    area_styles.append(
        (str(y_cols[2]), y_cols[2], COLOR_FAMILIES["blue"]["base"], COLOR_FAMILIES["blue"]["dark"], COLOR_FAMILIES["blue"]["base"], "-", 0.66, 1.8)
    )
area_styles.append(
    (str(y_cols[0]), y_cols[0], COLOR_FAMILIES["olive"]["base"], COLOR_FAMILIES["olive"]["dark"], COLOR_FAMILIES["olive"]["base"], "-", 0.72, 3.0)
)
for name, y, fill_color, edge_color, line_color, line_style, fill_alpha, zorder in area_styles:
    area = ax.fill_between(
        df[x_col], 0, df[y],
        color=fill_color, alpha=fill_alpha,
        edgecolor="none",
        linewidth=0,
        zorder=zorder,
    )
for name, y, _, _, line_color, line_style, _, _ in area_styles:
    ax.plot(df[x_col], df[y], color=line_color, linestyle=line_style, linewidth=1.05, label=name, zorder=5.2)
ax.legend(loc="lower left", bbox_to_anchor=(0, 1.02), frameon=False, ncol=min(len(area_styles), 4), borderaxespad=0)
add_chart_header(fig, ax, title, subtitle)
```

### Small Multiples

- Use: many trend lines.
- Data: x, y, facet.
- Snippet:
```python
g = sns.FacetGrid(df, col=facet_col, col_wrap=3, sharex=True, sharey=True)
facet_order = list(df[facet_col].drop_duplicates())
facet_palette = {facet: COLOR_FAMILIES["blue"]["base"] for facet in facet_order}
g.map_dataframe(sns.lineplot, x=x_col, y=y_col, hue=facet_col, palette=facet_palette, legend=False, linewidth=1.0)
g.set_titles("{col_name}", size=8.5)
add_chart_header(g.figure, g.axes.flat[0], title, subtitle)
```

### Grouped Column Bars

- Use: side-by-side category comparison.
- Data: category, series, value; few categories.
- Snippet:
```python
series_order = list(df[series_col].drop_duplicates())
category_order = list(df[category_col].drop_duplicates())
x = np.arange(len(category_order))
width = min(0.24, 0.72 / max(len(series_order), 1))
series_families = [COLOR_FAMILIES[name] for name in ["orange", "blue", "olive", "gold", "pink"]]
for i, series in enumerate(series_order):
    series_family = series_families[i % len(series_families)]
    values = df.loc[df[series_col] == series].set_index(category_col).loc[category_order, value_col].to_numpy()
    offset = (i - (len(series_order) - 1) / 2) * width
    bars = ax.bar(
        x + offset,
        values,
        width=width,
        label=series,
        color=series_family["base"],
        edgecolor=series_family["dark"],
        linewidth=1.0,
    )
ax.set_xticks(x, category_order)
ax.legend(loc="lower left", bbox_to_anchor=(0, 1.02), frameon=False, ncol=min(len(series_order), 4), borderaxespad=0)
add_chart_header(fig, ax, title, subtitle)
```

### Ranked Horizontal Bars

- Use: rank, top-N, long labels.
- Data: category, value; sort unless order matters.
- Snippet:
```python
plot_df = df.sort_values(value_col, ascending=True)
bar_family = COLOR_FAMILIES["orange"]
palette = palette_from_family(plot_df[category_col], bar_family, tones=("base", "light", "xlight", "open", "base"))
edge_colors = {category: bar_family["dark"] for category in plot_df[category_col]}
sns.barplot(data=plot_df, x=value_col, y=category_col, hue=category_col, palette=palette, legend=False, dodge=False, ax=ax, edgecolor=TOKENS["ink"], linewidth=1.0)
for patch, category in zip(ax.patches, plot_df[category_col]):
    patch.set_edgecolor(edge_colors[category])
add_chart_header(fig, ax, title, subtitle)
```

### Diverging Horizontal Bars

- Use: signed deltas or drivers around zero.
- Data: category, signed value.
- Snippet:
```python
plot_df = df.sort_values(value_col)
positive_family = COLOR_FAMILIES["olive"]
negative_family = COLOR_FAMILIES["orange"]
colors = np.where(plot_df[value_col] >= 0, positive_family["base"], negative_family["base"])
edge_colors = np.where(plot_df[value_col] >= 0, positive_family["dark"], negative_family["dark"])
bars = ax.barh(plot_df[category_col], plot_df[value_col], color=colors, edgecolor=edge_colors, linewidth=1.0)
neg_min = plot_df.loc[plot_df[value_col] < 0, value_col].min()
pos_max = plot_df.loc[plot_df[value_col] > 0, value_col].max()
neg_label_x = neg_min * 0.74
ax.set_xlim(neg_min * 1.36, pos_max * 1.12)
for bar, value in zip(bars, plot_df[value_col]):
    bar.set_edgecolor(positive_family["dark"] if value >= 0 else negative_family["dark"])
    label_x = value + 0.25 if value >= 0 else neg_label_x
    ax.text(label_x, bar.get_y() + bar.get_height() / 2, f"{value:+.1f}", ha="left", va="center", fontsize=8, color=TOKENS["ink"])
ax.axvline(0, color=TOKENS["ink"], linewidth=1.0)
ax.legend(
    handles=[
        Patch(facecolor=positive_family["base"], edgecolor=positive_family["dark"], label="Positive"),
        Patch(facecolor=negative_family["base"], edgecolor=negative_family["dark"], label="Negative"),
    ],
    loc="lower left",
    bbox_to_anchor=(0, 1.02),
    frameon=False,
    ncol=2,
    borderaxespad=0,
)
add_chart_header(fig, ax, title, subtitle)
```

### Dot Reference Comparison

- Use: compact target, before/after, or benchmark comparison.
- Data: category, value, optional reference.
- Snippet:
```python
value_family = COLOR_FAMILIES["orange"]
ax.hlines(df[category_col], df[reference_col], df[value_col], color=NEUTRAL_MARKS["base"], linewidth=1.0, label="Reference gap")
ax.scatter(df[value_col], df[category_col], facecolors=value_family["base"], edgecolors=value_family["dark"], linewidths=1.0, label="Actual")
ax.legend(loc="lower left", bbox_to_anchor=(0, 1.02), frameon=False, ncol=2, borderaxespad=0)
add_chart_header(fig, ax, title, subtitle)
```

### Concentration / Pareto

- Use: concentration of volume or impact.
- Data: entity, value; derive cumulative share.
- Snippet:
```python
plot_df = df.sort_values(value_col, ascending=False).head(top_n).assign(cum_share=lambda d: d[value_col].cumsum() / d[value_col].sum())
bar_family = COLOR_FAMILIES["orange"]
line_family = COLOR_FAMILIES["blue"]
sns.barplot(data=plot_df, x=category_col, y=value_col, ax=ax, color=bar_family["base"], edgecolor=bar_family["dark"], linewidth=1.0)
ax2 = ax.twinx()
ax2.grid(False)
ax2.plot(plot_df[category_col], plot_df["cum_share"], color=line_family["base"], linewidth=1.0, marker="o", label="Cumulative share")
ax2.set_ylim(0, 1.05)
ax2.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
ax2.tick_params(axis="y", colors=TOKENS["muted"], labelsize=8, length=0)
ax2.spines["right"].set_visible(False)
ax.legend(
    handles=[
        Patch(facecolor=bar_family["base"], edgecolor=bar_family["dark"], label=str(value_col).replace("_", " ").title()),
        ax2.lines[0],
    ],
    loc="lower left",
    bbox_to_anchor=(0, 1.02),
    frameon=False,
    ncol=2,
    borderaxespad=0,
)
add_chart_header(fig, ax, title, subtitle)
```

### Stacked Horizontal Bars

- Use: share-of-total, survey, or Likert buckets.
- Data: group, ordered segment, value or percent.
- Snippet:
```python
wide = df.pivot_table(index=group_col, columns=segment_col, values=value_col, fill_value=0).reindex(index=group_order, columns=segment_order)
left = np.zeros(len(wide))
segment_families = [COLOR_FAMILIES[name] for name in ["blue", "gold", "olive", "pink", "orange"]]
for i, segment in enumerate(segment_order):
    segment_family = segment_families[i % len(segment_families)]
    bars = ax.barh(wide.index, wide[segment], left=left, label=segment, color=segment_family["base"], edgecolor=segment_family["dark"], linewidth=1.0)
    left += wide[segment].to_numpy()
ax.xaxis.set_major_formatter(mticker.PercentFormatter(100))
ax.legend(loc="lower left", bbox_to_anchor=(0, 1.04), frameon=False, ncol=min(len(segment_order), 4), borderaxespad=0)
add_chart_header(fig, ax, title, subtitle)
```

### Pie Chart

- Use: rough part-to-whole with few slices.
- Data: category, value.
- Snippet:
```python
plot_df = df.sort_values(value_col, ascending=False)
slice_families = [COLOR_FAMILIES[name] for name in ["olive", "gold", "blue", "pink", "orange"]]
colors = [slice_families[i % len(slice_families)]["base"] for i in range(len(plot_df))]
wedges, _ = ax.pie(plot_df[value_col], startangle=90, counterclock=False, colors=colors, wedgeprops={"edgecolor": TOKENS["ink"], "linewidth": 1.0})
for i, (wedge, label, value) in enumerate(zip(wedges, plot_df[category_col], plot_df[value_col])):
    slice_family = slice_families[i % len(slice_families)]
    wedge.set_edgecolor(slice_family["dark"])
    angle = np.deg2rad((wedge.theta1 + wedge.theta2) / 2)
    ax.text(1.08 * np.cos(angle), 1.08 * np.sin(angle), f"{label}: {value:,.0f}", ha="left" if np.cos(angle) > 0 else "right", va="center")
add_chart_header(fig, ax, title, subtitle)
```

### Histogram / KDE

- Use: spread, skew, tail, or threshold.
- Data: one numeric value.
- Snippet:
```python
sns.histplot(data=df, x=value_col, bins=bins, ax=ax, color=family["base"], edgecolor=family["dark"], linewidth=1.0)
ax.axvline(df[value_col].median(), color=TOKENS["ink"], linestyle=":", linewidth=1.0)
add_chart_header(fig, ax, title, subtitle)
```

### Grouped Distribution Comparison

- Use: spread, skew, or outliers across cohorts.
- Data: group, numeric value.
- Snippet:
```python
group_order = list(df[group_col].drop_duplicates())
group_family = COLOR_FAMILIES["pink"]
box_tones = ["base", "light", "xlight"]
point_tones = ["base", "base", "base"]
box_palette = {group: group_family[box_tones[i % len(box_tones)]] for i, group in enumerate(group_order)}
point_palette = {group: group_family[point_tones[i % len(point_tones)]] for i, group in enumerate(group_order)}
edge_colors = {group: group_family["dark"] for group in group_order}
sns.boxplot(data=df, x=group_col, y=value_col, hue=group_col, palette=box_palette, legend=False, linewidth=1.0)
for patch, group in zip(ax.patches, group_order):
    patch.set_edgecolor(edge_colors[group])
sns.stripplot(data=df.sample(min(len(df), 500)), x=group_col, y=value_col, hue=group_col, palette=point_palette, legend=False, alpha=0.25, size=2)
add_chart_header(fig, ax, title, subtitle)
```

### Scatter

- Use: two-variable relationship.
- Data: numeric x/y, optional small group.
- Snippet:
```python
sns.scatterplot(data=df, x=x_col, y=y_col, ax=ax, color=family["base"], edgecolor=family["dark"], linewidth=0.6, alpha=0.65)
add_chart_header(fig, ax, title, subtitle)
```

### Bubble Chart

- Use: two-variable relationship where a third numeric metric materially changes interpretation.
- Data: numeric x/y, numeric size.
- Snippet:
```python
size_min = df[size_col].min()
size_max = df[size_col].max()
size_values = np.quantile(df[size_col], [0.25, 0.5, 0.75])

def marker_size(value):
    if size_max == size_min:
        return 240
    return 80 + (value - size_min) / (size_max - size_min) * 420

sns.scatterplot(
    data=df,
    x=x_col,
    y=y_col,
    size=size_col,
    sizes=(80, 500),
    legend=False,
    ax=ax,
    color=family["base"],
    edgecolor=family["dark"],
    linewidth=0.8,
    alpha=0.55,
)
handles = [
    ax.scatter([], [], s=marker_size(value), facecolors=family["base"], edgecolors=family["dark"], linewidths=0.8, alpha=0.55, label=f"{value:,.0f}")
    for value in size_values
]
ax.legend(handles=handles, title=str(size_col).replace("_", " ").title(), loc="lower left", bbox_to_anchor=(0, 1.02), frameon=False, ncol=len(handles), borderaxespad=0)
add_chart_header(fig, ax, title, subtitle)
```

### Scatter / Density

- Use: dense point cloud.
- Data: numeric x/y.
- Snippet:
```python
ax.hexbin(df[x_col], df[y_col], gridsize=28, mincnt=1, cmap=sns.blend_palette([TOKENS["panel"], family["light"], family["base"]], as_cmap=True))
fit = np.polyfit(df[x_col], df[y_col], deg=1)
x_fit = np.linspace(df[x_col].min(), df[x_col].max(), 100)
sns.lineplot(x=x_fit, y=fit[0] * x_fit + fit[1], ax=ax, color=family["base"], linewidth=1.0)
add_chart_header(fig, ax, title, subtitle)
```

### Ordered Line & Dot

- Use: ordered bins, calibration, or uncertainty comparisons.
- Data: ordered x/bin, estimate, optional bounds/series.
- Snippet:
```python
ax.errorbar(
    df[x_col], df[estimate_col],
    yerr=[df[estimate_col] - df[lower_col], df[upper_col] - df[estimate_col]],
    fmt="o", color=family["base"], linewidth=1.0, capsize=3,
)
ax.plot(df[x_col], df[estimate_col], color=family["light"], linewidth=1.0)
add_chart_header(fig, ax, title, subtitle)
```

### Faceted Dot & Interval

- Use: subgroup estimates against benchmark.
- Data: facet, estimate, lower, upper, label.
- Snippet:
```python
for ax, (facet, part) in zip(axes, df.groupby(facet_col)):
    facet_order = list(df[facet_col].drop_duplicates())
    facet_tones = ["base", "light", "base"]
    facet_color = COLOR_FAMILIES["gold"][facet_tones[facet_order.index(facet) % len(facet_tones)]]
    ax.errorbar(
        part[estimate_col], part[label_col],
        xerr=[part[estimate_col] - part[lower_col], part[upper_col] - part[estimate_col]],
        fmt="o", color=facet_color, linewidth=1.0,
    )
    ax.axvline(benchmark, color=TOKENS["ink"], linestyle=":", linewidth=1.0)
add_chart_header(fig, axes[0], title, subtitle)
```

### Experiment Lift With Confidence Intervals

- Use: lift, treatment effects, or model intervals.
- Data: label, estimate, lower, upper.
- Snippet:
```python
ax.axvline(0, color=TOKENS["ink"], linestyle=":", linewidth=1.0)
metric_family = COLOR_FAMILIES["gold"]
for _, row in df.iterrows():
    marker_face = TOKENS["panel"] if row[estimate_col] < 0 else metric_family["base"]
    ax.errorbar(
        row[estimate_col], row[label_col],
        xerr=np.array([[row[estimate_col] - row[lower_col]], [row[upper_col] - row[estimate_col]]]),
        fmt="o", color=metric_family["base"], markerfacecolor=marker_face, markeredgecolor=metric_family["dark"], linewidth=1.0, capsize=3,
    )
add_chart_header(fig, ax, title, subtitle)
```

### Heatmap

- Use: two-dimensional structure or cohort matrix.
- Data: ordered pivot matrix.
- Snippet:
```python
cmap = sns.blend_palette([TOKENS["panel"], family["xlight"], family["light"], family["base"]], as_cmap=True)
sns.heatmap(matrix, ax=ax, cmap=cmap, linewidths=1.0, linecolor=TOKENS["panel"], annot=annot, fmt=value_format)
add_chart_header(fig, ax, title, subtitle)
```

### Funnel Stage Bars

- Use: ordered stages, counts, conversion.
- Data: stage order, count, optional rate.
- Snippet:
```python
plot_df = df.set_index(stage_col).loc[stage_order].reset_index()
stage_families = [COLOR_FAMILIES[name] for name in ["olive", "gold", "blue", "pink", "orange"]]
palette = {stage: stage_families[i % len(stage_families)]["base"] for i, stage in enumerate(stage_order)}
edge_colors = {stage: stage_families[i % len(stage_families)]["dark"] for i, stage in enumerate(stage_order)}
sns.barplot(data=plot_df, x=stage_col, y=count_col, hue=stage_col, palette=palette, legend=False, dodge=False, ax=ax, edgecolor=TOKENS["ink"], linewidth=1.0)
for patch, stage in zip(ax.patches, plot_df[stage_col]):
    patch.set_edgecolor(edge_colors[stage])
add_chart_header(fig, ax, title, subtitle)
```

### Waterfall Bridge

- Use: additive bridge from start to end.
- Data: ordered drivers, signed deltas, start/end.
- Snippet:
```python
positive_family = COLOR_FAMILIES["olive"]
negative_family = COLOR_FAMILIES["orange"]
positive_fill = positive_family["base"]
negative_fill = negative_family["base"]
total_fill = NEUTRAL_MARKS["light"]
total_edge = NEUTRAL_MARKS["dark"]
x = np.arange(len(df) + 2)
driver_labels = ["Start", *df[label_col], "End"]
running = start_value + df[delta_col].cumsum().shift(fill_value=0)
ending = start_value + df[delta_col].cumsum()
end_value = ending.iloc[-1]
bottom = np.minimum(running, ending)
colors = np.where(df[delta_col] >= 0, positive_fill, negative_fill)
edge_colors = np.where(df[delta_col] >= 0, positive_family["dark"], negative_family["dark"])
ax.bar(x[0], start_value, color=total_fill, edgecolor=total_edge, linewidth=1.0)
bars = ax.bar(x[1:-1], df[delta_col].abs(), bottom=bottom, color=colors, edgecolor=edge_colors, linewidth=1.0)
for bar, delta in zip(bars, df[delta_col]):
    bar.set_edgecolor(positive_family["dark"] if delta >= 0 else negative_family["dark"])
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_y() + bar.get_height() + 2, f"{delta:+.0f}", ha="center", fontsize=8, color=TOKENS["ink"])
ax.bar(x[-1], end_value, color=total_fill, edgecolor=total_edge, linewidth=1.0)
ax.set_xticks(x, driver_labels)
ax.legend(
    handles=[
        Patch(facecolor=total_fill, edgecolor=total_edge, label="Start/end"),
        Patch(facecolor=positive_fill, edgecolor=positive_family["dark"], label="Positive delta"),
        Patch(facecolor=negative_fill, edgecolor=negative_family["dark"], label="Negative delta"),
    ],
    loc="lower left",
    bbox_to_anchor=(0, 1.02),
    frameon=False,
    ncol=3,
    borderaxespad=0,
)
add_chart_header(fig, ax, title, subtitle)
```
