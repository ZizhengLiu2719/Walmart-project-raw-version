export default function JsonParser(jsonText: string): any {
  try {
    return JSON.parse(jsonText);
  } catch (err) {
    throw new Error("JSON parse error: " + String(err));
  }
}
