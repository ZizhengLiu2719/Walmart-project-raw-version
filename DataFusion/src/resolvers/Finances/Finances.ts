import type { IResolvers } from "mercurius";
import { readFinancesCsv, readFinancesCsvById } from "../Utils.js";

export const FinancesResolvers: IResolvers = {
  FinancesQuery: {
    list: async () => {
      const rows = await readFinancesCsv();
      return rows;
    },

    byId: async (_parent, args: { id: string | number }) => {
      return await readFinancesCsvById(args.id);
    },

    byCategory: async (_parent, args: { category: string }) => {
      const rows = await readFinancesCsv();
      const target = String(args.category).trim().toUpperCase();
      return rows.filter(
        (r) => String(r.category).trim().toUpperCase() === target
      );
    },
  },
};
