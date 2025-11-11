import type { IResolvers } from "mercurius";
import { readWarehouseData } from "../Utils.js";

export const WarehouseResolvers: IResolvers = {
  WarehouseQuery: {
    warehouses: async () => {
      const rows = await readWarehouseData();

      // Normalize provider fields to match GraphQL types in src/schemas/providers/Warehouse.graphql
      return rows.map((w: any) => ({
        id: String(w.id ?? w.warehouse_id ?? w.warehouseId ?? ""),
        name: String(w.name ?? w.title ?? ""),
        location: String(w.location ?? w.address ?? ""),
        last_updated: String(
          w.last_updated ?? w.lastUpdated ?? w.lastUpdate ?? ""
        ),
        inventory: Array.isArray(w.inventory)
          ? w.inventory.map((it: any) => ({
              id: String(it.id ?? it.item_id ?? it.itemId ?? ""),
              name: String(it.name ?? it.title ?? ""),
              category: String(it.category ?? ""),
              quantity: Number(it.quantity ?? it.qty ?? 0),
              unit_price: Number(
                it.unit_price ?? it.unitPrice ?? it.price ?? 0
              ),
              supplier: String(it.supplier ?? ""),
              restock_date: String(
                it.restock_date ?? it.restockDate ?? it.restock ?? ""
              ),
            }))
          : [],
      }));
    },
    warehouseById: async (_parent, args: { id: string }) => {
      const rows = await readWarehouseData();

      // Accept either string or number id in args; normalize to string for comparison
      const requestedId = args?.id != null ? String(args.id) : null;

      if (!requestedId) return null;

      // Find the warehouse that matches the requested id. Accept matches against
      // common provider id fields (id, warehouse_id, warehouseId).
      const match = rows.find((w: any) => {
        const candidateIds = [w.id, w.warehouse_id, w.warehouseId];
        return candidateIds.some((c: any) => String(c ?? "") === requestedId);
      });

      if (!match) return null;

      // Normalize the matched warehouse to the same shape as the `warehouses` resolver
      return {
        id: String(match.id ?? match.warehouse_id ?? match.warehouseId ?? ""),
        name: String(match.name ?? match.title ?? ""),
        location: String(match.location ?? match.address ?? ""),
        last_updated: String(
          match.last_updated ?? match.lastUpdated ?? match.lastUpdate ?? ""
        ),
        inventory: Array.isArray(match.inventory)
          ? match.inventory.map((it: any) => ({
              id: String(it.id ?? it.item_id ?? it.itemId ?? ""),
              name: String(it.name ?? it.title ?? ""),
              category: String(it.category ?? ""),
              quantity: Number(it.quantity ?? it.qty ?? 0),
              unit_price: Number(
                it.unit_price ?? it.unitPrice ?? it.price ?? 0
              ),
              supplier: String(it.supplier ?? ""),
              restock_date: String(
                it.restock_date ?? it.restockDate ?? it.restock ?? ""
              ),
            }))
          : [],
      };
    },
  },
};

export default WarehouseResolvers;
