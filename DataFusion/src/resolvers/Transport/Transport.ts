import type { IResolvers } from "mercurius";
import { readTransportCsv, readTransportCsvById } from "../Utils.js";

export const TransportResolvers: IResolvers = {
  TransportQuery: {
    list: async () => {
      const rows = await readTransportCsv();
      return rows;
    },

    byId: async (_parent, args: { id: string | number }) => {
      return await readTransportCsvById(args.id);
    },

    byStatus: async (_parent, args: { status: string }) => {
      const rows = await readTransportCsv();
      const target = String(args.status).trim().toUpperCase();
      return rows.filter(
        (r) => String(r.status).trim().toUpperCase() === target
      );
    },
  },
};
