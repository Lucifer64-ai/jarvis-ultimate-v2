import React, { createContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import ApiService from './ApiService';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(null);
  const [username, setUsername] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStoredAuth();
  }, []);

  const loadStoredAuth = async () => {
    try {
      const storedToken = await AsyncStorage.getItem('token');
      const storedUsername = await AsyncStorage.getItem('username');
      if (storedToken && storedUsername) {
        setToken(storedToken);
        setUsername(storedUsername);
      }
    } catch (error) {
      console.error('Error loading auth:', error);
    } finally {
      setLoading(false);
    }
  };

  const login = async (user, pass) => {
    try {
      const response = await ApiService.login(user, pass);
      if (response.token) {
        await AsyncStorage.setItem('token', response.token);
        await AsyncStorage.setItem('username', user);
        setToken(response.token);
        setUsername(user);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };

  const logout = async () => {
    try {
      await AsyncStorage.removeItem('token');
      await AsyncStorage.removeItem('username');
      setToken(null);
      setUsername(null);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  if (loading) {
    return null;
  }

  return (
    <AuthContext.Provider value={{ token, username, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
