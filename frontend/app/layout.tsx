import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "KinderManager",
  description: "Система управления детским садом",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body className="bg-gray-50 text-gray-900">{children}</body>
    </html>
  );
}
