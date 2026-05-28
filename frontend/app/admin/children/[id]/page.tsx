"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";

interface Child {
  id: string;
  first_name: string;
  last_name: string;
  birth_date: string;
  gender?: string;
  allergies?: string;
  medical_notes?: string;
  group_id: string;
}

interface MedRecord {
  id: string;
  record_type: string;
  title: string;
  description?: string;
  date?: string;
  next_date?: string;
}

function calcAge(bd: string) {
  const today = new Date();
  const b = new Date(bd);
  let age = today.getFullYear() - b.getFullYear();
  if (today < new Date(today.getFullYear(), b.getMonth(), b.getDate())) age--;
  return age;
}

export default function ChildDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [child, setChild] = useState<Child | null>(null);
  const [records, setRecords] = useState<MedRecord[]>([]);

  useEffect(() => {
    api.get<Child>(`/children/${id}`).then(setChild).catch(() => {});
    api.get<MedRecord[]>(`/medical/${id}`).then(setRecords).catch(() => {});
  }, [id]);

  if (!child) return <div className="p-8 text-gray-400">Загрузка...</div>;

  const typeLabel: Record<string, string> = {
    vaccination: "💉 Прививка",
    illness: "🤒 Болезнь",
    checkup: "🔍 Осмотр",
  };

  return (
    <div className="p-8 max-w-2xl">
      <button onClick={() => router.back()} className="text-blue-500 text-sm mb-4 hover:underline">
        ← Назад
      </button>

      <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
        <div className="flex items-start gap-4">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center text-3xl">
            {child.gender === "F" ? "👧" : "👦"}
          </div>
          <div>
            <h1 className="text-2xl font-bold">{child.last_name} {child.first_name}</h1>
            <p className="text-gray-500 text-sm mt-1">
              🎂 {new Date(child.birth_date).toLocaleDateString("ru")} ({calcAge(child.birth_date)} лет)
            </p>
          </div>
        </div>

        <div className="mt-5 space-y-3">
          {child.allergies && (
            <div className="bg-orange-50 border border-orange-100 rounded-lg px-4 py-3 text-sm">
              <span className="font-medium text-orange-700">⚠️ Аллергии:</span>{" "}
              <span className="text-orange-600">{child.allergies}</span>
            </div>
          )}
          {child.medical_notes && (
            <div className="bg-blue-50 border border-blue-100 rounded-lg px-4 py-3 text-sm">
              <span className="font-medium text-blue-700">📝 Медзаметки:</span>{" "}
              <span className="text-blue-600">{child.medical_notes}</span>
            </div>
          )}
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-lg font-semibold mb-4">Медицинская карта</h2>
        {records.length === 0 ? (
          <p className="text-gray-400 text-sm">Записей нет</p>
        ) : (
          <div className="space-y-3">
            {records.map((r) => (
              <div key={r.id} className="border-l-4 border-blue-200 pl-4 py-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">{typeLabel[r.record_type] || r.record_type}</span>
                  <span className="text-xs text-gray-400">{r.date}</span>
                </div>
                <p className="text-sm text-gray-600 mt-0.5">{r.title}</p>
                {r.description && <p className="text-xs text-gray-400 mt-0.5">{r.description}</p>}
                {r.next_date && (
                  <p className="text-xs text-blue-500 mt-0.5">Следующий визит: {r.next_date}</p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
