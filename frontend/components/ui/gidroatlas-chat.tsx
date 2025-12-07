/**
 * GidroAtlas Chat Component
 * 
 * Beautiful chat interface inspired by RuixenMoonChat
 * Adapted for React Native with RAG API integration
 * Features: glassmorphism, quick actions, auto-resize input
 */

import React, { useState, useRef, useCallback, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  Dimensions,
  Platform,
  ActivityIndicator,
  KeyboardAvoidingView,
  ImageBackground,
} from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withTiming,
  FadeIn,
  FadeInUp,
  FadeInDown,
  SlideInUp,
  interpolate,
  Extrapolation,
} from 'react-native-reanimated';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { GidroAtlasColors } from '@/constants/theme';
import { ragAPI } from '@/lib/api-services';
import type { RAGQuery, RAGResponse } from '@/lib/gidroatlas-types';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');

// ============================================================================
// Types
// ============================================================================

interface ChatMessage {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  isLoading?: boolean;
}

interface QuickActionProps {
  icon: keyof typeof Ionicons.glyphMap;
  label: string;
  onPress: () => void;
  delay?: number;
}

// ============================================================================
// Quick Action Button Component
// ============================================================================

function QuickAction({ icon, label, onPress, delay = 0 }: QuickActionProps) {
  return (
    <Animated.View entering={FadeInUp.delay(delay).duration(400).springify()}>
      <TouchableOpacity 
        style={styles.quickAction} 
        onPress={onPress}
        activeOpacity={0.7}
      >
        <LinearGradient
          colors={['rgba(45, 154, 134, 0.15)', 'rgba(45, 154, 134, 0.05)']}
          style={styles.quickActionGradient}
        >
          <Ionicons name={icon} size={16} color={GidroAtlasColors.persianGreen} />
          <Text style={styles.quickActionLabel}>{label}</Text>
        </LinearGradient>
      </TouchableOpacity>
    </Animated.View>
  );
}

// ============================================================================
// Message Bubble Component
// ============================================================================

interface MessageBubbleProps {
  message: ChatMessage;
}

function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.sender === 'user';

  return (
    <Animated.View
      entering={FadeInUp.duration(300).springify()}
      style={[
        styles.messageBubble,
        isUser ? styles.userBubble : styles.aiBubble,
      ]}
    >
      {!isUser && (
        <View style={styles.aiAvatar}>
          <Ionicons name="water" size={14} color={GidroAtlasColors.white} />
        </View>
      )}
      <View style={[styles.messageContent, isUser ? styles.userContent : styles.aiContent]}>
        {message.isLoading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="small" color={GidroAtlasColors.persianGreen} />
            <Text style={styles.loadingText}>GidroAtlas is thinking...</Text>
          </View>
        ) : (
          <Text style={[styles.messageText, isUser ? styles.userText : styles.aiText]}>
            {message.text}
          </Text>
        )}
        <Text style={[styles.timestamp, isUser && styles.userTimestamp]}>
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </Text>
      </View>
    </Animated.View>
  );
}

// ============================================================================
// Main Chat Component
// ============================================================================

export default function GidroAtlasChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [inputHeight, setInputHeight] = useState(48);
  const scrollViewRef = useRef<ScrollView>(null);
  const insets = useSafeAreaInsets();

  const MIN_INPUT_HEIGHT = 48;
  const MAX_INPUT_HEIGHT = 120;

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messages.length > 0) {
      setTimeout(() => {
        scrollViewRef.current?.scrollToEnd({ animated: true });
      }, 100);
    }
  }, [messages]);

  // Handle sending message
  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      text: text.trim(),
      sender: 'user',
      timestamp: new Date(),
    };

    // Add user message and loading indicator
    setMessages(prev => [...prev, userMessage, {
      id: `loading-${Date.now()}`,
      text: '',
      sender: 'ai',
      timestamp: new Date(),
      isLoading: true,
    }]);

    setInputText('');
    setInputHeight(MIN_INPUT_HEIGHT);
    setIsLoading(true);

    try {
      const query: RAGQuery = {
        query: text.trim(),
        language: 'ru',
      };

      const response: RAGResponse = await ragAPI.query(query);

      // Replace loading message with actual response
      setMessages(prev => {
        const filtered = prev.filter(m => !m.isLoading);
        return [...filtered, {
          id: `ai-${Date.now()}`,
          text: response.answer,
          sender: 'ai',
          timestamp: new Date(),
        }];
      });
    } catch (error: any) {
      console.error('RAG API Error:', error);
      
      setMessages(prev => {
        const filtered = prev.filter(m => !m.isLoading);
        return [...filtered, {
          id: `ai-error-${Date.now()}`,
          text: 'Извините, произошла ошибка. Попробуйте еще раз.',
          sender: 'ai',
          timestamp: new Date(),
        }];
      });
    } finally {
      setIsLoading(false);
    }
  }, [isLoading]);

  // Quick actions data
  const quickActions = [
    { icon: 'water-outline' as const, label: 'Статус водоёмов', query: 'Какой текущий статус водных объектов в системе?' },
    { icon: 'alert-circle-outline' as const, label: 'Приоритеты', query: 'Покажи объекты с высоким приоритетом' },
    { icon: 'analytics-outline' as const, label: 'Аналитика', query: 'Дай общую аналитику по водным ресурсам' },
    { icon: 'map-outline' as const, label: 'Карта', query: 'Какие водоёмы находятся в критическом состоянии?' },
    { icon: 'document-text-outline' as const, label: 'Паспорта', query: 'Расскажи о системе паспортизации водных объектов' },
    { icon: 'shield-checkmark-outline' as const, label: 'Безопасность', query: 'Какие объекты требуют срочного внимания?' },
  ];

  // Handle new chat
  const handleNewChat = () => {
    setMessages([]);
    setInputText('');
  };

  // Handle content size change for auto-resize
  const handleContentSizeChange = (event: any) => {
    const { height } = event.nativeEvent.contentSize;
    const newHeight = Math.min(Math.max(height, MIN_INPUT_HEIGHT), MAX_INPUT_HEIGHT);
    setInputHeight(newHeight);
  };

  const hasMessages = messages.length > 0;

  return (
    <View style={[styles.container, { paddingTop: insets.top }]}>
      {/* Background with gradient overlay */}
      <LinearGradient
        colors={['#0a1628', '#0f2744', '#0a1628']}
        style={StyleSheet.absoluteFillObject}
      />
      
      {/* Decorative circles */}
      <View style={styles.decorativeCircle1} />
      <View style={styles.decorativeCircle2} />

      {/* Header */}
      <Animated.View 
        entering={FadeInDown.duration(500)}
        style={styles.header}
      >
        <View style={styles.headerLeft}>
          <View style={styles.logoContainer}>
            <Ionicons name="water" size={24} color={GidroAtlasColors.persianGreen} />
          </View>
          <View>
            <Text style={styles.headerTitle}>GidroAtlas AI</Text>
            <Text style={styles.headerSubtitle}>Интеллектуальный помощник</Text>
          </View>
        </View>
        <TouchableOpacity 
          style={styles.newChatButton}
          onPress={handleNewChat}
        >
          <Ionicons name="add-circle-outline" size={20} color={GidroAtlasColors.persianGreen} />
          <Text style={styles.newChatText}>Новый чат</Text>
        </TouchableOpacity>
      </Animated.View>

      {/* Main Content */}
      <KeyboardAvoidingView 
        style={styles.content}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
      >
        {!hasMessages ? (
          /* Welcome Screen */
          <View style={styles.welcomeContainer}>
            <Animated.View 
              entering={FadeIn.delay(200).duration(600)}
              style={styles.welcomeContent}
            >
              {/* Logo Animation */}
              <View style={styles.welcomeLogo}>
                <LinearGradient
                  colors={[GidroAtlasColors.persianGreen, '#1a7a6a']}
                  style={styles.welcomeLogoGradient}
                >
                  <Ionicons name="water" size={48} color={GidroAtlasColors.white} />
                </LinearGradient>
              </View>

              <Text style={styles.welcomeTitle}>GidroAtlas AI</Text>
              <Text style={styles.welcomeSubtitle}>
                Ваш интеллектуальный помощник для управления{'\n'}водными ресурсами Казахстана
              </Text>

              {/* Status indicator */}
              <View style={styles.statusBadge}>
                <View style={styles.statusDot} />
                <Text style={styles.statusText}>Готов к работе</Text>
              </View>
            </Animated.View>

            {/* Quick Actions Grid */}
            <View style={styles.quickActionsContainer}>
              <Text style={styles.quickActionsTitle}>Быстрые действия</Text>
              <View style={styles.quickActionsGrid}>
                {quickActions.map((action, index) => (
                  <QuickAction
                    key={action.label}
                    icon={action.icon}
                    label={action.label}
                    delay={300 + index * 100}
                    onPress={() => sendMessage(action.query)}
                  />
                ))}
              </View>
            </View>
          </View>
        ) : (
          /* Chat Messages */
          <ScrollView
            ref={scrollViewRef}
            style={styles.messagesContainer}
            contentContainerStyle={styles.messagesContent}
            showsVerticalScrollIndicator={false}
          >
            {messages.map(message => (
              <MessageBubble key={message.id} message={message} />
            ))}
          </ScrollView>
        )}

        {/* Input Area */}
        <Animated.View 
          entering={SlideInUp.delay(400).duration(500)}
          style={styles.inputContainer}
        >
          <View style={styles.inputWrapper}>
            {/* Attachment button */}
            <TouchableOpacity style={styles.attachButton}>
              <Ionicons name="attach" size={22} color={GidroAtlasColors.gray[400]} />
            </TouchableOpacity>

            {/* Text Input */}
            <TextInput
              style={[styles.textInput, { height: inputHeight }]}
              value={inputText}
              onChangeText={setInputText}
              placeholder="Введите ваш запрос..."
              placeholderTextColor={GidroAtlasColors.gray[500]}
              multiline
              onContentSizeChange={handleContentSizeChange}
              editable={!isLoading}
            />

            {/* Send Button */}
            <TouchableOpacity
              style={[
                styles.sendButton,
                (!inputText.trim() || isLoading) && styles.sendButtonDisabled
              ]}
              onPress={() => sendMessage(inputText)}
              disabled={!inputText.trim() || isLoading}
            >
              {isLoading ? (
                <ActivityIndicator size="small" color={GidroAtlasColors.white} />
              ) : (
                <Ionicons 
                  name="arrow-up" 
                  size={20} 
                  color={inputText.trim() ? GidroAtlasColors.white : GidroAtlasColors.gray[500]} 
                />
              )}
            </TouchableOpacity>
          </View>

          {/* Quick suggestions when chatting */}
          {hasMessages && !isLoading && (
            <View style={styles.quickSuggestions}>
              <TouchableOpacity 
                style={styles.suggestionChip}
                onPress={() => sendMessage('Покажи больше деталей')}
              >
                <Text style={styles.suggestionText}>Подробнее</Text>
              </TouchableOpacity>
              <TouchableOpacity 
                style={styles.suggestionChip}
                onPress={() => sendMessage('Какие еще есть варианты?')}
              >
                <Text style={styles.suggestionText}>Ещё варианты</Text>
              </TouchableOpacity>
            </View>
          )}
        </Animated.View>
      </KeyboardAvoidingView>
    </View>
  );
}

// ============================================================================
// Styles
// ============================================================================

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a1628',
  },

  // Decorative elements
  decorativeCircle1: {
    position: 'absolute',
    top: -100,
    right: -100,
    width: 300,
    height: 300,
    borderRadius: 150,
    backgroundColor: 'rgba(45, 154, 134, 0.1)',
  },
  decorativeCircle2: {
    position: 'absolute',
    bottom: 100,
    left: -150,
    width: 400,
    height: 400,
    borderRadius: 200,
    backgroundColor: 'rgba(45, 154, 134, 0.05)',
  },

  // Header
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 255, 255, 0.1)',
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  logoContainer: {
    width: 40,
    height: 40,
    borderRadius: 12,
    backgroundColor: 'rgba(45, 154, 134, 0.2)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: GidroAtlasColors.white,
  },
  headerSubtitle: {
    fontSize: 12,
    color: GidroAtlasColors.gray[400],
    marginTop: 2,
  },
  newChatButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: 'rgba(45, 154, 134, 0.3)',
  },
  newChatText: {
    fontSize: 13,
    color: GidroAtlasColors.persianGreen,
    fontWeight: '500',
  },

  // Content
  content: {
    flex: 1,
  },

  // Welcome Screen
  welcomeContainer: {
    flex: 1,
    justifyContent: 'center',
    paddingHorizontal: 20,
  },
  welcomeContent: {
    alignItems: 'center',
    marginBottom: 40,
  },
  welcomeLogo: {
    marginBottom: 24,
  },
  welcomeLogoGradient: {
    width: 100,
    height: 100,
    borderRadius: 30,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: GidroAtlasColors.persianGreen,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.4,
    shadowRadius: 20,
    elevation: 10,
  },
  welcomeTitle: {
    fontSize: 32,
    fontWeight: '700',
    color: GidroAtlasColors.white,
    marginBottom: 12,
  },
  welcomeSubtitle: {
    fontSize: 15,
    color: GidroAtlasColors.gray[400],
    textAlign: 'center',
    lineHeight: 22,
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginTop: 20,
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: 'rgba(45, 154, 134, 0.15)',
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#4ade80',
  },
  statusText: {
    fontSize: 13,
    color: GidroAtlasColors.persianGreen,
    fontWeight: '500',
  },

  // Quick Actions
  quickActionsContainer: {
    marginTop: 20,
  },
  quickActionsTitle: {
    fontSize: 14,
    color: GidroAtlasColors.gray[500],
    marginBottom: 16,
    textAlign: 'center',
  },
  quickActionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    gap: 10,
  },
  quickAction: {
    borderRadius: 20,
    overflow: 'hidden',
  },
  quickActionGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: 'rgba(45, 154, 134, 0.2)',
  },
  quickActionLabel: {
    fontSize: 13,
    color: GidroAtlasColors.gray[300],
    fontWeight: '500',
  },

  // Messages
  messagesContainer: {
    flex: 1,
  },
  messagesContent: {
    padding: 20,
    paddingBottom: 100,
  },
  messageBubble: {
    flexDirection: 'row',
    marginBottom: 16,
    maxWidth: '85%',
  },
  userBubble: {
    alignSelf: 'flex-end',
    flexDirection: 'row-reverse',
  },
  aiBubble: {
    alignSelf: 'flex-start',
  },
  aiAvatar: {
    width: 32,
    height: 32,
    borderRadius: 10,
    backgroundColor: GidroAtlasColors.persianGreen,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 10,
  },
  messageContent: {
    borderRadius: 16,
    padding: 14,
  },
  userContent: {
    backgroundColor: GidroAtlasColors.persianGreen,
    borderBottomRightRadius: 4,
  },
  aiContent: {
    backgroundColor: 'rgba(255, 255, 255, 0.08)',
    borderBottomLeftRadius: 4,
  },
  messageText: {
    fontSize: 15,
    lineHeight: 22,
  },
  userText: {
    color: GidroAtlasColors.white,
  },
  aiText: {
    color: GidroAtlasColors.gray[200],
  },
  timestamp: {
    fontSize: 11,
    color: 'rgba(255, 255, 255, 0.4)',
    marginTop: 6,
  },
  userTimestamp: {
    textAlign: 'right',
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  loadingText: {
    fontSize: 14,
    color: GidroAtlasColors.gray[400],
    fontStyle: 'italic',
  },

  // Input Area
  inputContainer: {
    paddingHorizontal: 20,
    paddingVertical: 16,
    paddingBottom: Platform.OS === 'ios' ? 30 : 20,
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    backgroundColor: 'rgba(255, 255, 255, 0.08)',
    borderRadius: 24,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
    paddingHorizontal: 6,
    paddingVertical: 6,
  },
  attachButton: {
    width: 40,
    height: 40,
    alignItems: 'center',
    justifyContent: 'center',
  },
  textInput: {
    flex: 1,
    fontSize: 15,
    color: GidroAtlasColors.white,
    paddingHorizontal: 8,
    paddingVertical: 10,
    maxHeight: 120,
  },
  sendButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: GidroAtlasColors.persianGreen,
    alignItems: 'center',
    justifyContent: 'center',
  },
  sendButtonDisabled: {
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
  },

  // Quick Suggestions
  quickSuggestions: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 10,
    marginTop: 12,
  },
  suggestionChip: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 16,
    backgroundColor: 'rgba(255, 255, 255, 0.08)',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  suggestionText: {
    fontSize: 13,
    color: GidroAtlasColors.gray[400],
  },
});
