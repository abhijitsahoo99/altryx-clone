import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Altryx - Data Pipeline Platform",
  description: "Visual data pipeline and analytics platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased font-sans">
        {children}
      </body>
    </html>
  );
}
