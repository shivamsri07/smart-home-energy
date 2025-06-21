// src/types.ts
export interface DevicePublic {
    id: string;
    name: string;
    type: string;
    owner_id: string;
  }
  
  export interface DeviceStats {
    device_id: string;
    time_period_days: number;
    max_usage: number | null;
    min_usage: number | null;
    avg_usage: number | null;
  }