/**
 * GidroAtlas API Type Definitions
 * 
 * Type definitions matching backend Pydantic schemas
 */

// ============================================================================
// Enums (matching backend exactly - Russian values)
// ============================================================================

export enum ResourceType {
    LAKE = "озеро",
    CANAL = "канал",
    RESERVOIR = "водохранилище",
    RIVER = "река",
    OTHER = "другое",
}

export enum WaterType {
    FRESH = "пресная",
    NON_FRESH = "непресная",
}

export enum FaunaType {
    FISH_BEARING = "рыбопродуктивная",
    NON_FISH_BEARING = "нерыбопродуктивная",
}

export enum PriorityLevel {
    HIGH = "высокий",
    MEDIUM = "средний",
    LOW = "низкий",
}

export enum UserRole {
    GUEST = "guest",
    EXPERT = "expert",
}

// ============================================================================
// Water Objects
// ============================================================================

export interface WaterObject {
    id: number;
    name: string;
    region: string;
    resource_type: ResourceType;
    water_type?: WaterType | null;
    fauna?: FaunaType | null;
    passport_date?: string | null; // ISO date string
    technical_condition: number; // 1-5
    latitude?: number | null;
    longitude?: number | null;
    pdf_url?: string | null;
    priority?: number; // Only for expert users
    priority_level?: PriorityLevel; // Only for expert users
    created_at: string;
    updated_at: string;
    deleted_at?: string | null;
}

export interface WaterObjectFilters {
    page?: number;
    page_size?: number;
    region?: string;
    resource_type?: ResourceType;
    water_type?: WaterType;
    has_fauna?: boolean;
    passport_date_from?: string;
    passport_date_to?: string;
    technical_condition_min?: number;
    technical_condition_max?: number;
    search?: string;
    priority_min?: number; // Expert only
    priority_max?: number; // Expert only
    priority_level?: PriorityLevel; // Expert only
    sort_by?: string;
    sort_order?: 'asc' | 'desc';
}

export interface WaterObjectList {
    items: WaterObject[];
    total: number;
    page: number;
    page_size: number;
}

// ============================================================================
// Priorities (Expert Only)
// ============================================================================

export interface PriorityTableItem {
    id: number;
    name: string;
    region: string;
    technical_condition: number;
    passport_date?: string | null;
    priority: number;
    priority_level: PriorityLevel;
}

export interface PriorityTable {
    items: PriorityTableItem[];
    total: number;
    page: number;
    page_size: number;
}

export interface PriorityStatistics {
    high: number;
    medium: number;
    low: number;
    total: number;
}

export interface PriorityFilters {
    page?: number;
    page_size?: number;
    region?: string;
    resource_type?: ResourceType;
    water_type?: WaterType;
    has_fauna?: boolean;
    passport_date_from?: string;
    passport_date_to?: string;
    technical_condition_min?: number;
    technical_condition_max?: number;
    priority_min?: number;
    priority_max?: number;
    priority_level?: PriorityLevel;
    sort_by?: string;
    sort_order?: 'asc' | 'desc';
}

// ============================================================================
// Passports
// ============================================================================

export interface PassportMetadata {
    object_id: number;
    exists: boolean;
    pdf_url?: string | null;
}

export interface PassportUploadRequest {
    object_id: number;
    file: File | Blob;
}

export interface PassportUploadResponse {
    object_id: number;
    pdf_url: string;
    message: string;
}

// ============================================================================
// RAG System
// ============================================================================

export interface RAGQuery {
    query: string;
    language?: 'ru' | 'en';
    context?: Record<string, any>;
    environment?: string;
    object_id?: number;
    region?: string;
    priority_level?: string;
    resource_type?: string;
}

export interface RAGResponse {
    answer: string;
    objects?: Array<{
        id: number;
        name: string;
        priority?: number;
    }>;
    sources?: string[];
    confidence?: number;
}

export interface RAGExplainPriorityRequest {
    language?: 'ru' | 'en';
}

export interface RAGExplainPriorityResponse {
    object_id: number;
    priority: number;
    priority_level: PriorityLevel;
    explanation: string;
}

// ============================================================================
// Authentication
// ============================================================================

export interface LoginRequest {
    email: string;
    password: string;
}

export interface RegisterRequest {
    name: string;
    surname: string;
    email: string;
    phone: string;
    password: string;
    avatar?: string | null;
}

export interface User {
    id: number;
    name: string;
    surname: string;
    email: string;
    phone: string;
    role: UserRole;
    avatar?: string | null;
    created_at: string;
    updated_at: string;
    deleted_at?: string | null;
}

export interface TokenResponse {
    access_token: string;
    token_type: string;
    user: User;
}

// ============================================================================
// Face ID Verification
// ============================================================================

export interface FaceVerifyRequest {
    image: string; // base64 encoded image
}

export interface FaceVerifyResponse {
    success: boolean;
    verified: boolean;
    message: string;
    token?: TokenResponse;
    confidence?: number;
    distance?: number;
    threshold?: number;
    model?: string;
    error?: string;
}

// ============================================================================
// API Error Response
// ============================================================================

export interface APIError {
    detail: string;
    status_code?: number;
}

// ============================================================================
// Generic Pagination Response
// ============================================================================

export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    page: number;
    page_size: number;
}
