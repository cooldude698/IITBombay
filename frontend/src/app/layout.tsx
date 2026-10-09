import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "VERIACT — Risk-Adaptive Runtime Verification Command Center",
  description: "Enterprise Pre-Execution Verification Layer for Autonomous AI Agents (IIT Bombay Techfest)",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen bg-[#0A121C] text-[#EAE6DE] antialiased selection:bg-[#EF8557]/30 selection:text-[#EAE6DE]">
        {children}
      </body>
    </html>
  );
}
