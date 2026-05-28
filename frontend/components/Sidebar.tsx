"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { clearAuth } from "@/lib/auth";

const navItems = [
  { href: "/admin", label: "Дашборд", icon: "🏠" },
  { href: "/admin/groups", label: "Группы", icon: "👥" },
  { href: "/admin/children", label: "Дети", icon: "👶" },
  { href: "/admin/teachers", label: "Воспитатели", icon: "👩‍🏫" },
  { href: "/admin/attendance", label: "Посещаемость", icon: "📋" },
  { href: "/admin/schedule", label: "Расписание", icon: "📅" },
  { href: "/admin/menu", label: "Меню", icon: "🍽️" },
  { href: "/admin/posts", label: "Новости", icon: "📰" },
  { href: "/admin/documents", label: "Документы", icon: "📄" },
  { href: "/admin/settings", label: "Настройки", icon: "⚙️" },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();

  function handleLogout() {
    clearAuth();
    document.cookie = "km_token=; Max-Age=0; path=/";
    router.push("/login");
  }

  return (
    <aside className="w-60 min-h-screen bg-white border-r border-gray-200 flex flex-col">
      <div className="p-6 border-b border-gray-100">
        <h1 className="text-xl font-bold text-blue-600">KinderManager</h1>
        <p className="text-xs text-gray-400 mt-1">Панель управления</p>
      </div>

      <nav className="flex-1 p-3 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href || (item.href !== "/admin" && pathname.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                isActive
                  ? "bg-blue-50 text-blue-700 font-medium"
                  : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
              }`}
            >
              <span className="text-lg">{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="p-3 border-t border-gray-100">
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-red-500 hover:bg-red-50 transition-colors"
        >
          <span className="text-lg">🚪</span>
          Выйти
        </button>
      </div>
    </aside>
  );
}
