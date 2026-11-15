import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, Switch } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function SettingsScreen() {
  const [serverIp, setServerIp] = useState('192.168.1.100');
  const [serverPort, setServerPort] = useState('8765');
  const [autoConnect, setAutoConnect] = useState(true);
  const [llmMode, setLlmMode] = useState('auto'); // auto, openai, ollama

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const ip = await AsyncStorage.getItem('serverIp');
      const port = await AsyncStorage.getItem('serverPort');
      const auto = await AsyncStorage.getItem('autoConnect');
      const mode = await AsyncStorage.getItem('llmMode');

      if (ip) setServerIp(ip);
      if (port) setServerPort(port);
      if (auto) setAutoConnect(auto === 'true');
      if (mode) setLlmMode(mode);
    } catch (e) {
      console.error('Ошибка загрузки настроек:', e);
    }
  };

  const saveSettings = async () => {
    try {
      await AsyncStorage.setItem('serverIp', serverIp);
      await AsyncStorage.setItem('serverPort', serverPort);
      await AsyncStorage.setItem('autoConnect', autoConnect.toString());
      await AsyncStorage.setItem('llmMode', llmMode);
      Alert.alert('Успешно', 'Настройки сохранены');
    } catch (e) {
      Alert.alert('Ошибка', 'Не удалось сохранить настройки');
    }
  };

  const testConnection = () => {
    Alert.alert('Тест подключения', `Подключение к ${serverIp}:${serverPort}...`);
    // Здесь будет реальная проверка подключения
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>⚙️ Настройки</Text>

      {/* Подключение */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🔌 Подключение</Text>

        <Text style={styles.label}>IP адрес сервера:</Text>
        <TextInput
          style={styles.input}
          value={serverIp}
          onChangeText={setServerIp}
          placeholder="192.168.1.100"
          placeholderTextColor="#666"
        />

        <Text style={styles.label}>Порт:</Text>
        <TextInput
          style={styles.input}
          value={serverPort}
          onChangeText={setServerPort}
          placeholder="8765"
          placeholderTextColor="#666"
          keyboardType="numeric"
        />

        <TouchableOpacity style={styles.testButton} onPress={testConnection}>
          <Text style={styles.testButtonText}>🔍 Проверить подключение</Text>
        </TouchableOpacity>
      </View>

      {/* LLM режим */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🧠 Режим LLM</Text>

        <TouchableOpacity
          style={[styles.modeButton, llmMode === 'auto' && styles.modeButtonActive]}
          onPress={() => setLlmMode('auto')}
        >
          <Text style={styles.modeButtonText}>🔄 Автоматический</Text>
          <Text style={styles.modeDescription}>OpenAI → Ollama (если нет ключа)</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.modeButton, llmMode === 'openai' && styles.modeButtonActive]}
          onPress={() => setLlmMode('openai')}
        >
          <Text style={styles.modeButtonText}>🤖 ChatGPT</Text>
          <Text style={styles.modeDescription}>Только OpenAI API</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.modeButton, llmMode === 'ollama' && styles.modeButtonActive]}
          onPress={() => setLlmMode('ollama')}
        >
          <Text style={styles.modeButtonText}>💻 Локальная модель</Text>
          <Text style={styles.modeDescription}>Только Ollama (оффлайн)</Text>
        </TouchableOpacity>
      </View>

      {/* Автоподключение */}
      <View style={styles.section}>
        <View style={styles.switchRow}>
          <Text style={styles.label}>Автоподключение при запуске</Text>
          <Switch
            value={autoConnect}
            onValueChange={setAutoConnect}
            trackColor={{ false: '#767577', true: '#00d4ff' }}
            thumbColor={autoConnect ? '#00d4ff' : '#f4f3f4'}
          />
        </View>
      </View>

      {/* Кнопка сохранения */}
      <TouchableOpacity style={styles.saveButton} onPress={saveSettings}>
        <Text style={styles.saveButtonText}>💾 Сохранить настройки</Text>
      </TouchableOpacity>
    </View>
  );
}

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
  section: {
    backgroundColor: '#1a1a2e',
    padding: 15,
    borderRadius: 10,
    marginBottom: 15
  },
  sectionTitle: {
    color: '#00d4ff',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15
  },
  label: {
    color: '#fff',
    fontSize: 14,
    marginBottom: 5
  },
  input: {
    backgroundColor: '#0f0f1e',
    color: '#fff',
    padding: 12,
    borderRadius: 8,
    marginBottom: 10,
    fontSize: 16
  },
  testButton: {
    backgroundColor: '#00d4ff',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 10
  },
  testButtonText: {
    color: '#0f0f1e',
    fontSize: 16,
    fontWeight: 'bold'
  },
  modeButton: {
    backgroundColor: '#0f0f1e',
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
    borderWidth: 2,
    borderColor: 'transparent'
  },
  modeButtonActive: {
    borderColor: '#00d4ff'
  },
  modeButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 5
  },
  modeDescription: {
    color: '#888',
    fontSize: 12
  },
  switchRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  saveButton: {
    backgroundColor: '#00d4ff',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 'auto'
  },
  saveButtonText: {
    color: '#0f0f1e',
    fontSize: 18,
    fontWeight: 'bold'
  }
});
