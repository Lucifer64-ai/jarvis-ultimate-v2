import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, StyleSheet, TouchableOpacity } from 'react-native';
import WebSocketService from '../services/websocket';

export default function LogScreen() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    const ws = new WebSocketService('ws://192.168.1.100:8765');
    ws.connect();

    ws.onMessage = (data) => {
      if (data.type === 'log') {
        setLogs(prev => [data.entry, ...prev]);
      }
    };

    // Загружаем историю логов
    ws.send({ type: 'get_logs' });
    ws.onMessage = (data) => {
      if (data.type === 'logs_history') {
        setLogs(data.logs);
      }
    };

    return () => ws.disconnect();
  }, []);

  const clearLogs = () => {
    setLogs([]);
    const ws = new WebSocketService('ws://192.168.1.100:8765');
    ws.connect();
    ws.send({ type: 'clear_logs' });
  };

  const renderLogItem = ({ item }) => (
    <View style={styles.logItem}>
      <View style={styles.logHeader}>
        <Text style={styles.logTime}>{item.timestamp}</Text>
        <Text style={[styles.logType, { color: getTypeColor(item.type) }]}>
          {item.type.toUpperCase()}
        </Text>
      </View>
      <Text style={styles.logCommand}>{item.command}</Text>
      {item.response && (
        <Text style={styles.logResponse}>{item.response}</Text>
      )}
    </View>
  );

  const getTypeColor = (type) => {
    switch (type) {
      case 'success': return '#00ff00';
      case 'error': return '#ff0000';
      case 'warning': return '#ffaa00';
      default: return '#00d4ff';
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>📝 Лог команд</Text>
        <TouchableOpacity style={styles.clearButton} onPress={clearLogs}>
          <Text style={styles.clearButtonText}>🗑️ Очистить</Text>
        </TouchableOpacity>
      </View>

      <FlatList
        data={logs}
        renderItem={renderLogItem}
        keyExtractor={(item, index) => index.toString()}
        contentContainerStyle={styles.logList}
        ListEmptyComponent={
          <Text style={styles.emptyText}>Нет записей в логе</Text>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f0f1e',
    padding: 20
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20
  },
  title: {
    color: '#00d4ff',
    fontSize: 24,
    fontWeight: 'bold'
  },
  clearButton: {
    backgroundColor: '#ff4444',
    padding: 10,
    borderRadius: 8
  },
  clearButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold'
  },
  logList: {
    paddingBottom: 20
  },
  logItem: {
    backgroundColor: '#1a1a2e',
    padding: 15,
    borderRadius: 10,
    marginBottom: 10,
    borderLeftWidth: 3,
    borderLeftColor: '#00d4ff'
  },
  logHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8
  },
  logTime: {
    color: '#888',
    fontSize: 12
  },
  logType: {
    fontSize: 12,
    fontWeight: 'bold'
  },
  logCommand: {
    color: '#fff',
    fontSize: 16,
    marginBottom: 5
  },
  logResponse: {
    color: '#aaa',
    fontSize: 14,
    fontStyle: 'italic'
  },
  emptyText: {
    color: '#666',
    fontSize: 16,
    textAlign: 'center',
    marginTop: 50
  }
});
