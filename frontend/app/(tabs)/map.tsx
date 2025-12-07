import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ActivityIndicator,
  TouchableOpacity,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { Colors } from '@/constants/theme';
import { waterObjectsAPI } from '@/lib/api-services';
import type { WaterObject } from '@/lib/gidroatlas-types';
import { useColorScheme } from '@/hooks/use-color-scheme';

// Conditionally import LeafletMap only on web
let LeafletMap: any = null;
if (Platform.OS === 'web') {
  LeafletMap = require('@/components/leaflet-map.web').default;
}

// Technical condition colors for markers
const conditionColors: Record<number, string> = {
  1: '#ef4444', // Red - Critical
  2: '#f97316', // Orange - Poor
  3: '#eab308', // Yellow - Fair
  4: '#22c55e', // Green - Good
  5: '#10b981', // Emerald - Excellent
};

export default function MapScreen() {
  const router = useRouter();
  const colorScheme = useColorScheme();
  const theme = Colors[colorScheme ?? 'light'];
  const [waterObjects, setWaterObjects] = useState<WaterObject[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchWaterObjects();
  }, []);

  const fetchWaterObjects = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch all water objects with coordinates
      const response = await waterObjectsAPI.list({
        page: 1,
        page_size: 1000, // Get all objects
      });

      // Filter objects that have coordinates
      const objectsWithCoords = response.items.filter(
        (obj) => obj.latitude !== null && obj.longitude !== null
      );

      setWaterObjects(objectsWithCoords);
    } catch (err: any) {
      setError(err.message || 'Failed to load water objects');
      console.error('Error fetching water objects:', err);
    } finally {
      setLoading(false);
    }
  };

  const getMarkerColor = (condition: number): string => {
    return conditionColors[condition] || '#6b7280';
  };

  const handleObjectPress = (objectId: number) => {
    router.push(`/water-object/${objectId}` as any);
  };

  return (
    <View style={[styles.container, { backgroundColor: theme.background }]}>
      <View style={[styles.header, { backgroundColor: theme.background, borderBottomColor: theme.border }]}>
        <Text style={[styles.headerTitle, { color: theme.text }]}>Карта водных объектов</Text>
        <TouchableOpacity onPress={fetchWaterObjects} style={styles.refreshButton}>
          <Ionicons name="refresh" size={24} color={theme.text} />
        </TouchableOpacity>
      </View>

      {loading && waterObjects.length === 0 ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={theme.primary} />
          <Text style={[styles.loadingText, { color: theme.text }]}>Загрузка водных объектов...</Text>
        </View>
      ) : error ? (
        <View style={styles.errorContainer}>
          <Ionicons name="alert-circle" size={48} color="#ef4444" />
          <Text style={styles.errorText}>{error}</Text>
          <TouchableOpacity onPress={fetchWaterObjects} style={[styles.retryButton, { backgroundColor: theme.primary }]}>
            <Text style={styles.retryButtonText}>Попробовать снова</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <>
          {/* Map container */}
          <View style={styles.mapContainer}>
            {Platform.OS === 'web' && LeafletMap ? (
              <LeafletMap 
                waterObjects={waterObjects} 
                onMarkerClick={handleObjectPress}
              />
            ) : (
              <View style={styles.noMapContainer}>
                <Ionicons name="map" size={64} color={theme.icon} />
                <Text style={[styles.noMapText, { color: theme.text }]}>
                  Карта доступна только в веб-версии
                </Text>
              </View>
            )}
          </View>

          {/* Stats overlay removed as requested */}

          {/* Legend overlay */}
          <View style={[styles.legendOverlay, { backgroundColor: 'rgba(255, 255, 255, 0.95)' }]}>
            <Text style={[styles.legendTitle, { color: '#1F2937' }]}>Легенда:</Text>
            {Object.entries(conditionColors).map(([condition, color]) => (
              <View key={condition} style={styles.legendItem}>
                <View style={[styles.legendColor, { backgroundColor: color }]} />
                <Text style={[styles.legendText, { color: '#1F2937' }]}>
                  {condition === '1' && 'Крит.'}
                  {condition === '2' && 'Плохое'}
                  {condition === '3' && 'Удовл.'}
                  {condition === '4' && 'Хорошее'}
                  {condition === '5' && 'Отл.'}
                </Text>
              </View>
            ))}
          </View>
        </>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: Platform.OS === 'ios' ? 60 : 40,
    paddingBottom: 16,
    borderBottomWidth: 1,
    zIndex: 1000,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  refreshButton: {
    padding: 8,
  },
  mapContainer: {
    flex: 1,
    position: 'relative',
  },
  noMapContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  noMapText: {
    marginTop: 16,
    fontSize: 16,
    textAlign: 'center',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  errorText: {
    marginTop: 16,
    fontSize: 16,
    color: '#ef4444',
    textAlign: 'center',
  },
  retryButton: {
    marginTop: 16,
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  retryButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  statsOverlay: {
    position: 'absolute',
    top: 20,
    left: 20,
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderRadius: 12,
    gap: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 3,
    zIndex: 1000,
  },
  statsText: {
    fontSize: 14,
    fontWeight: '600',
  },
  legendOverlay: {
    position: 'absolute',
    bottom: 20,
    left: 20,
    padding: 12,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 3,
    zIndex: 1000,
  },
  legendTitle: {
    fontSize: 12,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  legendColor: {
    width: 14,
    height: 14,
    borderRadius: 7,
    marginRight: 6,
  },
  legendText: {
    fontSize: 11,
  },
});
