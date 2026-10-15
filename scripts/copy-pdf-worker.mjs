import { copyFileSync, mkdirSync } from "node:fs";
import { dirname } from "node:path";

const from = "node_modules/pdfjs-dist/build/pdf.worker.min.mjs";
const to = "public/pdf.worker.min.mjs";

mkdirSync(dirname(to), { recursive: true });
copyFileSync(from, to);
