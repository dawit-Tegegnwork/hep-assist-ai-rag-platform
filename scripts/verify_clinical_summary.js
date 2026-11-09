#!/usr/bin/env node
/**
 * Regression checks for Hermona clinical-summary rules.
 * Extracts pure helpers from bahmni_panel/js/medimindSidePanel.js and asserts behavior.
 */
var fs = require("fs");
var path = require("path");

var srcPath = path.join(__dirname, "..", "bahmni_panel", "js", "medimindSidePanel.js");
var src = fs.readFileSync(srcPath, "utf8");

function extractFn(name) {
  var start = src.indexOf("function " + name + "(");
  if (start < 0) throw new Error("missing function " + name);
  var i = src.indexOf("{", start);
  var depth = 0;
  for (; i < src.length; i++) {
    if (src[i] === "{") depth++;
    else if (src[i] === "}") {
      depth--;
      if (depth === 0) {
        return src.slice(start, i + 1);
      }
    }
  }
  throw new Error("unclosed function " + name);
}

var bundle = [
  extractFn("diseaseDisplayName"),
  extractFn("stripIcdCodesInText"),
  extractFn("slot"),
  extractFn("vitalValue"),
  extractFn("chiefComplaintFromChart"),
  extractFn("chartOnset"),
  extractFn("chartSymptomBits"),
  extractFn("ruleBasedSummary")
].join("\n");

var exports = {};
var fn = new Function(
  "exports",
  bundle +
    "\nexports.diseaseDisplayName = diseaseDisplayName;" +
    "\nexports.stripIcdCodesInText = stripIcdCodesInText;" +
    "\nexports.ruleBasedSummary = ruleBasedSummary;"
);
fn(exports);

var fails = [];
function assert(cond, msg) {
  if (!cond) fails.push(msg);
}

assert(
  exports.diseaseDisplayName("FA80- - - Intervertebral disc degeneration") ===
    "Intervertebral disc degeneration",
  "strip FA80 dashed ICD label"
);
assert(
  exports.diseaseDisplayName("EH92.0- - - Corns or callosities") === "Corns or callosities",
  "strip EH92.0 dashed ICD label"
);
assert(
  exports.diseaseDisplayName("BD74.1 --- Lower limb varicose veins") ===
    "Lower limb varicose veins",
  "strip BD74.1 triple-dash ICD label (SHEWANGIZAW-style)"
);
assert(
  exports.diseaseDisplayName("osteomyelitis") === "osteomyelitis",
  "plain name unchanged"
);

var sample = exports.ruleBasedSummary(
  {
    diagnoses: [{ name: "FA80- - - Intervertebral disc degeneration" }],
    history: {
      medical: [
        "FA80- - - Intervertebral disc degeneration",
        "EH92.0- - - Corns or callosities",
        "R/O bilateral knee OA"
      ],
      allergies: []
    },
    medications: [],
    vitals: {}
  },
  { age: 36, gender: "male" }
);

assert(!/FA80|EH92|ICD/i.test(sample), "no ICD codes in summary");
assert(!/not documented/i.test(sample), "no 'not documented' filler");
assert(!/started at a time/i.test(sample), "no missing-onset wording");
assert(!/symptoms are characterized/i.test(sample), "omit empty symptoms section");
assert(!/Significantly,/i.test(sample), "omit undocumented red-flag narration");
assert(!/BP not recorded|HR not recorded|SpO₂ not recorded/i.test(sample), "omit missing vitals");
assert(/36-year-old male/i.test(sample), "keeps demographics");
assert(/intervertebral disc degeneration/i.test(sample), "keeps disease name");
assert(/Corns or callosities/i.test(sample), "keeps PMH display names");
assert(sample.length < 450, "compressed under 450 chars (got " + sample.length + ")");

var withSymptoms = exports.ruleBasedSummary(
  {
    formFill: { complaint: "severe low back pain", onset: "3 days ago", quality: "sharp" },
    diagnoses: [],
    history: { medical: [], allergies: ["penicillin"] },
    medications: [{ drug: "ibuprofen" }],
    vitals: { bp: { value: "120/80" }, hr: { value: "72", unit: "/min" } }
  },
  { age: 40, gender: "female" }
);
assert(/which started 3 days ago/.test(withSymptoms), "includes onset when present");
assert(/characterized as sharp/.test(withSymptoms), "includes symptom quality when present");
assert(/penicillin/.test(withSymptoms), "includes allergies when present");
assert(/BP 120\/80/.test(withSymptoms), "includes recorded vitals only");

if (src.indexOf("mm-draft-btn") >= 0 || src.indexOf("Draft ›") >= 0) {
  fails.push("Draft › button still present in side panel JS");
}
if (src.indexOf("mm-doc-editor") >= 0) {
  fails.push("draft textarea still present in side panel JS");
}
if (src.indexOf("httpsBahmniUrl") < 0 || src.indexOf("Open HTTPS for microphone") < 0) {
  fails.push("HTTPS microphone CTA missing");
}
if (src.indexOf("Show SOAP fields") < 0 || src.indexOf("mm-note-soap") < 0) {
  fails.push("Note SOAP should stay collapsed behind Show SOAP fields");
}

var varicose = exports.ruleBasedSummary(
  {
    diagnoses: [
      { name: "BD74.1 --- Lower limb varicose veins" },
      { name: "PAD" }
    ],
    history: { medical: [], allergies: [] },
    medications: [],
    vitals: {}
  },
  { age: 60, gender: "male" }
);
assert(!/BD74/i.test(varicose), "BD74.1 stripped from summary");
assert(/Lower limb varicose veins/i.test(varicose), "varicose veins name kept");

console.log("--- disc-degeneration sample ---");
console.log(sample);
console.log("--- end sample (" + sample.length + " chars) ---");

if (fails.length) {
  console.error("FAIL:");
  fails.forEach(function (f) { console.error(" - " + f); });
  process.exit(1);
}
console.log("OK: " + (8 + 4) + " clinical-summary checks passed");
