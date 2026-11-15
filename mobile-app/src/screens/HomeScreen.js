import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, TouchableOpacity, FlatList, StyleSheet, Alert } from 'react-native';
import Voice from 'react-native-voice';
import AsyncStorage from '@react-native-async-storage/async-storage';
import WebSocketService from '../services/websocket';

export default function HomeScreen({ navigation }) {
  const [command, setCommand] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [response, setResponse] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [serverUrl, setServerUrl] = useState('');

  useEffect(() => {
    // Загружаем настройки подключения
    loadConnectionSettings();

    // Инициализация голосового распознавания
    Voice.onSpeechStart = () => setIsListening(true);
    Voice.onSpeechEnd = () => setIsListening(false);
    Voice.onSpeechResults = (e) => {
      if (e.value && e.value[0]) {
        setCommand(e.value[0]);
        sendCommand(e.value[0]);
      }
    };

    return () => {
      Voice.destroy();
    };
  }, []);

  const loadConnectionSettings = async () => {
    try {
      const ip = await AsyncStorage.getItem('server_ip');
      const port = await AsyncStorage.getItem('server_port');
      const token = await AsyncStorage.getItem('auth_token');

      if (ip && port) {
        const url = `ws://${ip}:${port}`;
        setServerUrl(url);

        // Подключаемся к WebSocket
        const ws = new WebSocketService(url);
        ws.onConnect = () => {
          setIsConnected(true);
          // Отправляем токен авторизации
          if (token) {
            ws.send({ type: 'auth', token });
          }
        };
        ws.onDisconnect = () => setIsConnected(false);
        ws.onMessage = (data) => {
          if (data.type === 'auth_success') {
            Alert.alert('Успешно', 'Подключено к JARVIS!');
          } else if (data.type === 'command_result') {
            setResponse(data.result.message || 'Команда выполнена');
          }
        };
        ws.connect();
      }
    } catch (e) {
      console.error('Ошибка загрузки настроек:', e);
    }
  };

  const sendCommand = async (text) => {
    if (!isConnected) {
      Alert.alert('Ошибка', 'Нет подключения к JARVIS. Отсканируйте QR-код.');
      return;
    }

    const ws = new WebSocketService(serverUrl);
    await ws.connect();
    ws.send({ type: 'command', text });
  };

  const startListening = async () => {
    try {
      await Voice.start('ru-RU');
    } catch (e) {
      Alert.alert('Ошибка', 'Не удалось запустить голосовое распознавание');
    }
  };

  const stopListening = async () => {
    try {
      await Voice.stop();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <View style={styles.container}>
      {/* Статус подключения */}
      <View style={styles.statusBar}>
        <View style={[styles.statusDot, { backgroundColor: isConnected ? '#00ff00' : '#ff0000' }]} />
        <Text style={styles.statusText}>
          {isConnected ? 'Подключено' : 'Отключено'}
        </Text>

        {!isConnected && (
          <TouchableOpacity
            style={styles.qrButton}
            onPress={() => navigation.navigate('QRScanner')}
          >
            <Text style={styles.qrButtonText}>📷 Подключить</Text>
          </TouchableOpacity>
        )}
      </View>

      {/* Ответ JARVIS */}
      {response && (
        <View style={styles.responseBox}>
          <Text style={styles.responseLabel}>JARVIS:</Text>
          <Text style={styles.responseText}>{response}</Text>
        </View>
      )}

      {/* Поле ввода команды */}
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          placeholder="Введите команду..."
          placeholderTextColor="#666"
          value={command}
          onChangeText={setCommand}
          onSubmitEditing={() => sendCommand(command)}
        />
        <TouchableOpacity
          style={[styles.voiceButton, isListening && styles.voiceButtonActive]}
          onPress={isListening ? stopListening : startListening}
        >
          <Text style={styles.voiceButtonText}>
            {isListening ? '🎤' : '🎤'}
          </Text>
        </TouchableOpacity>
      </View>

      {/* Быстрые команды */}
      <View style={styles.quickCommands}>
        <Text style={styles.sectionTitle}>Быстрые команды:</Text>
        <View style={styles.commandGrid}>
          {[
            { text: 'Который час?', icon: '🕐' },
            { text: 'Какая погода?', icon: '🌤' },
            { text: 'Запусти браузер', icon: '🌐' },
            { text: 'Выключи компьютер', icon: '⏻' }
          ].map((cmd, idx) => (
            <TouchableOpacity
              key={idx}
              style={styles.commandButton}
              onPress={() => sendCommand(cmd.text)}
            >
              <Text style={styles.commandIcon}>{cmd.icon}</Text>
              <Text style={styles.commandText}>{cmd.text}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Навигация */}
      <View style={styles.navButtons}>
        <TouchableOpacity
          style={styles.navButton}
          onPress={() => navigation.navigate('Status')}
        >
          <Text style={styles.navButtonText}>📊 Статус</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.navButton}
          onPress={() => navigation.navigate('Log')}
        >
          <Text style={styles.navButtonText}>📝 Лог</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.navButton}
          onPress={() => navigation.navigate('Settings')}
        >
          <Text style={styles.navButtonText}>⚙️ Настройки</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f0f1e',
    padding: 20
  },
  statusBar: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20
  },
  statusDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginRight: 10
  },
  statusText: {
    color: '#00d4ff',
    fontSize: 16,
    flex: 1
  },
  qrButton: {
    backgroundColor: '#00d4ff',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 8
  },
  qrButtonText: {
    color: '#0f0f1e',
    fontSize: 14,
    fontWeight: 'bold'
  },
  responseBox: {
    backgroundColor: '#1a1a2e',
    padding: 15,
    borderRadius: 10,
    marginBottom: 20,
    borderLeftWidth: 3,
    borderLeftColor: '#00d4ff'
  },
  responseLabel: {
    color: '#00d4ff',
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 5
  },
  responseText: {
    color: '#fff',
    fontSize: 16
  },
  inputContainer: {
    flexDirection: 'row',
    marginBottom: 20
  },
  input: {
    flex: 1,
    backgroundColor: '#1a1a2e',
    color: '#fff',
    padding: 15,
    borderRadius: 10,
    marginRight: 10,
    fontSize: 16
  },
  voiceButton: {
    backgroundColor: '#1a1a2e',
    width: 50,
    height: 50,
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center'
  },
  voiceButtonActive: {
    backgroundColor: '#00d4ff'
  },
  voiceButtonText: {
    fontSize: 24
  },
  quickCommands: {
    marginBottom: 20
  },
  sectionTitle: {
    color: '#00d4ff',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10
  },
  commandGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between'
  },
  commandButton: {
    backgroundColor: '#1a1a2e',
    padding: 15,
    borderRadius: 10,
    width: '48%',
    marginBottom: 10,
    alignItems: 'center'
  },
  commandIcon: {
    fontSize: 24,
    marginBottom: 5
  },
  commandText: {
    color: '#fff',
    fontSize: 14,
    textAlign: 'center'
  },
  navButtons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: 'auto'
  },
  navButton: {
    backgroundColor: '#1a1a2e',
    padding: 15,
    borderRadius: 10,
    flex: 1,
    marginHorizontal: 5,
    alignItems: 'center'
  },
  navButtonText: {
    color: '#00d4ff',
    fontSize: 14,
    fontWeight: 'bold'
  }
});
