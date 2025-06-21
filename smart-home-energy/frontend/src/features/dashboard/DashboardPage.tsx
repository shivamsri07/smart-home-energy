// src/features/dashboard/DashboardPage.tsx
import { useEffect, useState } from "react";
import { getDevices } from "@/api/deviceApi";
import { DevicePublic } from "@/types";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { AddDeviceDialog } from "./AddDeviceDialog";
import { toast } from "sonner";
import { Link } from "react-router-dom"; // For making cards clickable

export default function DashboardPage() {
  const [devices, setDevices] = useState<DevicePublic[]>([]);

  const fetchDevices = () => {
    getDevices()
      .then(setDevices)
      .catch(() => toast.error("Could not fetch devices."));
  };

  useEffect(() => {
    fetchDevices();
  }, []);

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold tracking-tight">Your Devices</h2>
        <AddDeviceDialog onDeviceAdded={fetchDevices} />
      </div>

      {devices.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {devices.map((device) => (
            <Link to={`/device/${device.id}`} key={device.id}>
              <Card className="hover:bg-muted/50 transition-colors">
                <CardHeader>
                  <CardTitle>{device.name}</CardTitle>
                  <CardDescription>{device.type}</CardDescription>
                </CardHeader>
              </Card>
            </Link>
          ))}
        </div>
      ) : (
        <p>You have no devices yet. Click "Add New Device" to get started.</p>
      )}
    </div>
  );
}