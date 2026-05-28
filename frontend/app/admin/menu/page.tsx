"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { getUser } from "@/lib/auth";

interface MenuItem {
  id: string;
  meal_type: string;
  description: string;
  calories?: number;
  date: string;
}

const MEAL_LABELS: Record<string, string> = {
  breakfast: "🌅 Завтрак",
  lunch: "🌞 Обед",
  snack: "☕ Полдник",
  dinner: "🌙 Ужин",
};

const MEAL_ORDER = ["breakfast", "lunch", "snack", "dinner"];

export default function MenuPage() {
  const [items, setItems] = useState<MenuItem[]>([]);
  const [date, setDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ meal_type: "breakfast", description: "", calories: "" });

  function loadMenu(d: string) {
    const user = getUser();
    if (!user?.kindergarten_id) return;
    api.get<MenuItem[]>(`/menu/?kg_id=${user.kindergarten_id}&target_date=${d}`)
      .then(setItems).catch(() => {});
  }

  useEffect(() => { loadMenu(date); }, [date]);

  async function addItem() {
    if (!form.description) return;
    const user = getUser();
    await api.post("/menu/", {
      kg_id: user?.kindergarten_id,
      date,
      meal_type: form.meal_type,
      description: form.description,
      calories: form.calories ? parseInt(form.calories) : undefined,
    });
    loadMenu(date);
    setShowForm(false);
    setForm({ meal_type: "breakfast", description: "", calories: "" });
  }

  async function removeItem(id: string) {
    await api.delete(`/menu/${id}`);
    setItems((prev) => prev.filter((i) => i.id !== id));
  }

  return (
    <div className="p-8 max-w-2xl">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Меню питания</h1>
        <button
          onClick={() => setShowForm(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2 rounded-lg"
        >
          + Добавить
        </button>
      </div>

      <div className="flex items-center gap-3 mb-6">
        <input type="date" value={date} onChange={(e) => setDate(e.target.value)}
          className="border rounded-lg px-3 py-2 text-sm" />
      </div>

      <div className="space-y-4">
        {MEAL_ORDER.filter((mt) => items.some((i) => i.meal_type === mt)).map((mt) => (
          <div key={mt} className="bg-white rounded-xl shadow-sm p-4">
            <h3 className="font-semibold text-gray-700 mb-3">{MEAL_LABELS[mt]}</h3>
            <div className="space-y-2">
              {items.filter((i) => i.meal_type === mt).map((item) => (
                <div key={item.id} className="flex items-start justify-between group">
                  <div>
                    <p className="text-sm">{item.description}</p>
                    {item.calories && <p className="text-xs text-gray-400">{item.calories} ккал</p>}
                  </div>
                  <button
                    onClick={() => removeItem(item.id)}
                    className="text-red-400 text-xs opacity-0 group-hover:opacity-100 ml-4"
                  >
                    Удалить
                  </button>
                </div>
              ))}
            </div>
          </div>
        ))}
        {items.length === 0 && (
          <div className="text-gray-400 text-sm py-8 text-center bg-white rounded-xl shadow-sm">
            Меню на эту дату не добавлено
          </div>
        )}
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-[400px]">
            <h2 className="text-xl font-bold mb-4">Добавить блюдо</h2>
            <div className="space-y-3">
              <select value={form.meal_type}
                onChange={(e) => setForm({ ...form, meal_type: e.target.value })}
                className="w-full border rounded-lg px-3 py-2 text-sm">
                {Object.entries(MEAL_LABELS).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
              </select>
              <textarea placeholder="Описание *" value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                className="w-full border rounded-lg px-3 py-2 text-sm" rows={3} />
              <input type="number" placeholder="Калорийность (ккал)" value={form.calories}
                onChange={(e) => setForm({ ...form, calories: e.target.value })}
                className="w-full border rounded-lg px-3 py-2 text-sm" />
            </div>
            <div className="flex gap-2 mt-4">
              <button onClick={addItem} className="flex-1 bg-blue-500 text-white rounded-lg py-2 text-sm">
                Сохранить
              </button>
              <button onClick={() => setShowForm(false)} className="flex-1 border rounded-lg py-2 text-sm">
                Отмена
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
