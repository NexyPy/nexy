// Runs stripDocumentTags (document.ts) on stdin cases: { kind, source } -> prints the result.
import { stripDocumentTags } from "../../nexy/modules/frontend/document.ts";
const cases = JSON.parse(process.argv[2]);
console.log("@@" + JSON.stringify(cases.map((c) => stripDocumentTags(c.source, c.kind))) + "@@");
