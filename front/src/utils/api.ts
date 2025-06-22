import type { AuthResponse, LoginRequest, SignupRequest, User } from "../types";

const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  "https://d1g6vyk1f5.execute-api.us-east-1.amazonaws.com/dev";

// Auth token management
export const getAuthToken = (): string | null => {
  return localStorage.getItem("authToken");
};

export const setAuthToken = (token: string): void => {
  localStorage.setItem("authToken", token);
};

export const removeAuthToken = (): void => {
  localStorage.removeItem("authToken");
};

// API request helper with auth
const apiRequest = async (
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> => {
  const token = getAuthToken();

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    removeAuthToken();
    window.location.href = "/login";
  }

  return response;
};

// Auth API
export const authAPI = {
  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    const response = await apiRequest("/usuarios/login", {
      method: "POST",
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const errorData = await response.json();
      const errorMessage =
        errorData.message ||
        errorData.body?.message ||
        "Error al iniciar sesión";

      // Mensajes más específicos según el código de estado
      if (response.status === 401) {
        throw new Error(
          "Credenciales incorrectas. Verifica tu User ID, Tenant ID y contraseña."
        );
      } else if (response.status === 404) {
        throw new Error(
          "Usuario no encontrado. Verifica tu User ID y Tenant ID."
        );
      } else if (response.status === 400) {
        throw new Error(
          "Datos inválidos. Verifica que todos los campos estén completos."
        );
      } else {
        throw new Error(errorMessage);
      }
    }
    const data = await response.json();
    const responseData = data.body || data;
    const token = responseData.token || data.token;
    if (!token) {
      throw new Error(
        "Error de autenticación. Verifica tus credenciales e inténtalo de nuevo."
      );
    }
    return {
      user: {
        id: credentials.user_id,
        email: credentials.user_id,
        name: credentials.user_id.split("@")[0] || credentials.user_id,
      },
      token: token,
    };
  },
  signup: async (userData: SignupRequest): Promise<AuthResponse> => {
    const response = await apiRequest("/usuarios/registrar", {
      method: "POST",
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      const errorMessage =
        errorData.message || errorData.body?.message || "Error al registrarse";

      // Mensajes más específicos según el código de estado
      if (response.status === 409) {
        throw new Error(
          "Este usuario ya existe. Intenta con un User ID diferente o inicia sesión."
        );
      } else if (response.status === 400) {
        throw new Error(
          "Datos inválidos. Verifica que todos los campos estén completos y sean válidos."
        );
      } else {
        throw new Error(errorMessage);
      }
    }

    await response.json();

    // El registro fue exitoso, ahora hacer login automáticamente
    const loginResponse = await apiRequest("/usuarios/login", {
      method: "POST",
      body: JSON.stringify({
        user_id: userData.user_id,
        tenant_id: userData.tenant_id,
        password: userData.password,
      }),
    });

    if (!loginResponse.ok) {
      throw new Error("Usuario creado pero error al iniciar sesión");
    }
    const loginData = await loginResponse.json();
    const loginResponseData = loginData.body || loginData;
    const token = loginResponseData.token || loginData.token;
    if (!token) {
      throw new Error(
        "Error al iniciar sesión después del registro. Por favor, inicia sesión manualmente."
      );
    }

    // Adaptar el formato de respuesta del backend
    return {
      user: {
        id: userData.user_id,
        email: userData.user_id, // Usar user_id como email para mantener compatibilidad
        name: userData.user_id.split("@")[0] || userData.user_id, // Usar parte del user_id como nombre
      },
      token: token,
    };
  },

  verify: async (): Promise<{ user: User }> => {
    // Como el backend no tiene endpoint de verify, simulamos la verificación
    const token = getAuthToken();
    if (!token) {
      throw new Error("Token inválido");
    }

    // Recuperar datos del usuario desde localStorage
    const userEmail = localStorage.getItem("userEmail") || "usuario@email.com";
    const userName = localStorage.getItem("userName") || "Usuario";

    return {
      user: {
        id: "user-id",
        email: userEmail,
        name: userName,
      },
    };
  },
};

// Diagrams API
export const diagramsAPI = {
  generate: async (
    code: string,
    type: string
  ): Promise<{ imageUrl: string }> => {
    const response = await apiRequest("/diagramas/generar", {
      method: "POST",
      body: JSON.stringify({ codigo: code, tipo: type }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || "Error al generar el diagrama");
    }
    const data = await response.json();
    return {
      imageUrl: data.imagen_url || data.imageUrl || "",
    };
  },
};

// GitHub API
export const githubAPI = {
  fetchFile: async (url: string): Promise<string> => {
    // Convert GitHub URL to raw URL if needed
    const rawUrl =
      url.includes("github.com") && !url.includes("raw.githubusercontent.com")
        ? url
            .replace("github.com", "raw.githubusercontent.com")
            .replace("/blob/", "/")
        : url;

    const response = await fetch(rawUrl);

    if (!response.ok) {
      throw new Error("No se pudo cargar el archivo desde GitHub");
    }

    return response.text();
  },
};
