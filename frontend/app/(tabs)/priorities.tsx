import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Platform,
  RefreshControl,
  Dimensions,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import Markdown from 'react-native-markdown-display';
import { GidroAtlasColors } from '@/constants/theme';
import { prioritiesAPI, ragAPI } from '@/lib/api-services';
import { getUserData, UserData } from '@/lib/auth';
import { PriorityLevel } from '@/lib/gidroatlas-types';
import type { PriorityTableItem, PriorityStatistics, PriorityFilters } from '@/lib/gidroatlas-types';
import { AuroraBackground } from '@/components/ui/aurora-background';
import { Toast } from '@/components/ui/toast';

const { width } = Dimensions.get('window');
const isSmallScreen = width < 768;

// Priority level colors
const priorityColors: Record<string, string> = {
  'высокий': '#ef4444',
  'средний': '#f97316',
  'низкий': '#22c55e',
};

const priorityLabels: Record<string, string> = {
  'высокий': 'Высокий',
  'средний': 'Средний',
  'низкий': 'Низкий',
};

export default function PrioritiesScreen() {
  const router = useRouter();
  const [items, setItems] = useState<PriorityTableItem[]>([]);
  const [stats, setStats] = useState<PriorityStatistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedFilter, setSelectedFilter] = useState<PriorityLevel | 'all'>('all');
  const [filters, setFilters] = useState<PriorityFilters>({
    page: 1,
    page_size: 20,
    sort_by: 'priority',
    sort_order: 'desc',
  });
  const [expandedItem, setExpandedItem] = useState<number | null>(null);
  const [explanations, setExplanations] = useState<Record<number, string>>({});
  const [loadingExplanation, setLoadingExplanation] = useState<number | null>(null);
  const [isGuest, setIsGuest] = useState(false);
  const [toast, setToast] = useState<{ visible: boolean; message: string; type: 'success' | 'error' | 'info' }>({
    visible: false,
    message: '',
    type: 'info',
  });

  const showToast = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
    setToast({ visible: true, message, type });
  };

  const hideToast = () => {
    setToast(prev => ({ ...prev, visible: false }));
  };

  const checkUserRole = async () => {
    try {
      const user = await getUserData();
      if (user?.role === 'guest') {
        setIsGuest(true);
        setLoading(false);
        return false;
      }
      return true;
    } catch (error) {
      console.error('Error checking user role:', error);
      return false;
    }
  };

  const fetchData = useCallback(async (isRefresh = false) => {
    try {
      const isExpert = await checkUserRole();
      if (!isExpert) return;

      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      setError(null);

      const currentFilters: PriorityFilters = {
        ...filters,
        page: isRefresh ? 1 : filters.page,
        priority_level: selectedFilter !== 'all' ? selectedFilter : undefined,
      };

      const [tableResponse, statsResponse] = await Promise.all([
        prioritiesAPI.getTable(currentFilters),
        prioritiesAPI.getStats(),
      ]);

      setItems(tableResponse.items);
      setStats(statsResponse);
    } catch (err: any) {
      setError(err.message || 'Не удалось загрузить данные приоритетов. Требуется доступ эксперта.');
      console.error('Error fetching priorities:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [filters, selectedFilter]);

  useEffect(() => {
    fetchData();
  }, [selectedFilter]);

  const handleRefresh = () => {
    fetchData(true);
  };

  const handleFilterChange = (filter: PriorityLevel | 'all') => {
    setSelectedFilter(filter);
    setFilters(prev => ({ ...prev, page: 1 }));
  };

  const fetchExplanation = async (objectId: number) => {
    if (explanations[objectId]) {
      setExpandedItem(expandedItem === objectId ? null : objectId);
      return;
    }

    try {
      setLoadingExplanation(objectId);
      setExpandedItem(objectId);
      
      const response = await ragAPI.explainPriority(objectId, { language: 'en' });
      setExplanations(prev => ({
        ...prev,
        [objectId]: response.explanation,
      }));
    } catch (err: any) {
      setExplanations(prev => ({
        ...prev,
        [objectId]: 'Не удалось загрузить объяснение. Попробуйте ещё раз.',
      }));
      console.error('Error fetching explanation:', err);
    } finally {
      setLoadingExplanation(null);
    }
  };

  const renderStatCard = (label: string, value: number, color: string, icon: string) => (
    <View style={[styles.statCard, { borderLeftColor: color }]}>
      <Ionicons name={icon as any} size={24} color={color} />
      <Text style={styles.statValue}>{value}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </View>
  );

  const renderPriorityItem = (item: PriorityTableItem) => {
    const isExpanded = expandedItem === item.id;
    const priorityColor = priorityColors[item.priority_level] || '#9ca3af';

    return (
      <View key={item.id} style={styles.itemContainer}>
        <TouchableOpacity
          style={styles.itemCard}
          onPress={() => fetchExplanation(item.id)}
          activeOpacity={0.7}
        >
          <View style={styles.itemHeader}>
            <View style={[styles.priorityIndicator, { backgroundColor: priorityColor }]} />
            <View style={styles.itemInfo}>
              <Text style={styles.itemName} numberOfLines={1}>{item.name}</Text>
              <Text style={styles.itemRegion}>{item.region}</Text>
            </View>
            <View style={styles.itemStats}>
              <View style={[styles.priorityBadge, { backgroundColor: priorityColor }]}>
                <Text style={styles.priorityScore}>{item.priority.toFixed(1)}</Text>
              </View>
              <Ionicons
                name={isExpanded ? 'chevron-up' : 'chevron-down'}
                size={20}
                color={GidroAtlasColors.gray[400]}
              />
            </View>
          </View>

          <View style={styles.itemDetails}>
            <View style={styles.detailItem}>
              <Ionicons name="construct-outline" size={14} color={GidroAtlasColors.gray[400]} />
              <Text style={styles.detailText}>Состояние: {item.technical_condition}/5</Text>
            </View>
            {item.passport_date && (
              <View style={styles.detailItem}>
                <Ionicons name="document-outline" size={14} color={GidroAtlasColors.gray[400]} />
                <Text style={styles.detailText}>
                  Паспорт: {new Date(item.passport_date).toLocaleDateString()}
                </Text>
              </View>
            )}
            <View style={styles.detailItem}>
              <Ionicons name="flag-outline" size={14} color={priorityColor} />
              <Text style={[styles.detailText, { color: priorityColor, fontWeight: '600' }]}>
                {priorityLabels[item.priority_level] || item.priority_level} приоритет
              </Text>
            </View>
          </View>
        </TouchableOpacity>

        {isExpanded && (
          <View style={styles.explanationContainer}>
            {loadingExplanation === item.id ? (
              <View style={styles.explanationLoading}>
                <ActivityIndicator size="small" color={GidroAtlasColors.persianGreen} />
                <Text style={styles.explanationLoadingText}>Генерация AI-объяснения...</Text>
              </View>
            ) : (
              <View style={styles.explanationContent}>
                <View style={styles.explanationHeader}>
                  <Ionicons name="bulb" size={18} color={GidroAtlasColors.persianGreen} />
                  <Text style={styles.explanationTitle}>AI-объяснение приоритета</Text>
                </View>
                <Markdown style={markdownStyles}>
                  {explanations[item.id] || 'Недоступно.'}
                </Markdown>
              </View>
            )}
          </View>
        )}
      </View>
    );
  };

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
          <View style={styles.headerTitleContainer}>
            <Text style={styles.headerTitle}>Таблица приоритетов</Text>
            <Text style={styles.headerSubtitle}>Экспертная панель анализа</Text>
          </View>
        </View>

        {isGuest ? (
          <View style={styles.guestContainer}>
            <Ionicons name="lock-closed-outline" size={64} color={GidroAtlasColors.gray[300]} />
            <Text style={styles.guestTitle}>Доступ ограничен</Text>
            <Text style={styles.guestMessage}>
              Аналитика приоритетов доступна только для экспертов. Пожалуйста, войдите в аккаунт эксперта для просмотра данных.
            </Text>
            <TouchableOpacity 
              style={styles.loginButton}
              onPress={() => {
                router.replace('/login');
              }}
            >
              <Text style={styles.loginButtonText}>Войти как эксперт</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <>
            {/* Error Message */}
            {error && (
              <View style={styles.errorContainer}>
                <Ionicons name="lock-closed" size={20} color="#ef4444" />
                <Text style={styles.errorText}>{error}</Text>
                <TouchableOpacity onPress={handleRefresh}>
                  <Text style={styles.retryText}>Повторить</Text>
                </TouchableOpacity>
              </View>
            )}

            {/* Loading State */}
            {loading && items.length === 0 ? (
              <View style={styles.loadingContainer}>
                <ActivityIndicator size="large" color={GidroAtlasColors.persianGreen} />
                <Text style={styles.loadingText}>Загрузка данных приоритетов...</Text>
              </View>
            ) : (
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
              >
                {/* Statistics Cards */}
                {stats && (
                  <View style={styles.statsContainer}>
                    {renderStatCard('Высокий', stats.high, '#ef4444', 'alert-circle')}
                    {renderStatCard('Средний', stats.medium, '#f97316', 'warning')}
                    {renderStatCard('Низкий', stats.low, '#22c55e', 'checkmark-circle')}
                    {renderStatCard('Всего', stats.total, GidroAtlasColors.persianGreen, 'water')}
                  </View>
                )}

                {/* Filter Buttons */}
                <View style={styles.filterContainer}>
                  {(['all', PriorityLevel.HIGH, PriorityLevel.MEDIUM, PriorityLevel.LOW] as const).map((filter) => (
                    <TouchableOpacity
                      key={filter}
                      style={[
                        styles.filterButton,
                        selectedFilter === filter && styles.filterButtonActive,
                        selectedFilter === filter && { backgroundColor: filter === 'all' ? GidroAtlasColors.persianGreen : priorityColors[filter] },
                      ]}
                      onPress={() => handleFilterChange(filter)}
                    >
                      <Text style={[
                        styles.filterButtonText,
                        selectedFilter === filter && styles.filterButtonTextActive,
                      ]}>
                        {filter === 'all' ? 'Все' : priorityLabels[filter]}
                      </Text>
                    </TouchableOpacity>
                  ))}
                </View>

                {/* Priority Items */}
                {items.length === 0 ? (
                  <View style={styles.emptyContainer}>
                    <Ionicons name="analytics-outline" size={64} color={GidroAtlasColors.gray[300]} />
                    <Text style={styles.emptyText}>Данные приоритетов недоступны</Text>
                    <Text style={styles.emptySubtext}>Требуется доступ эксперта</Text>
                  </View>
                ) : (
                  <View style={styles.itemsList}>
                    {items.map(renderPriorityItem)}
                  </View>
                )}
              </ScrollView>
            )}
          </>
        )}
      </View>

      <Toast 
        visible={toast.visible}
        message={toast.message}
        type={toast.type}
        onHide={hideToast}
      />
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
  headerTitleContainer: {
    flex: 1,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: GidroAtlasColors.gray[800],
  },
  headerSubtitle: {
    fontSize: 13,
    color: GidroAtlasColors.gray[500],
    marginTop: 2,
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
  statsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    marginBottom: 20,
  },
  statCard: {
    flex: 1,
    minWidth: isSmallScreen ? '45%' : 150,
    backgroundColor: GidroAtlasColors.white,
    borderRadius: 12,
    padding: 16,
    borderLeftWidth: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 6,
    elevation: 2,
    alignItems: 'center',
  },
  statValue: {
    fontSize: 28,
    fontWeight: '700',
    color: GidroAtlasColors.gray[800],
    marginTop: 8,
  },
  statLabel: {
    fontSize: 12,
    color: GidroAtlasColors.gray[500],
    marginTop: 4,
  },
  filterContainer: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 16,
  },
  filterButton: {
    flex: 1,
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderRadius: 10,
    backgroundColor: GidroAtlasColors.white,
    borderWidth: 1,
    borderColor: GidroAtlasColors.gray[200],
    alignItems: 'center',
  },
  filterButtonActive: {
    borderColor: 'transparent',
  },
  filterButtonText: {
    fontSize: 13,
    fontWeight: '500',
    color: GidroAtlasColors.gray[600],
  },
  filterButtonTextActive: {
    color: GidroAtlasColors.white,
  },
  itemsList: {
    gap: 12,
  },
  itemContainer: {
    marginBottom: 4,
  },
  itemCard: {
    backgroundColor: GidroAtlasColors.white,
    borderRadius: 16,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 8,
    elevation: 3,
  },
  itemHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  priorityIndicator: {
    width: 4,
    height: 40,
    borderRadius: 2,
    marginRight: 12,
  },
  itemInfo: {
    flex: 1,
  },
  itemName: {
    fontSize: 16,
    fontWeight: '600',
    color: GidroAtlasColors.gray[800],
  },
  itemRegion: {
    fontSize: 13,
    color: GidroAtlasColors.gray[500],
    marginTop: 2,
  },
  itemStats: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  priorityBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
  },
  priorityScore: {
    color: GidroAtlasColors.white,
    fontSize: 14,
    fontWeight: '700',
  },
  itemDetails: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  detailItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  detailText: {
    fontSize: 12,
    color: GidroAtlasColors.gray[500],
  },
  explanationContainer: {
    marginTop: 8,
    marginLeft: 16,
    marginRight: 0,
    padding: 16,
    backgroundColor: `${GidroAtlasColors.persianGreen}08`,
    borderRadius: 12,
    borderLeftWidth: 3,
    borderLeftColor: GidroAtlasColors.persianGreen,
  },
  explanationLoading: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  explanationLoadingText: {
    fontSize: 14,
    color: GidroAtlasColors.gray[500],
    fontStyle: 'italic',
  },
  explanationContent: {},
  explanationHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 8,
  },
  explanationTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: GidroAtlasColors.persianGreen,
  },
  explanationText: {
    fontSize: 14,
    color: GidroAtlasColors.gray[700],
    lineHeight: 22,
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
  guestContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 32,
    paddingTop: 100,
  },
  guestTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: GidroAtlasColors.black,
    marginTop: 24,
    marginBottom: 12,
    textAlign: 'center',
  },
  guestMessage: {
    fontSize: 16,
    color: GidroAtlasColors.gray[500],
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 32,
  },
  loginButton: {
    backgroundColor: GidroAtlasColors.persianGreen,
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 12,
  },
  loginButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
});

const markdownStyles = StyleSheet.create({
  body: {
    fontSize: 14,
    color: GidroAtlasColors.gray[700],
    lineHeight: 22,
  },
  strong: {
    fontWeight: 'bold',
    color: GidroAtlasColors.gray[900],
  },
  heading1: {
    fontSize: 18,
    fontWeight: 'bold',
    color: GidroAtlasColors.persianGreen,
    marginVertical: 8,
  },
  heading2: {
    fontSize: 16,
    fontWeight: 'bold',
    color: GidroAtlasColors.persianGreen,
    marginVertical: 6,
  },
  list_item: {
    marginVertical: 2,
  },
  bullet_list: {
    marginVertical: 4,
  },
  code_inline: {
    backgroundColor: GidroAtlasColors.gray[100],
    paddingHorizontal: 4,
    paddingVertical: 2,
    borderRadius: 4,
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 12,
  },
  code_block: {
    backgroundColor: GidroAtlasColors.gray[100],
    padding: 12,
    borderRadius: 8,
    marginVertical: 8,
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 12,
  },
  fence: {
    backgroundColor: GidroAtlasColors.gray[100],
    padding: 12,
    borderRadius: 8,
    marginVertical: 8,
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 12,
  },
});
