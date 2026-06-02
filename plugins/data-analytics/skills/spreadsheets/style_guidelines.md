# Default Style and Formatting Instructions
Apply these defaults to all spreadsheet outputs but ensure user provided style reference(s), template, or explicit formatting instructions take precadence. If the user specifies a style, match that style.

## Formatting Baseline
- If editing an uploaded/template workbook: render first, preserve and match existing style unless user asks to restyle.
- Typical defaults when unspecified:
  - content columns: ~10-24
  - text-heavy columns: cap ~32-40
  - row heights: ~15-20 (titles may be larger)
  - avoid oversized body fonts (>12pt) except intentional titles
- Use fill colors, borders, and merged cells judiciously to give the spreadsheet a professional visual style with a clear layout without overdoing it
- Add data validation for editable categorical columns (`Status`, `Priority`, `Owner`) where feasible.
- Unless conflicting style guidelines are provided: style headers, correct number/date formats, sensible column widths, and row heights, light borders.
- Use larger text only for titles or major section labels.
- Use blank space or slightly taller section/header rows to separate sections
- Keep row heights consistent within each section unless wrapped content requires expansion.
- When text wraps, prefer widening the column before allowing deep multi-line rows; if wrapping is necessary, increase row height just enough to fully show the content.
- Before editing, inspect all relevant current styling attributes (fills, fonts, borders, merged cells, number formats). If changing values only, never overwrite or clear cell formats.
- Maintain structural elements (filters, tables, totals rows), and never introduce merged cells in calculation areas.
- If users are likely to edit the workbook after export, make worksheet cells the live source of truth: any downstream values or visual states that depend on editable inputs should be driven by formulas referencing worksheet cells, then styled with conditional formatting or presentation-only formatting instead of Python-precomputed values or one-time manual fills.
- Use simple helper values when they make behavior easier to inspect and formatting easier to apply;

## Document structure
When creating a new spreadsheet, compose a clear visual layout with distinct zones: a title/header area, the primary table or working region, and—when space and task type allow—a secondary adjacent to the main table to cover summary section or instructions for how to use the sheet. When appropriate, design the sheet so it reads like a structured document, not just a matrix of cells. Use layout, scale, and selective merging to create clear sections and give headers enough room to breathe.

- Vary font size and weight intentionally so the sheet has a readable hierarchy: larger for title, medium for section headers, standard for body text.
- Let major headers occupy more space than body cells so the sheet can feel like a real document with sections, not a uniformly sized table.
- Size status and other validated categorical columns to the longest expected label plus dropdown space; do not leave values clipped.
- If the same label would otherwise repeat across many adjacent rows or columns, prefer a grouped header band, merged label, or legend rather than repeating the text cell by cell.

### Create strong visual hierarchy
Establish at least three hierarchy levels:
1. page title band (larger type, stronger fill, centered, often merged)
2. section/header bands (distinct fill, bold text, clear alignment)
3. body area (light or neutral surface, restrained styling)

### Use a theme palette
Choose a small coordinated palette and assign colors by role:
- primary accent for titles or major headers
- secondary accent for subheaders or section bars
- soft surface/background fill for the working canvas
- neutral/light fill for body cells
- darker text colors for readability
- avoid harsh contrast, excessive saturation, or too many unrelated fills

### Avoiding gridlines
Define structure with explicit fills and borders rather than relying on default gridlines. Use subtle internal borders for separation and slightly stronger outside borders to frame sections or cards. Hide gridlines when explicit section styling already defines the sheet.

### Use adjacent whitespace intentionally
When appropriate, place summary cards, assumptions, instructions, charts, legends, and small supporting lists in unused columns to the right or below the primary table as compact bounded panels sized to their content. Keep these panels visually separate from the main data region with whitespace and aligned edges, but avoid oversized sparse blocks that consume more space than the information warrants. Keep short legends and short validation vocabularies on the main sheet when they fit cleanly; use a helper sheet only when the supporting data is large, heavily reused, or would clutter the main layout.

### Align and format by data type
Apply semantic formatting to entire columns or blocks:
- text/descriptive fields left-aligned
- labels centered or left-aligned depending on context
- numeric and currency fields right-aligned
- dates with explicit date formats
- financial values with explicit currency/accounting formats
- do not leave important numeric fields in raw General format

### Use typography intentionally but conservatively
Use one display-style font choice for titles/section headers and one neutral readable font for body content when supported by the workbook viewer. Keep body text modest in size, reserve larger fonts for titles, and avoid mixing many fonts or excessive emphasis.

### Style the body lightly for scanability
Body regions should remain readable and calm. Use light fills, subtle borders, and minimal emphasis. If one column is the primary descriptive field, it may receive slightly stronger text emphasis to aid scanning, but avoid over-styling entire data regions.
For dense operational tables, use subtle alternating row banding together with thin light borders so users can track across rows without making the grid feel heavy.

### Prefer visible summaries over buried totals
Important totals should usually appear in a visible summary area near the top or in a side panel, even if table-footer totals also exist. Use formulas, not hardcoded values, and style summary cards as distinct panels with their own fill and border treatment.

## Colors and borders
- Use a restrained and professional color palette that matches the nature of the task: neutral text/grid styling, one primary accent family, and at most one secondary accent for exceptions such as warnings or special states.
- Use thin, light borders for structure; use stronger borders only for important section breaks.
- If the sheet includes progress indicators, status indicators, timelines, heatmaps, or other cell-based visuals, make them read as consistent visual bands or blocks with restrained fills, uniform repeated-column styling, and clear accents for milestones or special states rather than noisy repeated symbols or unrelated colors.
- Ensure conditional formatting is applied properly (i.e. such as red for negative, green for positive values)

## Typography and whitespace
- Use bold sparingly and only to establish reading order.
- Give titles, summaries, and section breaks visible breathing room so the sheet does not feel cramped.

## Charting and plotting data
When a spreadsheet includes charts, they should feel like part of the document rather than generic spreadsheet defaults dropped onto the page.

- Create charts from a bounded source range whose first row is headers, whose first column contains the exact x-axis labels to display, and whose remaining columns are the plotted series. If the available data is not already in that shape, write a helper range in that shape first and chart the helper range instead of the raw block. Use clear titles and explicitly set axis titles and unit/number formats whenever the chart communicates a measured value or comparison.
- When the workbook needs both a detailed data table and a chart, keep the detailed table for browsing/filtering, but place the chart next to a smaller chart-driving range that contains only the fields actually plotted.
- Choose chart types intentionally (e.g., clustered column for group comparisons, line for trends over time, pie for share of a whole) and place them close to the relevant data.
- Use tables for structured data that benefits from filtering/sorting; name tables clearly.
- Do not place a chart so it is overlapping or hides data

### Axes, scales, and labels
- Use readable axis labels with sensible tick density; do not overcrowd the x-axis.
- If needed, angle the axis labels if they are at risk of overlapping and this would boost readability.
- For time-based charts, if raw dates would create crowded labels or unreliable date-axis grouping, add an explicit grouped field such as Year, Quarter, Month, or Week to the chart source and chart that field instead of charting every raw date.

## Citation Requirements
### Cite sources inside the spreadsheet
- Use plain-text URLs in spreadsheet cells.
- For financial models, cite model-input sources in cell comments.
- For researched row-wise data tables, include source URLs in a dedicated source column.
