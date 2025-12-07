/**
 * Water Objects API Service
 * 
 * Example service demonstrating how to use the axios client
 * with automatic JWT authentication for API requests.
 */

import apiClient, { getErrorMessage } from './axios-client';

// Type definitions matching backend schemas
export interface WaterObject {
  id: number;
  name: string;
  region: string;
  latitude?: number;
  longitude?: number;
  resource_type: string;
  water_type?: string;
  fauna?: string;
  technical_condition: number;
  passport_date?: string;
  passport_pdf_url?: string;
  created_at: string;
  updated_at: string;
  // Expert-only fields (included if user is expert)
  priority_score?: number;
  priority_level?: string;
  passport_age_years?: number;
}

export interface WaterObjectListResponse {
  items: WaterObject[];
  total: number;
  limit: number;
  offset: number;
}

export interface WaterObjectCreate {
  name: string;
  region: string;
  latitude?: number;
  longitude?: number;
  resource_type: string;
  water_type?: string;
  fauna?: string;
  technical_condition: number;
  passport_date?: string;
  passport_pdf_url?: string;
}

/**
 * Water Objects API Service
 */
export const WaterObjectsAPI = {
  /**
   * Get list of water objects with optional filters
   * Authentication: Required (guest or expert)
   * Role-based: Guests see limited data, experts see full data with priorities
   */
  async getList(params?: {
    region?: string;
    resource_type?: string;
    limit?: number;
    offset?: number;
    sort_by?: string;
    sort_order?: 'asc' | 'desc';
  }): Promise<WaterObjectListResponse> {
    try {
      const response = await apiClient.get<WaterObjectListResponse>('/api/objects', {
        params,
      });
      return response.data;
    } catch (error) {
      console.error('[API] Error fetching water objects:', getErrorMessage(error));
      throw error;
    }
  },

  /**
   * Get single water object by ID
   * Authentication: Required
   * Role-based: Response differs based on role
   */
  async getById(id: number): Promise<WaterObject> {
    try {
      const response = await apiClient.get<WaterObject>(`/api/objects/${id}`);
      return response.data;
    } catch (error) {
      console.error(`[API] Error fetching water object ${id}:`, getErrorMessage(error));
      throw error;
    }
  },

  /**
   * Create new water object
   * Authentication: Required
   * Role: Expert only (403 if guest)
   */
  async create(data: WaterObjectCreate): Promise<WaterObject> {
    try {
      const response = await apiClient.post<WaterObject>('/api/objects', data);
      return response.data;
    } catch (error) {
      console.error('[API] Error creating water object:', getErrorMessage(error));
      throw error;
    }
  },

  /**
   * Update water object
   * Authentication: Required
   * Role: Expert only
   */
  async update(id: number, data: Partial<WaterObjectCreate>): Promise<WaterObject> {
    try {
      const response = await apiClient.put<WaterObject>(`/api/objects/${id}`, data);
      return response.data;
    } catch (error) {
      console.error(`[API] Error updating water object ${id}:`, getErrorMessage(error));
      throw error;
    }
  },

  /**
   * Delete water object
   * Authentication: Required
   * Role: Expert only
   */
  async delete(id: number): Promise<void> {
    try {
      await apiClient.delete(`/api/objects/${id}`);
    } catch (error) {
      console.error(`[API] Error deleting water object ${id}:`, getErrorMessage(error));
      throw error;
    }
  },
};

/**
 * Priorities API Service (Expert only)
 */
export const PrioritiesAPI = {
  /**
   * Get priority statistics
   * Authentication: Required
   * Role: Expert only
   */
  async getStatistics(): Promise<{
    high: number;
    medium: number;
    low: number;
    total: number;
  }> {
    try {
      const response = await apiClient.get('/api/priorities/statistics');
      return response.data;
    } catch (error) {
      console.error('[API] Error fetching priority statistics:', getErrorMessage(error));
      throw error;
    }
  },

  /**
   * Get priority table data
   * Authentication: Required
   * Role: Expert only
   */
  async getTable(params?: {
    priority_level?: string;
    limit?: number;
    offset?: number;
  }): Promise<any> {
    try {
      const response = await apiClient.get('/api/priorities/table', { params });
      return response.data;
    } catch (error) {
      console.error('[API] Error fetching priority table:', getErrorMessage(error));
      throw error;
    }
  },
};

/**
 * Passports API Service
 */
export const PassportsAPI = {
  /**
   * Upload passport PDF
   * Authentication: Required
   * Role: Expert only
   */
  async uploadPDF(objectId: number, file: Blob): Promise<any> {
    try {
      const formData = new FormData();
      // @ts-ignore - FormData accepts Blob with filename
      formData.append('file', file, 'passport.pdf');

      const response = await apiClient.post(
        `/api/passports/${objectId}/upload`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return response.data;
    } catch (error) {
      console.error('[API] Error uploading passport:', getErrorMessage(error));
      throw error;
    }
  },

  /**
   * Get passport text
   * Authentication: Required
   * Role: Both guest and expert
   */
  async getText(objectId: number): Promise<any> {
    try {
      const response = await apiClient.get(`/api/passports/${objectId}/text`);
      return response.data;
    } catch (error) {
      console.error('[API] Error fetching passport text:', getErrorMessage(error));
      throw error;
    }
  },

  /**
   * Delete passport
   * Authentication: Required
   * Role: Expert only
   */
  async delete(objectId: number): Promise<void> {
    try {
      await apiClient.delete(`/api/passports/${objectId}`);
    } catch (error) {
      console.error('[API] Error deleting passport:', getErrorMessage(error));
      throw error;
    }
  },
};
