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

  // Transform hourly usage data for the chart
  const chartData = stats.hourly_usage.map(hour => ({
    time: `${new Date(hour.date).toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric' 
    })} ${hour.hour}:00`,
    energy: hour.total_energy,
    hour: hour.hour,
    date: hour.date
  }));

  return (
    <div className="space-y-4">
      <h2 className="text-3xl font-bold tracking-tight">Device Energy Usage</h2>
      <p className="text-muted-foreground">
        Hourly energy consumption for device <code className="bg-muted px-2 py-1 rounded">{deviceId}</code> over the last {stats.time_period_days} days.
      </p>
      <Card>
        <CardHeader>
          <CardTitle>Hourly Energy Usage (Watts)</CardTitle>
          <CardDescription>Total energy consumption per hour.</CardDescription>
        </CardHeader>
        <CardContent className="h-[400px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="time" 
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
              <Bar dataKey="energy" fill="#8884d8" name="Energy Usage (Watts)" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}