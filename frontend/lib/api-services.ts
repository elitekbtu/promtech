/**
 * GidroAtlas API Services
 * 
 * Type-safe API service layer for all GidroAtlas backend endpoints
 */

import { config } from './config';
import { getAuthToken } from './auth';
import type {
    WaterObject,
    WaterObjectList,
    WaterObjectFilters,
    PriorityTable,
    PriorityStatistics,
    PriorityFilters,
    PassportMetadata,
    PassportUploadRequest,
    PassportUploadResponse,
    RAGQuery,
    RAGResponse,
    RAGExplainPriorityRequest,
    RAGExplainPriorityResponse,
    FaceVerifyRequest,
    FaceVerifyResponse,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    APIError,
} from './gidroatlas-types';

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Default request timeout in milliseconds
 */
const DEFAULT_TIMEOUT = 50000; // 50 seconds

/**
 * Fetch with timeout support
 */
async function fetchWithTimeout(
    url: string,
    options: RequestInit = {},
    timeout: number = DEFAULT_TIMEOUT
): Promise<Response> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal,
        });
        clearTimeout(timeoutId);
        return response;
    } catch (error: any) {
        clearTimeout(timeoutId);

        // Handle different error types
        if (error.name === 'AbortError') {
            throw new Error('Request timeout - please check your connection');
        }
        if (error.message === 'Network request failed' || error.message?.includes('fetch')) {
            throw new Error('Network error - please check your connection');
        }
        throw error;
    }
}

/**
 * Build query string from filters object
 */
function buildQueryString(filters?: Record<string, any>): string {
    if (!filters) return '';

    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
            params.append(key, String(value));
        }
    });

    const queryString = params.toString();
    return queryString ? `?${queryString}` : '';
}

/**
 * Get authorization headers with JWT token
 */
async function getAuthHeaders(): Promise<HeadersInit> {
    const token = await getAuthToken();
    return {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    };
}

/**
 * Handle API response with proper error handling
 */
async function handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
        let error: APIError;
        try {
            error = await response.json();
        } catch {
            // If response body isn't valid JSON, create generic error
            error = {
                detail: `HTTP Error ${response.status}: ${response.statusText}`,
                status_code: response.status,
            };
        }
        throw new Error(error.detail || `API Error: ${response.status}`);
    }

    try {
        return await response.json();
    } catch (parseError) {
        throw new Error('Failed to parse response JSON');
    }
}

// ============================================================================
// Water Objects API
// ============================================================================

export const waterObjectsAPI = {
    /**
     * List water objects with optional filters
     */
    async list(filters?: WaterObjectFilters): Promise<WaterObjectList> {
        const url = `${config.backendURL}/api/objects${buildQueryString(filters)}`;
        const headers = await getAuthHeaders();

        const response = await fetchWithTimeout(url, { headers });
        return handleResponse<WaterObjectList>(response);
    },

    /**
     * Get single water object by ID
     */
    async getById(id: number): Promise<WaterObject> {
        const url = `${config.backendURL}/api/objects/${id}`;
        const headers = await getAuthHeaders();

        const response = await fetchWithTimeout(url, { headers });
        return handleResponse<WaterObject>(response);
    },

    /**
     * Get passport metadata for water object
     */
    async getPassport(objectId: number): Promise<PassportMetadata> {
        const url = `${config.backendURL}/api/objects/${objectId}/passport`;
        const headers = await getAuthHeaders();

        const response = await fetchWithTimeout(url, { headers });
        return handleResponse<PassportMetadata>(response);
    },
};

// ============================================================================
// Priorities API (Expert Only)
// ============================================================================

export const prioritiesAPI = {
    /**
     * Get priority table (expert only)
     */
    async getTable(filters?: PriorityFilters): Promise<PriorityTable> {
        const url = `${config.backendURL}/api/priorities/table${buildQueryString(filters)}`;
        const headers = await getAuthHeaders();

        const response = await fetchWithTimeout(url, { headers });
        return handleResponse<PriorityTable>(response);
    },

    /**
     * Get priority statistics (expert only)
     */
    async getStats(): Promise<PriorityStatistics> {
        const url = `${config.backendURL}/api/priorities/stats`;
        const headers = await getAuthHeaders();

        const response = await fetchWithTimeout(url, { headers });
        return handleResponse<PriorityStatistics>(response);
    },
};

// ============================================================================
// Passports API
// ============================================================================

export const passportsAPI = {
    /**
     * Get passport metadata
     */
    async get(objectId: number): Promise<PassportMetadata> {
        const url = `${config.backendURL}/api/passports/${objectId}`;
        const headers = await getAuthHeaders();

        const response = await fetchWithTimeout(url, { headers });
        return handleResponse<PassportMetadata>(response);
    },

    /**
     * Upload passport document (expert only)
     */
    async upload(request: PassportUploadRequest): Promise<PassportUploadResponse> {
        const url = `${config.backendURL}/api/passports/upload`;
        const token = await getAuthToken();

        const formData = new FormData();
        formData.append('object_id', String(request.object_id));
        formData.append('file', request.file);

        // Note: Don't set Content-Type for FormData - browser sets it automatically with boundary
        const response = await fetchWithTimeout(url, {
            method: 'POST',
            headers: {
                ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
                // Content-Type is intentionally omitted for multipart/form-data
            },
            body: formData,
        });

        return handleResponse<PassportUploadResponse>(response);
    },
};

// ============================================================================
// RAG System API
// ============================================================================

export const ragAPI = {
    /**
     * Send natural language query to RAG system
     */
    async query(request: RAGQuery): Promise<RAGResponse> {
        const url = `${config.backendURL}/api/rag/query`;
        const headers = await getAuthHeaders();

        const response = await fetchWithTimeout(url, {
            method: 'POST',
            headers,
            body: JSON.stringify(request),
        });

        return handleResponse<RAGResponse>(response);
    },

    /**
     * Get AI explanation for priority score (expert only)
     */
    async explainPriority(
        objectId: number,
        request?: RAGExplainPriorityRequest
    ): Promise<RAGExplainPriorityResponse> {
        const url = `${config.backendURL}/api/rag/explain-priority/${objectId}`;
        const headers = await getAuthHeaders();

        const response = await fetchWithTimeout(url, {
            method: 'POST',
            headers,
            body: JSON.stringify(request || { language: 'ru' }),
        });

        return handleResponse<RAGExplainPriorityResponse>(response);
    },
};

// ============================================================================
// Authentication API
// ============================================================================

export const authAPI = {
    /**
     * Login with email and password
     */
    async login(credentials: LoginRequest): Promise<TokenResponse> {
        const url = `${config.backendURL}/api/auth/login`;

        const response = await fetchWithTimeout(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(credentials),
        });

        return handleResponse<TokenResponse>(response);
    },

    /**
     * Register new user
     */
    async register(userData: RegisterRequest): Promise<TokenResponse> {
        const url = `${config.backendURL}/api/auth/register`;

        const response = await fetchWithTimeout(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData),
        });

        return handleResponse<TokenResponse>(response);
    },

    /**
     * Logout (clears local token, optionally calls backend)
     */
    async logout(): Promise<void> {
        const url = `${config.backendURL}/api/auth/logout`;
        const headers = await getAuthHeaders();

        try {
            await fetchWithTimeout(url, { method: 'POST', headers });
        } catch (error) {
            console.warn('[Auth] Logout API call failed:', error);
            // Continue with local logout even if API fails
        }
    },
};

// ============================================================================
// Face ID API
// ============================================================================

export const faceIdAPI = {
    /**
     * Verify face for authentication
     */
    async verify(request: FaceVerifyRequest): Promise<FaceVerifyResponse> {
        const url = `${config.backendURL}/api/faceid/verify`;

        const response = await fetchWithTimeout(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request),
        });

        return handleResponse<FaceVerifyResponse>(response);
    },
};

// ============================================================================
// Unified API Export
// ============================================================================

export const gidroatlasAPI = {
    waterObjects: waterObjectsAPI,
    priorities: prioritiesAPI,
    passports: passportsAPI,
    rag: ragAPI,
    auth: authAPI,
    faceId: faceIdAPI,
};

export default gidroatlasAPI;
