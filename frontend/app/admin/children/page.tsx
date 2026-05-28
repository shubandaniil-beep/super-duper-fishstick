"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { getUser } from "@/lib/auth";
import { AddChildModal } from "@/components/AddChildModal";

interface Child {
  id: string;
  first_name: string;
  last_name: string;
  birth_date: string;
  group_id: string;
  allergies?: string;
  medical_notes?: string;
  is_active: boolean;
}

interface Group {
  id: string;
  name: string;
}

function calcAge(birthDate: string): number {
  const today = new Date();
  const bd = new Date(birthDate);
  let age = today.getFullYear() - bd.getFullYear();
  if (today < new Date(today.getFullYear(), bd.getMonth(), bd.getDate())) age--;
  return age;
}

export default function ChildrenPage() {
  const [children, setChildren] = useState<Child[]>([]);
  const [groups, setGroups] = useState<Group[]>([]);
  const [search, setSearch] = useState("");
  const [filterGroup, setFilterGroup] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [loading, setLoading] = useState(true);

  function loadData() {
    const user = getUser();
    if (!user?.kindergarten_id) return;
    setLoading(true);
    Promise.all([
      api.get<Child[]>(`/children/?kg_id=${user.kindergarten_id}`),
      api.get<Group[]>(`/groups/?kg_id=${user.kindergarten_id}`),
    ])
      .then(([c, g]) => { setChildren(c); setGroups(g); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }

  useEffect(() => { loadData(); }, []);

  const groupMap = Object.fromEntries(groups.map((g) => [g.id, g.name]));

  const filtered = children.filter((c) => {
    const name = `${c.first_name} ${c.last_name}`.toLowerCase();
    return (
      name.includes(search.toLowerCase()) &&
      (filterGroup === "" || c.group_id === filterGroup)
    );
  });

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Дети</h1>
        <button
          onClick={() => setShowModal(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2 rounded-lg"
        >
          + Добавить ребёнка
        </button>
      </div>

      <div className="flex gap-3 mb-5">
        <input
          placeholder="Поиск по имени..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="border rounded-lg px-3 py-2 text-sm flex-1 max-w-xs"
        />
        <select
          value={filterGroup}
          onChange={(e) => setFilterGroup(e.target.value)}
          className="border rounded-lg px-3 py-2 text-sm"
        >
          <option value="">Все группы</option>
          {groups.map((g) => <option key={g.id} value={g.id}>{g.name}</option>)}
        </select>
      </div>

      {loading ? (
        <div className="text-gray-400 text-sm py-8 text-center">Загрузка...</div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-gray-500">Имя</th>
                <th className="px-4 py-3 text-left font-medium text-gray-500">Возраст</th>
                <th className="px-4 py-3 text-left font-medium text-gray-500">Группа</th>
                <th className="px-4 py-3 text-left font-medium text-gray-500">Аллергии</th>
                <th className="px-4 py-3 text-left font-medium text-gray-500">Действия</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {filtered.map((child) => (
                <tr key={child.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium">
                    {child.last_name} {child.first_name}
                  </td>
                  <td className="px-4 py-3 text-gray-500">{calcAge(child.birth_date)} лет</td>
                  <td className="px-4 py-3 text-gray-500">
                    {groupMap[child.group_id] || "—"}
                  </td>
                  <td className="px-4 py-3 text-gray-500 max-w-xs truncate">
                    {child.allergies ? (
                      <span className="text-orange-500">⚠️ {child.allergies}</span>
                    ) : "—"}
                  </td>
                  <td className="px-4 py-3">
                    <Link
                      href={`/admin/children/${child.id}`}
                      className="text-blue-500 hover:underline text-xs"
                    >
                      Подробнее
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {filtered.length === 0 && (
            <div className="text-center py-8 text-gray-400 text-sm">Дети не найдены</div>
          )}
        </div>
      )}

      {showModal && (
        <AddChildModal onClose={() => setShowModal(false)} onSave={loadData} />
      )}
    </div>
  );
}
