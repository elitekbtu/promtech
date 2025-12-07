import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  TextInput,
  Platform,
  RefreshControl,
  Linking,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { GidroAtlasColors } from '@/constants/theme';
import { waterObjectsAPI } from '@/lib/api-services';
import { config } from '@/lib/config';
import type { WaterObject, WaterObjectFilters, ResourceType } from '@/lib/gidroatlas-types';
import { AuroraBackground } from '@/components/ui/aurora-background';

// Resource type icons mapping
const resourceTypeIcons: Record<string, string> = {
  'озеро': 'water',
  'канал': 'git-branch',
  'водохранилище': 'cube',
  'река': 'water',
  'другое': 'ellipse',
};

// Technical condition colors
const conditionColors: Record<number, string> = {
  1: '#ef4444', // Red - Critical
  2: '#f97316', // Orange - Poor
  3: '#eab308', // Yellow - Fair
  4: '#22c55e', // Green - Good
  5: '#10b981', // Emerald - Excellent
};

const conditionLabels: Record<number, string> = {
  1: 'Critical',
  2: 'Poor',
  3: 'Fair',
  4: 'Good',
  5: 'Excellent',
};

export default function WaterObjectsScreen() {
  const router = useRouter();
  const [objects, setObjects] = useState<WaterObject[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<WaterObjectFilters>({
    page: 1,
    page_size: 20,
  });
  const [totalCount, setTotalCount] = useState(0);
  const [hasMore, setHasMore] = useState(true);

  const fetchObjects = useCallback(async (isRefresh = false) => {
    try {
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      setError(null);

      const currentFilters: WaterObjectFilters = {
        ...filters,
        page: isRefresh ? 1 : filters.page,
        search: searchQuery || undefined,
      };

      const response = await waterObjectsAPI.list(currentFilters);
      
      if (isRefresh || filters.page === 1) {
        setObjects(response.items);
      } else {
        setObjects(prev => [...prev, ...response.items]);
      }
      
      setTotalCount(response.total);
      setHasMore(response.items.length === filters.page_size);
    } catch (err: any) {
      setError(err.message || 'Failed to load water objects');
      console.error('Error fetching water objects:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [filters, searchQuery]);

  useEffect(() => {
    fetchObjects();
  }, []);

  const handleRefresh = () => {
    setFilters(prev => ({ ...prev, page: 1 }));
    fetchObjects(true);
  };

  const handleSearch = () => {
    setFilters(prev => ({ ...prev, page: 1 }));
    fetchObjects(true);
  };

  const loadMore = () => {
    if (!loading && hasMore) {
      setFilters(prev => ({ ...prev, page: (prev.page || 1) + 1 }));
      fetchObjects();
    }
  };

  const renderObjectCard = (item: WaterObject) => (
    <TouchableOpacity
      key={item.id}
      style={styles.card}
      onPress={async () => {
        if (item.pdf_url) {
          try {
            // Construct full URL if it's relative
            const fullUrl = item.pdf_url.startsWith('http') 
              ? item.pdf_url 
              : `${config.backendURL}${item.pdf_url.startsWith('/') ? '' : '/'}${item.pdf_url}`;

            // On web, simply open in new tab
            if (Platform.OS === 'web') {
              window.open(fullUrl, '_blank');
              return;
            }

            // On mobile, check if we can open it
            const supported = await Linking.canOpenURL(fullUrl);
            if (supported) {
              await Linking.openURL(fullUrl);
            } else {
              Alert.alert('Error', 'Cannot open this passport file.');
            }
          } catch (err) {
            console.error('Error opening PDF:', err);
            Alert.alert('Error', 'Failed to open passport.');
          }
        } else {
          if (Platform.OS === 'web') {
            alert('There is no passport available for this water object.');
          } else {
            Alert.alert('No Passport', 'There is no passport available for this water object.');
          }
        }
      }}
    >
      <View style={styles.cardHeader}>
        <View style={styles.cardIconContainer}>
          <Ionicons
            name={resourceTypeIcons[item.resource_type] as any || 'water'}
            size={24}
            color={GidroAtlasColors.persianGreen}
          />
        </View>
        <View style={styles.cardTitleContainer}>
          <Text style={styles.cardTitle} numberOfLines={1}>
            {item.name}
          </Text>
          <Text style={styles.cardSubtitle}>
            {item.region}
          </Text>
        </View>
        <View style={[styles.conditionBadge, { backgroundColor: conditionColors[item.technical_condition] || '#9ca3af' }]}>
          <Text style={styles.conditionText}>
            {item.technical_condition}/5
          </Text>
        </View>
      </View>

      <View style={styles.cardBody}>
        <View style={styles.cardRow}>
          <Text style={styles.cardLabel}>Type:</Text>
          <Text style={styles.cardValue}>{item.resource_type}</Text>
        </View>
        {item.water_type && (
          <View style={styles.cardRow}>
            <Text style={styles.cardLabel}>Water:</Text>
            <Text style={styles.cardValue}>{item.water_type}</Text>
          </View>
        )}
        {item.fauna && (
          <View style={styles.cardRow}>
            <Text style={styles.cardLabel}>Fauna:</Text>
            <Text style={styles.cardValue}>{item.fauna}</Text>
          </View>
        )}
        {item.passport_date && (
          <View style={styles.cardRow}>
            <Text style={styles.cardLabel}>Passport:</Text>
            <Text style={styles.cardValue}>
              {new Date(item.passport_date).toLocaleDateString()}
            </Text>
          </View>
        )}
      </View>

      {item.priority !== undefined && (
        <View style={styles.cardFooter}>
          <View style={[
            styles.priorityBadge,
            { backgroundColor: item.priority_level === 'высокий' ? '#ef4444' : 
                              item.priority_level === 'средний' ? '#f97316' : '#22c55e' }
          ]}>
            <Text style={styles.priorityText}>
              Priority: {item.priority.toFixed(1)} ({item.priority_level})
            </Text>
          </View>
        </View>
      )}
    </TouchableOpacity>
  );

  return (
    <AuroraBackground
      primaryColor={GidroAtlasColors.persianGreen}
      secondaryColor="#4FD1C5"
      accentColor={GidroAtlasColors.solar}
      backgroundColor={GidroAtlasColors.white}
      intensity={0.25}
    >
      <View style={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => router.back()}
          >
            <Ionicons name="arrow-back" size={24} color={GidroAtlasColors.persianGreen} />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Water Objects</Text>
          <Text style={styles.headerCount}>{totalCount} total</Text>
        </View>

        {/* Search Bar */}
        <View style={styles.searchContainer}>
          <Ionicons name="search" size={20} color={GidroAtlasColors.gray[400]} />
          <TextInput
            style={styles.searchInput}
            placeholder="Search by name or region..."
            placeholderTextColor={GidroAtlasColors.gray[400]}
            value={searchQuery}
            onChangeText={setSearchQuery}
            onSubmitEditing={handleSearch}
            returnKeyType="search"
          />
          {searchQuery.length > 0 && (
            <TouchableOpacity onPress={() => {
              setSearchQuery('');
              handleSearch();
            }}>
              <Ionicons name="close-circle" size={20} color={GidroAtlasColors.gray[400]} />
            </TouchableOpacity>
          )}
        </View>

        {/* Error Message */}
        {error && (
          <View style={styles.errorContainer}>
            <Ionicons name="alert-circle" size={20} color="#ef4444" />
            <Text style={styles.errorText}>{error}</Text>
            <TouchableOpacity onPress={handleRefresh}>
              <Text style={styles.retryText}>Retry</Text>
            </TouchableOpacity>
          </View>
        )}

        {/* Loading State */}
        {loading && objects.length === 0 ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color={GidroAtlasColors.persianGreen} />
            <Text style={styles.loadingText}>Loading water objects...</Text>
          </View>
        ) : (
          /* Objects List */
          <ScrollView
            style={styles.scrollView}
            contentContainerStyle={styles.scrollContent}
            showsVerticalScrollIndicator={false}
            refreshControl={
              <RefreshControl
                refreshing={refreshing}
                onRefresh={handleRefresh}
                colors={[GidroAtlasColors.persianGreen]}
                tintColor={GidroAtlasColors.persianGreen}
              />
            }
            onScroll={({ nativeEvent }) => {
              const { layoutMeasurement, contentOffset, contentSize } = nativeEvent;
              const isCloseToBottom = layoutMeasurement.height + contentOffset.y >= contentSize.height - 50;
              if (isCloseToBottom && !loading && hasMore) {
                loadMore();
              }
            }}
            scrollEventThrottle={400}
          >
            {objects.length === 0 ? (
              <View style={styles.emptyContainer}>
                <Ionicons name="water-outline" size={64} color={GidroAtlasColors.gray[300]} />
                <Text style={styles.emptyText}>No water objects found</Text>
                <Text style={styles.emptySubtext}>Try adjusting your search</Text>
              </View>
            ) : (
              <>
                {objects.map(renderObjectCard)}
                {loading && objects.length > 0 && (
                  <View style={styles.loadMoreContainer}>
                    <ActivityIndicator size="small" color={GidroAtlasColors.persianGreen} />
                  </View>
                )}
              </>
            )}
          </ScrollView>
        )}
      </View>
    </AuroraBackground>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingTop: Platform.OS === 'ios' ? 60 : 40,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingBottom: 16,
  },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: GidroAtlasColors.white,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: GidroAtlasColors.gray[800],
    flex: 1,
  },
  headerCount: {
    fontSize: 14,
    color: GidroAtlasColors.gray[500],
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginHorizontal: 20,
    marginBottom: 16,
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: GidroAtlasColors.white,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: GidroAtlasColors.gray[200],
  },
  searchInput: {
    flex: 1,
    marginLeft: 10,
    fontSize: 16,
    color: GidroAtlasColors.gray[800],
  },
  errorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginHorizontal: 20,
    marginBottom: 16,
    padding: 12,
    backgroundColor: '#fef2f2',
    borderRadius: 8,
    gap: 8,
  },
  errorText: {
    flex: 1,
    color: '#ef4444',
    fontSize: 14,
  },
  retryText: {
    color: GidroAtlasColors.persianGreen,
    fontWeight: '600',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 12,
    fontSize: 16,
    color: GidroAtlasColors.gray[500],
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: 20,
    paddingBottom: 120,
  },
  card: {
    backgroundColor: GidroAtlasColors.white,
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 8,
    elevation: 3,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  cardIconContainer: {
    width: 44,
    height: 44,
    borderRadius: 12,
    backgroundColor: `${GidroAtlasColors.persianGreen}15`,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  cardTitleContainer: {
    flex: 1,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: GidroAtlasColors.gray[800],
  },
  cardSubtitle: {
    fontSize: 13,
    color: GidroAtlasColors.gray[500],
    marginTop: 2,
  },
  conditionBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
  },
  conditionText: {
    color: GidroAtlasColors.white,
    fontSize: 12,
    fontWeight: '600',
  },
  cardBody: {
    gap: 6,
  },
  cardRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  cardLabel: {
    fontSize: 13,
    color: GidroAtlasColors.gray[500],
    width: 70,
  },
  cardValue: {
    fontSize: 13,
    color: GidroAtlasColors.gray[700],
    flex: 1,
  },
  cardFooter: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: GidroAtlasColors.gray[100],
  },
  priorityBadge: {
    alignSelf: 'flex-start',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
  },
  priorityText: {
    color: GidroAtlasColors.white,
    fontSize: 12,
    fontWeight: '600',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 100,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: GidroAtlasColors.gray[600],
    marginTop: 16,
  },
  emptySubtext: {
    fontSize: 14,
    color: GidroAtlasColors.gray[400],
    marginTop: 4,
  },
  loadMoreContainer: {
    paddingVertical: 20,
    alignItems: 'center',
  },
});
