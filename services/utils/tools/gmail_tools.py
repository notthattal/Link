import requests
import os
import base64
from email.mime.text import MIMEText
from services.utils.tools.app_tool import AppTool

class GmailAppTool(AppTool):
    def __init__(self, table):
        super().__init__(table)
        self.client_id = os.getenv('GMAIL_CLIENT_ID')
        self.client_secret = os.getenv('GMAIL_CLIENT_SECRET')
        self.refresh_url = 'https://oauth2.googleapis.com/token'
        self.service_name = 'gmail'

    def get_tools(self):
        """Get Gmail tool definitions for Bedrock"""
        return [
            {
                "toolSpec": {
                    "name": "gmail_send_email",
                    "description": "Send an email using Gmail",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "to": {"type": "string", "description": "Recipient email address"},
                                "subject": {"type": "string", "description": "Email subject"},
                                "body": {"type": "string", "description": "Email body text"}
                            },
                            "required": ["to", "subject", "body"]
                        }
                    }
                }
            },
            {
                "toolSpec": {
                    "name": "gmail_list_messages",
                    "description": "List the user's most recent Gmail messages",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "max_results": {"type": "integer", "description": "Max number of messages", "default": 5}
                            }
                        }
                    }
                }
            },
            {
                "toolSpec": {
                    "name": "gmail_get_message",
                    "description": "Get a specific Gmail message by ID",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "message_id": {"type": "string", "description": "Gmail message ID"}
                            },
                            "required": ["message_id"]
                        }
                    }
                }
            }
        ]

    def call_tool(self, tool_name, tool_args, user_id):
        headers = self.get_app_headers(user_id)

        if tool_name == 'gmail_send_email':
            msg = MIMEText(tool_args['body'])
            msg['to'] = tool_args['to']
            msg['subject'] = tool_args['subject']
            raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
            response = requests.post(
                'https://gmail.googleapis.com/gmail/v1/users/me/messages/send',
                headers={**headers, 'Content-Type': 'application/json'},
                json={'raw': raw}
            )
            return "Email sent successfully" if response.status_code == 200 else f"Error sending email: {response.status_code}"

        elif tool_name == 'gmail_list_messages':
            max_results = tool_args.get('max_results', 5)
            list_resp = requests.get(
                'https://gmail.googleapis.com/gmail/v1/users/me/messages',
                headers=headers,
                params={'maxResults': max_results}
            )

            if list_resp.status_code == 200:
                messages = list_resp.json().get('messages', [])
                results = []

                for msg in messages:
                    msg_id = msg['id']
                    msg_resp = requests.get(
                        f'https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}',
                        headers=headers,
                        params={'format': 'metadata', 'metadataHeaders': ['Subject', 'From']}
                    )

                    try:
                        headers_list = msg_resp.json().get('payload', {}).get('headers', [])
                        subject = next((h['value'] for h in headers_list if h['name'] == 'Subject'), 'No Subject')
                        sender = next((h['value'] for h in headers_list if h['name'] == 'From'), 'Unknown Sender')
                        results.append(f"From: {sender} | Subject: {subject}")
                    except Exception as e:
                        print("Error parsing message:", e)
                        results.append(f"ID: {msg_id} (error parsing headers)")

                return "\n".join(results)
            
            return f"Error listing messages: {list_resp.status_code}"

        elif tool_name == 'gmail_get_message':
            message_id = tool_args['message_id']
            response = requests.get(
                f'https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}',
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                return data.get('snippet', 'No preview available')
            return f"Error retrieving message: {response.status_code}"

        return f"Unknown tool: {tool_name}"