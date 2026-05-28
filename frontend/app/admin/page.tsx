"use client";

import { useEffect, useState } from "react";
import { StatCard } from "@/components/StatCard";
import { AttendanceChart } from "@/components/AttendanceChart";
import { api } from "@/lib/api";
import { getUser } from "@/lib/auth";

interface Stats {
  total_children: number;
  present_today: number;
  absent_today: number;
  total_teachers: number;
  groups_count: number;
  attendance_percent: number;
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const user = getUser();
    if (user?.kindergarten_id) {
      api.get<Stats>(`/stats/?kg_id=${user.kindergarten_id}`)
        .then(setStats)
        .catch(() => {})
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center h-64">
        <div className="text-gray-400 text-sm">Загрузка...</div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Дашборд</h1>
        <p className="text-gray-500 text-sm mt-1">
          {new Date().toLocaleDateString("ru", { weekday: "long", year: "numeric", month: "long", day: "numeric" })}
        </p>
      </div>

      {stats ? (
        <>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <StatCard
              title="Всего детей"
              value={stats.total_children}
              icon="👶"
              color="border-blue-500"
            />
            <StatCard
              title="Сегодня присутствуют"
              value={stats.present_today}
              icon="✅"
              color="border-green-500"
              subtitle={`${stats.attendance_percent}% от записанных`}
            />
            <StatCard
              title="Отсутствуют"
              value={stats.absent_today}
              icon="🤒"
              color="border-red-400"
            />
            <StatCard
              title="Воспитателей"
              value={stats.total_teachers}
              icon="👩‍🏫"
              color="border-purple-500"
              subtitle={`${stats.groups_count} групп`}
            />
          </div>
          <AttendanceChart />
        </>
      ) : (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6 text-sm text-yellow-700">
          Нет данных. Убедитесь, что ваш аккаунт привязан к садику.
        </div>
      )}
    </div>
  );
}
