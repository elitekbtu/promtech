/**
 * Zaman AI Chat Component
 * 
 * Beautiful chat interface with RAG API integration
 * Styled to match ZAMAN brand identity
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';
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
} from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withTiming,
  FadeIn,
  FadeInUp,
  SlideInUp,
} from 'react-native-reanimated';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { GidroAtlasColors } from '@/constants/theme';
import { ragAPI } from '@/lib/api-services';
import type { RAGQuery, RAGResponse } from '@/lib/gidroatlas-types';

// Use GidroAtlas colors as Zaman colors
const ZamanColors = GidroAtlasColors;

const { width: SCREEN_WIDTH } = Dimensions.get('window');

interface ChatMessage {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  isLoading?: boolean;
}

interface QuickStarterProps {
  icon: keyof typeof Ionicons.glyphMap;
  text: string;
  onPress: () => void;
}

function QuickStarter({ icon, text, onPress }: QuickStarterProps) {
  return (
    <TouchableOpacity style={styles.quickStarter} onPress={onPress} activeOpacity={0.7}>
      <Ionicons name={icon} size={16} color={ZamanColors.persianGreen} />
      <Text style={styles.quickStarterText}>{text}</Text>
    </TouchableOpacity>
  );
}

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
          <Ionicons name="sparkles" size={16} color={ZamanColors.white} />
        </View>
      )}
      <View style={[styles.messageContent, isUser ? styles.userContent : styles.aiContent]}>
        {message.isLoading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="small" color={ZamanColors.persianGreen} />
            <Text style={styles.loadingText}>Thinking...</Text>
          </View>
        ) : (
          <Text style={[styles.messageText, isUser ? styles.userText : styles.aiText]}>
            {message.text}
          </Text>
        )}
        <Text style={styles.timestamp}>
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </Text>
      </View>
    </Animated.View>
  );
}

export default function ZamanChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(true);
  const scrollViewRef = useRef<ScrollView>(null);
  const inputRef = useRef<TextInput>(null);

  // Initial greeting message
  useEffect(() => {
    const greeting: ChatMessage = {
      id: 'greeting',
      text: "I'm Zaman. Your future self asked me to help you get there.",
      sender: 'ai',
      timestamp: new Date(),
    };
    setMessages([greeting]);
  }, []);

  // Scroll to bottom when messages change
  useEffect(() => {
    setTimeout(() => {
      scrollViewRef.current?.scrollToEnd({ animated: true });
    }, 100);
  }, [messages]);

  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      text: text.trim(),
      sender: 'user',
      timestamp: new Date(),
    };

    const loadingMessage: ChatMessage = {
      id: `ai-loading-${Date.now()}`,
      text: '',
      sender: 'ai',
      timestamp: new Date(),
      isLoading: true,
    };

    setMessages(prev => [...prev, userMessage, loadingMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      const query: RAGQuery = {
        query: text.trim(),
        language: 'en',
      };

      const response: RAGResponse = await ragAPI.query(query);

      // Remove loading message and add real response
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
      
      // Remove loading message and add error message
      setMessages(prev => {
        const filtered = prev.filter(m => !m.isLoading);
        return [...filtered, {
          id: `ai-error-${Date.now()}`,
          text: "Sorry, I couldn't process your request. Please try again.",
          sender: 'ai',
          timestamp: new Date(),
        }];
      });
    } finally {
      setIsLoading(false);
    }
  }, [isLoading]);

  const quickStarters = [
    {
      icon: 'bulb-outline' as const,
      text: 'What Islamic banking products does Zaman offer?',
    },
    {
      icon: 'shield-checkmark-outline' as const,
      text: 'How does Zaman ensure Sharia compliance in its services?',
    },
    {
      icon: 'wallet-outline' as const,
      text: 'How can I open a halal savings account with Zaman?',
    },
    {
      icon: 'trending-up-outline' as const,
      text: 'What investment opportunities are available in Islamic banking?',
    },
  ];

  const showEmptyState = messages.length <= 1;

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.headerTitle}>Chat with Zaman</Text>
          <Text style={styles.headerSubtitle}>Your AI Wellness Coach</Text>
        </View>
        <View style={styles.statusBadge}>
          <View style={[styles.statusDot, isConnected && styles.statusDotConnected]} />
          <Text style={styles.statusText}>{isConnected ? 'Ready' : 'Offline'}</Text>
        </View>
      </View>

      {/* Chat Area */}
      <KeyboardAvoidingView
        style={styles.chatContainer}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
      >
        <ScrollView
          ref={scrollViewRef}
          style={styles.messagesContainer}
          contentContainerStyle={styles.messagesContent}
          showsVerticalScrollIndicator={false}
        >
          {/* Logo & Welcome */}
          {showEmptyState && (
            <Animated.View entering={FadeIn.duration(500)} style={styles.welcomeSection}>
              <View style={styles.logoContainer}>
                <Ionicons name="diamond" size={40} color={ZamanColors.persianGreen} />
              </View>
              <View style={styles.statusIndicator}>
                <View style={styles.readyDot} />
                <Text style={styles.readyText}>Ready</Text>
              </View>
            </Animated.View>
          )}

          {/* Messages */}
          {messages.map(message => (
            <MessageBubble key={message.id} message={message} />
          ))}

          {/* Quick Starters */}
          {showEmptyState && (
            <Animated.View entering={FadeInUp.delay(300).duration(500)} style={styles.quickStartersSection}>
              <Text style={styles.quickStartersTitle}>QUICK STARTERS:</Text>
              {quickStarters.map((starter, index) => (
                <QuickStarter
                  key={index}
                  icon={starter.icon}
                  text={starter.text}
                  onPress={() => sendMessage(starter.text)}
                />
              ))}
            </Animated.View>
          )}
        </ScrollView>

        {/* Input Area */}
        <View style={styles.inputContainer}>
          <View style={styles.inputWrapper}>
            <TextInput
              ref={inputRef}
              style={styles.textInput}
              placeholder="Message Zaman..."
              placeholderTextColor={ZamanColors.gray[400]}
              value={inputText}
              onChangeText={setInputText}
              multiline
              maxLength={1000}
              editable={!isLoading}
              onSubmitEditing={() => sendMessage(inputText)}
              blurOnSubmit={false}
            />
            <TouchableOpacity
              style={[
                styles.sendButton,
                (!inputText.trim() || isLoading) && styles.sendButtonDisabled,
              ]}
              onPress={() => sendMessage(inputText)}
              disabled={!inputText.trim() || isLoading}
            >
              {isLoading ? (
                <ActivityIndicator size="small" color={ZamanColors.white} />
              ) : (
                <Ionicons
                  name="send"
                  size={20}
                  color={inputText.trim() ? ZamanColors.white : ZamanColors.gray[400]}
                />
              )}
            </TouchableOpacity>
          </View>
        </View>
      </KeyboardAvoidingView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: ZamanColors.cloud,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: Platform.OS === 'ios' ? 60 : 40,
    paddingBottom: 16,
    backgroundColor: ZamanColors.white,
    borderBottomWidth: 1,
    borderBottomColor: ZamanColors.gray[200],
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: ZamanColors.black,
  },
  headerSubtitle: {
    fontSize: 13,
    color: ZamanColors.gray[500],
    marginTop: 2,
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: ZamanColors.cloud,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    gap: 6,
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: ZamanColors.gray[400],
  },
  statusDotConnected: {
    backgroundColor: '#22C55E',
  },
  statusText: {
    fontSize: 12,
    color: ZamanColors.gray[600],
    fontWeight: '500',
  },
  chatContainer: {
    flex: 1,
  },
  messagesContainer: {
    flex: 1,
  },
  messagesContent: {
    padding: 20,
    paddingBottom: 100,
  },
  welcomeSection: {
    alignItems: 'center',
    marginBottom: 24,
    marginTop: 40,
  },
  logoContainer: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: ZamanColors.white,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 4,
    marginBottom: 16,
  },
  statusIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  readyDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#22C55E',
  },
  readyText: {
    fontSize: 13,
    color: ZamanColors.gray[600],
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
    borderRadius: 16,
    backgroundColor: ZamanColors.persianGreen,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 8,
  },
  messageContent: {
    borderRadius: 16,
    paddingHorizontal: 16,
    paddingVertical: 12,
    maxWidth: SCREEN_WIDTH * 0.7,
  },
  userContent: {
    backgroundColor: ZamanColors.persianGreen,
    borderBottomRightRadius: 4,
  },
  aiContent: {
    backgroundColor: ZamanColors.white,
    borderBottomLeftRadius: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  messageText: {
    fontSize: 15,
    lineHeight: 22,
  },
  userText: {
    color: ZamanColors.white,
  },
  aiText: {
    color: ZamanColors.black,
  },
  timestamp: {
    fontSize: 11,
    color: ZamanColors.gray[400],
    marginTop: 6,
    alignSelf: 'flex-end',
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  loadingText: {
    fontSize: 14,
    color: ZamanColors.gray[500],
    fontStyle: 'italic',
  },
  quickStartersSection: {
    marginTop: 24,
  },
  quickStartersTitle: {
    fontSize: 11,
    fontWeight: '600',
    color: ZamanColors.gray[500],
    letterSpacing: 1,
    marginBottom: 12,
  },
  quickStarter: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: ZamanColors.white,
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderRadius: 12,
    marginBottom: 8,
    gap: 12,
    borderWidth: 1,
    borderColor: ZamanColors.gray[200],
  },
  quickStarterText: {
    flex: 1,
    fontSize: 14,
    color: ZamanColors.gray[700],
  },
  inputContainer: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: ZamanColors.white,
    paddingHorizontal: 16,
    paddingVertical: 12,
    paddingBottom: Platform.OS === 'ios' ? 32 : 16,
    borderTopWidth: 1,
    borderTopColor: ZamanColors.gray[200],
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    backgroundColor: ZamanColors.cloud,
    borderRadius: 24,
    paddingHorizontal: 16,
    paddingVertical: 8,
    gap: 12,
  },
  textInput: {
    flex: 1,
    fontSize: 16,
    color: ZamanColors.black,
    maxHeight: 100,
    paddingVertical: 8,
  },
  sendButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: ZamanColors.persianGreen,
    alignItems: 'center',
    justifyContent: 'center',
  },
  sendButtonDisabled: {
    backgroundColor: ZamanColors.gray[300],
  },
});
