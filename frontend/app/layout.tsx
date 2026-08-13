import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "PAIOS - AI Orchestration & Self-Healing",
  description: "Developed by Upadrasta Harsha Vardhan",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} antialiased bg-slate-950 text-slate-50`}>
        {children}
      </body>
    </html>
  );
}
