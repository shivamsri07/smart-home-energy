// src/features/dashboard/DeviceDetailsPage.tsx
import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { getDeviceStats } from "@/api/deviceApi";
import { DeviceStats } from "@/types";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { toast } from "sonner";

export default function DeviceDetailsPage() {
  const { deviceId } = useParams<{ deviceId: string }>();
  const [stats, setStats] = useState<DeviceStats | null>(null);

  useEffect(() => {
    if (deviceId) {
      getDeviceStats(deviceId)
        .then(setStats)
        .catch(() => toast.error("Could not fetch device stats."));
    }
  }, [deviceId]);

  if (!stats) return <div>Loading stats...</div>;

  const chartData = [
    { name: 'Min Usage', value: stats.min_usage || 0 },
    { name: 'Avg Usage', value: stats.avg_usage || 0 },
    { name: 'Max Usage', value: stats.max_usage || 0 },
  ];

  return (
    <div className="space-y-4">
      <h2 className="text-3xl font-bold tracking-tight">Device Statistics</h2>
      <p className="text-muted-foreground">
        Showing stats for device <code className="bg-muted px-2 py-1 rounded">{deviceId}</code> for the last {stats.time_period_days} days.
      </p>
      <Card>
        <CardHeader>
          <CardTitle>Energy Usage (Watts)</CardTitle>
          <CardDescription>A summary of the device's consumption.</CardDescription>
        </CardHeader>
        <CardContent className="h-[400px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="value" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}