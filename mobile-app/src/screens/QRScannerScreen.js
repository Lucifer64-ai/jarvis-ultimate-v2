import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, Alert, TouchableOpacity } from 'react-native';
import { RNCamera } from 'react-native-camera';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function QRScannerScreen({ navigation }) {
  const [scanning, setScanning] = useState(true);
  const [lastScan, setLastScan] = useState(null);

  const handleBarCodeRead = async (data) => {
    if (!scanning) return;

    setScanning(false);

    try {
      const qrData = JSON.parse(data.data);

      // Проверяем тип QR-кода
      if (qrData.type !== 'jarvis_connection') {
        Alert.alert('Ошибка', 'Это не QR-код JARVIS');
        setScanning(true);
        return;
      }

      // Проверяем срок действия
      const now = Math.floor(Date.now() / 1000);
      if (now > qrData.expires_at) {
        Alert.alert('Ошибка', 'QR-код истёк');
        setScanning(true);
        return;
      }

      // Сохраняем данные подключения
      await AsyncStorage.setItem('server_ip', qrData.server_ip);
      await AsyncStorage.setItem('server_port', qrData.server_port.toString());
      await AsyncStorage.setItem('auth_token', qrData.auth_token);

      Alert.alert(
        'Успешно!',
        `Подключение к JARVIS установлено!\nIP: ${qrData.server_ip}:${qrData.server_port}`,
        [
          {
            text: 'OK',
            onPress: () => navigation.navigate('Home')
          }
        ]
      );

    } catch (e) {
      Alert.alert('Ошибка', 'Не удалось прочитать QR-код');
      setScanning(true);
    }
  };

  return (
    <View style={styles.container}>
      <RNCamera
        style={styles.camera}
        onBarCodeRead={scanning ? handleBarCodeRead : undefined}
        captureAudio={false}
        type={RNCamera.Constants.Type.back}
        flashMode={RNCamera.Constants.FlashMode.auto}
      >
        <View style={styles.overlay}>
          <View style={styles.scanArea}>
            <Text style={styles.scanText}>
              Наведите камеру на QR-код JARVIS
            </Text>
          </View>

          <View style={styles.infoBox}>
            <Text style={styles.infoText}>
              📱 Откройте JARVIS на компьютере{'
'}
              🖥️ Перейдите в раздел "Подключение"{'
'}
              🔳 Покажите QR-код камере
            </Text>
          </View>

          <TouchableOpacity
            style={styles.cancelButton}
            onPress={() => navigation.goBack()}
          >
            <Text style={styles.cancelButtonText}>Отмена</Text>
          </TouchableOpacity>
        </View>
      </RNCamera>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000'
  },
  camera: {
    flex: 1
  },
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center'
  },
  scanArea: {
    width: 250,
    height: 250,
    borderWidth: 2,
    borderColor: '#00d4ff',
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0,212,255,0.1)'
  },
  scanText: {
    color: '#fff',
    fontSize: 16,
    textAlign: 'center',
    padding: 20
  },
  infoBox: {
    marginTop: 30,
    padding: 20,
    backgroundColor: 'rgba(26,26,46,0.9)',
    borderRadius: 10,
    marginHorizontal: 20
  },
  infoText: {
    color: '#fff',
    fontSize: 14,
    lineHeight: 24
  },
  cancelButton: {
    marginTop: 30,
    backgroundColor: '#ff4444',
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 10
  },
  cancelButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold'
  }
});
