"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { getUser } from "@/lib/auth";

interface Group {
  id: string;
  name: string;
  age_from?: number;
  age_to?: number;
  teacher_id?: string;
}

interface Teacher {
  id: string;
  full_name: string;
}

export default function GroupsPage() {
  const [groups, setGroups] = useState<Group[]>([]);
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", age_from: "", age_to: "", teacher_id: "" });

  function loadData() {
    const user = getUser();
    if (!user?.kindergarten_id) return;
    Promise.all([
      api.get<Group[]>(`/groups/?kg_id=${user.kindergarten_id}`),
      api.get<Teacher[]>(`/users/?kg_id=${user.kindergarten_id}&role=teacher`),
    ]).then(([g, t]) => { setGroups(g); setTeachers(t); }).catch(() => {});
  }

  useEffect(() => { loadData(); }, []);

  const teacherMap = Object.fromEntries(teachers.map((t) => [t.id, t.full_name]));

  async function createGroup() {
    if (!form.name) return;
    const user = getUser();
    await api.post("/groups/", {
      kindergarten_id: user?.kindergarten_id,
      name: form.name,
      age_from: form.age_from ? parseInt(form.age_from) : undefined,
      age_to: form.age_to ? parseInt(form.age_to) : undefined,
      teacher_id: form.teacher_id || undefined,
    });
    loadData();
    setShowForm(false);
    setForm({ name: "", age_from: "", age_to: "", teacher_id: "" });
  }

  async function deleteGroup(id: string) {
    if (!confirm("Удалить группу?")) return;
    await api.delete(`/groups/${id}`);
    setGroups((prev) => prev.filter((g) => g.id !== id));
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Группы</h1>
        <button
          onClick={() => setShowForm(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2 rounded-lg"
        >
          + Создать группу
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {groups.map((group) => (
          <div key={group.id} className="bg-white rounded-xl shadow-sm p-5">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="font-semibold text-gray-800">{group.name}</h3>
                {(group.age_from || group.age_to) && (
                  <p className="text-sm text-gray-400 mt-0.5">
                    Возраст: {group.age_from}–{group.age_to} лет
                  </p>
                )}
                <p className="text-sm text-gray-500 mt-1">
                  👩‍🏫 {group.teacher_id ? teacherMap[group.teacher_id] || "назначен" : "без воспитателя"}
                </p>
              </div>
              <button
                onClick={() => deleteGroup(group.id)}
                className="text-red-400 hover:text-red-600 text-xs"
              >
                Удалить
              </button>
            </div>
          </div>
        ))}
        {groups.length === 0 && (
          <div className="col-span-3 text-center py-12 text-gray-400 text-sm">
            Групп пока нет
          </div>
        )}
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-[400px]">
            <h2 className="text-xl font-bold mb-4">Создать группу</h2>
            <div className="space-y-3">
              <input placeholder="Название группы *" value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                className="w-full border rounded-lg px-3 py-2 text-sm" />
              <div className="grid grid-cols-2 gap-2">
                <input type="number" placeholder="Возраст от" value={form.age_from}
                  onChange={(e) => setForm({ ...form, age_from: e.target.value })}
                  className="border rounded-lg px-3 py-2 text-sm" />
                <input type="number" placeholder="Возраст до" value={form.age_to}
                  onChange={(e) => setForm({ ...form, age_to: e.target.value })}
                  className="border rounded-lg px-3 py-2 text-sm" />
              </div>
              <select value={form.teacher_id}
                onChange={(e) => setForm({ ...form, teacher_id: e.target.value })}
                className="w-full border rounded-lg px-3 py-2 text-sm">
                <option value="">Без воспитателя</option>
                {teachers.map((t) => <option key={t.id} value={t.id}>{t.full_name}</option>)}
              </select>
            </div>
            <div className="flex gap-2 mt-4">
              <button onClick={createGroup}
                className="flex-1 bg-blue-500 text-white rounded-lg py-2 text-sm">Создать</button>
              <button onClick={() => setShowForm(false)}
                className="flex-1 border rounded-lg py-2 text-sm">Отмена</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
