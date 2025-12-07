import { StyleSheet, View, Text, TextInput, TouchableOpacity, Alert, Modal, Image, ActivityIndicator, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
import { useState } from 'react';
import { useRouter } from 'expo-router';
import FaceCamera from '@/components/face-camera';
import GidroAtlasLogo from '@/components/gidroatlas-logo';
import { Ionicons } from '@expo/vector-icons';
import { GidroAtlasColors } from '@/constants/theme';
import { config } from '@/lib/config';
import { TokenResponse, saveAuthResponse } from '@/lib/auth';

interface FaceVerificationResult {
  success: boolean;
  verified: boolean;
  message: string;
  token?: TokenResponse;
  confidence?: number;
  distance?: number;
  threshold?: number;
  model?: string;
  error?: string;
}

export default function LoginScreen() {
  const router = useRouter();
  const [view, setView] = useState<'selection' | 'expert'>('selection');
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [showCamera, setShowCamera] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  
  // Form fields
  const [name, setName] = useState('');
  const [surname, setSurname] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [capturedPhoto, setCapturedPhoto] = useState<string | null>(null);
  
  const resetForm = () => {
    setName('');
    setSurname('');
    setEmail('');
    setPhone('');
    setPassword('');
    setCapturedPhoto(null);
  };

  const switchMode = () => {
    setMode(mode === 'login' ? 'register' : 'login');
    resetForm();
  };

  async function handlePhotoCapture(photoUri: string) {
    setCapturedPhoto(photoUri);
    setShowCamera(false);
  }

  async function saveUserSession(tokenResponse: TokenResponse) {
    try {
      await saveAuthResponse(tokenResponse);
      console.log('✅ Auth data saved securely (role:', tokenResponse.user.role, ')');
    } catch (error) {
      console.error('❌ Error saving user session:', error);
      throw error;
    }
  }

  function validateEmail(email: string): boolean {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email.trim());
  }

  async function handleGuestLogin() {
    setIsLoading(true);
    try {
      // Create dummy guest session
      const guestToken: TokenResponse = {
        access_token: 'guest-token',
        token_type: 'bearer',
        user: {
          id: 0,
          name: 'Guest',
          surname: 'User',
          email: 'guest@gidroatlas.kz',
          phone: '',
          role: 'guest',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        }
      };
      
      await saveUserSession(guestToken);
      console.log('✅ Guest login successful');
      router.replace('/(tabs)');
    } catch (error) {
      console.error('Error during guest login:', error);
      Alert.alert('Error', 'Could not login as guest');
    } finally {
      setIsLoading(false);
    }
  }

  async function handleFaceVerify() {
    if (!capturedPhoto) {
      Alert.alert('Error', 'Please capture a photo first');
      return;
    }

    if (isLoading) return;
    setIsLoading(true);
    
    try {
      const response = await fetch(capturedPhoto);
      const blob = await response.blob();
      
      const formData = new FormData();
      // @ts-ignore
      formData.append('file', blob, 'photo.jpg');

      const verifyResponse = await fetch(`${config.backendURL}/api/faceid/verify`, {
        method: 'POST',
        body: formData,
      });

      if (!verifyResponse.ok) {
        throw new Error(`Server error: ${verifyResponse.status}`);
      }

      const result: FaceVerificationResult = await verifyResponse.json();

      if (result.success && result.verified && result.token) {
        setCapturedPhoto(null);
        await saveUserSession(result.token);
        router.replace('/(tabs)');
      } else if (result.success && !result.verified) {
        Alert.alert('❌ Face Not Recognized', result.message || 'No matching face found.');
      } else {
        Alert.alert('❌ Login Failed', result.message || 'Face verification failed.');
      }
    } catch (error: any) {
      console.error('Error during face verification:', error);
      Alert.alert('🔌 Connection Error', 'Could not connect to the server.');
    } finally {
      setIsLoading(false);
    }
  }

  async function handleEmailPasswordLogin() {
    if (!email.trim() || !password.trim()) {
      Alert.alert('❌ Validation Error', 'Please enter both email and password');
      return;
    }

    if (!validateEmail(email)) {
      Alert.alert('❌ Invalid Email', 'Please enter a valid email address');
      return;
    }

    setIsLoading(true);

    try {
      const loginResponse = await fetch(`${config.backendURL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: email.trim().toLowerCase(),
          password: password,
        }),
      });

      if (loginResponse.ok) {
        const tokenData: TokenResponse = await loginResponse.json();
        await saveUserSession(tokenData);
        router.replace('/(tabs)');
      } else {
        const errorData = await loginResponse.json();
        Alert.alert('❌ Login Failed', errorData.detail || 'Login failed');
      }
    } catch (error) {
      console.error('Error during login:', error);
      Alert.alert('🔌 Connection Error', 'Could not connect to the server.');
    } finally {
      setIsLoading(false);
    }
  }

  async function handleRegister() {
    if (!name.trim() || !surname.trim() || !email.trim() || !phone.trim() || !password.trim()) {
      Alert.alert('❌ Validation Error', 'Please fill in all required fields');
      return;
    }

    if (!validateEmail(email)) {
      Alert.alert('❌ Invalid Email', 'Please enter a valid email address');
      return;
    }

    if (!capturedPhoto) {
      Alert.alert('❌ Photo Required', 'Please capture your face photo for Face ID registration');
      return;
    }

    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append('name', name.trim());
      formData.append('surname', surname.trim());
      formData.append('email', email.trim().toLowerCase());
      formData.append('phone', phone.trim());
      formData.append('password', password);

      const response = await fetch(capturedPhoto);
      const blob = await response.blob();
      // @ts-ignore
      formData.append('avatar', blob, 'avatar.jpg');

      const registerResponse = await fetch(`${config.backendURL}/api/auth/register`, {
        method: 'POST',
        body: formData,
      });

      if (registerResponse.ok) {
        const tokenData: TokenResponse = await registerResponse.json();
        setCapturedPhoto(null);
        await saveUserSession(tokenData);
        router.replace('/(tabs)');
      } else {
        const errorData = await registerResponse.json();
        Alert.alert('❌ Registration Failed', errorData.detail || 'Registration failed');
      }
    } catch (error) {
      console.error('Error during registration:', error);
      Alert.alert('🔌 Connection Error', 'Could not connect to the server.');
    } finally {
      setIsLoading(false);
    }
  }

  if (view === 'selection') {
    return (
      <View style={styles.container}>
        <View style={styles.header}>
          <View style={styles.logoMark}>
            <GidroAtlasLogo size={90} withAccent />
          </View>
          <Text style={styles.appName}>GidroAtlas</Text>
          <Text style={styles.tagline}>Select your role</Text>
        </View>

        <View style={styles.content}>
          <TouchableOpacity 
            style={styles.roleButton}
            onPress={handleGuestLogin}
            disabled={isLoading}
          >
            <Ionicons name="person-outline" size={32} color={GidroAtlasColors.black} />
            <Text style={styles.roleButtonText}>Enter as Guest</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={[styles.roleButton, styles.expertButton]}
            onPress={() => setView('expert')}
            disabled={isLoading}
          >
            <Ionicons name="briefcase-outline" size={32} color={GidroAtlasColors.white} />
            <Text style={[styles.roleButtonText, styles.expertButtonText]}>Enter as Expert</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <KeyboardAvoidingView 
        style={styles.keyboardView} 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <ScrollView 
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          {/* Header with Back Button */}
          <View style={styles.header}>
            <TouchableOpacity 
              style={styles.backButton} 
              onPress={() => setView('selection')}
            >
              <Ionicons name="arrow-back" size={24} color={GidroAtlasColors.black} />
            </TouchableOpacity>
            
            <View style={styles.logoMark}>
              <GidroAtlasLogo size={90} withAccent />
            </View>
            <Text style={styles.appName}>GidroAtlas</Text>
            <Text style={styles.tagline}>
              {mode === 'login' ? 'Expert Login' : 'Expert Registration'}
            </Text>
          </View>

          {/* Content */}
          <View style={styles.content}>
            {/* Face ID Section */}
            <View style={styles.section}>
              <Text style={styles.sectionLabel}>
                {mode === 'login' ? 'Face ID' : 'Face ID (Required)'}
              </Text>
              
              {capturedPhoto ? (
                <View style={styles.photoContainer}>
                  <Image source={{ uri: capturedPhoto }} style={styles.photo} />
                  <TouchableOpacity 
                    style={styles.linkButton}
                    onPress={() => setShowCamera(true)}
                    disabled={isLoading}
                  >
                    <Text style={styles.linkText}>Retake</Text>
                  </TouchableOpacity>
                </View>
              ) : (
                <TouchableOpacity 
                  style={styles.captureButton}
                  onPress={() => setShowCamera(true)}
                  disabled={isLoading}
                >
                  <Ionicons name="camera-outline" size={24} color={GidroAtlasColors.persianGreen} />
                  <Text style={styles.captureButtonText}>
                    {mode === 'login' ? 'Scan face' : 'Capture face'}
                  </Text>
                </TouchableOpacity>
              )}

              {mode === 'login' && capturedPhoto && (
                <TouchableOpacity 
                  style={styles.primaryButton}
                  onPress={handleFaceVerify}
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <ActivityIndicator color={GidroAtlasColors.black} />
                  ) : (
                    <Text style={styles.primaryButtonText}>Verify & Login</Text>
                  )}
                </TouchableOpacity>
              )}
            </View>

            {/* Divider */}
            {mode === 'login' && (
              <View style={styles.divider}>
                <View style={styles.dividerLine} />
                <Text style={styles.dividerText}>or</Text>
                <View style={styles.dividerLine} />
              </View>
            )}

            {/* Email/Password Login */}
            {mode === 'login' && (
              <View style={styles.section}>
                <Text style={styles.sectionLabel}>Email & Password</Text>
                
                <TextInput
                  style={styles.input}
                  placeholder="Email"
                  placeholderTextColor={GidroAtlasColors.gray[400]}
                  value={email}
                  onChangeText={setEmail}
                  keyboardType="email-address"
                  autoCapitalize="none"
                  editable={!isLoading}
                />
                
                <TextInput
                  style={styles.input}
                  placeholder="Password"
                  placeholderTextColor={GidroAtlasColors.gray[400]}
                  value={password}
                  onChangeText={setPassword}
                  secureTextEntry
                  editable={!isLoading}
                />
                
                <TouchableOpacity 
                  style={styles.primaryButton}
                  onPress={handleEmailPasswordLogin}
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <ActivityIndicator color={GidroAtlasColors.black} />
                  ) : (
                    <Text style={styles.primaryButtonText}>Login</Text>
                  )}
                </TouchableOpacity>
              </View>
            )}

            {/* Register Form */}
            {mode === 'register' && (
              <View style={styles.section}>
                <Text style={styles.sectionLabel}>Personal Information</Text>
                
                <TextInput
                  style={styles.input}
                  placeholder="First name"
                  placeholderTextColor={GidroAtlasColors.gray[400]}
                  value={name}
                  onChangeText={setName}
                  autoCapitalize="words"
                  editable={!isLoading}
                />
                
                <TextInput
                  style={styles.input}
                  placeholder="Last name"
                  placeholderTextColor={GidroAtlasColors.gray[400]}
                  value={surname}
                  onChangeText={setSurname}
                  autoCapitalize="words"
                  editable={!isLoading}
                />
                
                <TextInput
                  style={styles.input}
                  placeholder="Email"
                  placeholderTextColor={GidroAtlasColors.gray[400]}
                  value={email}
                  onChangeText={setEmail}
                  keyboardType="email-address"
                  autoCapitalize="none"
                  editable={!isLoading}
                />
                
                <TextInput
                  style={styles.input}
                  placeholder="Phone"
                  placeholderTextColor={GidroAtlasColors.gray[400]}
                  value={phone}
                  onChangeText={setPhone}
                  keyboardType="phone-pad"
                  editable={!isLoading}
                />
                
                <TextInput
                  style={styles.input}
                  placeholder="Password (min 8 characters)"
                  placeholderTextColor={GidroAtlasColors.gray[400]}
                  value={password}
                  onChangeText={setPassword}
                  secureTextEntry
                  editable={!isLoading}
                />

                <TouchableOpacity 
                  style={styles.primaryButton}
                  onPress={handleRegister}
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <ActivityIndicator color={GidroAtlasColors.black} />
                  ) : (
                    <Text style={styles.primaryButtonText}>Create Account</Text>
                  )}
                </TouchableOpacity>
              </View>
            )}

            {/* Switch Mode */}
            <TouchableOpacity 
              style={styles.switchButton}
              onPress={switchMode}
              disabled={isLoading}
            >
              <Text style={styles.switchText}>
                {mode === 'login' 
                  ? "Don't have an account? " 
                  : 'Already have an account? '}
              </Text>
              <Text style={styles.switchTextBold}>
                {mode === 'login' ? 'Sign up' : 'Sign in'}
              </Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>

      {/* Camera Modal */}
      <Modal
        visible={showCamera}
        animationType="slide"
        presentationStyle="fullScreen"
      >
        <FaceCamera
          onCapture={handlePhotoCapture}
          onClose={() => setShowCamera(false)}
          isVerifying={false}
        />
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: GidroAtlasColors.white,
  },
  keyboardView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
  },
  header: {
    paddingTop: Platform.OS === 'ios' ? 80 : 60,
    paddingBottom: 40,
    paddingHorizontal: 32,
    alignItems: 'center',
    position: 'relative',
  },
  backButton: {
    position: 'absolute',
    top: Platform.OS === 'ios' ? 80 : 60,
    left: 32,
    zIndex: 10,
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
    marginBottom: 8,
  },
  tagline: {
    fontSize: 15,
    color: GidroAtlasColors.gray[500],
    fontWeight: '400',
  },
  content: {
    paddingHorizontal: 32,
    paddingBottom: 40,
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
    marginBottom: 16,
  },
  captureButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: GidroAtlasColors.white,
    borderWidth: 1,
    borderColor: GidroAtlasColors.gray[300],
    borderRadius: 12,
    paddingVertical: 20,
    gap: 12,
  },
  captureButtonText: {
    fontSize: 16,
    color: GidroAtlasColors.persianGreen,
    fontWeight: '500',
  },
  photoContainer: {
    alignItems: 'center',
    gap: 16,
  },
  photo: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: GidroAtlasColors.gray[100],
    borderWidth: 2,
    borderColor: GidroAtlasColors.persianGreen,
  },
  linkButton: {
    paddingVertical: 8,
  },
  linkText: {
    fontSize: 15,
    color: GidroAtlasColors.persianGreen,
    fontWeight: '500',
  },
  input: {
    backgroundColor: GidroAtlasColors.white,
    borderWidth: 1,
    borderColor: GidroAtlasColors.gray[300],
    borderRadius: 12,
    paddingVertical: 16,
    paddingHorizontal: 16,
    fontSize: 16,
    color: GidroAtlasColors.black,
    marginBottom: 12,
  },
  primaryButton: {
    backgroundColor: GidroAtlasColors.solar,
    borderRadius: 12,
    paddingVertical: 18,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 8,
  },
  primaryButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: GidroAtlasColors.black,
  },
  divider: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 32,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: GidroAtlasColors.gray[200],
  },
  dividerText: {
    marginHorizontal: 16,
    fontSize: 13,
    color: GidroAtlasColors.gray[400],
    fontWeight: '400',
  },
  switchButton: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: 32,
    paddingVertical: 16,
  },
  switchText: {
    fontSize: 15,
    color: GidroAtlasColors.gray[600],
  },
  switchTextBold: {
    fontSize: 15,
    color: GidroAtlasColors.persianGreen,
    fontWeight: '600',
  },
  roleButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: GidroAtlasColors.white,
    borderWidth: 1,
    borderColor: GidroAtlasColors.gray[300],
    borderRadius: 16,
    paddingVertical: 24,
    marginBottom: 20,
    gap: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  roleButtonText: {
    fontSize: 18,
    fontWeight: '600',
    color: GidroAtlasColors.black,
  },
  expertButton: {
    backgroundColor: GidroAtlasColors.black,
    borderColor: GidroAtlasColors.black,
  },
  expertButtonText: {
    color: GidroAtlasColors.white,
  },
});

