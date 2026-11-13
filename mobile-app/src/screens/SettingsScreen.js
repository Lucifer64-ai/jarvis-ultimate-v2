import React, { useContext } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Alert } from 'react-native';
import { AuthContext } from '../services/AuthContext';

export default function SettingsScreen({ navigation }) {
  const { logout } = useContext(AuthContext);

  const handleLogout = () => {
    Alert.alert(
      '¾´',
      ' ²µµ½, ¾ ¾¸µ ²¹¸?',
      [
        { text: '¼µ½°', style: 'cancel' },
        {
          text: '¹¸',
          style: 'destructive',
          onPress: () => {
            logout();
            navigation.replace('Login');
          },
        },
      ]
    );
  };

  return (
    <View style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.title}>°¾¹º¸</Text>
        
        <TouchableOpacity style={styles.menuItem}>
          <Text style={styles.menuText}>¾´º»µ½¸µ º µ²µ</Text>
          <Text style={styles.menuValue}>°¾µ½¾</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.menuItem}>
          <Text style={styles.menuText}>£²µ´¾¼»µ½¸</Text>
          <Text style={styles.menuValue}>º»µ½</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.menuItem}>
          <Text style={styles.menuText}>¢µ¼°</Text>
          <Text style={styles.menuValue}>¢¼½°</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.menuItem}>
          <Text style={styles.menuText}>¯·º</Text>
          <Text style={styles.menuValue}> º¸¹</Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
        <Text style={styles.logoutText}>¹¸ ¸· °ºº°½°</Text>
      </TouchableOpacity>

      <View style={styles.footer}>
        <Text style={styles.footerText}>JARVIS Mobile v1.0.0</Text>
        <Text style={styles.footerText}>© 2026</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f0f1e',
    padding: 20,
  },
  card: {
    backgroundColor: '#1a1a2e',
    borderRadius: 15,
    padding: 20,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#00d4ff',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#00d4ff',
    marginBottom: 20,
  },
  menuItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#333',
  },
  menuText: {
    fontSize: 16,
    color: '#fff',
  },
  menuValue: {
    fontSize: 14,
    color: '#666',
  },
  logoutButton: {
    backgroundColor: '#ff4444',
    borderRadius: 10,
    padding: 15,
    alignItems: 'center',
    marginBottom: 20,
  },
  logoutText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  footer: {
    alignItems: 'center',
    marginTop: 'auto',
  },
  footerText: {
    color: '#666',
    fontSize: 12,
    marginBottom: 5,
  },
});
