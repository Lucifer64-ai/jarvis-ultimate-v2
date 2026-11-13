import React, { useContext, useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ScrollView, Alert } from 'react-native';
import { AuthContext } from '../services/AuthContext';
import ApiService from '../services/ApiService';

export default function CommandScreen() {
  const { token } = useContext(AuthContext);
  const [command, setCommand] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const sendCommand = async () => {
    if (!command.trim()) {
      Alert.alert('¸±º°', '²µ´¸µ º¾¼°½´');
      return;
    }

    setLoading(true);
    try {
      const data = await ApiService.sendCommand(token, command);
      setResult(data);
    } catch (error) {
      Alert.alert('¸±º°', 'µ ´°»¾ ²¿¾»½¸ º¾¼°½´');
    } finally {
      setLoading(false);
    }
  };

  const quickCommands = [
    '¾¾¹ °?',
    '°º° ¿¾³¾´°?',
    '¡° ¸µ¼',
    'º¾¹ YouTube',
    'º»¸ ²µ',
  ];

  return (
    <View style={styles.container}>
      <ScrollView>
        <View style={styles.inputCard}>
          <TextInput
            style={styles.input}
            placeholder="²µ´¸µ º¾¼°½´..."
            placeholderTextColor="#666"
            value={command}
            onChangeText={setCommand}
            multiline
          />
          <TouchableOpacity
            style={[styles.sendButton, loading && styles.sendButtonDisabled]}
            onPress={sendCommand}
            disabled={loading}
          >
            <Text style={styles.sendButtonText}>
              {loading ? '¿¾»½µ½¸µ...' : '¿°²¸'}
            </Text>
          </TouchableOpacity>
        </View>

        <View style={styles.quickCommands}>
          <Text style={styles.sectionTitle}>µ º¾¼°½´</Text>
          {quickCommands.map((cmd, index) => (
            <TouchableOpacity
              key={index}
              style={styles.quickButton}
              onPress={() => setCommand(cmd)}
            >
              <Text style={styles.quickButtonText}>{cmd}</Text>
            </TouchableOpacity>
          ))}
        </View>

        {result && (
          <View style={styles.resultCard}>
            <Text style={styles.sectionTitle}> µ·»°</Text>
            <Text style={styles.resultText}>
              {JSON.stringify(result, null, 2)}
            </Text>
          </View>
        )}
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
  inputCard: {
    backgroundColor: '#1a1a2e',
    borderRadius: 15,
    padding: 15,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#00d4ff',
  },
  input: {
    backgroundColor: '#0f0f1e',
    borderRadius: 10,
    padding: 15,
    color: '#fff',
    fontSize: 16,
    minHeight: 100,
    textAlignVertical: 'top',
    marginBottom: 10,
  },
  sendButton: {
    backgroundColor: '#00d4ff',
    borderRadius: 10,
    padding: 15,
    alignItems: 'center',
  },
  sendButtonDisabled: {
    opacity: 0.5,
  },
  sendButtonText: {
    color: '#0f0f1e',
    fontSize: 16,
    fontWeight: 'bold',
  },
  quickCommands: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#00d4ff',
    marginBottom: 10,
  },
  quickButton: {
    backgroundColor: '#1a1a2e',
    borderRadius: 10,
    padding: 12,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#333',
  },
  quickButtonText: {
    color: '#fff',
    fontSize: 14,
  },
  resultCard: {
    backgroundColor: '#1a1a2e',
    borderRadius: 15,
    padding: 15,
    borderWidth: 1,
    borderColor: '#00ff88',
  },
  resultText: {
    color: '#fff',
    fontSize: 12,
    fontFamily: 'monospace',
  },
});
