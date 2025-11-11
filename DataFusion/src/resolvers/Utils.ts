import { fetch } from "undici";
import {
  parseCsvToJson,
  parseCsvToJsonWithColumns,
} from "../parsers/CSVParser.js";
import XmlParser from "../parsers/XMLParser.js";

const env: Record<string, string | undefined> =
  ((globalThis as any).process?.env as Record<string, string | undefined>) ??
  {};

//***************************************** URLs *******************************************
export const BASE_NWS = env.NWS_BASE ?? "http://localhost:8081";
export const BASE_FINANCES = env.FINANCES_BASE ?? "http://localhost:8085";
export const BASE_TRANSPORT = env.TRANSPORT_BASE ?? "http://localhost:8084";
//***************************************** URLs *******************************************

/**
 * Given an endpoint, the function will fetch and parse XML into a JSON object.
 * @param url
 * @returns
 */
export async function fetchAndParseXML(url: string): Promise<any> {
  const response = await fetch(url);
  const text = await response.text();

  const contentType = (
    response.headers.get("content-type") ?? ""
  ).toLowerCase();
  if (contentType.includes("json")) {
    try {
      return JSON.parse(text);
    } catch (err) {
      throw new Error("Invalid JSON from upstream: " + String(err));
    }
  }

  if (!contentType.includes("xml") && !text.trim().startsWith("<")) {
    throw new Error("Content Type is not XML or JSON: " + String(contentType));
  }

  try {
    return XmlParser(text);
  } catch (err) {
    throw new Error("XML parse error: " + String(err));
  }
}

// Preferred: fetch CSV via DataProvider HTTP services
export async function fetchFinancesCsvText(): Promise<string> {
  const res = await fetch(`${BASE_FINANCES}/finances`);
  if (!res.ok) throw new Error(`Finances HTTP ${res.status}`);
  return await res.text();
}

export async function fetchTransportCsvText(): Promise<string> {
  const res = await fetch(`${BASE_TRANSPORT}/transport`);
  if (!res.ok) throw new Error(`Transport HTTP ${res.status}`);
  return await res.text();
}

export async function fetchFinancesCsvTextById(
  id: string | number
): Promise<string> {
  const res = await fetch(
    `${BASE_FINANCES}/finances/${encodeURIComponent(String(id))}`
  );
  if (!res.ok) throw new Error(`Finances byId HTTP ${res.status}`);
  return await res.text();
}

export async function fetchTransportCsvTextById(
  id: string | number
): Promise<string> {
  const res = await fetch(
    `${BASE_TRANSPORT}/transport/${encodeURIComponent(String(id))}`
  );
  if (!res.ok) throw new Error(`Transport byId HTTP ${res.status}`);
  return await res.text();
}

export async function readFinancesCsv(filePath?: string): Promise<
  Array<{
    id: string;
    transactionDate: string;
    description: string;
    amount: number | null;
    currency: string;
    category: string;
  }>
> {
  const csv = await fetchFinancesCsvText();
  let rows: Array<Record<string, any>> = await parseCsvToJson(csv);
  if (rows.length === 0 || rows[0].id === undefined) {
    rows = await parseCsvToJsonWithColumns(csv, [
      "id",
      "transactionDate",
      "description",
      "amount",
      "currency",
      "category",
    ]);
  }
  return rows.map((row) => ({
    id: String(row.id),
    transactionDate: String(row.transactionDate),
    description: String(row.description ?? ""),
    amount:
      row.amount !== undefined && row.amount !== null
        ? Number(row.amount)
        : null,
    currency: String(row.currency ?? ""),
    category: String(row.category ?? ""),
  }));
}

export async function readTransportCsv(filePath?: string): Promise<
  Array<{
    id: string;
    vehicleType: string;
    origin: string;
    destination: string;
    departureTime: string;
    arrivalTime: string;
    status: string;
    area: string;
  }>
> {
  const csv = await fetchTransportCsvText();
  let rows: Array<Record<string, any>> = await parseCsvToJson(csv);
  if (rows.length === 0 || rows[0].id === undefined) {
    rows = await parseCsvToJsonWithColumns(csv, [
      "id",
      "vehicleType",
      "origin",
      "destination",
      "departureTime",
      "arrivalTime",
      "status",
      "area",
    ]);
  }
  return rows.map((row) => ({
    id: String(row.id),
    vehicleType: String(row.vehicleType ?? ""),
    origin: String(row.origin ?? ""),
    destination: String(row.destination ?? ""),
    departureTime: String(row.departureTime ?? ""),
    arrivalTime: String(row.arrivalTime ?? ""),
    status: String(row.status ?? ""),
    area: String(row.area ?? ""),
  }));
}

export async function readFinancesCsvById(
  id: string | number,
  filePath?: string
): Promise<{
  id: string;
  transactionDate: string;
  description: string;
  amount: number | null;
  currency: string;
  category: string;
} | null> {
  try {
    const csv = await fetchFinancesCsvTextById(id);
    let rows: Array<Record<string, any>> = await parseCsvToJson(csv);
    if (rows.length === 0 || rows[0].id === undefined) {
      rows = await parseCsvToJsonWithColumns(csv, [
        "id",
        "transactionDate",
        "description",
        "amount",
        "currency",
        "category",
      ]);
    }
    const first = rows[0];
    if (!first) return null;
    return {
      id: String(first.id),
      transactionDate: String(first.transactionDate),
      description: String(first.description ?? ""),
      amount:
        first.amount !== undefined && first.amount !== null
          ? Number(first.amount)
          : null,
      currency: String(first.currency ?? ""),
      category: String(first.category ?? ""),
    };
  } catch (_e) {
    // As a last resort, fetch all and filter in-memory
    const rows = await readFinancesCsv(filePath);
    return rows.find((r) => String(r.id) === String(id)) ?? null;
  }
}

export async function readTransportCsvById(
  id: string | number,
  filePath?: string
): Promise<{
  id: string;
  vehicleType: string;
  origin: string;
  destination: string;
  departureTime: string;
  arrivalTime: string;
  status: string;
  area: string;
} | null> {
  try {
    const csv = await fetchTransportCsvTextById(id);
    let rows: Array<Record<string, any>> = await parseCsvToJson(csv);
    if (rows.length === 0 || rows[0].id === undefined) {
      rows = await parseCsvToJsonWithColumns(csv, [
        "id",
        "vehicleType",
        "origin",
        "destination",
        "departureTime",
        "arrivalTime",
        "status",
        "area",
      ]);
    }
    const first = rows[0];
    if (!first) return null;
    return {
      id: String(first.id),
      vehicleType: String(first.vehicleType ?? ""),
      origin: String(first.origin ?? ""),
      destination: String(first.destination ?? ""),
      departureTime: String(first.departureTime ?? ""),
      arrivalTime: String(first.arrivalTime ?? ""),
      status: String(first.status ?? ""),
      area: String(first.area ?? ""),
    };
  } catch (_e) {
    // As a last resort, fetch all and filter in-memory
    const rows = await readTransportCsv(filePath);
    return rows.find((r) => String(r.id) === String(id)) ?? null;
  }
}

//-------------------// Warehouse YAML //-------------------//
import { yamlToJson } from "../parsers/YAMLParser.js";

export const BASE_WAREHOUSE = env.WAREHOUSE_BASE ?? "http://localhost:8004";

/**
 * Fetch raw YAML text from the Warehouse provider endpoint.
 */
export async function fetchWarehouseYamlText(): Promise<string> {
  const res = await fetch(`${BASE_WAREHOUSE}/warehouses`);
  if (!res.ok) throw new Error(`Warehouse HTTP ${res.status}`);
  return await res.text();
}

/**
 * Read and parse warehouse YAML into a normalized array of warehouse objects.
 * Attempts to handle several common shapes returned by providers:
 *  - an array of warehouses
 *  - { warehouses: [...] }
 *  - a single warehouse object
 */
export async function readWarehouseData(): Promise<Array<any>> {
  const text = await fetchWarehouseYamlText();
  try {
    const parsed = yamlToJson(text);
    if (Array.isArray(parsed)) return parsed;
    if (parsed && Array.isArray(parsed.warehouses)) return parsed.warehouses;
    if (parsed && typeof parsed === "object") return [parsed];
    return [];
  } catch (err) {
    throw new Error("YAML parse error: " + String(err));
  }
}

//----------------------------------------------------------//
//-------------------// Generic JSON Parser //-------------------//
// -------------------// Employees JSON //-------------------//
export const BASE_EMPLOYEES = env.EMPLOYEES_BASE ?? "http://localhost:8001";

/**
 * Fetch all employees (JSON array)
 */
export async function readEmployeesData(): Promise<Array<any>> {
  try {
    const res = await fetch(`${BASE_EMPLOYEES}/employees`);
    if (!res.ok) throw new Error(`Employees HTTP ${res.status}`);
    const data = await res.json();
    return Array.isArray(data) ? data : [];
  } catch (err) {
    throw new Error("Employees fetch/parse error: " + String(err));
  }
}

/**
 * Fetch a single employee by ID
 */
export async function readEmployeesDataById(
  id: string | number
): Promise<any | null> {
  try {
    const res = await fetch(`${BASE_EMPLOYEES}/employees/${id}`);
    if (!res.ok) {
      if (res.status === 404) return null;
      throw new Error(`Employees byId HTTP ${res.status}`);
    }
    return await res.json();
  } catch (err) {
    throw new Error("Employees fetchById error: " + String(err));
  }
}

// -------------------// Inventory JSON //-------------------//
export const BASE_INVENTORY = env.INVENTORY_BASE ?? "http://localhost:8002";

/**
 * Fetch all inventory items (JSON array)
 */
export async function readInventoryData(): Promise<Array<any>> {
  try {
    const res = await fetch(`${BASE_INVENTORY}/inventory`);
    if (!res.ok) throw new Error(`Inventory HTTP ${res.status}`);
    const data = await res.json();
    return Array.isArray(data) ? data : [];
  } catch (err) {
    throw new Error("Inventory fetch/parse error: " + String(err));
  }
}

/**
 * Fetch a single inventory item by ID
 */
export async function readInventoryDataById(
  id: string | number
): Promise<any | null> {
  try {
    const res = await fetch(`${BASE_INVENTORY}/inventory/${id}`);
    if (!res.ok) {
      if (res.status === 404) return null;
      throw new Error(`Inventory byId HTTP ${res.status}`);
    }
    return await res.json();
  } catch (err) {
    throw new Error("Inventory fetchById error: " + String(err));
  }
}
