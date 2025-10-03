# synthetic_data_kit/create/qa_generator.py
import os
import json
from typing import List, Dict, Any
from synthetic_data_kit.utils.chunker import chunk_text
from synthetic_data_kit.providers.bedrock_provider import BedrockProvider

class Generator:
    def __init__(self, provider: BedrockProvider, config: Dict[str, Any]):
        self.provider = provider
        self.config = config
        self.prompts = config['prompts']

    def generate_pairs(self, text_chunk: str, num_pairs: int = 5, generation_type: str = "qa") -> List[Dict[str, Any]]:
        """Generate QA or CoT pairs from a single chunk"""
        if generation_type not in ["qa", "cot"]:
            raise ValueError("generation_type must be 'qa' or 'cot'")

        prompt_key = "qa_generation" if generation_type == "qa" else "cot_generation"
        prompt_template = self.prompts[prompt_key]
        prompt = prompt_template.format(text=text_chunk, num_pairs=num_pairs)

        response = self.provider.generate(
            prompt,
            temperature=self.config['generation']['temperature']
        )

        # Extract text from Claude response
        text_output = ""
        if "content" in response and len(response["content"]) > 0:
            text_output = response["content"][0]["text"]

        # Parse JSON
        try:
            pairs = json.loads(text_output.strip())
            if not isinstance(pairs, list):
                pairs = [pairs]
            return pairs
        except json.JSONDecodeError:
            print("❌ Failed to parse JSON.")
            print("Raw response:", text_output)
            return []

    def process_document(self, text: str, num_pairs: int = 10, generation_type: str = "qa") -> List[Dict[str, Any]]:
        """Split doc into chunks and generate pairs"""
        chunk_size = self.config['generation']['chunk_size']
        chunk_overlap = self.config['generation']['chunk_overlap']

        chunks = chunk_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        pairs_per_chunk = max(1, num_pairs // len(chunks))

        all_pairs = []
        for i, chunk in enumerate(chunks):
            # Adjust for last chunk
            if i == len(chunks) - 1:
                remaining = num_pairs - len(all_pairs)
                pairs_this_chunk = max(pairs_per_chunk, remaining)
            else:
                pairs_this_chunk = pairs_per_chunk

            pairs = self.generate_pairs(chunk, pairs_this_chunk, generation_type)
            all_pairs.extend(pairs)

            if len(all_pairs) >= num_pairs:
                break

        return all_pairs[:num_pairs]

    def save_pairs(self, pairs: List[Dict[str, Any]], pdf_name: str, generation_type: str):
        os.makedirs("data/generated", exist_ok=True)
        suffix = "qa" if generation_type == "qa" else "cot"
        out_path = f"data/generated/{pdf_name}_{suffix}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(pairs, f, indent=2)
        print(f"💾 Saved {len(pairs)} {generation_type.upper()} pairs to {out_path}")

    def parse_json_response(self, response_text: str) -> List[Dict]:
        """Parse JSON response from the model"""
        try:
            # Clean up markdown formatting
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            cleaned_text = cleaned_text.strip()
            
            return json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON.")
            print(f"Raw response: {response_text[:200]}...")
            return []