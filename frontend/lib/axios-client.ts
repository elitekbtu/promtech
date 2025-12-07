/**
 * Axios HTTP Client with JWT Authentication
 * 
 * Configured axios instance with automatic JWT token injection
 * and 401 error handling for expired tokens.
 */

import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { router } from 'expo-router';
import { config } from './config';
import { getAuthToken, clearAuth } from './auth';

/**
 * Create axios instance with base configuration
 */
const apiClient = axios.create({
    baseURL: config.backendURL,
    timeout: 30000, // 30 seconds
    headers: {
        'Content-Type': 'application/json',
    },
});

/**
 * Request Interceptor
 * Automatically adds JWT Bearer token to all requests
 */
apiClient.interceptors.request.use(
    async (config: InternalAxiosRequestConfig) => {
        try {
            // Get JWT token from secure storage
            const token = await getAuthToken();

            if (token) {
                // Add Authorization header with Bearer token
                config.headers.Authorization = `Bearer ${token}`;
            }

            // Log request in development
            if (__DEV__) {
                console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
                if (token) {
                    console.log('[API] Auth token attached');
                }
            }

            return config;
        } catch (error) {
            console.error('[API] Error in request interceptor:', error);
            return Promise.reject(error);
        }
    },
    (error: AxiosError) => {
        console.error('[API] Request interceptor error:', error);
        return Promise.reject(error);
    }
);

/**
 * Response Interceptor
 * Handles 401 errors (expired/invalid tokens) and redirects to login
 */
apiClient.interceptors.response.use(
    (response) => {
        // Log successful responses in development
        if (__DEV__) {
            console.log(`[API] ✅ ${response.status} ${response.config.url}`);
        }
        return response;
    },
    async (error: AxiosError) => {
        if (error.response) {
            const { status, config: requestConfig } = error.response;

            // Handle 401 Unauthorized (expired/invalid token)
            if (status === 401) {
                console.warn('[API] 401 Unauthorized - Token expired or invalid');

                // Clear auth data
                try {
                    await clearAuth();
                } catch (clearError) {
                    console.error('[API] Error clearing auth:', clearError);
                }

                // Redirect to login screen
                // Use setTimeout to avoid navigation during render
                setTimeout(() => {
                    router.replace('/login');
                }, 0);

                return Promise.reject(new Error('Authentication expired. Please log in again.'));
            }

            // Handle 403 Forbidden (insufficient permissions)
            if (status === 403) {
                console.warn('[API] 403 Forbidden - Insufficient permissions');
                return Promise.reject(new Error('You do not have permission to perform this action.'));
            }

            // Log other errors in development
            if (__DEV__) {
                console.error(`[API] ❌ ${status} ${requestConfig?.url}`, error.response.data);
            }
        } else if (error.request) {
            // Network error (no response received)
            console.error('[API] Network error - No response received:', error.message);
        } else {
            // Request setup error
            console.error('[API] Request setup error:', error.message);
        }

        return Promise.reject(error);
    }
);

/**
 * Export configured axios instance
 */
export default apiClient;

/**
 * Helper function to check if error is a 401
 */
export function isUnauthorizedError(error: any): boolean {
    return axios.isAxiosError(error) && error.response?.status === 401;
}

/**
 * Helper function to check if error is a 403
 */
export function isForbiddenError(error: any): boolean {
    return axios.isAxiosError(error) && error.response?.status === 403;
}

/**
 * Helper function to extract error message
 */
export function getErrorMessage(error: any): string {
    if (axios.isAxiosError(error)) {
        const data = error.response?.data;
        if (typeof data === 'object' && data !== null) {
            return data.detail || data.message || 'An error occurred';
        }
        return error.message || 'Network error';
    }
    return 'An unexpected error occurred';
}
