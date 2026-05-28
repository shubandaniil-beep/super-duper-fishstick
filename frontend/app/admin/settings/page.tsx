"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { getUser } from "@/lib/auth";

interface KG {
  id: string;
  name: string;
  city?: string;
  address?: string;
  phone?: string;
}

export default function SettingsPage() {
  const [kg, setKg] = useState<KG | null>(null);
  const [form, setForm] = useState({ name: "", city: "", address: "", phone: "" });
  const [saved, setSaved] = useState(false);
  const [inviteCode, setInviteCode] = useState("");
  const [inviteRole, setInviteRole] = useState<"teacher" | "parent">("parent");

  useEffect(() => {
    const user = getUser();
    if (!user?.kindergarten_id) return;
    api.get<KG>(`/kindergartens/${user.kindergarten_id}`).then((data) => {
      setKg(data);
      setForm({ name: data.name, city: data.city || "", address: data.address || "", phone: data.phone || "" });
    }).catch(() => {});
  }, []);

  async function saveSettings() {
    const user = getUser();
    if (!user?.kindergarten_id) return;
    await api.put(`/kindergartens/${user.kindergarten_id}`, form);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  }

  async function generateInvite() {
    const user = getUser();
    const result = await api.post<{ code: string }>("/invites/generate", {
      kg_id: user?.kindergarten_id,
      role: inviteRole,
    });
    setInviteCode(result.code);
  }

  return (
    <div className="p-8 max-w-xl">
      <h1 className="text-2xl font-bold mb-6">Настройки садика</h1>

      <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
        <h2 className="font-semibold text-gray-700 mb-4">Основные данные</h2>
        <div className="space-y-3">
          <div>
            <label className="text-xs text-gray-500 block mb-1">Название садика</label>
            <input value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="w-full border rounded-lg px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="text-xs text-gray-500 block mb-1">Город</label>
            <input value={form.city}
              onChange={(e) => setForm({ ...form, city: e.target.value })}
              className="w-full border rounded-lg px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="text-xs text-gray-500 block mb-1">Адрес</label>
            <input value={form.address}
              onChange={(e) => setForm({ ...form, address: e.target.value })}
              className="w-full border rounded-lg px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="text-xs text-gray-500 block mb-1">Телефон</label>
            <input value={form.phone}
              onChange={(e) => setForm({ ...form, phone: e.target.value })}
              className="w-full border rounded-lg px-3 py-2 text-sm" />
          </div>
        </div>
        <button
          onClick={saveSettings}
          className="mt-4 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2 rounded-lg"
        >
          {saved ? "✓ Сохранено!" : "Сохранить изменения"}
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="font-semibold text-gray-700 mb-4">Пригласительные коды</h2>
        <p className="text-sm text-gray-500 mb-3">
          Сгенерируйте код и передайте его воспитателю или родителю.
          Код действует 7 дней.
        </p>
        <div className="flex gap-2 items-end">
          <div>
            <label className="text-xs text-gray-500 block mb-1">Роль</label>
            <select value={inviteRole} onChange={(e) => setInviteRole(e.target.value as "teacher" | "parent")}
              className="border rounded-lg px-3 py-2 text-sm">
              <option value="teacher">👩‍🏫 Воспитатель</option>
              <option value="parent">👨‍👩‍👧 Родитель</option>
            </select>
          </div>
          <button onClick={generateInvite}
            className="bg-green-500 hover:bg-green-600 text-white text-sm font-medium px-4 py-2 rounded-lg">
            Сгенерировать
          </button>
        </div>

        {inviteCode && (
          <div className="mt-4 bg-green-50 border border-green-200 rounded-xl p-4 flex items-center gap-3">
            <span className="text-3xl font-bold text-green-700 tracking-widest">{inviteCode}</span>
            <div>
              <p className="text-sm text-green-700 font-medium">
                Код для {inviteRole === "teacher" ? "воспитателя" : "родителя"}
              </p>
              <p className="text-xs text-green-500">Передайте этот код через Telegram или лично</p>
            </div>
            <button onClick={() => setInviteCode("")} className="ml-auto text-green-400 text-xl">×</button>
          </div>
        )}
      </div>
    </div>
  );
}
