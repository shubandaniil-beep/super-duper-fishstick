"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { getUser } from "@/lib/auth";

interface Group {
  id: string;
  name: string;
}

interface ScheduleItem {
  id: string;
  day_of_week: number;
  time_start: string;
  time_end: string;
  subject: string;
  room?: string;
}

const DAYS = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"];
const TIME_SLOTS = ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"];

export default function SchedulePage() {
  const [groups, setGroups] = useState<Group[]>([]);
  const [selectedGroup, setSelectedGroup] = useState("");
  const [items, setItems] = useState<ScheduleItem[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ day_of_week: 1, time_start: "09:00", time_end: "09:30", subject: "", room: "" });

  useEffect(() => {
    const user = getUser();
    if (user?.kindergarten_id) {
      api.get<Group[]>(`/groups/?kg_id=${user.kindergarten_id}`).then(setGroups).catch(() => {});
    }
  }, []);

  useEffect(() => {
    if (!selectedGroup) return;
    api.get<ScheduleItem[]>(`/schedule/?group_id=${selectedGroup}`).then(setItems).catch(() => {});
  }, [selectedGroup]);

  async function addItem() {
    if (!form.subject || !selectedGroup) return;
    await api.post("/schedule/", { ...form, group_id: selectedGroup });
    const updated = await api.get<ScheduleItem[]>(`/schedule/?group_id=${selectedGroup}`);
    setItems(updated);
    setShowForm(false);
    setForm({ day_of_week: 1, time_start: "09:00", time_end: "09:30", subject: "", room: "" });
  }

  async function removeItem(id: string) {
    if (!confirm("Удалить занятие?")) return;
    await api.delete(`/schedule/${id}`);
    setItems((prev) => prev.filter((i) => i.id !== id));
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Расписание</h1>
        {selectedGroup && (
          <button
            onClick={() => setShowForm(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2 rounded-lg"
          >
            + Добавить занятие
          </button>
        )}
      </div>

      <div className="mb-5">
        <select
          value={selectedGroup}
          onChange={(e) => setSelectedGroup(e.target.value)}
          className="border rounded-lg px-3 py-2 text-sm"
        >
          <option value="">Выберите группу</option>
          {groups.map((g) => <option key={g.id} value={g.id}>{g.name}</option>)}
        </select>
      </div>

      {selectedGroup && (
        <div className="bg-white rounded-xl shadow-sm overflow-x-auto">
          <table className="w-full text-sm min-w-[700px]">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-3 py-2 text-left font-medium text-gray-500 w-20">Время</th>
                {DAYS.map((d) => (
                  <th key={d} className="px-3 py-2 text-left font-medium text-gray-500">{d}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {TIME_SLOTS.map((slot) => (
                <tr key={slot} className="hover:bg-gray-50">
                  <td className="px-3 py-2 text-gray-400 text-xs">{slot}</td>
                  {[1, 2, 3, 4, 5].map((day) => {
                    const dayItems = items.filter(
                      (i) => i.day_of_week === day && i.time_start >= slot && i.time_start < TIME_SLOTS[TIME_SLOTS.indexOf(slot) + 1]
                    );
                    return (
                      <td key={day} className="px-3 py-1.5">
                        {dayItems.map((item) => (
                          <div
                            key={item.id}
                            className="bg-blue-50 border border-blue-100 rounded px-2 py-1 mb-1 group relative"
                          >
                            <p className="text-xs font-medium text-blue-700">{item.subject}</p>
                            <p className="text-xs text-blue-400">
                              {item.time_start}–{item.time_end}
                              {item.room && ` · ${item.room}`}
                            </p>
                            <button
                              onClick={() => removeItem(item.id)}
                              className="absolute top-1 right-1 text-red-400 opacity-0 group-hover:opacity-100 text-xs"
                            >
                              ×
                            </button>
                          </div>
                        ))}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-[400px]">
            <h2 className="text-xl font-bold mb-4">Добавить занятие</h2>
            <div className="space-y-3">
              <select
                value={form.day_of_week}
                onChange={(e) => setForm({ ...form, day_of_week: parseInt(e.target.value) })}
                className="w-full border rounded-lg px-3 py-2 text-sm"
              >
                {DAYS.map((d, i) => <option key={i} value={i + 1}>{d}</option>)}
              </select>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-xs text-gray-500">Начало</label>
                  <input type="time" value={form.time_start}
                    onChange={(e) => setForm({ ...form, time_start: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 text-sm mt-1" />
                </div>
                <div>
                  <label className="text-xs text-gray-500">Конец</label>
                  <input type="time" value={form.time_end}
                    onChange={(e) => setForm({ ...form, time_end: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 text-sm mt-1" />
                </div>
              </div>
              <input placeholder="Название занятия *" value={form.subject}
                onChange={(e) => setForm({ ...form, subject: e.target.value })}
                className="w-full border rounded-lg px-3 py-2 text-sm" />
              <input placeholder="Кабинет" value={form.room}
                onChange={(e) => setForm({ ...form, room: e.target.value })}
                className="w-full border rounded-lg px-3 py-2 text-sm" />
            </div>
            <div className="flex gap-2 mt-4">
              <button onClick={addItem}
                className="flex-1 bg-blue-500 text-white rounded-lg py-2 text-sm">Сохранить</button>
              <button onClick={() => setShowForm(false)}
                className="flex-1 border rounded-lg py-2 text-sm">Отмена</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
