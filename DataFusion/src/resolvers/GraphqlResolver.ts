import type { IResolvers, MercuriusContext } from "mercurius";
import { FinancesResolvers } from "./Finances/Finances.js";
import { NationalWeatherServiceResolvers } from "./NationalWeatherService/NationalWeatherService.js";
import { TransportResolvers } from "./Transport/Transport.js";
import { WarehouseResolvers } from "./Warehouse/Warehouse.js";
import { EmployeesResolvers } from "./Employees/Employees.js";
import { InventoryResolvers } from "./Inventory/Inventory.js";

export interface AppContext extends MercuriusContext {
  requestId?: string;
  user?: { id: string } | null;
}

const QueryResolvers: IResolvers = {
  Query: {
    NationalWeatherService: () => ({}),
    Finances: () => ({}),
    Transport: () => ({}),
    Warehouse: () => ({}),
    Employees: () => ({}),
    Inventory: () => ({}),
  },
};

export const Resolvers: IResolvers = {
  ...QueryResolvers,

  // spread provider-specific nested type resolvers
  ...NationalWeatherServiceResolvers,
  ...FinancesResolvers,
  ...TransportResolvers,
  ...WarehouseResolvers,
  ...EmployeesResolvers,
  ...InventoryResolvers,
  // Spread additional data providers here:
  // ...OtherProviderResolvers,
};
