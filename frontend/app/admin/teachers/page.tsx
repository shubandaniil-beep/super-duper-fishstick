"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { getUser } from "@/lib/auth";

interface Teacher {
  id: string;
  full_name: string;
  phone?: string;
  email?: string;
  telegram_id?: number;
  is_active: boolean;
}

export default function TeachersPage() {
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ full_name: "", phone: "", email: "", password: "" });
  const [inviteCode, setInviteCode] = useState("");

  function loadTeachers() {
    const user = getUser();
    if (!user?.kindergarten_id) return;
    api.get<Teacher[]>(`/users/?kg_id=${user.kindergarten_id}&role=teacher`)
      .then(setTeachers).catch(() => {});
  }

  useEffect(() => { loadTeachers(); }, []);

  async function createTeacher() {
    if (!form.full_name) return;
    const user = getUser();
    await api.post("/users/", {
      ...form,
      role: "teacher",
      kindergarten_id: user?.kindergarten_id,
    });
    loadTeachers();
    setShowForm(false);
    setForm({ full_name: "", phone: "", email: "", password: "" });
  }

  async function generateInvite() {
    const user = getUser();
    const result = await api.post<{ code: string }>("/invites/generate", {
      kg_id: user?.kindergarten_id,
      role: "teacher",
    });
    setInviteCode(result.code);
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Воспитатели</h1>
        <div className="flex gap-2">
          <button
            onClick={generateInvite}
            className="border border-blue-500 text-blue-500 hover:bg-blue-50 text-sm font-medium px-4 py-2 rounded-lg"
          >
            📩 Пригласительный код
          </button>
          <button
            onClick={() => setShowForm(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2 rounded-lg"
          >
            + Добавить
          </button>
        </div>
      </div>

      {inviteCode && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-4 mb-5 flex items-center gap-3">
          <span className="text-2xl font-bold text-green-700 tracking-widest">{inviteCode}</span>
          <div>
            <p className="text-sm text-green-700 font-medium">Код для воспитателя</p>
            <p className="text-xs text-green-500">Действует 7 дней. Отправьте его воспитателю.</p>
          </div>
          <button onClick={() => setInviteCode("")} className="ml-auto text-green-400 text-lg">×</button>
        </div>
      )}

      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="px-4 py-3 text-left font-medium text-gray-500">Имя</th>
              <th className="px-4 py-3 text-left font-medium text-gray-500">Телефон</th>
              <th className="px-4 py-3 text-left font-medium text-gray-500">Email</th>
              <th className="px-4 py-3 text-left font-medium text-gray-500">Telegram</th>
              <th className="px-4 py-3 text-left font-medium text-gray-500">Статус</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {teachers.map((t) => (
              <tr key={t.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium">{t.full_name}</td>
                <td className="px-4 py-3 text-gray-500">{t.phone || "—"}</td>
                <td className="px-4 py-3 text-gray-500">{t.email || "—"}</td>
                <td className="px-4 py-3 text-gray-500">
                  {t.telegram_id ? <span className="text-green-500">✓ Привязан</span> : "—"}
                </td>
                <td className="px-4 py-3">
                  <span className={`text-xs px-2 py-0.5 rounded-full ${t.is_active ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}>
                    {t.is_active ? "Активен" : "Неактивен"}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {teachers.length === 0 && (
          <div className="text-center py-8 text-gray-400 text-sm">Воспитателей нет</div>
        )}
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-[400px]">
            <h2 className="text-xl font-bold mb-4">Добавить воспитателя</h2>
            <div className="space-y-3">
              <input placeholder="ФИО *" value={form.full_name}
                onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                className="w-full border rounded-lg px-3 py-2 text-sm" />
              <input placeholder="Телефон" value={form.phone}
                onChange={(e) => setForm({ ...form, phone: e.target.value })}
                className="w-full border rounded-lg px-3 py-2 text-sm" />
              <input type="email" placeholder="Email" value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                className="w-full border rounded-lg px-3 py-2 text-sm" />
              <input type="password" placeholder="Пароль (если нужен вход)" value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                className="w-full border rounded-lg px-3 py-2 text-sm" />
            </div>
            <div className="flex gap-2 mt-4">
              <button onClick={createTeacher}
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
