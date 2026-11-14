"""
Управление сетью для JARVIS
"""

import subprocess
import socket
import psutil
from typing import Dict, List, Optional


class NetworkManager:
    """Управление сетевыми операциями Windows."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger

    def get_ip_info(self) -> Dict:
        """Получить информацию об IP-адресах."""
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)

            # Получаем все сетевые интерфейсы
            interfaces = []
            for name, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == socket.AF_INET:
                        interfaces.append({
                            "name": name,
                            "ip": addr.address,
                            "netmask": addr.netmask
                        })

            return {
                "status": "ok",
                "hostname": hostname,
                "local_ip": local_ip,
                "interfaces": interfaces
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения IP информации: {e}")
            return {"status": "error", "message": str(e)}

    def get_public_ip(self) -> Dict:
        """Получить публичный IP-адрес."""
        try:
            import urllib.request
            import json

            # Используем несколько сервисов для надёжности
            services = [
                "https://api.ipify.org?format=json",
                "https://ipinfo.io/json",
                "https://api.my-ip.io/v2/ip.json"
            ]

            for service in services:
                try:
                    req = urllib.request.Request(service, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=5) as response:
                        data = json.loads(response.read().decode())
                        ip = data.get('ip') or data.get('query')
                        if ip:
                            return {
                                "status": "ok",
                                "public_ip": ip,
                                "service": service
                            }
                except Exception:
                    continue

            return {"status": "error", "message": "Не удалось получить публичный IP"}
        except Exception as e:
            self.logger.error(f"Ошибка получения публичного IP: {e}")
            return {"status": "error", "message": str(e)}

    def get_network_stats(self) -> Dict:
        """Получить статистику сети."""
        try:
            net_io = psutil.net_io_counters()

            return {
                "status": "ok",
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
                "errin": net_io.errin,
                "errout": net_io.errout,
                "dropin": net_io.dropin,
                "dropout": net_io.dropout,
                "sent_mb": round(net_io.bytes_sent / (1024 * 1024), 2),
                "recv_mb": round(net_io.bytes_recv / (1024 * 1024), 2)
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения статистики сети: {e}")
            return {"status": "error", "message": str(e)}

    def get_active_connections(self) -> Dict:
        """Получить список активных сетевых соединений."""
        try:
            connections = []
            for conn in psutil.net_connections(kind='inet'):
                try:
                    if conn.status == 'ESTABLISHED':
                        connections.append({
                            "fd": conn.fd,
                            "family": str(conn.family),
                            "type": str(conn.type),
                            "local_addr": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                            "remote_addr": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                            "status": conn.status,
                            "pid": conn.pid
                        })
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    pass

            return {
                "status": "ok",
                "count": len(connections),
                "connections": connections[:50]  # Ограничиваем до 50
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения соединений: {e}")
            return {"status": "error", "message": str(e)}

    def ping(self, host: str, count: int = 4) -> Dict:
        """Выполнить ping к хосту."""
        try:
            # Windows ping
            result = subprocess.run(
                ['ping', '-n', str(count), host],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                # Парсим результат
                output = result.stdout
                avg_time = None

                # Ищем среднее время
                for line in output.split('\n'):
                    if 'Среднее' in line or 'Average' in line:
                        # Извлекаем число
                        import re
                        match = re.search(r'(\d+)\s*мс', line)
                        if match:
                            avg_time = int(match.group(1))

                return {
                    "status": "ok",
                    "host": host,
                    "reachable": True,
                    "avg_time_ms": avg_time,
                    "output": output
                }
            else:
                return {
                    "status": "ok",
                    "host": host,
                    "reachable": False,
                    "output": result.stdout
                }
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "Таймаут ping"}
        except Exception as e:
            self.logger.error(f"Ошибка ping: {e}")
            return {"status": "error", "message": str(e)}

    def speed_test(self) -> Dict:
        """Тест скорости интернета (упрощённый)."""
        try:
            import urllib.request
            import time

            # Тест загрузки (скачиваем 1MB файл)
            test_url = "http://speedtest.tele2.net/1MB.zip"

            start_time = time.time()
            req = urllib.request.Request(test_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30) as response:
                data = response.read()
            end_time = time.time()

            duration = end_time - start_time
            size_mb = len(data) / (1024 * 1024)
            speed_mbps = (size_mb * 8) / duration  # Mbps

            return {
                "status": "ok",
                "download_speed_mbps": round(speed_mbps, 2),
                "test_size_mb": round(size_mb, 2),
                "duration_sec": round(duration, 2)
            }
        except Exception as e:
            self.logger.error(f"Ошибка теста скорости: {e}")
            return {"status": "error", "message": str(e)}

    def get_wifi_networks(self) -> Dict:
        """Получить список доступных Wi-Fi сетей (Windows)."""
        try:
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'networks'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                networks = []
                current_ssid = None
                current_signal = None

                for line in result.stdout.split('\n'):
                    if 'SSID' in line and ':' in line:
                        current_ssid = line.split(':')[1].strip()
                    elif 'Signal' in line and ':' in line:
                        current_signal = line.split(':')[1].strip()
                        if current_ssid:
                            networks.append({
                                "ssid": current_ssid,
                                "signal": current_signal
                            })
                            current_ssid = None

                return {
                    "status": "ok",
                    "count": len(networks),
                    "networks": networks
                }
            else:
                return {"status": "error", "message": "Ошибка выполнения netsh"}
        except Exception as e:
            self.logger.error(f"Ошибка получения Wi-Fi сетей: {e}")
            return {"status": "error", "message": str(e)}

    def flush_dns(self) -> Dict:
        """Очистить DNS кэш."""
        try:
            result = subprocess.run(
                ['ipconfig', '/flushdns'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                self.logger.info("DNS кэш очищен")
                return {"status": "ok", "message": "DNS кэш очищен"}
            else:
                return {"status": "error", "message": "Ошибка очистки DNS"}
        except Exception as e:
            self.logger.error(f"Ошибка очистки DNS: {e}")
            return {"status": "error", "message": str(e)}

    def release_renew_ip(self) -> Dict:
        """Освободить и обновить IP-адрес (DHCP)."""
        try:
            # Release
            subprocess.run(['ipconfig', '/release'], capture_output=True, timeout=10)
            # Renew
            result = subprocess.run(
                ['ipconfig', '/renew'],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                self.logger.info("IP-адрес обновлён")
                return {"status": "ok", "message": "IP-адрес обновлён"}
            else:
                return {"status": "error", "message": "Ошибка обновления IP"}
        except Exception as e:
            self.logger.error(f"Ошибка обновления IP: {e}")
            return {"status": "error", "message": str(e)}
