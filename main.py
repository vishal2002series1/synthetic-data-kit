"""
Main pipeline for synthetic data generation
Replicates Meta's Llama Synthetic Data Kit functionality using AWS Bedrock Claude Sonnet
"""
import yaml
import logging
import json
from pathlib import Path

from synthetic_data_kit.providers.bedrock_provider import BedrockProvider
from synthetic_data_kit.ingest.pdf_parser import PDFParser
from synthetic_data_kit.utils.chunker import chunk_text
from synthetic_data_kit.create.qa_generator import Generator
from synthetic_data_kit.create.tool_use_generator import ToolUseGenerator
from synthetic_data_kit.curate.judge import QualityCurator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: str = "configs/config.yaml"):
    """Load configuration file"""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def main():
    """
    Main pipeline that processes PDFs and generates synthetic training data for LLM fine-tuning
    
    Pipeline Steps:
    1. PDF Ingestion: Parse and chunk PDF documents
    2. QA Generation: Generate question-answer pairs
    3. COT Generation: Generate chain-of-thought reasoning pairs  
    4. Tool-Use Generation: Generate tool-calling conversation examples
    5. Quality Curation: Filter and rate all generated pairs
    """
    
    # ═══════════════════════════════════════════════════════════════
    # INITIALIZATION
    # ═══════════════════════════════════════════════════════════════
    
    # Load configuration
    config = load_config()
    logger.info("✓ Loaded configuration from configs/config.yaml")

    # Initialize Bedrock provider
    provider = BedrockProvider(
        model_id=config["bedrock"]["model"],
        region=config["bedrock"]["region"],
    )
    logger.info(f"✓ Initialized Bedrock provider ({config['bedrock']['model']})")

    # Setup directories with fallbacks
    input_dir = Path(config.get("data", {}).get("input_dir", "data/input"))
    output_dir = Path(config.get("data", {}).get("output_dir", "data"))
    output_dir.mkdir(parents=True, exist_ok=True)

    # ═══════════════════════════════════════════════════════════════
    # STEP 1: PDF INGESTION AND PARSING
    # ═══════════════════════════════════════════════════════════════
    logger.info("\n" + "=" * 50)
    logger.info("STEP 1: PDF Ingestion and Parsing")
    logger.info("=" * 50)

    pdf_parser = PDFParser()
    all_chunks = {}

    pdf_files = list(input_dir.glob("*.pdf"))
    logger.info(f"Found {len(pdf_files)} PDF(s).")

    for pdf_path in pdf_files:
        logger.info(f"\nProcessing {pdf_path.name}")

        # Parse PDF to extract text
        text = pdf_parser.parse(str(pdf_path))
        logger.info(f"Extracted {len(text)} characters")

        # Chunk text for processing
        chunks = chunk_text(
            text,
            chunk_size=config["generation"]["chunk_size"],
            chunk_overlap=config["generation"]["chunk_overlap"],
        )
        logger.info(f"Created {len(chunks)} chunks")

        all_chunks[pdf_path.stem] = chunks

        # Save parsed text for reference
        parsed_dir = Path("data/parsed")
        parsed_dir.mkdir(parents=True, exist_ok=True)
        with open(parsed_dir / f"{pdf_path.stem}.txt", "w", encoding="utf-8") as f:
            f.write(text)

    # Combine all chunks from all PDFs
    all_combined_chunks = []
    for chunks in all_chunks.values():
        all_combined_chunks.extend(chunks)

    logger.info(f"\nTotal chunks across all PDFs: {len(all_combined_chunks)}")

    # ═══════════════════════════════════════════════════════════════
    # STEP 2: QA PAIR GENERATION
    # ═══════════════════════════════════════════════════════════════
    logger.info("\n" + "=" * 50)
    logger.info("STEP 2: QA Generation")
    logger.info("=" * 50)

    qa_generator = Generator(provider, config)
    num_qa_questions = config["generation"]["num_qa_pairs"]

    # Generate QA pairs from combined document content
    qa_pairs = qa_generator.process_document(
        text="\n".join(all_combined_chunks),
        num_pairs=num_qa_questions,
        generation_type="qa",
    )
    qa_generator.save_pairs(qa_pairs, "combined", generation_type="qa")
    logger.info(f"✓ Generated {len(qa_pairs)} QA pairs")

    # ═══════════════════════════════════════════════════════════════
    # STEP 3: CHAIN-OF-THOUGHT (COT) GENERATION
    # ═══════════════════════════════════════════════════════════════
    logger.info("\n" + "=" * 50)
    logger.info("STEP 3: Chain-of-Thought (COT) Generation")
    logger.info("=" * 50)

    num_cot_questions = config["generation"]["num_cot_pairs"]

    # Generate COT pairs with reasoning steps
    cot_pairs = qa_generator.process_document(
        text="\n".join(all_combined_chunks),
        num_pairs=num_cot_questions,
        generation_type="cot",
    )
    qa_generator.save_pairs(cot_pairs, "combined", generation_type="cot")
    logger.info(f"✓ Generated {len(cot_pairs)} COT pairs")

    # ═══════════════════════════════════════════════════════════════
    # STEP 4: TOOL-USE CONVERSATION GENERATION
    # ═══════════════════════════════════════════════════════════════
    if config.get("tool_use", {}).get("enabled", False):
        logger.info("\n" + "=" * 50)
        logger.info("STEP 4: Tool-Use Generation")
        logger.info("=" * 50)

        try:
            tool_use_generator = ToolUseGenerator(provider)
            queries_per_chunk = config["tool_use"].get("queries_per_chunk", 3)

            # Limit chunks to avoid excessive API calls
            max_chunks_for_tools = config["tool_use"].get("max_chunks", 5)
            selected_chunks = all_combined_chunks[:max_chunks_for_tools]

            # Generate tool-calling conversation examples
            tool_examples = tool_use_generator.generate_from_chunks(
                chunks=selected_chunks,
                queries_per_chunk=queries_per_chunk,
            )

            # Save tool-use examples
            tool_output_file = output_dir / "generated" / "combined_tool_use.jsonl"
            tool_output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(tool_output_file, "w") as f:
                for example in tool_examples:
                    f.write(json.dumps(example) + "\n")

            logger.info(f"✓ Generated {len(tool_examples)} tool-calling conversation examples")
            logger.info(f"✓ Saved to {tool_output_file}")
            
            # Also save as regular JSON for easier inspection
            tool_json_file = output_dir / "generated" / "combined_tool_use.json"
            with open(tool_json_file, "w") as f:
                json.dump(tool_examples, f, indent=2)
            
        except Exception as e:
            logger.error(f"Tool-use generation failed: {e}")
            logger.info("Continuing with curation...")
            tool_examples = []
    else:
        logger.info("Tool-use generation skipped (disabled in config)")
        tool_examples = []

    # ═══════════════════════════════════════════════════════════════
    # STEP 5: QUALITY CURATION
    # ═══════════════════════════════════════════════════════════════
    logger.info("\n" + "=" * 50)
    logger.info("STEP 5: Quality Curation")
    logger.info("=" * 50)

    curator = QualityCurator(provider, config)

    # Curate QA pairs
    curated_qa, qa_metrics = curator.curate(qa_pairs, "combined", "qa")
    logger.info(f"✓ QA curation complete: {len(curated_qa)}/{len(qa_pairs)} pairs kept")

    # Curate COT pairs
    curated_cot, cot_metrics = curator.curate(cot_pairs, "combined", "cot")
    logger.info(f"✓ COT curation complete: {len(curated_cot)}/{len(cot_pairs)} pairs kept")

    # ═══════════════════════════════════════════════════════════════
    # STEP 6: FINAL DATASET COMPILATION
    # ═══════════════════════════════════════════════════════════════
    logger.info("\n" + "=" * 50)
    logger.info("STEP 6: Final Dataset Compilation")
    logger.info("=" * 50)

    # Create final training dataset
    final_dataset = {
        "qa_pairs": curated_qa,
        "cot_pairs": curated_cot,
        "tool_use_conversations": tool_examples,
        "metadata": {
            "source_pdfs": [f.name for f in pdf_files],
            "total_chunks": len(all_combined_chunks),
            "generation_config": config["generation"],
            "qa_metrics": qa_metrics,
            "cot_metrics": cot_metrics
        }
    }

    # Save final compiled dataset
    final_dataset_file = output_dir / "final_training_dataset.json"
    with open(final_dataset_file, "w") as f:
        json.dump(final_dataset, f, indent=2)

    logger.info(f"✓ Final training dataset saved to {final_dataset_file}")

    # ═══════════════════════════════════════════════════════════════
    # PIPELINE SUMMARY
    # ═══════════════════════════════════════════════════════════════
    logger.info("\n" + "=" * 50)
    logger.info("PIPELINE COMPLETE - SUMMARY")
    logger.info("=" * 50)
    logger.info(f"📄 PDFs processed: {len(pdf_files)}")
    logger.info(f"📝 Total chunks: {len(all_combined_chunks)}")
    logger.info(f"❓ QA pairs: {len(qa_pairs)} → curated: {len(curated_qa)}")
    logger.info(f"🧠 COT pairs: {len(cot_pairs)} → curated: {len(curated_cot)}")
    logger.info(f"🔧 Tool-use examples: {len(tool_examples)}")
    logger.info(f"💾 Final dataset: {final_dataset_file}")
    logger.info(f"📊 Total training examples: {len(curated_qa) + len(curated_cot) + len(tool_examples)}")


if __name__ == "__main__":
    main()