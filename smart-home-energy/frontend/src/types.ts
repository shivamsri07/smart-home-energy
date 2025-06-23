// src/types.ts
export interface DevicePublic {
    id: string;
    name: string;
    owner_id: string;
  }
  
  export type TimeWindow = "7d" | "12h" | "6h";
  
  export interface EnergyUsagePoint {
    timestamp: string;
    total_energy: number;
    label: string;
  }
  
  export interface DeviceStats {
    device_id: string;
    time_window: TimeWindow;
    data_points: EnergyUsagePoint[];
  }