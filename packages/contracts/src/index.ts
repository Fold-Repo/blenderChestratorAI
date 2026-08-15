export interface HealthResponse {
  status: 'ok';
  service: string;
  version: string;
  timestamp: string;
  requestId: string;
}

export interface ApiErrorResponse {
  error: {
    code: string;
    message: string;
    requestId: string;
    details?: unknown;
  };
}

export interface AuthUser {
  id: string;
  username: string;
  email: string;
}

export interface AuthResponse {
  user: AuthUser;
  token: string;
  requestId: string;
}

export interface UsageRecord {
  id: string;
  runId: string;
  userId: string;
  projectId: string;
  provider: string;
  model: string;
  tokenUsage?: {
    inputTokens: number;
    outputTokens: number;
    totalTokens: number;
  };
  toolCallsCount: number;
  estimatedCost: number;
  createdAt: string;
}

export interface AuditLog {
  id: string;
  userId: string;
  projectId: string;
  action: string;
  tool?: string;
  parametersMetadata?: unknown;
  approvalRequired: boolean;
  approved: boolean;
  executionResult?: string;
  timestamp: string;
}
