from openai import OpenAI
from pydantic import BaseModel
import os
import requests
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Persona(BaseModel):
    name: str
    description: str


class PersonaAgent:
    def __init__(self):
        self.current_persona = None
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def set_persona(self, message: str) -> Persona:
        completion = self.client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI assistant whose sole goal is to detect what persona the user is trying to set to. "
                            "You should return the persona name and a one sentence description of the persona. "
                            "If you do not know who the persona is, make up a fun persona that's one sentence."
                },
                {"role": "user", "content": message}
            ],
            response_format=Persona,
        )
        
        # return a fallback persona if gpt call fails
        if not completion.choices or not completion.choices[0].message.parsed:
            self.current_persona = Persona(name="Default Hero", description="A brave hero ready to help anyone in need.")
            return
        
        self.current_persona = completion.choices[0].message.parsed
                
    def build_persona_prompt(self, user_message: str) -> str:
        """Build system prompt with persona context"""
        system_prompt = f"""You are {self.current_persona.name}. 

Your one sentence persona description is:        
{self.current_persona.description}

Instructions:
- Respond completely in character
- Use their speech patterns, worldview, and personality
- Use information you have of this character even if it is not explicitly mentioned in the description
- Stay true to their established traits and motivations
- Be helpful while maintaining character authenticity
- Don't break character or mention you're an AI

User message: {user_message}"""
        
        return system_prompt
    
    def process_message(self, user_message: str, conversation_history: List = None, auth_header: str = None) -> str:
        """Main message processing with persona handling"""
        
        if not self.current_persona:
            self.set_persona(user_message)
            return {'completion': f"{self.current_persona.name} speaking"}
        
        # Build prompt based on current persona
        if self.current_persona:
            prompt = self.build_persona_prompt(user_message)
        else:
            prompt = user_message
        
        # Call Bedrock Lambda
        return self.call_bedrock(prompt, conversation_history, auth_header)
    
    def call_bedrock(self, prompt: str, conversation_history: List = None, auth_header: str = None) -> str:
        full_prompt = prompt
        if conversation_history:
            history_text = "\n".join([f"User: {msg['user']}\nAssistant: {msg['assistant']}" for msg in conversation_history[-5:]])
            full_prompt = f"Previous conversation:\n{history_text}\n\nCurrent message: {prompt}"
        
        response = requests.post(
            'https://x2pwa5y235.execute-api.us-east-1.amazonaws.com/Prod/generate',
            json={'prompt': full_prompt},
            headers={"Authorization": auth_header}
        )
        
        return response.json()