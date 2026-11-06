// Rasterise the official marks (recolour-only variants from the archlang repo) for the end card.
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { Resvg } from "@resvg/resvg-js";

mkdirSync("build/brand", { recursive: true });
for (const [src, width] of [["archlang-icon.svg", 512], ["archlang-icon-plum.svg", 512], ["archlang-wordmark.svg", 1400], ["archlang-wordmark-black.svg", 1400]]) {
  const png = new Resvg(readFileSync(`brand/${src}`), { fitTo: { mode: "width", value: width } }).render().asPng();
  writeFileSync(`build/brand/${src.replace(".svg", ".png")}`, png);
  console.log(src, png.length);
}
