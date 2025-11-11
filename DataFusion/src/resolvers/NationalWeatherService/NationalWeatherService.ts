import type { IResolvers } from "mercurius";
import { fetchAndParseXML, BASE_NWS } from "../Utils.js";

export const NationalWeatherServiceResolvers: IResolvers = {
  // Name must match the GraphQL object type in your SDL
  NationalWeatherServiceQuery: {
    alertList: async () => {
      const doc = await fetchAndParseXML(`${BASE_NWS}/weather-alert`);
      if (doc?.WeatherAlerts) return doc.WeatherAlerts;
      if (doc?.WeatherAlert) {
        return {
          WeatherAlert: Array.isArray(doc.WeatherAlert)
            ? doc.WeatherAlert
            : [doc.WeatherAlert],
        };
      }
      return null;
    },

    alertById: async (_parent, args: { id: number }) => {
      const doc = await fetchAndParseXML(
        `${BASE_NWS}/weather-alert?id=${args.id}`
      );
      if (doc?.WeatherAlert) {
        return Array.isArray(doc.WeatherAlert)
          ? doc.WeatherAlert[0]
          : doc.WeatherAlert;
      }
      if (doc?.Event) return doc;
      return null;
    },
  },
};
