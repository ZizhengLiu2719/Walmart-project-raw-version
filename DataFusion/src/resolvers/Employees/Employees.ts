import type { IResolvers } from "mercurius";
import {
  readEmployeesData,
  readEmployeesDataById,
} from "../Utils.js";

export const EmployeesResolvers: IResolvers = {
  EmployeesQuery: {
    employees: async () => {
      return await readEmployeesData();
    },
    employeeById: async (_: any, { id }: { id: string | number }) => {
      return await readEmployeesDataById(id);
    },
  },
};
