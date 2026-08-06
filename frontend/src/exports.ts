import type { GraphDataset } from "./types.js";

function downloadBlob(filename: string, blob: Blob): void {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function matrixCellToOriginalText(cell: unknown): string {
  if (Array.isArray(cell)) {
    return `[${cell.map((value) => String(Number(value))).join(", ")}]`;
  }

  if (typeof cell === "number") {
    return String(cell);
  }

  const numericValue = Number(cell);
  return Number.isFinite(numericValue) ? String(numericValue) : String(cell ?? 0);
}

function formatMatrixLikeNumpy(matrix: unknown[][]): string {
  const containsLists = matrix.some((row) => row.some((cell) => Array.isArray(cell)));

  if (containsLists) {
    const rows = matrix.map(
      (row) => `[${row.map(matrixCellToOriginalText).join(", ")}]`,
    );
    return `[${rows.join(", ")}]`;
  }

  return matrix
    .map((row, index) => {
      const prefix = index === 0 ? "[[" : " [";
      const suffix = index === matrix.length - 1 ? "]]" : "]";
      return `${prefix}${row.map(matrixCellToOriginalText).join(" ")}${suffix}`;
    })
    .join("\n");
}

function formatAdjacencyListLikeOriginal(matrix: unknown[][]): string {
  return matrix
    .map((row, vertex) => {
      const entries: string[] = [];

      row.forEach((cell, target) => {
        if (Array.isArray(cell)) {
          cell.forEach((weight) => {
            entries.push(`(${target}, ${String(Number(weight))})`);
          });
          return;
        }

        const value = Number(cell);
        if (Number.isFinite(value) && value > 0) {
          entries.push(`(${target}, ${String(value)})`);
        }
      });

      return `${vertex}: [${entries.join(", ")}]`;
    })
    .join("\n");
}

function formatDatasetAsOriginalTxt(dataset: GraphDataset): string {
  const matrixRows = dataset.adjacency_matrix
    .map((row) => row.map(matrixCellToOriginalText).join(" "))
    .join("\n");

  return [
    `numV: ${dataset.number_vertices}, numA: ${dataset.number_edges}, seed: ${dataset.seed}, n: ${dataset.id}`,
    matrixRows,
    formatMatrixLikeNumpy(dataset.adjacency_matrix),
    formatAdjacencyListLikeOriginal(dataset.adjacency_matrix),
  ].join("\n");
}

export function exportDatasetTxt(dataset: GraphDataset): void {
  downloadBlob(
    `${dataset.name}.txt`,
    new Blob([formatDatasetAsOriginalTxt(dataset)], {
      type: "text/plain;charset=utf-8",
    }),
  );
}

export function exportAllDatasetsTxt(datasets: GraphDataset[]): void {
  const content = datasets.map(formatDatasetAsOriginalTxt).join("\n\n");
  downloadBlob(
    "todos-os-datasets.txt",
    new Blob([content], { type: "text/plain;charset=utf-8" }),
  );
}

export async function exportImagePng(
  imageUrl: string,
  filename: string,
): Promise<void> {
  const response = await fetch(imageUrl);
  if (!response.ok) {
    throw new Error("Não foi possível baixar a imagem gerada.");
  }
  const blob = await response.blob();
  downloadBlob(`${filename}.png`, blob);
}

interface ZipEntry {
  filename: string;
  data: Uint8Array;
  crc32: number;
  offset: number;
}

const CRC_TABLE = (() => {
  const table = new Uint32Array(256);
  for (let index = 0; index < 256; index += 1) {
    let value = index;
    for (let bit = 0; bit < 8; bit += 1) {
      value = (value & 1) !== 0
        ? 0xedb88320 ^ (value >>> 1)
        : value >>> 1;
    }
    table[index] = value >>> 0;
  }
  return table;
})();

function calculateCrc32(data: Uint8Array): number {
  let crc = 0xffffffff;
  for (const byte of data) {
    const tableValue = CRC_TABLE[(crc ^ byte) & 0xff] ?? 0;
    crc = tableValue ^ (crc >>> 8);
  }
  return (crc ^ 0xffffffff) >>> 0;
}

function getDosDateTime(date = new Date()): { time: number; day: number } {
  const year = Math.max(1980, date.getFullYear());
  const time =
    (date.getHours() << 11) |
    (date.getMinutes() << 5) |
    Math.floor(date.getSeconds() / 2);
  const day =
    ((year - 1980) << 9) |
    ((date.getMonth() + 1) << 5) |
    date.getDate();
  return { time, day };
}

function concatenateArrays(arrays: Uint8Array[]): Uint8Array {
  const totalLength = arrays.reduce((total, array) => total + array.length, 0);
  const result = new Uint8Array(totalLength);
  let offset = 0;
  for (const array of arrays) {
    result.set(array, offset);
    offset += array.length;
  }
  return result;
}

function createStoredZip(files: Array<{ filename: string; data: Uint8Array }>): Blob {
  const encoder = new TextEncoder();
  const { time, day } = getDosDateTime();
  const localParts: Uint8Array[] = [];
  const entries: ZipEntry[] = [];
  let currentOffset = 0;

  for (const file of files) {
    const filenameBytes = encoder.encode(file.filename);
    const crc32 = calculateCrc32(file.data);
    const header = new Uint8Array(30);
    const view = new DataView(header.buffer);

    view.setUint32(0, 0x04034b50, true);
    view.setUint16(4, 20, true);
    view.setUint16(6, 0x0800, true);
    view.setUint16(8, 0, true);
    view.setUint16(10, time, true);
    view.setUint16(12, day, true);
    view.setUint32(14, crc32, true);
    view.setUint32(18, file.data.length, true);
    view.setUint32(22, file.data.length, true);
    view.setUint16(26, filenameBytes.length, true);
    view.setUint16(28, 0, true);

    localParts.push(header, filenameBytes, file.data);
    entries.push({
      filename: file.filename,
      data: file.data,
      crc32,
      offset: currentOffset,
    });
    currentOffset += header.length + filenameBytes.length + file.data.length;
  }

  const centralParts: Uint8Array[] = [];
  let centralSize = 0;

  for (const entry of entries) {
    const filenameBytes = encoder.encode(entry.filename);
    const header = new Uint8Array(46);
    const view = new DataView(header.buffer);

    view.setUint32(0, 0x02014b50, true);
    view.setUint16(4, 20, true);
    view.setUint16(6, 20, true);
    view.setUint16(8, 0x0800, true);
    view.setUint16(10, 0, true);
    view.setUint16(12, time, true);
    view.setUint16(14, day, true);
    view.setUint32(16, entry.crc32, true);
    view.setUint32(20, entry.data.length, true);
    view.setUint32(24, entry.data.length, true);
    view.setUint16(28, filenameBytes.length, true);
    view.setUint16(30, 0, true);
    view.setUint16(32, 0, true);
    view.setUint16(34, 0, true);
    view.setUint16(36, 0, true);
    view.setUint32(38, 0, true);
    view.setUint32(42, entry.offset, true);

    centralParts.push(header, filenameBytes);
    centralSize += header.length + filenameBytes.length;
  }

  const endRecord = new Uint8Array(22);
  const endView = new DataView(endRecord.buffer);
  endView.setUint32(0, 0x06054b50, true);
  endView.setUint16(4, 0, true);
  endView.setUint16(6, 0, true);
  endView.setUint16(8, entries.length, true);
  endView.setUint16(10, entries.length, true);
  endView.setUint32(12, centralSize, true);
  endView.setUint32(16, currentOffset, true);
  endView.setUint16(20, 0, true);

  const zipData = concatenateArrays([...localParts, ...centralParts, endRecord]);
  return new Blob([zipData], { type: "application/zip" });
}

export async function exportAllImagesPng(datasets: GraphDataset[]): Promise<void> {
  const files: Array<{ filename: string; data: Uint8Array }> = [];

  for (const dataset of datasets) {
    if (!dataset.image_url) continue;

    const response = await fetch(dataset.image_url);
    if (!response.ok) {
      throw new Error(`Não foi possível baixar a imagem do dataset ${dataset.id}.`);
    }

    const data = new Uint8Array(await response.arrayBuffer());
    files.push({ filename: `${dataset.name}.png`, data });
  }

  if (files.length === 0) {
    throw new Error("Nenhuma imagem foi encontrada para exportação.");
  }

  downloadBlob("todos-os-datasets-png.zip", createStoredZip(files));
}
