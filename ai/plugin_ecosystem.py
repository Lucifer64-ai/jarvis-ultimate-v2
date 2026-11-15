"""
JARVIS Plugin Ecosystem
Интеграция с Gmail, Google Calendar, Slack, Notion
"""

import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class PluginEcosystem:
    """Система плагинов для JARVIS"""

    def __init__(self):
        self.plugins = {}
        self._init_plugins()

    def _init_plugins(self):
        """Инициализация плагинов"""

        # Gmail Plugin
        self.plugins['gmail'] = {
            'name': 'Gmail',
            'enabled': False,
            'client': None,
            'methods': {
                'send_email': self._gmail_send,
                'read_emails': self._gmail_read,
                'search_emails': self._gmail_search
            }
        }

        # Google Calendar Plugin
        self.plugins['calendar'] = {
            'name': 'Google Calendar',
            'enabled': False,
            'client': None,
            'methods': {
                'create_event': self._calendar_create,
                'list_events': self._calendar_list,
                'delete_event': self._calendar_delete
            }
        }

        # Slack Plugin
        self.plugins['slack'] = {
            'name': 'Slack',
            'enabled': False,
            'client': None,
            'methods': {
                'send_message': self._slack_send,
                'read_messages': self._slack_read,
                'list_channels': self._slack_channels
            }
        }

        # Notion Plugin
        self.plugins['notion'] = {
            'name': 'Notion',
            'enabled': False,
            'client': None,
            'methods': {
                'create_page': self._notion_create,
                'read_page': self._notion_read,
                'search_pages': self._notion_search
            }
        }

    def enable_plugin(self, plugin_name: str, credentials: Dict) -> bool:
        """Включение плагина с учётными данными"""
        if plugin_name not in self.plugins:
            print(f"❌ Плагин не найден: {plugin_name}")
            return False

        try:
            if plugin_name == 'gmail':
                from google.oauth2.credentials import Credentials
                from googleapiclient.discovery import build

                creds = Credentials.from_authorized_user_info(credentials)
                self.plugins['gmail']['client'] = build('gmail', 'v1', credentials=creds)
                self.plugins['gmail']['enabled'] = True
                print("✅ Gmail плагин включён")
                return True

            elif plugin_name == 'calendar':
                from google.oauth2.credentials import Credentials
                from googleapiclient.discovery import build

                creds = Credentials.from_authorized_user_info(credentials)
                self.plugins['calendar']['client'] = build('calendar', 'v3', credentials=creds)
                self.plugins['calendar']['enabled'] = True
                print("✅ Google Calendar плагин включён")
                return True

            elif plugin_name == 'slack':
                import slack_sdk

                token = credentials.get('token')
                self.plugins['slack']['client'] = slack_sdk.WebClient(token=token)
                self.plugins['slack']['enabled'] = True
                print("✅ Slack плагин включён")
                return True

            elif plugin_name == 'notion':
                from notion_client import Client

                token = credentials.get('token')
                self.plugins['notion']['client'] = Client(auth=token)
                self.plugins['notion']['enabled'] = True
                print("✅ Notion плагин включён")
                return True

        except Exception as e:
            print(f"❌ Ошибка включения плагина {plugin_name}: {e}")
            return False

    def call_method(self, plugin_name: str, method_name: str, **kwargs):
        """Вызов метода плагина"""
        if plugin_name not in self.plugins:
            return {'success': False, 'error': 'Плагин не найден'}

        plugin = self.plugins[plugin_name]

        if not plugin['enabled']:
            return {'success': False, 'error': f"Плагин {plugin_name} не включён"}

        if method_name not in plugin['methods']:
            return {'success': False, 'error': f"Метод {method_name} не найден"}

        try:
            result = plugin['methods'][method_name](**kwargs)
            return {'success': True, 'result': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # Gmail методы
    def _gmail_send(self, to: str, subject: str, body: str) -> Dict:
        """Отправка email через Gmail"""
        from email.mime.text import MIMEText
        import base64

        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        result = self.plugins['gmail']['client'].users().messages().send(
            userId='me',
            body={'raw': raw}
        ).execute()

        return {'message_id': result['id']}

    def _gmail_read(self, max_results: int = 10) -> List[Dict]:
        """Чтение последних email"""
        results = self.plugins['gmail']['client'].users().messages().list(
            userId='me',
            maxResults=max_results
        ).execute()

        messages = results.get('messages', [])
        emails = []

        for msg in messages:
            message = self.plugins['gmail']['client'].users().messages().get(
                userId='me',
                id=msg['id']
            ).execute()

            emails.append({
                'id': message['id'],
                'subject': next((h['value'] for h in message['payload']['headers'] if h['name'] == 'Subject'), ''),
                'from': next((h['value'] for h in message['payload']['headers'] if h['name'] == 'From'), ''),
                'date': next((h['value'] for h in message['payload']['headers'] if h['name'] == 'Date'), '')
            })

        return emails

    def _gmail_search(self, query: str, max_results: int = 10) -> List[Dict]:
        """Поиск email"""
        results = self.plugins['gmail']['client'].users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results
        ).execute()

        return results.get('messages', [])

    # Calendar методы
    def _calendar_create(self, summary: str, start_time: str, end_time: str, description: str = "") -> Dict:
        """Создание события в календаре"""
        event = {
            'summary': summary,
            'description': description,
            'start': {'dateTime': start_time, 'timeZone': 'Europe/Moscow'},
            'end': {'dateTime': end_time, 'timeZone': 'Europe/Moscow'}
        }

        result = self.plugins['calendar']['client'].events().insert(
            calendarId='primary',
            body=event
        ).execute()

        return {'event_id': result['id'], 'link': result.get('htmlLink')}

    def _calendar_list(self, max_results: int = 10) -> List[Dict]:
        """Список предстоящих событий"""
        now = datetime.utcnow().isoformat() + 'Z'

        events_result = self.plugins['calendar']['client'].events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        return [{
            'id': event['id'],
            'summary': event.get('summary', ''),
            'start': event['start'].get('dateTime', event['start'].get('date')),
            'end': event['end'].get('dateTime', event['end'].get('date'))
        } for event in events]

    def _calendar_delete(self, event_id: str) -> bool:
        """Удаление события"""
        self.plugins['calendar']['client'].events().delete(
            calendarId='primary',
            eventId=event_id
        ).execute()
        return True

    # Slack методы
    def _slack_send(self, channel: str, text: str) -> Dict:
        """Отправка сообщения в Slack"""
        result = self.plugins['slack']['client'].chat_postMessage(
            channel=channel,
            text=text
        )
        return {'ts': result['ts'], 'channel': result['channel']}

    def _slack_read(self, channel: str, limit: int = 10) -> List[Dict]:
        """Чтение сообщений из Slack"""
        result = self.plugins['slack']['client'].conversations_history(
            channel=channel,
            limit=limit
        )
        return result.get('messages', [])

    def _slack_channels(self) -> List[Dict]:
        """Список каналов Slack"""
        result = self.plugins['slack']['client'].conversations_list()
        return result.get('channels', [])

    # Notion методы
    def _notion_create(self, parent_id: str, title: str, content: str) -> Dict:
        """Создание страницы в Notion"""
        new_page = self.plugins['notion']['client'].pages.create(
            parent={'page_id': parent_id},
            properties={
                'title': {'title': [{'text': {'content': title}}]}
            },
            children=[
                {
                    'object': 'block',
                    'type': 'paragraph',
                    'paragraph': {
                        'rich_text': [{'type': 'text', 'text': {'content': content}}]
                    }
                }
            ]
        )
        return {'page_id': new_page['id'], 'url': new_page['url']}

    def _notion_read(self, page_id: str) -> Dict:
        """Чтение страницы из Notion"""
        page = self.plugins['notion']['client'].pages.retrieve(page_id=page_id)
        blocks = self.plugins['notion']['client'].blocks.children.list(block_id=page_id)

        return {
            'page': page,
            'blocks': blocks.get('results', [])
        }

    def _notion_search(self, query: str) -> List[Dict]:
        """Поиск страниц в Notion"""
        results = self.plugins['notion']['client'].search(query=query)
        return results.get('results', [])

    def list_plugins(self) -> List[Dict]:
        """Список всех плагинов"""
        return [{
            'name': name,
            'enabled': plugin['enabled'],
            'methods': list(plugin['methods'].keys())
        } for name, plugin in self.plugins.items()]

# Пример использования
if __name__ == "__main__":
    ecosystem = PluginEcosystem()

    # Включение Gmail
    ecosystem.enable_plugin('gmail', {
        'token': 'your-token',
        'refresh_token': 'your-refresh-token',
        'client_id': 'your-client-id',
        'client_secret': 'your-client-secret'
    })

    # Отправка email
    result = ecosystem.call_method('gmail', 'send_email',
        to='test@example.com',
        subject='Test',
        body='Hello from JARVIS!'
    )
    print(result)
