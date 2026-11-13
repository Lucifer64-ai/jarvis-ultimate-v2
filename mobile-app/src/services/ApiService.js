import axios from 'axios';

const API_BASE_URL = 'http://YOUR_PC_IP:8080';

class ApiService {
  static async login(username, password) {
    const response = await axios.post(`${API_BASE_URL}/api/auth/login`, {
      username,
      password,
    });
    return response.data;
  }

  static async getStatus(token) {
    const response = await axios.get(`${API_BASE_URL}/api/status`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  }

  static async sendCommand(token, command) {
    const response = await axios.post(
      `${API_BASE_URL}/api/command`,
      { command },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    return response.data;
  }

  static async getDevices(token) {
    const response = await axios.get(`${API_BASE_URL}/api/devices`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  }

  static async controlDevice(token, entityId, action) {
    const response = await axios.post(
      `${API_BASE_URL}/api/device/control`,
      { entity_id: entityId, action },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    return response.data;
  }

  static async getSensors(token) {
    const response = await axios.get(`${API_BASE_URL}/api/sensors`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  }
}

export default ApiService;
