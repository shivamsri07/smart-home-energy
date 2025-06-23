// src/features/dashboard/DeviceDetailsPage.tsx
import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { getDeviceStats } from "@/api/deviceApi";
import { DeviceStats, TimeWindow } from "@/types";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { toast } from "sonner";

const TIME_WINDOWS: { label: string; value: TimeWindow }[] = [
  { label: "7 Days", value: "7d" },
  { label: "12 Hours", value: "12h" },
  { label: "6 Hours", value: "6h" },
];

export default function DeviceDetailsPage() {
  const { deviceId } = useParams<{ deviceId: string }>();
  const [stats, setStats] = useState<DeviceStats | null>(null);
  const [selectedTimeWindow, setSelectedTimeWindow] = useState<TimeWindow>("7d");

  useEffect(() => {
    if (deviceId) {
      getDeviceStats(deviceId, selectedTimeWindow)
        .then(setStats)
        .catch(() => toast.error("Could not fetch device stats."));
    }
  }, [deviceId, selectedTimeWindow]);

  if (!stats) return <div>Loading stats...</div>;

  return (
    <div className="space-y-4">
      <h2 className="text-3xl font-bold tracking-tight">Device Energy Usage</h2>
      <p className="text-muted-foreground">
        Energy consumption for device <code className="bg-muted px-2 py-1 rounded">{deviceId}</code>
      </p>

      <div className="flex gap-2">
        {TIME_WINDOWS.map(({ label, value }) => (
          <Button
            key={value}
            variant={selectedTimeWindow === value ? "default" : "outline"}
            onClick={() => setSelectedTimeWindow(value)}
          >
            {label}
          </Button>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Energy Usage (Watts)</CardTitle>
          <CardDescription>
            {selectedTimeWindow === "7d" 
              ? "Daily energy consumption for the last 7 days"
              : `Hourly energy consumption for the last ${selectedTimeWindow === "12h" ? "12" : "6"} hours`}
          </CardDescription>
        </CardHeader>
        <CardContent className="h-[400px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={stats.data_points}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="label" 
                angle={-45}
                textAnchor="end"
                height={80}
                interval={0}
              />
              <YAxis />
              <Tooltip 
                formatter={(value: number) => [`${value.toFixed(2)} Watts`, 'Energy Usage']}
                labelFormatter={(label) => `Time: ${label}`}
              />
              <Legend />
              <Bar dataKey="total_energy" fill="#8884d8" name="Energy Usage (Watts)" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}