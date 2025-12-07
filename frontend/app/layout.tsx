import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Smart Web Scraper",
  description: "Modern web scraping platform with FastAPI backend",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
