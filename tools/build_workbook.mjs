import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const repoRoot = path.resolve(process.argv[2] || ".");
const outputPath = path.join(repoRoot, "data", "ai-compute-economics.xlsx");

function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const ch = text[i];
    if (quoted) {
      if (ch === '"' && text[i + 1] === '"') {
        field += '"';
        i += 1;
      } else if (ch === '"') {
        quoted = false;
      } else {
        field += ch;
      }
    } else if (ch === '"') {
      quoted = true;
    } else if (ch === ",") {
      row.push(field);
      field = "";
    } else if (ch === "\n") {
      row.push(field.replace(/\r$/, ""));
      if (row.some((value) => value !== "")) rows.push(row);
      row = [];
      field = "";
    } else {
      field += ch;
    }
  }
  if (field !== "" || row.length) {
    row.push(field.replace(/\r$/, ""));
    rows.push(row);
  }
  return rows;
}

function typed(value, header) {
  if (value === "") return null;
  if (header === "date") return new Date(`${value}T00:00:00Z`);
  const numericHeaders = new Set([
    "revenue_input_usd", "annualization_factor", "attribution_pct",
    "reported_power_mw", "pue", "availability", "reserve_factor", "utilization",
    "value", "compute_content_usd_bn_per_it_gw", "facility_usd_bn_per_it_gw",
    "total_usd_bn_per_it_gw", "revenue_low_usd_bn_per_it_gw_year",
    "revenue_high_usd_bn_per_it_gw_year",
  ]);
  if (numericHeaders.has(header) && !Number.isNaN(Number(value))) return Number(value);
  return value;
}

async function readData(fileName) {
  const text = await fs.readFile(path.join(repoRoot, "data", fileName), "utf8");
  const rows = parseCsv(text);
  const headers = rows[0];
  return {
    headers,
    rows: rows.slice(1).map((row) => headers.map((header, index) => typed(row[index] ?? "", header))),
  };
}

function columnName(index) {
  let n = index + 1;
  let result = "";
  while (n > 0) {
    const rem = (n - 1) % 26;
    result = String.fromCharCode(65 + rem) + result;
    n = Math.floor((n - 1) / 26);
  }
  return result;
}

const headerLabels = {
  method_id: "Method ID",
  revenue_input_usd: "Revenue input (USD)",
  annualization_factor: "Annualization factor",
  attribution_pct: "AI / compute attribution",
  reported_power_mw: "Reported power (MW)",
  power_scope: "Power scope",
  pue: "PUE",
  reserve_factor: "Reserve factor",
  source_id: "Source ID",
  method_note: "Method note",
  annualized_attributed_revenue_usd: "Annualized attributed revenue (USD)",
  it_load_mw: "IT-load MW",
  effective_utilized_it_mw: "Effective utilized IT MW",
  revenue_usd_m_per_effective_mw_year: "Revenue ($M / effective MW-year)",
  calculation_status: "Calculation status",
  architecture_or_site: "Architecture / site",
  compute_content_usd_bn_per_it_gw: "Compute content ($B / IT GW)",
  facility_usd_bn_per_it_gw: "Facility ($B / IT GW)",
  total_usd_bn_per_it_gw: "Total ($B / IT GW)",
  revenue_low_usd_bn_per_it_gw_year: "Revenue low ($B / IT GW-year)",
  revenue_high_usd_bn_per_it_gw_year: "Revenue high ($B / IT GW-year)",
  gross_revenue_payback_low_years: "Gross payback low (years)",
  gross_revenue_payback_high_years: "Gross payback high (years)",
  artifact_type: "Artifact type",
  evidence_state: "Evidence state",
  unique_adjustment: "Unique adjustment",
};

function displayHeader(header) {
  if (headerLabels[header]) return headerLabels[header];
  return header
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function writeTitle(sheet, title, subtitle, lastColumn) {
  sheet.showGridLines = false;
  sheet.getRange(`A2:${lastColumn}2`).format.borders = {
    bottom: { style: "thin", color: "#23415C" },
  };
  sheet.getRange("A2").values = [[title]];
  sheet.getRange("A2").format.font = { name: "Arial", size: 15, bold: true, color: "#172B3A" };
  sheet.getRange("A3").values = [[subtitle]];
  sheet.getRange(`A3:${lastColumn}3`).format.font = { name: "Arial", size: 10, italic: true, color: "#5B6670" };
}

function styleHeader(range) {
  range.format = {
    fill: "#23415C",
    font: { name: "Arial", size: 10, bold: true, color: "#FFFFFF" },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    wrapText: true,
    borders: {
      insideVertical: { style: "thin", color: "#FFFFFF" },
      bottom: { style: "medium", color: "#23415C" },
    },
  };
  range.format.rowHeight = 32;
}

function styleBody(range) {
  range.format.font = { name: "Arial", size: 10, color: "#1F2933" };
  range.format.verticalAlignment = "center";
  range.format.borders = { bottom: { style: "thin", color: "#D9E1E8" } };
}

function writeDataset(sheet, startRow, startCol, dataset, tableName) {
  const rowCount = dataset.rows.length;
  const colCount = dataset.headers.length;
  const start = `${columnName(startCol)}${startRow}`;
  const end = `${columnName(startCol + colCount - 1)}${startRow + rowCount}`;
  sheet.getRange(start).write([dataset.headers.map(displayHeader), ...dataset.rows]);
  const table = sheet.tables.add(`${start}:${end}`, true, tableName);
  table.style = "TableStyleMedium2";
  return { headerRow: startRow, firstDataRow: startRow + 1, lastDataRow: startRow + rowCount, colCount };
}

const [companyData, methodData, tokenData, benchmarkData, sourceData] = await Promise.all([
  readData("company-models.csv"),
  readData("company-methods.csv"),
  readData("token-economics.csv"),
  readData("power-compute-benchmarks.csv"),
  readData("source-register.csv"),
]);

const workbook = Workbook.create();
const dashboard = workbook.worksheets.add("Dashboard");
const companies = workbook.worksheets.add("Company Models");
const methods = workbook.worksheets.add("Methods");
const token = workbook.worksheets.add("Token Economics");
const benchmarks = workbook.worksheets.add("Benchmarks");
const sources = workbook.worksheets.add("Sources");
const readme = workbook.worksheets.add("Read Me");

dashboard.tabColor = "#17324D";
companies.tabColor = "#2C628F";
methods.tabColor = "#5B8DB8";
token.tabColor = "#2C628F";
benchmarks.tabColor = "#5B8DB8";
sources.tabColor = "#8E9AA3";
readme.tabColor = "#8E9AA3";

// Company model build
writeTitle(
  companies,
  "Company revenue per effective MW",
  "Blue cells are editable source inputs. Formula outputs remain blank when a required numerator or denominator is missing.",
  "T",
);
const companyHeaders = [
  ...companyData.headers,
  "annualized_attributed_revenue_usd",
  "it_load_mw",
  "effective_utilized_it_mw",
  "revenue_usd_m_per_effective_mw_year",
  "calculation_status",
].map(displayHeader);
companies.getRange(`A4:T${4 + companyData.rows.length}`).values = [
  companyHeaders,
  ...companyData.rows.map((row) => [...row, null, null, null, null, null]),
];
styleHeader(companies.getRange("A4:T4"));
styleBody(companies.getRange(`A5:T${4 + companyData.rows.length}`));

for (let row = 5; row <= 4 + companyData.rows.length; row += 1) {
  companies.getRange(`P${row}`).formulas = [[`=IF(OR(D${row}="",E${row}="",F${row}=""),"",D${row}*E${row}*F${row})`]];
  companies.getRange(`Q${row}`).formulas = [[`=IF(G${row}="","",IF(H${row}="IT load",G${row},IF(H${row}="Facility power",IF(I${row}="","",G${row}/I${row}),IF(H${row}="Generation",IF(OR(I${row}="",J${row}="",K${row}=""),"",G${row}*J${row}*K${row}/I${row}),IF(H${row}="Effective utilized IT",G${row},"")))))`]];
  companies.getRange(`R${row}`).formulas = [[`=IF(Q${row}="","",IF(H${row}="Effective utilized IT",Q${row},IF(L${row}="","",Q${row}*L${row})))`]];
  companies.getRange(`S${row}`).formulas = [[`=IF(OR(P${row}="",R${row}="",R${row}=0),"",P${row}/R${row}/1000000)`]];
  companies.getRange(`T${row}`).formulas = [[`=IF(S${row}<>"","Calculated",IF(OR(N${row}="VENDOR ONLY",N${row}="CAPEX ONLY"),"Not an operator output","Missing numerator or denominator"))`]];
}

companies.getRange(`D5:L${4 + companyData.rows.length}`).format.font = { name: "Arial", size: 10, color: "#0066CC" };
companies.getRange(`D5:L${4 + companyData.rows.length}`).format.fill = "#FFF4CC";
companies.getRange(`P5:T${4 + companyData.rows.length}`).format.font = { name: "Arial", size: 10, color: "#000000" };
companies.getRange(`D5:D${4 + companyData.rows.length}`).format.numberFormat = "$#,##0;[Red]($#,##0);-";
companies.getRange(`E5:E${4 + companyData.rows.length}`).format.numberFormat = "0.0x";
companies.getRange(`F5:F${4 + companyData.rows.length}`).format.numberFormat = "0.0%";
companies.getRange(`G5:G${4 + companyData.rows.length}`).format.numberFormat = "#,##0.0";
companies.getRange(`I5:L${4 + companyData.rows.length}`).format.numberFormat = "0.00";
companies.getRange(`P5:P${4 + companyData.rows.length}`).format.numberFormat = "$#,##0;[Red]($#,##0);-";
companies.getRange(`Q5:R${4 + companyData.rows.length}`).format.numberFormat = "#,##0.0";
companies.getRange(`S5:S${4 + companyData.rows.length}`).format.numberFormat = "$#,##0.0";
companies.getRange(`T5:T${4 + companyData.rows.length}`).conditionalFormats.add("containsText", {
  text: "Missing",
  format: { fill: "#FDE8E7", font: { color: "#B42318", bold: true } },
});
companies.getRange(`T5:T${4 + companyData.rows.length}`).conditionalFormats.add("containsText", {
  text: "Calculated",
  format: { fill: "#E6F4EA", font: { color: "#176B3A", bold: true } },
});
companies.freezePanes.freezeRows(4);
companies.freezePanes.freezeColumns(2);
const companyWidths = [22, 20, 16, 17, 14, 13, 14, 18, 9, 11, 12, 11, 18, 15, 48, 21, 14, 20, 20, 28];
companyWidths.forEach((width, index) => { companies.getRange(`${columnName(index)}:${columnName(index)}`).format.columnWidth = width; });
companies.getRange(`O5:O${4 + companyData.rows.length}`).format.wrapText = true;

// Methods
writeTitle(methods, "Company method registry", "The normalized output is shared; each company's numerator and denominator logic remains explicit.", "G");
const methodRegion = writeDataset(methods, 4, 0, methodData, "CompanyMethodsTable");
styleHeader(methods.getRange(`A4:G4`));
styleBody(methods.getRange(`A5:G${methodRegion.lastDataRow}`));
methods.getRange(`C5:G${methodRegion.lastDataRow}`).format.wrapText = true;
methods.freezePanes.freezeRows(4);
[20, 23, 18, 42, 38, 48, 24].forEach((width, index) => { methods.getRange(`${columnName(index)}:${columnName(index)}`).format.columnWidth = width; });

// Token economics
writeTitle(token, "Token economics", "Dated observations remain platform-specific. The Jevons calculator uses realized price, volume, and spend identities.", "M");
const tokenRegion = writeDataset(token, 4, 0, tokenData, "TokenEconomicsTable");
styleHeader(token.getRange("A4:I4"));
styleBody(token.getRange(`A5:I${tokenRegion.lastDataRow}`));
token.getRange(`A5:A${tokenRegion.lastDataRow}`).format.numberFormat = "mm/dd/yy";
token.getRange(`D5:D${tokenRegion.lastDataRow}`).format.numberFormat = "0.0000";
token.getRange(`I5:I${tokenRegion.lastDataRow}`).format.wrapText = true;
token.getRange("K4:M4").values = [["July 2026 Jevons test", "Value", "Formula / meaning"]];
styleHeader(token.getRange("K4:M4"));
token.getRange("K5:M10").values = [
  ["Realized price decline", 0.136, "Observed"],
  ["Exact volume break-even", null, "d / (1 - d)"],
  ["Observed token-volume growth", 0.59, "Observed"],
  ["Implied spend growth", null, "(1 + g) × (1 - d) - 1"],
  ["Log-change coverage", null, "ln(1 + g) / -ln(1 - d)"],
  ["Regime", null, "Volume clears exact break-even"],
];
token.getRange("L6").formulas = [["=L5/(1-L5)"]];
token.getRange("L8").formulas = [["=(1+L7)*(1-L5)-1"]];
token.getRange("L9").formulas = [["=LN(1+L7)/-LN(1-L5)"]];
token.getRange("L10").formulas = [["=IF(L7>L6,\"Jevons absorption\",\"Price deflation wins\")"]];
token.getRange("K5:M10").format.font = { name: "Arial", size: 10, color: "#1F2933" };
token.getRange("K5:M10").format.borders = { bottom: { style: "thin", color: "#D9E1E8" } };
token.getRange("L5:L8").format.numberFormat = "0.0%";
token.getRange("L9").format.numberFormat = "0.00x";
token.getRange("L5:L7").format.font = { name: "Arial", size: 10, color: "#0066CC" };
token.getRange("L5:L7").format.fill = "#FFF4CC";
token.freezePanes.freezeRows(4);
[13, 18, 35, 14, 24, 12, 22, 18, 44, 3, 30, 16, 34].forEach((width, index) => { token.getRange(`${columnName(index)}:${columnName(index)}`).format.columnWidth = width; });

// Benchmarks
writeTitle(benchmarks, "Power and compute benchmarks", "All figures are per IT-load GW. Facility cost remains project-specific.", "L");
const benchmarkHeaders = [...benchmarkData.headers, "gross_revenue_payback_low_years", "gross_revenue_payback_high_years"].map(displayHeader);
benchmarks.getRange(`A4:L${4 + benchmarkData.rows.length}`).values = [
  benchmarkHeaders,
  ...benchmarkData.rows.map((row) => [...row, null, null]),
];
styleHeader(benchmarks.getRange("A4:L4"));
styleBody(benchmarks.getRange(`A5:L${4 + benchmarkData.rows.length}`));
for (let row = 5; row <= 4 + benchmarkData.rows.length; row += 1) {
  benchmarks.getRange(`K${row}`).formulas = [[`=IF(OR(E${row}="",G${row}="",G${row}=0),"",E${row}/G${row})`]];
  benchmarks.getRange(`L${row}`).formulas = [[`=IF(OR(E${row}="",F${row}="",F${row}=0),"",E${row}/F${row})`]];
}
benchmarks.getRange(`C5:G${4 + benchmarkData.rows.length}`).format.numberFormat = "$0.0";
benchmarks.getRange(`K5:L${4 + benchmarkData.rows.length}`).format.numberFormat = "0.0x";
benchmarks.getRange(`J5:J${4 + benchmarkData.rows.length}`).format.wrapText = true;
benchmarks.freezePanes.freezeRows(4);
[22, 30, 18, 18, 18, 18, 18, 22, 16, 48, 18, 18].forEach((width, index) => { benchmarks.getRange(`${columnName(index)}:${columnName(index)}`).format.columnWidth = width; });

// Sources
writeTitle(sources, "Source register", "Every hard-coded observation should resolve to one source ID here.", "I");
const sourceRegion = writeDataset(sources, 4, 0, sourceData, "SourceRegisterTable");
styleHeader(sources.getRange("A4:I4"));
styleBody(sources.getRange(`A5:I${sourceRegion.lastDataRow}`));
sources.getRange(`B5:B${sourceRegion.lastDataRow}`).format.numberFormat = "mm/dd/yy";
sources.getRange(`D5:I${sourceRegion.lastDataRow}`).format.wrapText = true;
sources.freezePanes.freezeRows(4);
[24, 13, 24, 38, 22, 58, 42, 20, 46].forEach((width, index) => { sources.getRange(`${columnName(index)}:${columnName(index)}`).format.columnWidth = width; });

// Dashboard
writeTitle(dashboard, "AI compute economics", "Revenue manufactured per effective utilized IT MW, with token monetization and capex context.", "H");
dashboard.getRange("A5:B9").values = [
  ["Current measures", "Value"],
  ["Companies configured", companyData.rows.length],
  ["Operator outputs calculated", null],
  ["Nscale contracted revenue ($M / effective MW-year)", null],
  ["July Jevons result", null],
];
styleHeader(dashboard.getRange("A5:B5"));
styleBody(dashboard.getRange("A6:B9"));
dashboard.getRange("B7").formulas = [[`=COUNT('Company Models'!S5:S${4 + companyData.rows.length})`]];
dashboard.getRange("B8").formulas = [["='Company Models'!S13"]];
dashboard.getRange("B9").formulas = [["='Token Economics'!L10"]];
dashboard.getRange("B8").format.numberFormat = "$#,##0.0";
dashboard.getRange("D5:H5").values = [["Benchmark", "Low", "High", "Class", "Question"]];
styleHeader(dashboard.getRange("D5:H5"));
dashboard.getRange("D6:H9").values = [
  ["Spot compute revenue ($B / IT GW-year)", 10, 12, "Merchant", "Does utilization or price weaken?"],
  ["Acceptability line", 15, 15, "External threshold", "Derivation remains open"],
  ["Nscale / Anthropic", 16.3, 16.3, "Contracted", "Does the offtake premium persist?"],
  ["Healthy long-term case", 25, 25, "Aspirational", "Can Rubin lift operator revenue/GW?"],
];
styleBody(dashboard.getRange("D6:H9"));
dashboard.getRange("E6:F9").format.numberFormat = "$0.0";
dashboard.getRange("A12:F12").values = [["Company", "Method", "Role", "Input status", "Revenue $M / effective MW-year", "Calculation status"]];
styleHeader(dashboard.getRange("A12:F12"));
for (let index = 0; index < companyData.rows.length; index += 1) {
  const dashRow = 13 + index;
  const modelRow = 5 + index;
  dashboard.getRange(`A${dashRow}:F${dashRow}`).formulas = [[
    `='Company Models'!A${modelRow}`,
    `='Company Models'!B${modelRow}`,
    `=IFERROR(INDEX(Methods!$C$5:$C$${4 + methodData.rows.length},MATCH(B${dashRow},Methods!$A$5:$A$${4 + methodData.rows.length},0)),"")`,
    `='Company Models'!N${modelRow}`,
    `=IF('Company Models'!S${modelRow}="","",'Company Models'!S${modelRow})`,
    `='Company Models'!T${modelRow}`,
  ]];
}
styleBody(dashboard.getRange(`A13:F${12 + companyData.rows.length}`));
dashboard.getRange(`E13:E${12 + companyData.rows.length}`).format.numberFormat = "$#,##0.0";
dashboard.getRange("A28").values = [["Central forward test"]];
dashboard.getRange("A28:H28").format = { fill: "#DCEAF5", font: { name: "Arial", size: 11, bold: true, color: "#17324D" } };
dashboard.getRange("A29").values = [["Rubin raises NVIDIA content per IT-load GW from $25B to $40B, about 60%. Operator revenue/GW must rise comparably to preserve gross-revenue payback. If revenue/GW stays flat again, vendor economics strengthen while operator replacement economics deteriorate."]];
dashboard.getRange("A29:H29").format = { font: { name: "Arial", size: 10, color: "#1F2933" }, wrapText: true };
dashboard.getRange("A29:H29").format.rowHeight = 68;
dashboard.freezePanes.freezeRows(12);
[52, 24, 18, 35, 14, 14, 24, 42].forEach((width, index) => { dashboard.getRange(`${columnName(index)}:${columnName(index)}`).format.columnWidth = width; });

// Read Me
writeTitle(readme, "How to update this workbook", "The CSV files are the git-diffable input layer; this workbook is the reader-facing calculation layer.", "F");
readme.getRange("A5:B15").values = [
  ["Rule", "Required action"],
  ["Power scope", "Label every MW as generation, facility, IT load, or effective utilized IT."],
  ["Period", "Match revenue to weighted-average active capacity for the same period."],
  ["Attribution", "Keep AI or compute attribution explicit and sourced. Blank is acceptable."],
  ["Company method", "Use the registered method; do not force every company through one numerator."],
  ["Contracted compute", "Separate contract rate from physical utilization and realized revenue."],
  ["Token price", "Use realized expenditure for the Jevons test; list price is a separate series."],
  ["Exact break-even", "Price decline d requires volume growth d / (1 - d) to hold revenue flat."],
  ["Sources", "Add a source ID before adding a hard-coded observation."],
  ["Unknowns", "Leave missing numerators or denominators blank; never replace them with zero."],
  ["Corrections", "Retain superseded observations and state what changed."],
];
styleHeader(readme.getRange("A5:B5"));
styleBody(readme.getRange("A6:B15"));
readme.getRange("B6:B15").format.wrapText = true;
readme.getRange("A:A").format.columnWidth = 24;
readme.getRange("B:B").format.columnWidth = 95;

workbook.recalculate();

const companyCheck = await workbook.inspect({
  kind: "table",
  range: `Company Models!A4:T${4 + companyData.rows.length}`,
  include: "values,formulas",
  tableMaxRows: 18,
  tableMaxCols: 20,
});
console.log(companyCheck.ndjson);

const dashboardCheck = await workbook.inspect({
  kind: "table",
  range: "Dashboard!A5:H30",
  include: "values,formulas",
  tableMaxRows: 30,
  tableMaxCols: 8,
});
console.log(dashboardCheck.ndjson);

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",
  options: { useRegex: true, maxResults: 300 },
  summary: "final formula error scan",
});
console.log(errors.ndjson);

const previewSheets = ["Dashboard", "Company Models", "Methods", "Token Economics", "Benchmarks", "Sources", "Read Me"];
await fs.mkdir(path.join(repoRoot, ".artifact_tmp"), { recursive: true });
for (const sheetName of previewSheets) {
  const preview = await workbook.render({ sheetName, autoCrop: "all", scale: 1, format: "png" });
  const safeName = sheetName.toLowerCase().replaceAll(" ", "-");
  await fs.writeFile(path.join(repoRoot, ".artifact_tmp", `${safeName}.png`), new Uint8Array(await preview.arrayBuffer()));
}

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.log(`Saved ${outputPath}`);
