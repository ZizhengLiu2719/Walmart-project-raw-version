import http from 'http';
import yaml from 'js-yaml';

export function yamlToJson(yamlString: string): any {
    try {
        return yaml.load(yamlString);
    }
    catch (error) {
      throw error;
    }
}

export function jsonToYaml(jsonString: string): string {
    try {
        const jsonObj = JSON.parse(jsonString); // Parse the JSON string back to an object

        return yaml.dump(jsonObj);
    }
    catch (error) {
      throw error;
    }
}