// gta6-meme-x-01 entry program.
//
// The bounty deliverable is a single file, POST.json, which points at the
// live X post carrying the meme. The grader runs this program with two
// environment variables:
//
//   MAKEFUN_BOT_DIR    where this program's files live   (default "/bot")
//   MAKEFUN_OUTPUT_DIR where POST.json must be delivered (default "/output")
//
// All this program does is create the output directory when needed and
// copy POST.json into it. Any failure is reported on stderr and exits 1.

import { copyFileSync, mkdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

function fail(message: string): never {
  console.error(`gta6-meme-x-entry: ${message}`);
  process.exit(1);
}

// Read POST.json and make sure it really carries one usable X post URL
// before anything is delivered. A malformed file fails loudly here
// instead of surfacing later as a broken submission.
function checkPostFile(sourcePath: string): void {
  let raw: string;
  try {
    raw = readFileSync(sourcePath, "utf8");
  } catch (err) {
    fail(`could not read "${sourcePath}": ${String(err)}`);
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(raw);
  } catch (err) {
    fail(`"${sourcePath}" is not valid JSON: ${String(err)}`);
  }

  const url: unknown =
    typeof parsed === "object" && parsed !== null
      ? (parsed as { url?: unknown }).url
      : undefined;

  if (typeof url !== "string" || url.length === 0) {
    fail(`"${sourcePath}" must contain a non-empty string field "url"`);
  }

  let parsedUrl: URL;
  try {
    parsedUrl = new URL(url);
  } catch {
    fail(`"url" in "${sourcePath}" is not a valid URL: ${url}`);
  }

  if (parsedUrl.protocol !== "https:" || !parsedUrl.pathname.includes("/status/")) {
    fail(
      `"url" in "${sourcePath}" should be an https X post link ` +
        `containing "/status/", got: ${url}`,
    );
  }
}

function main(): void {
  const botDir: string = process.env.MAKEFUN_BOT_DIR ?? "/bot";
  const outputDir: string = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

  const sourcePath: string = join(botDir, "POST.json");
  const targetPath: string = join(outputDir, "POST.json");

  checkPostFile(sourcePath);

  try {
    mkdirSync(outputDir, { recursive: true });
  } catch (err) {
    fail(`could not create output directory "${outputDir}": ${String(err)}`);
  }

  try {
    copyFileSync(sourcePath, targetPath);
  } catch (err) {
    fail(`could not copy "${sourcePath}" to "${targetPath}": ${String(err)}`);
  }

  console.log(`delivered POST.json to ${targetPath}`);
}

main();
