import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  TouchableOpacity,
  Platform,
  Linking,
  Alert,
} from 'react-native';
import { useLocalSearchParams, useRouter, Stack } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { GidroAtlasColors } from '@/constants/theme';
import { waterObjectsAPI } from '@/lib/api-services';
import { getBackendURL } from '@/lib/config';
import type { WaterObject } from '@/lib/gidroatlas-types';
import { AuroraBackground } from '@/components/ui/aurora-background';

// Technical condition colors
const conditionColors: Record<number, string> = {
  1: '#ef4444', // Red - Critical
  2: '#f97316', // Orange - Poor
  3: '#eab308', // Yellow - Fair
  4: '#22c55e', // Green - Good
  5: '#22c55e', // Green - Excellent
};

const conditionLabels: Record<number, string> = {
  1: 'Критическое',
  2: 'Плохое',
  3: 'Удовлетворительное',
  4: 'Хорошее',
  5: 'Отличное',
};

export default function WaterObjectDetailScreen() {
  const { id } = useLocalSearchParams();
  const router = useRouter();
  const insets = useSafeAreaInsets();
  
  const [object, setObject] = useState<WaterObject | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      fetchObjectDetails(Number(id));
    }
  }, [id]);

  const fetchObjectDetails = async (objectId: number) => {
    try {
      setLoading(true);
      setError(null);
      const data = await waterObjectsAPI.getById(objectId);
      setObject(data);
    } catch (err: any) {
      setError(err.message || 'Не удалось загрузить данные объекта');
      console.error('Error fetching object details:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    if (router.canGoBack()) {
      router.back();
    } else {
      router.replace('/(tabs)/');
    }
  };

  const getConditionColor = (condition: number) => {
    return conditionColors[condition] || '#6b7280';
  };

  const getConditionLabel = (condition: number) => {
    return conditionLabels[condition] || 'Неизвестно';
  };

  const handleDownloadPdf = async () => {
    if (!object?.pdf_url) return;
    
    try {
      let url = object.pdf_url;
      // If it's a relative path, prepend the backend URL
      if (!url.startsWith('http')) {
        const baseUrl = getBackendURL();
        // Remove double slashes if any
        url = `${baseUrl.replace(/\/$/, '')}/${url.replace(/^\//, '')}`;
      }
      
      const supported = await Linking.canOpenURL(url);
      if (supported) {
        await Linking.openURL(url);
      } else {
        Alert.alert('Ошибка', 'Не удалось открыть ссылку на паспорт');
      }
    } catch (error) {
      console.error("An error occurred", error);
      Alert.alert('Ошибка', 'Произошла ошибка при открытии файла');
    }
  };

  if (loading) {
    return (
      <AuroraBackground
        primaryColor={GidroAtlasColors.persianGreen}
        secondaryColor="#4FD1C5"
        accentColor={GidroAtlasColors.solar}
        backgroundColor={GidroAtlasColors.white}
        intensity={0.2}
      >
        <View style={styles.centerContent}>
          <ActivityIndicator size="large" color={GidroAtlasColors.persianGreen} />
          <Text style={styles.loadingText}>Загрузка данных...</Text>
        </View>
      </AuroraBackground>
    );
  }

  if (error || !object) {
    return (
      <AuroraBackground
        primaryColor={GidroAtlasColors.persianGreen}
        secondaryColor="#4FD1C5"
        accentColor={GidroAtlasColors.solar}
        backgroundColor={GidroAtlasColors.white}
        intensity={0.2}
      >
        <View style={styles.centerContent}>
          <Ionicons name="alert-circle-outline" size={48} color="#ef4444" />
          <Text style={styles.errorText}>{error || 'Объект не найден'}</Text>
          <TouchableOpacity
            style={styles.retryButton}
            onPress={() => id && fetchObjectDetails(Number(id))}
          >
            <Text style={styles.retryButtonText}>Повторить</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.backButton}
            onPress={handleBack}
          >
            <Text style={{ color: GidroAtlasColors.persianGreen }}>Вернуться назад</Text>
          </TouchableOpacity>
        </View>
      </AuroraBackground>
    );
  }

  return (
    <AuroraBackground
      primaryColor={GidroAtlasColors.persianGreen}
      secondaryColor="#4FD1C5"
      accentColor={GidroAtlasColors.solar}
      backgroundColor={GidroAtlasColors.white}
      intensity={0.2}
    >
      <Stack.Screen options={{ headerShown: false }} />
      
      <View style={[styles.header, { paddingTop: insets.top + 10 }]}>
        <TouchableOpacity
          style={styles.headerBackButton}
          onPress={handleBack}
          hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
        >
          <Ionicons name="arrow-back" size={24} color={GidroAtlasColors.persianGreen} />
        </TouchableOpacity>
        <Text style={styles.headerTitle} numberOfLines={1}>{object.name}</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Main Info Card */}
        <View style={styles.card}>
          <View style={styles.titleRow}>
            <View style={styles.iconContainer}>
              <Ionicons name="water" size={24} color={GidroAtlasColors.persianGreen} />
            </View>
            <View style={{ flex: 1 }}>
              <Text style={styles.title}>{object.name}</Text>
              <View style={styles.row}>
                <Ionicons name="location-outline" size={16} color={GidroAtlasColors.gray[500]} />
                <Text style={styles.subtitle}>{object.region}</Text>
              </View>
            </View>
          </View>
          
          <View style={styles.badgeContainer}>
            <View style={styles.badge}>
              <Text style={styles.badgeText}>{object.resource_type}</Text>
            </View>
          </View>
        </View>

        {/* Technical Condition Card */}
        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Техническое состояние</Text>
          
          <View style={styles.conditionContainer}>
            <View 
              style={[
                styles.conditionCircle, 
                { backgroundColor: getConditionColor(object.technical_condition) }
              ]}
            >
              <Text style={styles.conditionScore}>{object.technical_condition}</Text>
            </View>
            <View style={styles.conditionInfo}>
              <Text style={[styles.conditionLabel, { color: getConditionColor(object.technical_condition) }]}>
                {getConditionLabel(object.technical_condition)}
              </Text>
              <Text style={styles.conditionDescription}>
                Оценка по 5-балльной шкале
              </Text>
            </View>
          </View>
        </View>

        {/* Details Card */}
        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Характеристики</Text>
          
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Тип воды:</Text>
            <Text style={styles.detailValue}>{object.water_type || 'Не указано'}</Text>
          </View>
          
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Фауна:</Text>
            <Text style={styles.detailValue}>{object.fauna || 'Не указано'}</Text>
          </View>

          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Координаты:</Text>
            <Text style={styles.detailValue}>
              {object.latitude && object.longitude 
                ? `${object.latitude.toFixed(4)}, ${object.longitude.toFixed(4)}`
                : 'Не указаны'}
            </Text>
          </View>

          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Дата паспортизации:</Text>
            <Text style={styles.detailValue}>
              {object.passport_date 
                ? new Date(object.passport_date).toLocaleDateString('ru-RU')
                : 'Нет данных'}
            </Text>
          </View>
        </View>

        {/* Actions */}
        {object.pdf_url && (
          <TouchableOpacity 
            style={styles.actionButton}
            onPress={handleDownloadPdf}
          >
            <Ionicons name="document-text-outline" size={20} color="#fff" />
            <Text style={styles.actionButtonText}>Скачать паспорт</Text>
          </TouchableOpacity>
        )}

      </ScrollView>
    </AuroraBackground>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  centerContent: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingBottom: 16,
    zIndex: 100,
  },
  headerBackButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: GidroAtlasColors.white,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: GidroAtlasColors.gray[800],
    flex: 1,
    textAlign: 'center',
    marginHorizontal: 16,
  },
  scrollContent: {
    padding: 20,
    paddingBottom: 40,
    gap: 16,
  },
  loadingText: {
    marginTop: 12,
    fontSize: 16,
    color: GidroAtlasColors.gray[600],
  },
  errorText: {
    marginTop: 12,
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 20,
    color: GidroAtlasColors.gray[800],
  },
  retryButton: {
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
    backgroundColor: GidroAtlasColors.persianGreen,
  },
  retryButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
  backButton: {
    marginTop: 16,
    padding: 10,
  },
  card: {
    backgroundColor: GidroAtlasColors.white,
    borderRadius: 20,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.08,
    shadowRadius: 12,
    elevation: 4,
  },
  titleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  iconContainer: {
    width: 56,
    height: 56,
    borderRadius: 16,
    backgroundColor: `${GidroAtlasColors.persianGreen}15`,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: GidroAtlasColors.gray[900],
    marginBottom: 4,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  subtitle: {
    fontSize: 15,
    color: GidroAtlasColors.gray[500],
  },
  badgeContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  badge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
    backgroundColor: GidroAtlasColors.gray[100],
  },
  badgeText: {
    fontSize: 14,
    fontWeight: '600',
    color: GidroAtlasColors.gray[700],
    textTransform: 'capitalize',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: GidroAtlasColors.gray[900],
    marginBottom: 16,
  },
  conditionContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 16,
  },
  conditionCircle: {
    width: 64,
    height: 64,
    borderRadius: 32,
    justifyContent: 'center',
    alignItems: 'center',
  },
  conditionScore: {
    color: '#fff',
    fontSize: 28,
    fontWeight: 'bold',
  },
  conditionInfo: {
    flex: 1,
  },
  conditionLabel: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  conditionDescription: {
    fontSize: 14,
    color: GidroAtlasColors.gray[500],
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: GidroAtlasColors.gray[100],
  },
  detailLabel: {
    fontSize: 15,
    color: GidroAtlasColors.gray[500],
  },
  detailValue: {
    fontSize: 15,
    fontWeight: '500',
    color: GidroAtlasColors.gray[900],
    flex: 1,
    textAlign: 'right',
    marginLeft: 16,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 18,
    borderRadius: 16,
    backgroundColor: GidroAtlasColors.persianGreen,
    gap: 8,
    shadowColor: GidroAtlasColors.persianGreen,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 6,
  },
  actionButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});
