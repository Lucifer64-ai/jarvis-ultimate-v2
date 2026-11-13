import React, { useContext, useEffect, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { AuthContext } from '../services/AuthContext';
import ApiService from '../services/ApiService';

export default function HomeScreen({ navigation }) {
  const { token } = useContext(AuthContext);
  const [status, setStatus] = useState(null);

  useEffect(() => {
    loadStatus();
  }, []);

  const loadStatus = async () => {
    try {
      const data = await ApiService.getStatus(token);
      setStatus(data);
    } catch (error) {
      console.error('Error loading status:', error);
    }
  };

  return (
    <View style={styles.container}>
      <ScrollView>
        <View style={styles.card}>
          <Text style={styles.title}>¡¸µ¼½¹ °</Text>
          {status && (
            <>
              <View style={styles.statRow}>
                <Text style={styles.statLabel}>CPU:</Text>
                <Text style={styles.statValue}>{status.cpu}%</Text>
              </View>
              <View style={styles.statRow}>
                <Text style={styles.statLabel}>RAM:</Text>
                <Text style={styles.statValue}>{status.ram}%</Text>
              </View>
              <View style={styles.statRow}>
                <Text style={styles.statLabel}>¡°:</Text>
                <Text style={[styles.statValue, styles.statusOnline]}>
                  {status.status || 'Online'}
                </Text>
              </View>
            </>
          )}
        </View>

        <View style={styles.menuGrid}>
          <TouchableOpacity
            style={styles.menuButton}
            onPress={() => navigation.navigate('Devices')}
          >
            <Text style={styles.menuIcon}> </Text>
            <Text style={styles.menuText}>£¾¹²°</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.menuButton}
            onPress={() => navigation.navigate('Command')}
          >
            <Text style={styles.menuIcon}>¤</Text>
            <Text style={styles.menuText}>¾¼°½´</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.menuButton}
            onPress={() => navigation.navigate('Settings')}
          >
            <Text style={styles.menuIcon}>¸</Text>
            <Text style={styles.menuText}>°¾¹º¸</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
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
    marginBottom: 15,
  },
  statRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#333',
  },
  statLabel: {
    fontSize: 16,
    color: '#999',
  },
  statValue: {
    fontSize: 16,
    color: '#fff',
    fontWeight: 'bold',
  },
  statusOnline: {
    color: '#00ff88',
  },
  menuGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  menuButton: {
    backgroundColor: '#1a1a2e',
    borderRadius: 15,
    padding: 20,
    width: '48%',
    marginBottom: 15,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#00d4ff',
  },
  menuIcon: {
    fontSize: 40,
    marginBottom: 10,
  },
  menuText: {
    fontSize: 16,
    color: '#fff',
    fontWeight: 'bold',
  },
});
