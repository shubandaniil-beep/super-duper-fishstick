"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { getUser } from "@/lib/auth";

interface Child {
  id: string;
  first_name: string;
  last_name: string;
}

interface AttRecord {
  child_id: string;
  date: string;
  status: string;
}

interface Group {
  id: string;
  name: string;
}

const STATUS_ICON: Record<string, string> = {
  present: "✅",
  absent_sick: "🤒",
  absent_vacation: "✈️",
  absent_other: "❓",
};

export default function AttendancePage() {
  const [groups, setGroups] = useState<Group[]>([]);
  const [children, setChildren] = useState<Child[]>([]);
  const [records, setRecords] = useState<AttRecord[]>([]);
  const [selectedGroup, setSelectedGroup] = useState("");
  const [month, setMonth] = useState(() => {
    const d = new Date();
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const user = getUser();
    if (user?.kindergarten_id) {
      api.get<Group[]>(`/groups/?kg_id=${user.kindergarten_id}`).then(setGroups).catch(() => {});
    }
  }, []);

  useEffect(() => {
    if (!selectedGroup) return;
    const user = getUser();
    if (!user?.kindergarten_id) return;
    setLoading(true);

    const [year, mon] = month.split("-");
    const dateFrom = `${year}-${mon}-01`;
    const lastDay = new Date(parseInt(year), parseInt(mon), 0).getDate();
    const dateTo = `${year}-${mon}-${String(lastDay).padStart(2, "0")}`;

    Promise.all([
      api.get<Child[]>(`/children/?kg_id=${user.kindergarten_id}&group_id=${selectedGroup}`),
      api.get<AttRecord[]>(`/attendance/report?kg_id=${user.kindergarten_id}&date_from=${dateFrom}&date_to=${dateTo}&group_id=${selectedGroup}`),
    ])
      .then(([c, r]) => { setChildren(c); setRecords(r); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [selectedGroup, month]);

  const [year, mon] = month.split("-");
  const lastDay = new Date(parseInt(year), parseInt(mon), 0).getDate();
  const days = Array.from({ length: lastDay }, (_, i) => i + 1);

  const attMap: Record<string, string> = {};
  records.forEach((r) => {
    const day = parseInt(r.date.split("-")[2]);
    attMap[`${r.child_id}_${day}`] = r.status;
  });

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">Посещаемость</h1>

      <div className="flex gap-3 mb-5">
        <select
          value={selectedGroup}
          onChange={(e) => setSelectedGroup(e.target.value)}
          className="border rounded-lg px-3 py-2 text-sm"
        >
          <option value="">Выберите группу</option>
          {groups.map((g) => <option key={g.id} value={g.id}>{g.name}</option>)}
        </select>
        <input
          type="month"
          value={month}
          onChange={(e) => setMonth(e.target.value)}
          className="border rounded-lg px-3 py-2 text-sm"
        />
      </div>

      {loading && <div className="text-gray-400 text-sm py-4">Загрузка...</div>}

      {!loading && selectedGroup && children.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm overflow-x-auto">
          <table className="text-xs min-w-max">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-3 py-2 text-left font-medium text-gray-500 sticky left-0 bg-gray-50 min-w-[160px]">
                  Ребёнок
                </th>
                {days.map((d) => (
                  <th key={d} className="px-1.5 py-2 text-center font-medium text-gray-400 w-8">{d}</th>
                ))}
                <th className="px-3 py-2 text-center font-medium text-gray-500">Итого</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {children.map((child) => {
                const total = days.filter((d) => attMap[`${child.id}_${d}`]).length;
                const present = days.filter((d) => attMap[`${child.id}_${d}`] === "present").length;
                return (
                  <tr key={child.id} className="hover:bg-gray-50">
                    <td className="px-3 py-2 sticky left-0 bg-white font-medium">
                      {child.last_name} {child.first_name}
                    </td>
                    {days.map((d) => {
                      const status = attMap[`${child.id}_${d}`];
                      return (
                        <td key={d} className="px-1 py-2 text-center">
                          {status ? STATUS_ICON[status] || "?" : <span className="text-gray-200">–</span>}
                        </td>
                      );
                    })}
                    <td className="px-3 py-2 text-center font-medium text-gray-600">
                      {present}/{total}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {!selectedGroup && (
        <div className="text-gray-400 text-sm py-8 text-center">Выберите группу для просмотра</div>
      )}
    </div>
  );
}
