# synthetic_data_kit/curate/judge.py
import os
import json
import re
from typing import List, Dict, Any, Tuple
from synthetic_data_kit.providers.bedrock_provider import BedrockProvider


class QualityCurator:
    def __init__(self, provider: BedrockProvider, config: Dict[str, Any]):
        self.provider = provider
        self.config = config
        self.rating_prompt = config['prompts']['qa_rating']
        self.threshold = config['curate']['threshold']
        self.batch_size = config['curate']['batch_size']

    def clean_json_response(self, text: str) -> str:
        """Remove markdown code fences and extra whitespace"""
        text = text.strip()

        # Remove ```json ... ``` or ``` ... ``` blocks
        if text.startswith("```"):
            text = re.sub(r"```[a-zA-Z]*\n?", "", text)
            text = text.replace("```", "").strip()

        return text

    def safe_json_parse(self, text_output: str):
        """Try to parse JSON with fallbacks for minor formatting issues"""
        text_output = self.clean_json_response(text_output)

        try:
            return json.loads(text_output)
        except json.JSONDecodeError:
            # Try trimming trailing commas/brackets
            repaired = text_output.rstrip(", \n")
            try:
                return json.loads(repaired)
            except Exception:
                # Fallback: return empty to avoid crash
                print("❌ Still failed to parse JSON, returning []. Raw starts with:")
                print(text_output[:300])
                return []

    def rate_batch(
        self, qa_pairs: List[Dict[str, Any]]
    ) -> List[Tuple[Dict[str, Any], Dict[str, float]]]:
        """Send a batch of QA pairs to model for rating"""
        pairs_json = json.dumps(
            [{"question": p.get("question"), "answer": p.get("answer")} for p in qa_pairs],
            indent=2
        )

        prompt = self.rating_prompt.format(pairs=pairs_json)
        
        # ← INCREASED max_tokens for curation to 4096
        response = self.provider.generate(prompt, temperature=0.2, max_tokens=4096)

        # Extract text
        text_output = ""
        if "content" in response and len(response["content"]) > 0:
            text_output = response["content"][0]["text"]

        ratings = self.safe_json_parse(text_output)
        if not isinstance(ratings, list):
            ratings = [ratings] if ratings else []

        results = []
        for pair, rating_obj in zip(qa_pairs, ratings):
            accuracy = rating_obj.get("accuracy", 0)
            relevance = rating_obj.get("relevance", 0)
            clarity = rating_obj.get("clarity", 0)
            usefulness = rating_obj.get("usefulness", 0)
            combined = rating_obj.get(
                "combined_score",
                accuracy + relevance + clarity + usefulness,
            )

            # Attach evaluation metrics to pair
            pair_with_eval = {
                **pair,
                "evaluation": {
                    "accuracy": accuracy,
                    "relevance": relevance,
                    "clarity": clarity,
                    "usefulness": usefulness,
                    "combined_score": combined,
                },
            }

            eval_dict = {
                "accuracy": accuracy,
                "relevance": relevance,
                "clarity": clarity,
                "usefulness": usefulness,
                "combined_score": combined,
            }

            results.append((pair_with_eval, eval_dict))

        return results

    def curate(self, qa_pairs: List[Dict[str, Any]], pdf_name: str, generation_type: str):
        """Curate dataset by filtering low-rated pairs"""
        curated = []

        all_accuracy, all_relevance, all_clarity, all_usefulness, all_combined = (
            [],
            [],
            [],
            [],
            [],
        )

        for i in range(0, len(qa_pairs), self.batch_size):
            batch = qa_pairs[i : i + self.batch_size]
            batch_results = self.rate_batch(batch)

            for pair_with_eval, eval_dict in batch_results:
                all_accuracy.append(eval_dict["accuracy"])
                all_relevance.append(eval_dict["relevance"])
                all_clarity.append(eval_dict["clarity"])
                all_usefulness.append(eval_dict["usefulness"])
                all_combined.append(eval_dict["combined_score"])

                if eval_dict["combined_score"] >= self.threshold:
                    curated.append(pair_with_eval)

        # Compute averages
        metrics = {
            "total": len(qa_pairs),
            "kept": len(curated),
            "avg_accuracy": round(sum(all_accuracy) / len(all_accuracy), 2)
            if all_accuracy
            else 0,
            "avg_relevance": round(sum(all_relevance) / len(all_relevance), 2)
            if all_relevance
            else 0,
            "avg_clarity": round(sum(all_clarity) / len(all_clarity), 2)
            if all_clarity
            else 0,
            "avg_usefulness": round(sum(all_usefulness) / len(all_usefulness), 2)
            if all_usefulness
            else 0,
            "avg_combined_score": round(sum(all_combined) / len(all_combined), 2)
            if all_combined
            else 0,
        }

        # Save curated output
        os.makedirs("data/curated", exist_ok=True)
        suffix = "qa" if generation_type == "qa" else "cot"
        out_file = f"data/curated/{pdf_name}_{suffix}_curated.json"

        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(curated, f, indent=2)

        print(f"\n💾 Saved {len(curated)}/{len(qa_pairs)} curated {generation_type.upper()} pairs → {out_file}")
        print("📊 Metrics:")
        print(f"   - Accuracy:    {metrics['avg_accuracy']}/3")
        print(f"   - Relevance:   {metrics['avg_relevance']}/2")
        print(f"   - Clarity:     {metrics['avg_clarity']}/2")
        print(f"   - Usefulness:  {metrics['avg_usefulness']}/3")
        print(f"   - Combined:    {metrics['avg_combined_score']}/10")

        return curated, metrics