import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { Buffer } from "node:buffer";
import test from "node:test";
import ts from "typescript";

async function loadChartTransforms() {
  const source = await readFile(new URL("../src/analytics-app/charting/chart-transforms.ts", import.meta.url), "utf8");
  const { outputText } = ts.transpileModule(source, {
    compilerOptions: {
      module: ts.ModuleKind.ES2022,
      target: ts.ScriptTarget.ES2022,
    },
  });
  const url = `data:text/javascript;base64,${Buffer.from(outputText).toString("base64")}`;
  return import(url);
}

function dailyRows(startDate, count) {
  const start = new Date(`${startDate}T00:00:00.000Z`);
  return Array.from({ length: count }, (_, index) => {
    const date = new Date(start);
    date.setUTCDate(start.getUTCDate() + index);
    return {
      reporting_date: date.toISOString().slice(0, 10),
      value: index,
    };
  });
}

test("date axis ticks show every label for short windows", async () => {
  const { getDateAxisTicks } = await loadChartTransforms();

  assert.deepEqual(
    getDateAxisTicks(dailyRows("2026-05-04", 7), "reporting_date", 760),
    [
      "2026-05-04",
      "2026-05-05",
      "2026-05-06",
      "2026-05-07",
      "2026-05-08",
      "2026-05-09",
      "2026-05-10",
    ],
  );
});

test("date axis ticks keep enough context for a two-week daily trend", async () => {
  const { getDateAxisTicks } = await loadChartTransforms();

  assert.deepEqual(
    getDateAxisTicks(dailyRows("2026-05-04", 14), "reporting_date", 760),
    [
      "2026-05-04",
      "2026-05-06",
      "2026-05-08",
      "2026-05-10",
      "2026-05-12",
      "2026-05-14",
      "2026-05-16",
      "2026-05-17",
    ],
  );
});

test("date axis ticks stay bounded for longer ranges", async () => {
  const { getDateAxisTicks } = await loadChartTransforms();
  const ticks = getDateAxisTicks(dailyRows("2026-01-01", 60), "reporting_date", 760);

  assert.equal(ticks.length, 8);
  assert.equal(ticks[0], "2026-01-01");
  assert.equal(ticks[ticks.length - 1], "2026-03-01");
});

test("date axis ticks ignore non-date axes", async () => {
  const { getDateAxisTicks } = await loadChartTransforms();

  assert.equal(getDateAxisTicks([{ x: "alpha" }, { x: "beta" }], "x", 760), undefined);
});

test("word percent units format semantic rates", async () => {
  const { formatValue } = await loadChartTransforms();

  assert.equal(formatValue(0.6, "compact", "percent"), "60%");
  assert.equal(formatValue(0.625, "number", "percentage"), "62.5%");
  assert.equal(formatValue(60, "compact", "%"), "60%");
});
