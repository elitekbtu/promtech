/**
 * Authentication Hooks
 * 
 * React hooks for managing authentication state and role-based access
 */

import { useState, useEffect } from 'react';
import { getUserData, getUserRole, isAuthenticated, isExpertUser, UserData } from '@/lib/auth';

/**
 * Hook to get current user data
 * @returns User data, loading state, and refresh function
 */
export function useUser() {
  const [user, setUser] = useState<UserData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const refresh = async () => {
    try {
      setLoading(true);
      setError(null);
      const userData = await getUserData();
      setUser(userData);
    } catch (err) {
      console.error('Error fetching user data:', err);
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  return { user, loading, error, refresh };
}

/**
 * Hook to check if user is authenticated
 * @returns Authentication status and loading state
 */
export function useAuth() {
  const [authenticated, setAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const isAuth = await isAuthenticated();
        setAuthenticated(isAuth);
      } catch (error) {
        console.error('Error checking authentication:', error);
        setAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  return { authenticated, loading };
}

/**
 * Hook to get user's role
 * @returns User role, loading state, and helper functions
 */
export function useUserRole() {
  const [role, setRole] = useState<'guest' | 'expert' | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRole = async () => {
      try {
        const userRole = await getUserRole();
        setRole(userRole);
      } catch (error) {
        console.error('Error fetching user role:', error);
        setRole(null);
      } finally {
        setLoading(false);
      }
    };

    fetchRole();
  }, []);

  const isGuest = role === 'guest';
  const isExpert = role === 'expert';

  return { role, isGuest, isExpert, loading };
}

/**
 * Hook to check if user has expert role
 * @returns Expert status and loading state
 */
export function useIsExpert() {
  const [isExpert, setIsExpert] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkExpert = async () => {
      try {
        const expert = await isExpertUser();
        setIsExpert(expert);
      } catch (error) {
        console.error('Error checking expert status:', error);
        setIsExpert(false);
      } finally {
        setLoading(false);
      }
    };

    checkExpert();
  }, []);

  return { isExpert, loading };
}

/**
 * Hook for role-based conditional rendering
 * Usage: const canEdit = useRequireRole('expert');
 * 
 * @param requiredRole - Required role ('guest' or 'expert')
 * @returns Whether user has the required role
 */
export function useRequireRole(requiredRole: 'guest' | 'expert') {
  const { role, loading } = useUserRole();

  if (loading) return false;

  if (requiredRole === 'guest') {
    // Both guest and expert can access guest content
    return role === 'guest' || role === 'expert';
  }

  // Only expert can access expert content
  return role === 'expert';
}

/**
 * Hook to manage authentication state with refresh capability
 * Useful for screens that need to react to auth changes
 */
export function useAuthState() {
  const { user, loading: userLoading, refresh } = useUser();
  const { authenticated, loading: authLoading } = useAuth();

  const loading = userLoading || authLoading;

  return {
    user,
    authenticated,
    loading,
    refresh,
    isExpert: user?.role === 'expert',
    isGuest: user?.role === 'guest',
  };
}
