import os
import boto3
from typing import List
from dotenv import load_dotenv
from services.utils.cognito_utils import get_user_from_token

load_dotenv()

class BedrockAgent:
    def __init__(self, app_manager):
        self.client = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.model_id = 'anthropic.claude-3-haiku-20240307-v1:0'
        self.app_manager = app_manager
        self.bedrock_guardrail_id = os.getenv('BEDROCK_GUARD_RAIL_ID')
        self.bedrock_guardrail_version = os.getenv('BEDROCK_GUARD_RAIL_VERSION')

    def call_bedrock(self, prompt: str, conversation_history: List = None, auth_header: str = None, tools: List = None) -> str:
        if conversation_history:
            history_text = "\n".join([f"User: {msg['user']}\nAssistant: {msg['assistant']}" for msg in conversation_history[-5:]])
            prompt = f"Previous conversation:\n{history_text}\n\nCurrent message: {prompt}"

        messages = [{"role": "user", "content": [{"text": prompt}]}]

        request_body = {
            "modelId": self.model_id,
            "messages": messages,
            "guardrailConfig": {
                "guardrailIdentifier": self.bedrock_guardrail_id,
                "guardrailVersion": self.bedrock_guardrail_version,
                "trace": "enabled"
            }
        }

        if tools:
            request_body["toolConfig"] = {"tools": tools}

        response = self.client.converse(**request_body)

        message_content = response['output']['message']['content']
        tool_use = next((c.get('toolUse') for c in message_content if 'toolUse' in c), None)

        if tool_use:
            tool_name = tool_use['name']
            tool_args = tool_use['input']
            user_id = get_user_from_token(auth_header)

            tool_result = self.app_manager.call_app_tool(tool_name, tool_args, user_id)
            messages.append({"role": "assistant", "content": [{"toolUse": tool_use}]})
            messages.append({
                "role": "user",
                "content": [{
                    "toolResult": {
                        "toolUseId": tool_use['toolUseId'],
                        "content": [{"text": tool_result}]
                    }
                }]
            })

        messages.append({"role": "user", "content": [{"text": "Please format this response nicely. Don't mention that you are formatting anything"}]})
        response = self.client.converse(
            modelId=self.model_id, 
            messages=messages, 
            toolConfig={"tools": tools},
            guardrailConfig={
                "guardrailIdentifier": self.bedrock_guardrail_id,
                "guardrailVersion": self.bedrock_guardrail_version,
                "trace": "enabled"
            })

        return {'completion': response['output']['message']['content'][0]['text']}