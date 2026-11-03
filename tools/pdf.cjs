// Prints tools/guide-print.html (written by build.py) to economic-report-guide.pdf (the "Download the PDF" file).
// Needs Playwright. On Marc's Mac:
//   python3 -m http.server 8742 &   (from the repo root)
//   NODE_PATH=~/odyssey/node_modules node tools/pdf.cjs
const { chromium } = require("playwright");

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto("http://localhost:8742/tools/guide-print.html", { waitUntil: "networkidle" });
  await page.pdf({ path: "economic-report-guide.pdf", format: "Letter", printBackground: true, preferCSSPageSize: true });
  await browser.close();
  console.log("wrote economic-report-guide.pdf");
})();
