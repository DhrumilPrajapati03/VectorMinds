import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Lexo",
  description: "AI-powered legal document assistant",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
