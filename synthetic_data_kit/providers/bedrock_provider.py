# synthetic_data_kit/providers/bedrock_provider.py
import boto3, json
from typing import List, Dict

class BedrockProvider:
    def __init__(self, model_id="global.anthropic.claude-sonnet-4-20250514-v1:0", region="us-east-1"):
        self.model_id = model_id
        self.client = boto3.client("bedrock-runtime", region_name=region)

    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 64000):
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body)
        )
        result = json.loads(response["body"].read())
        return result
    def generate_with_tools(self, messages: List[Dict], tools: List[Dict], max_tokens: int = 2000) -> Dict:
        """Generate response with tool calling capability"""
        
        # Convert messages to Claude format
        system_message = "You are a helpful assistant with access to tools."
        user_messages = []
        
        for msg in messages:
            if msg["role"] == "user":
                if isinstance(msg["content"], list):
                    # Handle tool results
                    content_text = ""
                    for item in msg["content"]:
                        if isinstance(item, dict) and "content" in item:
                            content_text += f"Tool result: {item['content']}\n"
                        else:
                            content_text += str(item)
                    user_messages.append(content_text)
                else:
                    user_messages.append(msg["content"])
        
        # Combine all user messages
        combined_prompt = "\n".join(user_messages)
        
        # Add tool descriptions to prompt
        tool_descriptions = []
        for tool in tools:
            tool_desc = f"Tool: {tool['name']} - {tool['description']}"
            tool_descriptions.append(tool_desc)
        
        enhanced_prompt = f"""You have access to these tools:
    {chr(10).join(tool_descriptions)}

    When you need to use a tool, respond with:
    <tool_use>
    <tool_name>tool_name_here</tool_name>
    <parameters>
    {{"param1": "value1", "param2": "value2"}}
    </parameters>
    </tool_use>

    User request: {combined_prompt}"""
        
        response = self.generate(enhanced_prompt, max_tokens=max_tokens)
        
        # Parse response for tool usage
        if isinstance(response, dict) and "content" in response:
            text_content = ""
            for content_block in response["content"]:
                if content_block.get("type") == "text":
                    text_content += content_block.get("text", "")
            
            # Check for tool usage
            if "<tool_use>" in text_content:
                # Simple tool parsing - you can enhance this
                return {
                    "content": [{"type": "text", "text": text_content}],
                    "stop_reason": "tool_use"
                }
            else:
                return {
                    "content": [{"type": "text", "text": text_content}],
                    "stop_reason": "end_turn"
                }
        
        return response