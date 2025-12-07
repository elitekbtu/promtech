import { Tabs, Redirect, usePathname, useRouter } from 'expo-router';
import React from 'react';
import { ActivityIndicator, View } from 'react-native';

import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { useAuth } from '@/hooks/use-auth';
import DockMorph from '@/components/ui/dock-morph';

export default function TabLayout() {
  const colorScheme = useColorScheme();
  const { authenticated, loading } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" color={Colors[colorScheme ?? 'light'].tint} />
      </View>
    );
  }

  if (!authenticated) {
    return <Redirect href="/login" />;
  }

  // Define dock items
  const dockItems = [
    {
      icon: 'home' as const,
      label: 'Home',
      onPress: () => router.push('/(tabs)/'),
    },
    {
      icon: 'compass' as const,
      label: 'Explore',
      onPress: () => router.push('/(tabs)/explore'),
    },
    {
      icon: 'chatbubbles' as const,
      label: 'Live Chat',
      onPress: () => router.push('/(tabs)/live-chat'),
      badge: 3, // Example badge
    },
  ];

  // Determine active index based on pathname
  const getActiveIndex = () => {
    if (pathname === '/(tabs)' || pathname === '/(tabs)/index') return 0;
    if (pathname.includes('explore')) return 1;
    if (pathname.includes('live-chat')) return 2;
    return 0;
  };

  return (
    <>
      <Tabs
        screenOptions={{
          headerShown: false,
          tabBarStyle: { display: 'none' }, // Hide default tab bar
        }}>
        <Tabs.Screen name="index" />
        <Tabs.Screen name="explore" />
        <Tabs.Screen name="live-chat" />
      </Tabs>
      
      {/* Custom DockMorph Navigation */}
      <DockMorph
        items={dockItems}
        activeIndex={getActiveIndex()}
        position="bottom"
        variant="glass"
      />
    </>
  );
}
