import type { IResolvers } from "mercurius";
import {
  readInventoryData,
  readInventoryDataById,
} from "../Utils.js";

export const InventoryResolvers: IResolvers = {
  InventoryQuery: {
    items: async () => {
      return await readInventoryData();
    },
    itemById: async (_: any, { id }: { id: string | number }) => {
      return await readInventoryDataById(id);
    },
  },
};
