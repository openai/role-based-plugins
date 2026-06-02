import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

test("inline Recharts bridge normalizes word percent units into valueFormat", async () => {
  const source = await readFile(new URL("../src/recharts-renderer.jsx", import.meta.url), "utf8");

  assert.match(source, /const percentWordUnit = isPercentWordUnit\(rawUnit\);/);
  assert.match(source, /const unit = percentWordUnit \? "" : rawUnit;/);
  assert.match(source, /valueFormat: existing\.valueFormat \|\| \(percentWordUnit \? "percent" : unit === "\$" \? "currency" : "compact"\)/);
});
