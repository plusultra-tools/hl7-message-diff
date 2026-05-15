// hl7-message-diff — vanilla JS port of the Python differ.
// Runs entirely in the browser; no network calls. Safe for PHI.

(function () {
  "use strict";

  // ----- Embedded HL7 v2.6 labels (subset matching labels.py) -----
  const LABELS = {
    MSH: {
      1: "Field Separator", 2: "Encoding Characters", 3: "Sending Application",
      4: "Sending Facility", 5: "Receiving Application", 6: "Receiving Facility",
      7: "Date/Time of Message", 8: "Security", 9: "Message Type",
      10: "Message Control ID", 11: "Processing ID", 12: "Version ID",
      13: "Sequence Number", 14: "Continuation Pointer",
      15: "Accept Acknowledgement Type", 16: "Application Acknowledgement Type",
      17: "Country Code", 18: "Character Set",
      19: "Principal Language of Message",
      20: "Alternate Character Set Handling Scheme",
      21: "Message Profile Identifier",
    },
    EVN: {
      1: "Event Type Code", 2: "Recorded Date/Time",
      3: "Date/Time Planned Event", 4: "Event Reason Code",
      5: "Operator ID", 6: "Event Occurred", 7: "Event Facility",
    },
    PID: {
      1: "Set ID - PID", 2: "Patient ID (External)",
      3: "Patient Identifier List", 4: "Alternate Patient ID",
      5: "Patient Name", 6: "Mother's Maiden Name",
      7: "Date/Time of Birth", 8: "Administrative Sex", 9: "Patient Alias",
      10: "Race", 11: "Patient Address", 12: "County Code",
      13: "Phone Number - Home", 14: "Phone Number - Business",
      15: "Primary Language", 16: "Marital Status", 17: "Religion",
      18: "Patient Account Number", 19: "SSN Number - Patient",
      20: "Driver's License Number", 21: "Mother's Identifier",
      22: "Ethnic Group", 23: "Birth Place", 24: "Multiple Birth Indicator",
      25: "Birth Order", 26: "Citizenship", 27: "Veterans Military Status",
      28: "Nationality", 29: "Patient Death Date and Time",
      30: "Patient Death Indicator",
    },
    PV1: {
      1: "Set ID - PV1", 2: "Patient Class", 3: "Assigned Patient Location",
      4: "Admission Type", 5: "Preadmit Number", 6: "Prior Patient Location",
      7: "Attending Doctor", 8: "Referring Doctor", 9: "Consulting Doctor",
      10: "Hospital Service", 17: "Admitting Doctor", 19: "Visit Number",
      44: "Admit Date/Time", 45: "Discharge Date/Time",
    },
    OBR: {
      1: "Set ID - OBR", 2: "Placer Order Number", 3: "Filler Order Number",
      4: "Universal Service Identifier", 7: "Observation Date/Time",
      16: "Ordering Provider", 25: "Result Status",
    },
    OBX: {
      1: "Set ID - OBX", 2: "Value Type", 3: "Observation Identifier",
      4: "Observation Sub-ID", 5: "Observation Value", 6: "Units",
      7: "References Range", 8: "Abnormal Flags",
      11: "Observation Result Status", 14: "Date/Time of the Observation",
    },
    NK1: { 1: "Set ID - NK1", 2: "Name", 3: "Relationship", 4: "Address" },
    AL1: {
      1: "Set ID - AL1", 2: "Allergen Type Code",
      3: "Allergen Code/Mnemonic/Description", 4: "Allergy Severity Code",
      5: "Allergy Reaction Code", 6: "Identification Date",
    },
    DG1: {
      1: "Set ID - DG1", 2: "Diagnosis Coding Method", 3: "Diagnosis Code",
      4: "Diagnosis Description", 5: "Diagnosis Date/Time", 6: "Diagnosis Type",
    },
    IN1: {
      1: "Set ID - IN1", 2: "Insurance Plan ID",
      3: "Insurance Company ID", 4: "Insurance Company Name",
    },
  };

  function labelFor(segment, field) {
    const segLabels = LABELS[segment] || {};
    const name = segLabels[field];
    return name ? `${segment}-${field} ${name}` : `${segment}-${field}`;
  }

  // ----- Parser -----
  function parseMessage(raw) {
    if (!raw) return [];
    const normalised = raw.replace(/\r\n/g, "\r").replace(/\n/g, "\r");
    const rawSegments = normalised.split("\r").filter(s => s.trim().length > 0);
    if (rawSegments.length === 0) return [];

    let fieldSep = "|";
    const first = rawSegments[0];
    if (first.startsWith("MSH") && first.length >= 4) {
      fieldSep = first[3];
    }

    return rawSegments.map((rawSeg, idx) => {
      const parts = rawSeg.split(fieldSep);
      const name = parts[0];
      let fields;
      if (name === "MSH") {
        fields = [fieldSep].concat(parts.slice(1));
      } else {
        fields = parts.slice(1);
      }
      return { name, fields, index: idx };
    });
  }

  // ----- Differ -----
  function diffSegmentPair(a, b) {
    const diffs = [];
    const maxLen = Math.max(a.fields.length, b.fields.length);
    for (let i = 0; i < maxLen; i++) {
      const aVal = i < a.fields.length ? a.fields[i] : null;
      const bVal = i < b.fields.length ? b.fields[i] : null;
      if (aVal === bVal) continue;
      const position = i + 1;
      let kind = "changed";
      if (aVal === null) kind = "added";
      else if (bVal === null) kind = "removed";
      diffs.push({
        segment: a.name,
        segment_index: a.index,
        field: position,
        field_name: labelFor(a.name, position),
        before: aVal,
        after: bVal,
        kind,
      });
    }
    return diffs;
  }

  function diffMessages(rawA, rawB) {
    const aSegs = parseMessage(rawA);
    const bSegs = parseMessage(rawB);
    const diffs = [];
    const maxSegs = Math.max(aSegs.length, bSegs.length);
    for (let i = 0; i < maxSegs; i++) {
      const a = i < aSegs.length ? aSegs[i] : null;
      const b = i < bSegs.length ? bSegs[i] : null;
      if (!a && b) {
        diffs.push({
          segment: b.name, segment_index: i, field: 0,
          field_name: `${b.name} (segment present only in second message)`,
          before: null, after: b.name, kind: "segment-only-in-b",
        });
        continue;
      }
      if (a && !b) {
        diffs.push({
          segment: a.name, segment_index: i, field: 0,
          field_name: `${a.name} (segment present only in first message)`,
          before: a.name, after: null, kind: "segment-only-in-a",
        });
        continue;
      }
      if (a.name !== b.name) {
        diffs.push({
          segment: `${a.name}/${b.name}`, segment_index: i, field: 0,
          field_name: `Segment type mismatch at index ${i}: ${a.name} vs ${b.name}`,
          before: a.name, after: b.name, kind: "segment-mismatch",
        });
        continue;
      }
      diffs.push.apply(diffs, diffSegmentPair(a, b));
    }
    return diffs;
  }

  // ----- Render -----
  function escapeHtml(s) {
    if (s === null || s === undefined) return "";
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function renderDiffs(diffs) {
    if (diffs.length === 0) {
      return '<span class="ok">No differences.</span>';
    }
    const lines = [];
    for (const d of diffs) {
      if (d.kind === "segment-mismatch") {
        lines.push(`<div class="seg-mismatch">${escapeHtml(d.field_name)}</div>`);
      } else if (d.kind === "segment-only-in-a") {
        lines.push(`<div class="seg-only-a">${escapeHtml(d.field_name)}</div>`);
      } else if (d.kind === "segment-only-in-b") {
        lines.push(`<div class="seg-only-b">${escapeHtml(d.field_name)}</div>`);
      } else {
        lines.push(`<div class="field-name">${escapeHtml(d.field_name)}</div>`);
        if (d.before !== null) {
          lines.push(`<div class="before">  - ${escapeHtml(d.before)}</div>`);
        }
        if (d.after !== null) {
          lines.push(`<div class="after">  + ${escapeHtml(d.after)}</div>`);
        }
      }
    }
    return lines.join("");
  }

  // ----- DOM wiring -----
  const SAMPLE_A =
    "MSH|^~\\&|HIS|HOSPITAL|LIS|LAB|202601010900||ADT^A01|MSG001|P|2.6\r" +
    "EVN|A01|202601010900\r" +
    "PID|1||12345^^^MR||DOE^JOHN||19800101|M|||123 MAIN ST^^BOSTON^MA^02101\r" +
    "PV1|1|I|2000^2012^01||||004777^ATTEND^AARON^A.\r";

  const SAMPLE_B =
    "MSH|^~\\&|HIS|HOSPITAL|LIS|LAB|202601010900||ADT^A01|MSG001|P|2.6\r" +
    "EVN|A01|202601010900\r" +
    "PID|1||12345^^^MR||DOE^JOHN||19800102|M|||456 OAK AVE^^BOSTON^MA^02101\r" +
    "PV1|1|I|2000^2012^01||||004777^ATTEND^AARON^A.\r";

  function $(id) { return document.getElementById(id); }

  function run() {
    const a = $("msg-a").value;
    const b = $("msg-b").value;
    const out = $("diff-output");
    try {
      const diffs = diffMessages(a, b);
      out.innerHTML = renderDiffs(diffs);
    } catch (err) {
      out.innerHTML = `<span class="before">Error: ${escapeHtml(err.message)}</span>`;
    }
  }

  function loadSample() {
    $("msg-a").value = SAMPLE_A.replace(/\r/g, "\n");
    $("msg-b").value = SAMPLE_B.replace(/\r/g, "\n");
    run();
  }

  function clearAll() {
    $("msg-a").value = "";
    $("msg-b").value = "";
    $("diff-output").innerHTML = '<p class="hint">Paste two HL7 v2 messages above and click <strong>Diff</strong>.</p>';
  }

  document.addEventListener("DOMContentLoaded", function () {
    $("run-diff").addEventListener("click", run);
    $("load-sample").addEventListener("click", loadSample);
    $("clear").addEventListener("click", clearAll);
  });

  // Expose for testing if needed.
  window.hl7diff = { diffMessages, parseMessage, labelFor };
})();
