function humanize(value) {
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function markdownValue(value, depth = 3) {
  if (Array.isArray(value)) {
    return value
      .map((item) => {
        if (item && typeof item === "object") {
          return markdownValue(item, depth + 1);
        }
        return `- ${item}`;
      })
      .join("\n");
  }

  if (value && typeof value === "object") {
    return Object.entries(value)
      .map(
        ([key, nested]) =>
          `${"#".repeat(Math.min(depth, 6))} ${humanize(key)}\n\n${markdownValue(
            nested,
            depth + 1,
          )}`,
      )
      .join("\n\n");
  }

  return String(value);
}

function download(filename, content, type) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

export function packageToMarkdown(contentPackage) {
  const sections = {
    topic_analysis: contentPackage.topic_analysis,
    titles: contentPackage.titles,
    script: contentPackage.script,
    thumbnail_texts: contentPackage.thumbnail_texts,
    seo: contentPackage.seo,
    shorts: contentPackage.shorts,
    review: contentPackage.review,
  };

  return [
    `# ${contentPackage.request.topic}`,
    "",
    ...Object.entries(sections).flatMap(([key, value]) => [
      `## ${humanize(key)}`,
      "",
      markdownValue(value),
      "",
    ]),
  ].join("\n");
}

export function downloadJson(contentPackage) {
  download(
    "creatorflow-content-package.json",
    JSON.stringify(contentPackage, null, 2),
    "application/json",
  );
}

export function downloadMarkdown(contentPackage) {
  download(
    "creatorflow-content-package.md",
    packageToMarkdown(contentPackage),
    "text/markdown",
  );
}

export async function copyToClipboard(value) {
  const text =
    typeof value === "string" ? value : JSON.stringify(value, null, 2);
  await navigator.clipboard.writeText(text);
}
