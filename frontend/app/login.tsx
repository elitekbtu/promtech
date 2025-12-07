import { StyleSheet, View, Text, TextInput, TouchableOpacity, Alert, Modal, Image, ActivityIndicator, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
import { useState } from 'react';
import { useRouter } from 'expo-router';
import FaceCamera from '@/components/face-camera';
import ZamanLogo from '@/components/zaman-logo';
import { Ionicons } from '@expo/vector-icons';
import { ZamanColors } from '@/constants/theme';
import { config } from '@/lib/config';
import { TokenResponse, saveAuthResponse } from '@/lib/auth';
import { AuroraBackground } from '@/components/ui/aurora-background';
import { AnimatedButton, AnimatedText, AnimatedContainer } from '@/components/ui/animated-button';

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
      <AuroraBackground
        primaryColor={ZamanColors.persianGreen}
        secondaryColor="#4FD1C5"
        accentColor={ZamanColors.solar}
        backgroundColor={ZamanColors.white}
        intensity={0.5}
      >
        <View style={styles.selectionContainer}>
          {/* Animated Header */}
          <AnimatedContainer delay={100} style={styles.header}>
            <View style={styles.logoMark}>
              <ZamanLogo size={90} withAccent />
            </View>
          </AnimatedContainer>
          
          <AnimatedText variant="title" delay={200} style={styles.appName}>
            ZAMAN
          </AnimatedText>
          
          <AnimatedText variant="subtitle" delay={300} style={styles.tagline}>
            Select your role
          </AnimatedText>

          {/* Animated Buttons */}
          <View style={styles.buttonContainer}>
            <AnimatedButton
              title="Enter as Guest"
              icon="person-outline"
              variant="default"
              delay={500}
              onPress={handleGuestLogin}
              disabled={isLoading}
            />

            <AnimatedButton
              title="Enter as Expert"
              icon="briefcase-outline"
              variant="dark"
              delay={650}
              onPress={() => setView('expert')}
              disabled={isLoading}
            />
          </View>
        </View>
      </AuroraBackground>
    );
  }

  return (
    <AuroraBackground
      primaryColor={ZamanColors.persianGreen}
      secondaryColor="#4FD1C5"
      accentColor={ZamanColors.solar}
      backgroundColor={ZamanColors.white}
      intensity={0.4}
    >
      <KeyboardAvoidingView 
        style={styles.keyboardView} 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <ScrollView 
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          {/* Back Button */}
          <TouchableOpacity 
            style={styles.backButton} 
            onPress={() => setView('selection')}
          >
            <Ionicons name="arrow-back" size={24} color={ZamanColors.black} />
          </TouchableOpacity>

          {/* Centered Content */}
          <View style={styles.authContainer}>
            {/* Header */}
            <AnimatedContainer delay={100} style={styles.authHeader}>
              <View style={styles.logoMark}>
                <ZamanLogo size={70} withAccent />
              </View>
            </AnimatedContainer>
            
            <AnimatedText variant="title" delay={150} style={styles.authTitle}>
              {mode === 'login' ? 'Welcome back' : 'Create account'}
            </AnimatedText>
            
            <AnimatedText variant="subtitle" delay={200} style={styles.authSubtitle}>
              {mode === 'login' 
                ? 'Sign in to continue to ZAMAN' 
                : 'Join ZAMAN as an expert'}
            </AnimatedText>

            {/* Face ID Button - Primary Auth */}
            <AnimatedContainer delay={300} style={styles.faceIdSection}>
              {capturedPhoto ? (
                <View style={styles.capturedPhotoSection}>
                  <Image source={{ uri: capturedPhoto }} style={styles.capturedPhoto} />
                  <View style={styles.photoActions}>
                    <TouchableOpacity 
                      style={styles.retakeButton}
                      onPress={() => setShowCamera(true)}
                      disabled={isLoading}
                    >
                      <Ionicons name="refresh-outline" size={20} color={ZamanColors.persianGreen} />
                      <Text style={styles.retakeText}>Retake</Text>
                    </TouchableOpacity>
                    
                    {mode === 'login' && (
                      <TouchableOpacity 
                        style={styles.faceLoginButton}
                        onPress={handleFaceVerify}
                        disabled={isLoading}
                      >
                        {isLoading ? (
                          <ActivityIndicator color={ZamanColors.white} />
                        ) : (
                          <>
                            <Ionicons name="scan-outline" size={20} color={ZamanColors.white} />
                            <Text style={styles.faceLoginButtonText}>Verify Face ID</Text>
                          </>
                        )}
                      </TouchableOpacity>
                    )}
                  </View>
                </View>
              ) : (
                <TouchableOpacity 
                  style={styles.faceIdButton}
                  onPress={() => setShowCamera(true)}
                  disabled={isLoading}
                >
                  <View style={styles.faceIdIconContainer}>
                    <Ionicons name="scan" size={32} color={ZamanColors.white} />
                  </View>
                  <View style={styles.faceIdTextContainer}>
                    <Text style={styles.faceIdButtonTitle}>
                      {mode === 'login' ? 'Sign in with Face ID' : 'Capture Face ID'}
                    </Text>
                    <Text style={styles.faceIdButtonSubtitle}>
                      {mode === 'login' ? 'Quick and secure authentication' : 'Required for expert verification'}
                    </Text>
                  </View>
                  <Ionicons name="chevron-forward" size={24} color={ZamanColors.gray[400]} />
                </TouchableOpacity>
              )}
            </AnimatedContainer>

            {/* Divider */}
            {mode === 'login' && (
              <AnimatedContainer delay={400} style={styles.dividerContainer}>
                <View style={styles.dividerLine} />
                <Text style={styles.dividerText}>or continue with email</Text>
                <View style={styles.dividerLine} />
              </AnimatedContainer>
            )}

            {/* Login Form */}
            {mode === 'login' && (
              <AnimatedContainer delay={500} style={styles.formSection}>
                <View style={styles.inputContainer}>
                  <Ionicons name="mail-outline" size={20} color={ZamanColors.gray[400]} style={styles.inputIcon} />
                  <TextInput
                    style={styles.modernInput}
                    placeholder="Email address"
                    placeholderTextColor={ZamanColors.gray[400]}
                    value={email}
                    onChangeText={setEmail}
                    keyboardType="email-address"
                    autoCapitalize="none"
                    editable={!isLoading}
                  />
                </View>
                
                <View style={styles.inputContainer}>
                  <Ionicons name="lock-closed-outline" size={20} color={ZamanColors.gray[400]} style={styles.inputIcon} />
                  <TextInput
                    style={styles.modernInput}
                    placeholder="Password"
                    placeholderTextColor={ZamanColors.gray[400]}
                    value={password}
                    onChangeText={setPassword}
                    secureTextEntry
                    editable={!isLoading}
                  />
                </View>
                
                <TouchableOpacity 
                  style={styles.submitButton}
                  onPress={handleEmailPasswordLogin}
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <ActivityIndicator color={ZamanColors.black} />
                  ) : (
                    <Text style={styles.submitButtonText}>Sign in</Text>
                  )}
                </TouchableOpacity>
              </AnimatedContainer>
            )}

            {/* Register Form */}
            {mode === 'register' && (
              <AnimatedContainer delay={400} style={styles.formSection}>
                <View style={styles.nameRow}>
                  <View style={[styles.inputContainer, styles.halfInput]}>
                    <TextInput
                      style={styles.modernInput}
                      placeholder="First name"
                      placeholderTextColor={ZamanColors.gray[400]}
                      value={name}
                      onChangeText={setName}
                      autoCapitalize="words"
                      editable={!isLoading}
                    />
                  </View>
                  
                  <View style={[styles.inputContainer, styles.halfInput]}>
                    <TextInput
                      style={styles.modernInput}
                      placeholder="Last name"
                      placeholderTextColor={ZamanColors.gray[400]}
                      value={surname}
                      onChangeText={setSurname}
                      autoCapitalize="words"
                      editable={!isLoading}
                    />
                  </View>
                </View>
                
                <View style={styles.inputContainer}>
                  <Ionicons name="mail-outline" size={20} color={ZamanColors.gray[400]} style={styles.inputIcon} />
                  <TextInput
                    style={styles.modernInput}
                    placeholder="Email address"
                    placeholderTextColor={ZamanColors.gray[400]}
                    value={email}
                    onChangeText={setEmail}
                    keyboardType="email-address"
                    autoCapitalize="none"
                    editable={!isLoading}
                  />
                </View>
                
                <View style={styles.inputContainer}>
                  <Ionicons name="call-outline" size={20} color={ZamanColors.gray[400]} style={styles.inputIcon} />
                  <TextInput
                    style={styles.modernInput}
                    placeholder="Phone number"
                    placeholderTextColor={ZamanColors.gray[400]}
                    value={phone}
                    onChangeText={setPhone}
                    keyboardType="phone-pad"
                    editable={!isLoading}
                  />
                </View>
                
                <View style={styles.inputContainer}>
                  <Ionicons name="lock-closed-outline" size={20} color={ZamanColors.gray[400]} style={styles.inputIcon} />
                  <TextInput
                    style={styles.modernInput}
                    placeholder="Password (min 8 characters)"
                    placeholderTextColor={ZamanColors.gray[400]}
                    value={password}
                    onChangeText={setPassword}
                    secureTextEntry
                    editable={!isLoading}
                  />
                </View>

                <TouchableOpacity 
                  style={[styles.submitButton, !capturedPhoto && styles.submitButtonDisabled]}
                  onPress={handleRegister}
                  disabled={isLoading || !capturedPhoto}
                >
                  {isLoading ? (
                    <ActivityIndicator color={ZamanColors.black} />
                  ) : (
                    <Text style={styles.submitButtonText}>Create Account</Text>
                  )}
                </TouchableOpacity>
                
                {!capturedPhoto && (
                  <Text style={styles.faceIdRequiredText}>
                    * Face ID capture is required for registration
                  </Text>
                )}
              </AnimatedContainer>
            )}

            {/* Switch Mode */}
            <AnimatedContainer delay={600} style={styles.switchModeContainer}>
              <Text style={styles.switchModeText}>
                {mode === 'login' 
                  ? "Don't have an account? " 
                  : 'Already have an account? '}
              </Text>
              <TouchableOpacity onPress={switchMode} disabled={isLoading}>
                <Text style={styles.switchModeLink}>
                  {mode === 'login' ? 'Sign up' : 'Sign in'}
                </Text>
              </TouchableOpacity>
            </AnimatedContainer>
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
    </AuroraBackground>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: ZamanColors.white,
  },
  selectionContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 32,
  },
  buttonContainer: {
    width: '100%',
    maxWidth: 340,
    marginTop: 48,
    gap: 12,
  },
  keyboardView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
  },
  header: {
    paddingTop: Platform.OS === 'ios' ? 80 : 60,
    paddingBottom: 20,
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
    marginBottom: 16,
    alignItems: 'center',
  },
  appName: {
    fontSize: 36,
    fontWeight: '300',
    letterSpacing: 10,
    color: ZamanColors.black,
    marginBottom: 12,
    textAlign: 'center',
  },
  tagline: {
    fontSize: 17,
    color: ZamanColors.gray[500],
    fontWeight: '300',
    textAlign: 'center',
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
    color: ZamanColors.gray[600],
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: 16,
  },
  captureButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: ZamanColors.white,
    borderWidth: 1,
    borderColor: ZamanColors.gray[300],
    borderRadius: 12,
    paddingVertical: 20,
    gap: 12,
  },
  captureButtonText: {
    fontSize: 16,
    color: ZamanColors.persianGreen,
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
    backgroundColor: ZamanColors.gray[100],
    borderWidth: 2,
    borderColor: ZamanColors.persianGreen,
  },
  linkButton: {
    paddingVertical: 8,
  },
  linkText: {
    fontSize: 15,
    color: ZamanColors.persianGreen,
    fontWeight: '500',
  },
  input: {
    backgroundColor: ZamanColors.white,
    borderWidth: 1,
    borderColor: ZamanColors.gray[300],
    borderRadius: 12,
    paddingVertical: 16,
    paddingHorizontal: 16,
    fontSize: 16,
    color: ZamanColors.black,
    marginBottom: 12,
  },
  primaryButton: {
    backgroundColor: ZamanColors.solar,
    borderRadius: 12,
    paddingVertical: 18,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 8,
  },
  primaryButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: ZamanColors.black,
  },
  divider: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 32,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: ZamanColors.gray[200],
  },
  dividerText: {
    marginHorizontal: 16,
    fontSize: 13,
    color: ZamanColors.gray[400],
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
    color: ZamanColors.gray[600],
  },
  switchTextBold: {
    fontSize: 15,
    color: ZamanColors.persianGreen,
    fontWeight: '600',
  },
  roleButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: ZamanColors.white,
    borderWidth: 1,
    borderColor: ZamanColors.gray[300],
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
    color: ZamanColors.black,
  },
  expertButton: {
    backgroundColor: ZamanColors.black,
    borderColor: ZamanColors.black,
  },
  expertButtonText: {
    color: ZamanColors.white,
  },
  
  // New Auth Styles
  authContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 24,
    paddingTop: Platform.OS === 'ios' ? 100 : 80,
    paddingBottom: 40,
  },
  authHeader: {
    alignItems: 'center',
    marginBottom: 8,
  },
  authTitle: {
    fontSize: 28,
    fontWeight: '700',
    color: ZamanColors.black,
    marginBottom: 8,
    textAlign: 'center',
  },
  authSubtitle: {
    fontSize: 16,
    color: ZamanColors.gray[500],
    fontWeight: '400',
    textAlign: 'center',
    marginBottom: 32,
  },
  
  // Face ID Section
  faceIdSection: {
    width: '100%',
    maxWidth: 400,
  },
  faceIdButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: ZamanColors.white,
    borderRadius: 16,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 4,
    borderWidth: 1,
    borderColor: ZamanColors.gray[100],
  },
  faceIdIconContainer: {
    width: 56,
    height: 56,
    borderRadius: 14,
    backgroundColor: ZamanColors.persianGreen,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 16,
  },
  faceIdTextContainer: {
    flex: 1,
  },
  faceIdButtonTitle: {
    fontSize: 17,
    fontWeight: '600',
    color: ZamanColors.black,
    marginBottom: 4,
  },
  faceIdButtonSubtitle: {
    fontSize: 13,
    color: ZamanColors.gray[500],
  },
  capturedPhotoSection: {
    alignItems: 'center',
    backgroundColor: ZamanColors.white,
    borderRadius: 16,
    padding: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 4,
  },
  capturedPhoto: {
    width: 100,
    height: 100,
    borderRadius: 50,
    marginBottom: 16,
    borderWidth: 3,
    borderColor: ZamanColors.persianGreen,
  },
  photoActions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 16,
  },
  retakeButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: ZamanColors.persianGreen,
    gap: 6,
  },
  retakeText: {
    fontSize: 14,
    color: ZamanColors.persianGreen,
    fontWeight: '500',
  },
  faceLoginButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: ZamanColors.persianGreen,
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 20,
    gap: 8,
  },
  faceLoginButtonText: {
    fontSize: 14,
    color: ZamanColors.white,
    fontWeight: '600',
  },
  
  // Divider
  dividerContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    width: '100%',
    maxWidth: 400,
    marginVertical: 24,
  },
  
  // Form Section
  formSection: {
    width: '100%',
    maxWidth: 400,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: ZamanColors.white,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: ZamanColors.gray[200],
    marginBottom: 12,
    paddingHorizontal: 16,
  },
  inputIcon: {
    marginRight: 12,
  },
  modernInput: {
    flex: 1,
    paddingVertical: 16,
    fontSize: 16,
    color: ZamanColors.black,
  },
  nameRow: {
    flexDirection: 'row',
    gap: 12,
  },
  halfInput: {
    flex: 1,
  },
  submitButton: {
    backgroundColor: ZamanColors.solar,
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 8,
    shadowColor: ZamanColors.solar,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  submitButtonDisabled: {
    backgroundColor: ZamanColors.gray[200],
    shadowOpacity: 0,
  },
  submitButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: ZamanColors.black,
  },
  faceIdRequiredText: {
    fontSize: 13,
    color: ZamanColors.gray[500],
    textAlign: 'center',
    marginTop: 12,
  },
  
  // Switch Mode
  switchModeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 24,
  },
  switchModeText: {
    fontSize: 15,
    color: ZamanColors.gray[600],
  },
  switchModeLink: {
    fontSize: 15,
    color: ZamanColors.persianGreen,
    fontWeight: '600',
  },
});

