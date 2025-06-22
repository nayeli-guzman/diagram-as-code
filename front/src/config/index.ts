export const config = {
  apiUrl: import.meta.env.VITE_API_URL || "http://localhost:8000/api",
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,

  // Feature flags
  features: {
    githubIntegration: true,
    offlineMode: false,
    analytics: import.meta.env.PROD,
  },

  // Editor settings
  editor: {
    theme: "vs-dark",
    fontSize: 14,
    wordWrap: "on" as const,
    minimap: false,
  },

  // Toast settings
  toast: {
    position: "top-right" as const,
    duration: 4000,
  },
} as const;
