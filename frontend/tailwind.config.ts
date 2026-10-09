import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Strictly requested brand palette
        brand: {
          cream: "#EAE6DE",
          blue: "#226192",
          orange: "#EF8557",
          dark: "#0F1A24",
          surface: "#172533",
          border: "#23394E",
        },
        veriact: {
          bg: "#0B131B",
          card: "#121E2B",
          elevated: "#1A2C3E",
          border: "#226192",
          text: "#EAE6DE",
          muted: "#94A3B8",
          execute: "#10B981",
          escalate: "#EF8557",
          block: "#EF4444",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
