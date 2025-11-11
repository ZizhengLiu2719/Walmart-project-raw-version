import { parse } from "csv-parse/sync";

export function parseCsvToJson(csvText: string): Array<Record<string, string>> {
  try {
    const records = parse(csvText, {
      columns: true,
      skip_empty_lines: true,
      trim: true,
    });
    return Array.isArray(records)
      ? (records as Array<Record<string, string>>)
      : [];
  } catch (err) {
    throw new Error("CSV parse error: " + String(err));
  }
}

export function parseCsvToJsonWithColumns(
  csvText: string,
  columns: string[]
): Array<Record<string, string>> {
  try {
    const records = parse(csvText, {
      columns,
      skip_empty_lines: true,
      trim: true,
    });
    return Array.isArray(records)
      ? (records as Array<Record<string, string>>)
      : [];
  } catch (err) {
    throw new Error("CSV parse error: " + String(err));
  }
}
