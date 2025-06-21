// src/api/deviceApi.ts
import api from '@/lib/axios';
import { DevicePublic, DeviceStats } from '@/types'; // We will define these types

export const getDevices = async (): Promise<DevicePublic[]> => {
  const response = await api.get('/devices/');
  return response.data;
};

export const createDevice = async (name: string, type: string = "APPLIANCE"): Promise<DevicePublic> => {
  const response = await api.post('/devices/', { name, type });
  return response.data;
};

export const getDeviceStats = async (deviceId: string, days: number = 7): Promise<DeviceStats> => {
  const response = await api.get(`/devices/${deviceId}/stats?days=${days}`);
  return response.data;
};