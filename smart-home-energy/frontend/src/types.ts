// src/types.ts
export interface DevicePublic {
    id: string;
    name: string;
    type: string;
    owner_id: string;
  }
  
  export interface HourlyEnergyUsage {
    date: string;
    hour: number;
    total_energy: number;
  }
  
  export interface DeviceStats {
    device_id: string;
    time_period_days: number;
    hourly_usage: HourlyEnergyUsage[];
  }