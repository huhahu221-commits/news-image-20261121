// News-image-daily entry (Node 22, standard library only).
//
// Validates entry.png itself -- PNG signature, IHDR dimensions, file size -- then
// copies it byte for byte into the output directory and confirms the copy by size.
// The gate accepts a whole PNG of at most 1 MiB and at most 1024x1024 pixels, so
// anything outside that is rejected here rather than at grading time.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, existsSync, mkdirSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

const MAX_PIXELS = 1024;
const MAX_BYTES = 1048576; // 1 MiB
const PNG_SIGNATURE = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

interface PngHeader {
  width: number;
  height: number;
  byteLength: number;
}

function fail(message: string): never {
  console.error(`error: ${message}`);
  process.exit(1);
}

// Reads and validates the 8-byte signature plus the IHDR chunk of a PNG buffer.
// The IHDR chunk is mandatory and first: 4-byte big-endian length, "IHDR", then
// 13 bytes of payload whose first 8 are width and height, big-endian.
function readPngHeader(bytes: Buffer, label: string): PngHeader {
  if (bytes.byteLength < 24) {
    fail(`${label} is only ${bytes.byteLength} bytes -- too short to hold a PNG header`);
  }
  if (!bytes.subarray(0, 8).equals(PNG_SIGNATURE)) {
    fail(`${label} is not a PNG (bad 8-byte signature)`);
  }
  const chunkType = bytes.toString('latin1', 12, 16);
  const chunkLength = bytes.readUInt32BE(8);
  if (chunkType !== 'IHDR' || chunkLength !== 13) {
    fail(`${label} is not a valid PNG (first chunk is "${chunkType}", expected IHDR)`);
  }
  const width = bytes.readUInt32BE(16);
  const height = bytes.readUInt32BE(20);
  if (width === 0 || height === 0) {
    fail(`${label} declares an empty image (${width}x${height})`);
  }
  if (width > MAX_PIXELS || height > MAX_PIXELS) {
    fail(`${label} is ${width}x${height}, larger than the ${MAX_PIXELS}x${MAX_PIXELS} limit`);
  }
  return { width, height, byteLength: bytes.byteLength };
}

function main(): void {
  const source = fileURLToPath(new URL('./entry.png', import.meta.url));
  const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
  const destination = join(outputDir, 'entry.png');

  if (!existsSync(source)) {
    fail(`missing input image: ${source}`);
  }

  const bytes = readFileSync(source);
  if (bytes.byteLength > MAX_BYTES) {
    fail(`${bytes.byteLength} bytes exceeds the ${MAX_BYTES}-byte (1 MiB) limit`);
  }
  const header = readPngHeader(bytes, 'entry.png');

  try {
    mkdirSync(outputDir, { recursive: true });
    copyFileSync(source, destination);
  } catch (error) {
    fail(`cannot write ${destination}: ${(error as Error).message}`);
  }

  const copiedBytes = statSync(destination).size;
  if (copiedBytes !== header.byteLength) {
    fail(`copy verification failed: wrote ${copiedBytes} of ${header.byteLength} bytes to ${destination}`);
  }

  console.log(
    `entry.png ${header.width}x${header.height}, ${header.byteLength} bytes -> ${destination}`,
  );
}

main();
