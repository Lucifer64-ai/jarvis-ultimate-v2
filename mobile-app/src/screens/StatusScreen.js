import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, RefreshControl } from 'react-native';
import WebSocketService from '../services/websocket';

export default function StatusScreen() {
  const [status, setStatus] = useState({
    cpu: 0,
    ram: 0,
    network: 'N/A',
    uptime: '0:00:00',
    processes: 0
  });
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000); // Обновление каждые 5 секунд
    return () => clearInterval(interval);
  }, []);

  const fetchStatus = async () => {
    try {
      const ws = new WebSocketService('ws://192.168.1.100:8765');
      await ws.connect();
      ws.send({ type: 'get_status' });

      ws.onMessage = (data) => {
        if (data.type === 'status') {
          setStatus(data.data);
        }
      };
    } catch (e) {
      console.error('Ошибка получения статуса:', e);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchStatus();
    setRefreshing(false);
  };

  return (
    <ScrollView 
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <Text style={styles.title}>📊 Статус системы</Text>

      {/* CPU */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>💻 Процессор</Text>
        <View style={styles.progressBar}>
          <View style={[styles.progressFill, { width: `${status.cpu}%`, backgroundColor: getProgressColor(status.cpu) }]} />
        </View>
        <Text style={styles.progressText}>{status.cpu}%</Text>
      </View>

      {/* RAM */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>🧠 Память</Text>
        <View style={styles.progressBar}>
          <View style={[styles.progressFill, { width: `${status.ram}%`, backgroundColor: getProgressColor(status.ram) }]} />
        </View>
        <Text style={styles.progressText}>{status.ram}%</Text>
      </View>

      {/* Network */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>🌐 Сеть</Text>
        <Text style={styles.value}>{status.network}</Text>
      </View>

      {/* Uptime */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>⏱️ Время работы</Text>
        <Text style={styles.value}>{status.uptime}</Text>
      </View>

      {/* Processes */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>⚙️ Процессы</Text>
        <Text style={styles.value}>{status.processes}</Text>
      </View>
    </ScrollView>
  );
}

const getProgressColor = (value) => {
  if (value < 50) return '#00ff00';
  if (value < 80) return '#ffaa00';
  return '#ff0000';
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f0f1e',
    padding: 20
  },
  title: {
    color: '#00d4ff',
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center'
  },
  card: {
    backgroundColor: '#1a1a2e',
    padding: 20,
    borderRadius: 10,
    marginBottom: 15
  },
  cardTitle: {
    color: '#00d4ff',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10
  },
  progressBar: {
    height: 20,
    backgroundColor: '#0f0f1e',
    borderRadius: 10,
    overflow: 'hidden',
    marginBottom: 5
  },
  progressFill: {
    height: '100%',
    borderRadius: 10
  },
  progressText: {
    color: '#fff',
    fontSize: 14,
    textAlign: 'right'
  },
  value: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold'
  }
});
