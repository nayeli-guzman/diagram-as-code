import React, { createContext, useReducer, useEffect } from "react";
import type { ReactNode } from "react";
import type { AuthState, User } from "../types";
import {
  authAPI,
  getAuthToken,
  setAuthToken,
  removeAuthToken,
} from "../utils/api";
import toast from "react-hot-toast";

interface AuthContextType extends AuthState {
  login: (userId: string, tenantId: string, password: string) => Promise<void>;
  signup: (userId: string, tenantId: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export { AuthContext };

type AuthAction =
  | { type: "SET_LOADING"; payload: boolean }
  | { type: "SET_USER"; payload: { user: User; token: string } }
  | { type: "CLEAR_USER" };

const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case "SET_LOADING":
      return { ...state, isLoading: action.payload };
    case "SET_USER":
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        isLoading: false,
      };
    case "CLEAR_USER":
      return {
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
      };
    default:
      return state;
  }
};

const initialState: AuthState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  useEffect(() => {
    const initializeAuth = async () => {
      const token = getAuthToken();
      if (token) {
        try {
          const { user } = await authAPI.verify();
          dispatch({ type: "SET_USER", payload: { user, token } });
        } catch {
          removeAuthToken();
          dispatch({ type: "CLEAR_USER" });
        }
      } else {
        dispatch({ type: "SET_LOADING", payload: false });
      }
    };

    initializeAuth();
  }, []);
  const login = async (userId: string, tenantId: string, password: string) => {
    try {
      dispatch({ type: "SET_LOADING", payload: true });
      const { user, token } = await authAPI.login({
        user_id: userId,
        tenant_id: tenantId,
        password,
      });
      setAuthToken(token);

      // Guardar información del usuario en localStorage
      localStorage.setItem("userEmail", user.email);
      localStorage.setItem("userName", user.name);

      dispatch({ type: "SET_USER", payload: { user, token } });
      toast.success("¡Sesión iniciada correctamente!");
    } catch (error) {
      dispatch({ type: "SET_LOADING", payload: false });
      toast.error(
        error instanceof Error ? error.message : "Error al iniciar sesión"
      );
      throw error;
    }
  };

  const signup = async (userId: string, tenantId: string, password: string) => {
    try {
      dispatch({ type: "SET_LOADING", payload: true });
      const { user, token } = await authAPI.signup({
        user_id: userId,
        tenant_id: tenantId,
        password,
      });
      setAuthToken(token);

      // Guardar información del usuario en localStorage
      localStorage.setItem("userEmail", user.email); // user:_id
      localStorage.setItem("userName", user.id); // tenant

      dispatch({ type: "SET_USER", payload: { user, token } });
      toast.success("¡Cuenta creada correctamente!");
    } catch (error) {
      dispatch({ type: "SET_LOADING", payload: false });
      toast.error(
        error instanceof Error ? error.message : "Error al crear la cuenta"
      );
      throw error;
    }
  };

  const logout = () => {
    removeAuthToken();
    localStorage.removeItem("userEmail");
    localStorage.removeItem("userName");
    dispatch({ type: "CLEAR_USER" });
    toast.success("Sesión cerrada");
  };

  const value: AuthContextType = {
    ...state,
    login,
    signup,
    logout,
  };
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
