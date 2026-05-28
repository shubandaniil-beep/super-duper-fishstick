"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { getUser } from "@/lib/auth";

interface Post {
  id: string;
  type: string;
  title?: string;
  content?: string;
  created_at: string;
  is_sent: boolean;
  group_id?: string;
}

interface Group {
  id: string;
  name: string;
}

const TYPE_LABEL: Record<string, string> = {
  news: "📰 Новость",
  announcement: "📢 Объявление",
  photo: "📸 Фото",
};

export default function PostsPage() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [groups, setGroups] = useState<Group[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ type: "news", title: "", content: "", group_id: "" });

  function loadPosts() {
    const user = getUser();
    if (!user?.kindergarten_id) return;
    api.get<Post[]>(`/posts/?kg_id=${user.kindergarten_id}`).then(setPosts).catch(() => {});
  }

  useEffect(() => {
    loadPosts();
    const user = getUser();
    if (user?.kindergarten_id) {
      api.get<Group[]>(`/groups/?kg_id=${user.kindergarten_id}`).then(setGroups).catch(() => {});
    }
  }, []);

  async function createPost() {
    if (!form.title && !form.content) return;
    const user = getUser();
    await api.post("/posts/", {
      kg_id: user?.kindergarten_id,
      group_id: form.group_id || undefined,
      type: form.type,
      title: form.title || undefined,
      content: form.content || undefined,
    });
    loadPosts();
    setShowForm(false);
    setForm({ type: "news", title: "", content: "", group_id: "" });
  }

  async function deletePost(id: string) {
    if (!confirm("Удалить пост?")) return;
    await api.delete(`/posts/${id}`);
    setPosts((prev) => prev.filter((p) => p.id !== id));
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Новости и объявления</h1>
        <button
          onClick={() => setShowForm(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2 rounded-lg"
        >
          + Создать
        </button>
      </div>

      <div className="space-y-3">
        {posts.map((post) => (
          <div key={post.id} className="bg-white rounded-xl shadow-sm p-4 flex items-start justify-between">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">
                  {TYPE_LABEL[post.type] || post.type}
                </span>
                {post.is_sent && (
                  <span className="text-xs text-green-500">✓ Отправлено</span>
                )}
              </div>
              {post.title && <p className="font-medium text-gray-800">{post.title}</p>}
              {post.content && <p className="text-sm text-gray-500 mt-1 line-clamp-2">{post.content}</p>}
              <p className="text-xs text-gray-400 mt-2">
                {new Date(post.created_at).toLocaleDateString("ru", {
                  day: "numeric", month: "long", year: "numeric"
                })}
              </p>
            </div>
            <button
              onClick={() => deletePost(post.id)}
              className="text-red-400 hover:text-red-600 text-sm ml-4"
            >
              Удалить
            </button>
          </div>
        ))}
        {posts.length === 0 && (
          <div className="text-gray-400 text-sm py-12 text-center bg-white rounded-xl shadow-sm">
            Постов пока нет
          </div>
        )}
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-[500px]">
            <h2 className="text-xl font-bold mb-4">Новый пост</h2>
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-2">
                <select value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })}
                  className="border rounded-lg px-3 py-2 text-sm">
                  <option value="news">📰 Новость</option>
                  <option value="announcement">📢 Объявление</option>
                  <option value="photo">📸 Фото</option>
                </select>
                <select value={form.group_id} onChange={(e) => setForm({ ...form, group_id: e.target.value })}
                  className="border rounded-lg px-3 py-2 text-sm">
                  <option value="">🏫 Всему садику</option>
                  {groups.map((g) => <option key={g.id} value={g.id}>👥 {g.name}</option>)}
                </select>
              </div>
              <input placeholder="Заголовок" value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
                className="w-full border rounded-lg px-3 py-2 text-sm" />
              <textarea placeholder="Текст сообщения" value={form.content}
                onChange={(e) => setForm({ ...form, content: e.target.value })}
                className="w-full border rounded-lg px-3 py-2 text-sm" rows={4} />
            </div>
            <div className="flex gap-2 mt-4">
              <button onClick={createPost}
                className="flex-1 bg-blue-500 text-white rounded-lg py-2 text-sm">
                Опубликовать
              </button>
              <button onClick={() => setShowForm(false)}
                className="flex-1 border rounded-lg py-2 text-sm">
                Отмена
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
