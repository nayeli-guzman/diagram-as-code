export interface User {
  id: string;
  email: string;
  name: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface LoginRequest {
  user_id: string;
  tenant_id: string;
  password: string;
}

export interface SignupRequest {
  user_id: string;
  tenant_id: string;
  password: string;
}

export interface AuthResponse {
  user: User;
  token: string;
}

export interface DiagramGenerationRequest {
  code: string;
  type: DiagramType;
}

export interface DiagramGenerationResponse {
  imageUrl: string;
  success: boolean;
  message?: string;
}

export type DiagramType =
  | "aws"
  | "azure"
  | "gcp"
  | "k8s"
  | "network"
  | "onprem"
  | "programming"
  | "generic";

export interface DiagramTemplate {
  name: string;
  type: DiagramType;
  code: string;
  description: string;
}

export interface GitHubFileRequest {
  url: string;
}
