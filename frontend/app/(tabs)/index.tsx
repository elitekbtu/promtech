import { View, Text, Platform, StyleSheet, ScrollView, TouchableOpacity, Alert } from 'react-native';
import { useState, useEffect } from 'react';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Link } from 'expo-router';
import { GidroAtlasColors } from '@/constants/theme';
import GidroAtlasLogo from '@/components/gidroatlas-logo';
import { clearAuth, getUserData, UserData } from '@/lib/auth';
import { authAPI } from '@/lib/api-services';
import { AuroraBackground } from '@/components/ui/aurora-background';

export default function HomeScreen() {
  const router = useRouter();
  const [user, setUser] = useState<UserData | null>(null);

  useEffect(() => {
    loadUser();
  }, []);

  async function loadUser() {
    try {
      const userData = await getUserData();
      setUser(userData);
    } catch (error) {
      console.error('Error loading user:', error);
    }
  }

  async function performLogout() {
    try {
      // Call backend logout API
      await authAPI.logout();
    } catch (error) {
      console.warn('Backend logout failed:', error);
    }
    // Always clear local auth data
    await clearAuth();
    router.replace('/login');
  }

  function handleLogout() {
    // On web, Alert.alert doesn't work, so use confirm
    if (Platform.OS === 'web') {
      if (window.confirm('Вы уверены, что хотите выйти?')) {
        performLogout();
      }
    } else {
      Alert.alert(
        'Выход',
        'Вы уверены, что хотите выйти?',
        [
          { text: 'Отмена', style: 'cancel' },
          { 
            text: 'Выйти', 
            style: 'destructive',
            onPress: () => performLogout()
          }
        ]
      );
    }
  }

  const features = [
    {
      title: 'Голосовой чат',
      description: 'AI-разговоры в реальном времени',
      icon: 'chatbubbles',
      href: '/(tabs)/live-chat' as const,
      bgColor: GidroAtlasColors.cloud
    },
    {
      title: 'Водные объекты',
      description: 'Просмотр всех водных объектов',
      icon: 'water',
      href: '/(tabs)/water-objects' as const,
      bgColor: GidroAtlasColors.cloud
    },
    {
      title: 'Таблица приоритетов',
      description: 'Экспертный анализ приоритетов',
      icon: 'stats-chart',
      href: '/(tabs)/priorities' as const,
      bgColor: GidroAtlasColors.cloud
    },
    {
      title: 'AI-поиск',
      description: 'Задавайте вопросы о водных ресурсах',
      icon: 'search',
      href: '/(tabs)/explore' as const,
      bgColor: GidroAtlasColors.cloud
    }
  ];

  return (
    <AuroraBackground
      primaryColor={GidroAtlasColors.persianGreen}
      secondaryColor="#4FD1C5"
      accentColor={GidroAtlasColors.solar}
      backgroundColor={GidroAtlasColors.white}
      intensity={0.35}
    >
      {/* Logout Button - Top Right */}
      {user && (
        <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
          <Text style={styles.logoutText}>Выйти</Text>
        </TouchableOpacity>
      )}

      <ScrollView 
        style={styles.scrollView}
        contentContainerStyle={styles.contentContainer}
        showsVerticalScrollIndicator={false}
      >
        {/* Minimal Header */}
        <View style={styles.header}>
          <View style={styles.logoMark}>
            <GidroAtlasLogo size={90} withAccent />
          </View>
          <Text style={styles.appName}>GidroAtlas</Text>
          <Text style={styles.welcomeText}>
            Добро пожаловать, {user ? `${user.name} ${user.surname}` : 'Пользователь'}
          </Text>
          <Text style={styles.subtitleText}>
            Ваша AI-платформа для управления водными ресурсами
          </Text>
        </View>

        {/* Content */}
        <View style={styles.content}>
          {/* Quick Actions */}
          <View style={styles.section}>   
            <View style={styles.quickActions}>
              {features.map((feature, index) => (
                <Link key={index} href={feature.href} asChild>
                  <TouchableOpacity style={styles.featureCard}>
                    <View style={styles.iconContainer}>
                      <Ionicons 
                        name={feature.icon as any} 
                        size={28} 
                        color={GidroAtlasColors.white}
                      />
                    </View>
                    <Text style={styles.cardTitle}>
                      {feature.title}
                    </Text>
                    <Text style={styles.cardDescription}>
                      {feature.description}
                    </Text>
                  </TouchableOpacity>
                </Link>
              ))}
            </View>
          </View>
        </View>
      </ScrollView>
    </AuroraBackground>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: GidroAtlasColors.white,
  },
  scrollView: {
    flex: 1,
  },
  contentContainer: {
    flexGrow: 1,
    paddingBottom: 100,
  },
  logoutButton: {
    position: 'absolute',
    top: Platform.OS === 'ios' ? 60 : 40,
    right: 24,
    backgroundColor: GidroAtlasColors.white,
    borderWidth: 1,
    borderColor: GidroAtlasColors.gray[300],
    paddingVertical: 10,
    paddingHorizontal: 24,
    borderRadius: 12,
    zIndex: 100,
  },
  logoutText: {
    color: GidroAtlasColors.persianGreen,
    fontWeight: '500',
    fontSize: 15,
  },
  header: {
    paddingTop: Platform.OS === 'ios' ? 80 : 60,
    paddingBottom: 50,
    paddingHorizontal: 32,
    alignItems: 'center',
    backgroundColor: GidroAtlasColors.white,
  },
  logoMark: {
    marginBottom: 20,
    alignItems: 'center',
  },
  appName: {
    fontSize: 32,
    fontWeight: '300',
    letterSpacing: 8,
    color: GidroAtlasColors.black,
    marginBottom: 24,
  },
  welcomeText: {
    fontSize: 20,
    fontWeight: '600',
    color: GidroAtlasColors.black,
    marginBottom: 8,
    textAlign: 'center',
  },
  subtitleText: {
    fontSize: 15,
    color: GidroAtlasColors.gray[500],
    fontWeight: '400',
    textAlign: 'center',
    marginBottom: 24,
  },
  content: {
    paddingHorizontal: 32,
    paddingBottom: 120,
  },
  section: {
    marginBottom: 40,
  },
  sectionLabel: {
    fontSize: 13,
    fontWeight: '600',
    color: GidroAtlasColors.gray[600],
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: 20,
  },
  quickActions: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 16,
  },
  featureCard: {
    width: '47%',
    backgroundColor: GidroAtlasColors.white,
    borderWidth: 1,
    borderColor: GidroAtlasColors.gray[300],
    borderRadius: 16,
    padding: 24,
    alignItems: 'center',
    minHeight: 180,
    justifyContent: 'center',
  },
  iconContainer: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: GidroAtlasColors.persianGreen,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: GidroAtlasColors.black,
    marginBottom: 8,
    textAlign: 'center',
  },
  cardDescription: {
    fontSize: 13,
    color: GidroAtlasColors.gray[500],
    textAlign: 'center',
    lineHeight: 18,
  },
});
