// src/api/deviceApi.ts
import api from '@/lib/axios';
import { DevicePublic, DeviceStats, TimeWindow } from '@/types'; // We will define these types

export const getDevices = async (): Promise<DevicePublic[]> => {
  const response = await api.get('/devices/');
  return response.data;
};

export const createDevice = async (name: string, type: string = "APPLIANCE"): Promise<DevicePublic> => {
  const response = await api.post('/devices/', { name, type });
  return response.data;
};

export const getDeviceStats = async (deviceId: string, timeWindow: TimeWindow): Promise<DeviceStats> => {
  const response = await api.get(`/devices/${deviceId}/stats?time_window=${timeWindow}`);
  return response.data;
};