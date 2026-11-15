"""
JARVIS Confirmation-Gated Shell
Безопасное выполнение опасных команд с подтверждением
"""

import subprocess
import time
from typing import Callable, Optional

class ConfirmationShell:
    """Безопасное выполнение команд с подтверждением"""

    def __init__(self, voice_confirm_callback: Optional[Callable] = None):
        self.voice_confirm_callback = voice_confirm_callback
        self.dangerous_commands = [
            'rm', 'del', 'format', 'shutdown', 'restart',
            'fdisk', 'diskpart', 'reg delete', 'taskkill /F'
        ]
        self.pending_command = None
        self.confirmation_timeout = 30

    def is_dangerous(self, command: str) -> bool:
        """Проверка, является ли команда опасной"""
        command_lower = command.lower()
        return any(dangerous in command_lower for dangerous in self.dangerous_commands)

    def execute(self, command: str, require_confirmation: bool = True) -> dict:
        """Выполнение команды"""
        if self.is_dangerous(command) and require_confirmation:
            self.pending_command = command

            if self.voice_confirm_callback:
                self.voice_confirm_callback(
                    f"Выполнить опасную команду: {command}? Скажите 'да' для подтверждения"
                )

                start_time = time.time()
                while time.time() - start_time < self.confirmation_timeout:
                    if self.pending_command is None:
                        return self._execute_command(command)
                    time.sleep(0.1)

                self.pending_command = None
                return {
                    'success': False,
                    'error': 'Время подтверждения истекло'
                }
            else:
                response = input(f"⚠️ Опасная команда: {command}\nПодтвердите выполнение (да/нет): ")
                if response.lower() in ['да', 'yes', 'y']:
                    return self._execute_command(command)
                else:
                    return {
                        'success': False,
                        'error': 'Выполнение отменено'
                    }
        else:
            return self._execute_command(command)

    def confirm(self):
        """Подтверждение выполнения pending команды"""
        if self.pending_command:
            command = self.pending_command
            self.pending_command = None
            return self._execute_command(command)
        return {'success': False, 'error': 'Нет ожидающей команды'}

    def cancel(self):
        """Отмена pending команды"""
        if self.pending_command:
            self.pending_command = None
            return {'success': True, 'message': 'Команда отменена'}
        return {'success': False, 'error': 'Нет ожидающей команды'}

    def _execute_command(self, command: str) -> dict:
        """Внутренний метод выполнения команды"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )

            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Время выполнения истекло'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
