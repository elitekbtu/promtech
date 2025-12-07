/**
 * Authentication Utility
 * 
 * Secure storage for JWT tokens and user data using Expo SecureStore (Native) or localStorage (Web).
 * Provides functions for managing authentication state.
 */

import * as SecureStore from 'expo-secure-store';
import { Platform } from 'react-native';

// Storage keys
const TOKEN_KEY = 'jwt_access_token';
const USER_KEY = 'user_data';

// Type definitions
export interface UserData {
    id: number;
    name: string;
    surname: string;
    email: string;
    phone: string;
    role: 'guest' | 'expert';
    avatar?: string;
    created_at: string;
    updated_at: string;
    deleted_at?: string | null;
}

export interface TokenResponse {
    access_token: string;
    token_type: string;
    user: UserData;
}

// Helper functions for cross-platform storage
async function setItem(key: string, value: string): Promise<void> {
    if (Platform.OS === 'web') {
        try {
            localStorage.setItem(key, value);
        } catch (e) {
            console.error('Local storage is not available:', e);
        }
    } else {
        await SecureStore.setItemAsync(key, value);
    }
}

async function getItem(key: string): Promise<string | null> {
    if (Platform.OS === 'web') {
        try {
            return localStorage.getItem(key);
        } catch (e) {
            console.error('Local storage is not available:', e);
            return null;
        }
    } else {
        return await SecureStore.getItemAsync(key);
    }
}

async function deleteItem(key: string): Promise<void> {
    if (Platform.OS === 'web') {
        try {
            localStorage.removeItem(key);
        } catch (e) {
            console.error('Local storage is not available:', e);
        }
    } else {
        await SecureStore.deleteItemAsync(key);
    }
}

/**
 * Save JWT access token securely
 * @param token - JWT access token
 */
export async function saveAuthToken(token: string): Promise<void> {
    try {
        await setItem(TOKEN_KEY, token);
    } catch (error) {
        console.error('Error saving auth token:', error);
        throw error;
    }
}

/**
 * Retrieve JWT access token
 * @returns JWT token or null if not found
 */
export async function getAuthToken(): Promise<string | null> {
    try {
        return await getItem(TOKEN_KEY);
    } catch (error) {
        console.error('Error retrieving auth token:', error);
        return null;
    }
}

/**
 * Save user data securely
 * @param user - User data object
 */
export async function saveUserData(user: UserData): Promise<void> {
    try {
        await setItem(USER_KEY, JSON.stringify(user));
    } catch (error) {
        console.error('Error saving user data:', error);
        throw error;
    }
}

/**
 * Retrieve user data
 * @returns User data or null if not found
 */
export async function getUserData(): Promise<UserData | null> {
    try {
        const data = await getItem(USER_KEY);
        return data ? JSON.parse(data) : null;
    } catch (error) {
        console.error('Error retrieving user data:', error);
        return null;
    }
}

/**
 * Save complete authentication response (token + user data)
 * @param tokenResponse - Response from login/register endpoint
 */
export async function saveAuthResponse(tokenResponse: TokenResponse): Promise<void> {
    try {
        await Promise.all([
            saveAuthToken(tokenResponse.access_token),
            saveUserData(tokenResponse.user),
        ]);
    } catch (error) {
        console.error('Error saving auth response:', error);
        throw error;
    }
}

/**
 * Check if user is authenticated
 * @returns true if token exists
 */
export async function isAuthenticated(): Promise<boolean> {
    const token = await getAuthToken();
    return !!token;
}

/**
 * Check if current user has expert role
 * @returns true if user is expert
 */
export async function isExpertUser(): Promise<boolean> {
    const user = await getUserData();
    return user?.role === 'expert';
}

/**
 * Get user's role
 * @returns User role or null
 */
export async function getUserRole(): Promise<'guest' | 'expert' | null> {
    const user = await getUserData();
    return user?.role || null;
}

/**
 * Clear all authentication data (logout)
 */
export async function clearAuth(): Promise<void> {
    try {
        await Promise.all([
            deleteItem(TOKEN_KEY),
            deleteItem(USER_KEY),
        ]);
    } catch (error) {
        console.error('Error clearing auth data:', error);
        throw error;
    }
}

/**
 * Check if SecureStore is available on current platform
 * @returns true if available
 */
export async function isSecureStoreAvailable(): Promise<boolean> {
    if (Platform.OS === 'web') return true; // LocalStorage is available
    try {
        return await SecureStore.isAvailableAsync();
    } catch (error) {
        console.error('Error checking SecureStore availability:', error);
        return false;
    }
}
