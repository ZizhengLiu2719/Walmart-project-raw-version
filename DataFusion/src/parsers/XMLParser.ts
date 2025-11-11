import { XMLParser } from "fast-xml-parser";

const parser = new XMLParser();

export default function XmlParser(xmlObjectString: string) {
  try {
    const jsonObj = parser.parse(xmlObjectString);
    return jsonObj;
  } catch (err) {
    throw err;
  }
}
