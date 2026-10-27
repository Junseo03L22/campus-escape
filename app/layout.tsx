import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "출튀 대작전",
  description: "교수님의 시선을 피해 탈출하고 단계별 온라인 순위에 도전하세요.",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body className="antialiased">{children}</body>
    </html>
  );
}
