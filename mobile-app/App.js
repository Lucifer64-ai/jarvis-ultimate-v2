import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import HomeScreen from './src/screens/HomeScreen';
import StatusScreen from './src/screens/StatusScreen';
import SettingsScreen from './src/screens/SettingsScreen';
import LogScreen from './src/screens/LogScreen';
import QRScannerScreen from './src/screens/QRScannerScreen';

const Stack = createStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator 
        initialRouteName="Home"
        screenOptions={{
          headerStyle: { backgroundColor: '#1a1a2e' },
          headerTintColor: '#00d4ff',
          headerTitleStyle: { fontWeight: 'bold' }
        }}
      >
        <Stack.Screen 
          name="Home" 
          component={HomeScreen}
          options={{ title: '🤖 JARVIS' }}
        />
        <Stack.Screen 
          name="QRScanner" 
          component={QRScannerScreen}
          options={{ title: '📷 Сканировать QR' }}
        />
        <Stack.Screen 
          name="Status" 
          component={StatusScreen}
          options={{ title: '📊 Статус системы' }}
        />
        <Stack.Screen 
          name="Settings" 
          component={SettingsScreen}
          options={{ title: '⚙️ Настройки' }}
        />
        <Stack.Screen 
          name="Log" 
          component={LogScreen}
          options={{ title: '📝 Лог команд' }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
