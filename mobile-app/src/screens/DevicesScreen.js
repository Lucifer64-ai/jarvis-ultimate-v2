import React, { useContext, useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, Alert } from 'react-native';
import { AuthContext } from '../services/AuthContext';
import ApiService from '../services/ApiService';

export default function DevicesScreen() {
  const { token } = useContext(AuthContext);
  const [devices, setDevices] = useState([]);

  useEffect(() => {
    loadDevices();
  }, []);

  const loadDevices = async () => {
    try {
      const data = await ApiService.getDevices(token);
      setDevices(data.devices || []);
    } catch (error) {
      Alert.alert('¸±º°', 'µ ´°»¾ ·°³·¸ ¾¹²°');
    }
  };

  const toggleDevice = async (entityId, currentState) => {
    try {
      const action = currentState === 'on' ? 'off' : 'on';
      await ApiService.controlDevice(token, entityId, action);
      loadDevices();
    } catch (error) {
      Alert.alert('¸±º°', 'µ ´°»¾ ¿°²» ¾¹²¾¼');
    }
  };

  const renderItem = ({ item }) => (
    <View style={styles.deviceCard}>
      <View style={styles.deviceInfo}>
        <Text style={styles.deviceName}>
          {item.attributes?.friendly_name || item.entity_id}
        </Text>
        <Text style={styles.deviceType}>{item.entity_id.split('.')[0]}</Text>
      </View>
      <TouchableOpacity
        style={[styles.toggleButton, item.state === 'on' && styles.toggleButtonOn]}
        onPress={() => toggleDevice(item.entity_id, item.state)}
      >
        <Text style={styles.toggleText}>
          {item.state === 'on' ? 'ON' : 'OFF'}
        </Text>
      </TouchableOpacity>
    </View>
  );

  return (
    <View style={styles.container}>
      <FlatList
        data={devices}
        keyExtractor={(item) => item.entity_id}
        renderItem={renderItem}
        ListEmptyComponent={
          <Text style={styles.emptyText}>£¾¹²° ½µ ½°¹´µ½</Text>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f0f1e',
    padding: 20,
  },
  deviceCard: {
    backgroundColor: '#1a1a2e',
    borderRadius: 10,
    padding: 15,
    marginBottom: 10,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#333',
  },
  deviceInfo: {
    flex: 1,
  },
  deviceName: {
    fontSize: 16,
    color: '#fff',
    fontWeight: 'bold',
    marginBottom: 5,
  },
  deviceType: {
    fontSize: 12,
    color: '#666',
  },
  toggleButton: {
    backgroundColor: '#333',
    borderRadius: 20,
    padding: 10,
    paddingHorizontal: 20,
  },
  toggleButtonOn: {
    backgroundColor: '#00d4ff',
  },
  toggleText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  emptyText: {
    textAlign: 'center',
    color: '#666',
    fontSize: 16,
    marginTop: 50,
  },
});
