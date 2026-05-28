"use client";

import { useEffect, useState } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";

interface DayData {
  date: string;
  present: number;
}

export function AttendanceChart() {
  const [data, setData] = useState<DayData[]>([]);

  useEffect(() => {
    // Mock data for demonstration — replace with real API call
    const today = new Date();
    const mock: DayData[] = Array.from({ length: 20 }, (_, i) => {
      const d = new Date(today);
      d.setDate(d.getDate() - (19 - i));
      return {
        date: d.toLocaleDateString("ru", { day: "numeric", month: "short" }),
        present: Math.floor(Math.random() * 30 + 55),
      };
    });
    setData(mock);
  }, []);

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm">
      <h3 className="text-lg font-semibold mb-4">Посещаемость за месяц</h3>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="date" tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip />
          <Line type="monotone" dataKey="present" stroke="#3b82f6" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
