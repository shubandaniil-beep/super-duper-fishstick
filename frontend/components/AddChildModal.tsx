"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { getUser } from "@/lib/auth";

interface Group {
  id: string;
  name: string;
}

interface AddChildModalProps {
  onClose: () => void;
  onSave: () => void;
}

export function AddChildModal({ onClose, onSave }: AddChildModalProps) {
  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    birth_date: "",
    group_id: "",
    gender: "",
    allergies: "",
    medical_notes: "",
  });
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const user = getUser();
    if (user?.kindergarten_id) {
      api.get<Group[]>(`/groups/?kg_id=${user.kindergarten_id}`).then(setGroups).catch(() => {});
    }
  }, []);

  async function handleSubmit() {
    if (!form.first_name || !form.last_name || !form.birth_date || !form.group_id) {
      setError("Заполните обязательные поля");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const user = getUser();
      await api.post("/children/", { ...form, kindergarten_id: user?.kindergarten_id });
      onSave();
      onClose();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-6 w-[520px] max-h-[90vh] overflow-y-auto">
        <h2 className="text-xl font-bold mb-4">Добавить ребёнка</h2>
        {error && <p className="text-red-500 text-sm mb-3">{error}</p>}
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <input
              placeholder="Имя *"
              value={form.first_name}
              onChange={(e) => setForm({ ...form, first_name: e.target.value })}
              className="border rounded-lg px-3 py-2 text-sm"
            />
            <input
              placeholder="Фамилия *"
              value={form.last_name}
              onChange={(e) => setForm({ ...form, last_name: e.target.value })}
              className="border rounded-lg px-3 py-2 text-sm"
            />
          </div>
          <input
            type="date"
            value={form.birth_date}
            onChange={(e) => setForm({ ...form, birth_date: e.target.value })}
            className="w-full border rounded-lg px-3 py-2 text-sm"
          />
          <select
            value={form.group_id}
            onChange={(e) => setForm({ ...form, group_id: e.target.value })}
            className="w-full border rounded-lg px-3 py-2 text-sm"
          >
            <option value="">Выберите группу *</option>
            {groups.map((g) => (
              <option key={g.id} value={g.id}>{g.name}</option>
            ))}
          </select>
          <select
            value={form.gender}
            onChange={(e) => setForm({ ...form, gender: e.target.value })}
            className="w-full border rounded-lg px-3 py-2 text-sm"
          >
            <option value="">Пол</option>
            <option value="M">Мальчик</option>
            <option value="F">Девочка</option>
          </select>
          <textarea
            placeholder="Аллергии (если есть)"
            value={form.allergies}
            onChange={(e) => setForm({ ...form, allergies: e.target.value })}
            className="w-full border rounded-lg px-3 py-2 text-sm"
            rows={2}
          />
          <textarea
            placeholder="Медицинские заметки"
            value={form.medical_notes}
            onChange={(e) => setForm({ ...form, medical_notes: e.target.value })}
            className="w-full border rounded-lg px-3 py-2 text-sm"
            rows={2}
          />
        </div>
        <div className="flex gap-2 mt-4">
          <button
            onClick={handleSubmit}
            disabled={loading}
            className="flex-1 bg-blue-500 hover:bg-blue-600 text-white rounded-lg py-2 text-sm font-medium disabled:opacity-50"
          >
            {loading ? "Сохранение..." : "Сохранить"}
          </button>
          <button
            onClick={onClose}
            className="flex-1 border rounded-lg py-2 text-sm hover:bg-gray-50"
          >
            Отмена
          </button>
        </div>
      </div>
    </div>
  );
}
