"""Main pipeline for synthetic data generation"""
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
    # Load configuration
    config = load_config()
    logger.info("✓ Loaded configuration from configs/config.yaml")

    # Init provider
    provider = BedrockProvider(
        model_id=config["bedrock"]["model"],
        region=config["bedrock"]["region"],
    )
    logger.info(f"✓ Initialized Bedrock provider ({config['bedrock']['model']})")

    # Setup directories with fallbacks
    input_dir = Path(config.get("data", {}).get("input_dir", "data/input"))
    output_dir = Path(config.get("data", {}).get("output_dir", "data"))
    output_dir.mkdir(parents=True, exist_ok=True)

    # STEP 1: INGEST PDF
    logger.info("\n" + "=" * 50)
    logger.info("STEP 1: PDF Ingestion and Parsing")
    logger.info("=" * 50)

    pdf_parser = PDFParser()
    all_chunks = {}

    pdf_files = list(input_dir.glob("*.pdf"))
    logger.info(f"Found {len(pdf_files)} PDF(s).")

    for pdf_path in pdf_files:
        logger.info(f"\nProcessing {pdf_path.name}")

        text = pdf_parser.parse(str(pdf_path))
        logger.info(f"Extracted {len(text)} characters")

        # Chunk
        chunks = chunk_text(
            text,
            chunk_size=config["generation"]["chunk_size"],
            chunk_overlap=config["generation"]["chunk_overlap"],
        )
        logger.info(f"Created {len(chunks)} chunks")

        all_chunks[pdf_path.stem] = chunks

        # save parsed text
        parsed_dir = Path("data/parsed")
        parsed_dir.mkdir(parents=True, exist_ok=True)
        with open(parsed_dir / f"{pdf_path.stem}.txt", "w", encoding="utf-8") as f:
            f.write(text)

    # combine all chunks
    all_combined_chunks = []
    for chunks in all_chunks.values():
        all_combined_chunks.extend(chunks)

    logger.info(f"\nTotal chunks across PDFs: {len(all_combined_chunks)}")

    # STEP 2: QA GENERATION
    logger.info("\n" + "=" * 50)
    logger.info("STEP 2: QA Generation")
    logger.info("=" * 50)

    qa_generator = Generator(provider, config)
    num_qa_questions = config["generation"]["num_qa_pairs"]

    qa_pairs = qa_generator.process_document(
        text="\n".join(all_combined_chunks),
        num_pairs=num_qa_questions,
        generation_type="qa",
    )
    qa_generator.save_pairs(qa_pairs, "combined", generation_type="qa")

    # STEP 3: COT GENERATION
    logger.info("\n" + "=" * 50)
    logger.info("STEP 3: Chain-of-Thought (COT) Generation")
    logger.info("=" * 50)

    num_cot_questions = config["generation"]["num_cot_pairs"]

    cot_pairs = qa_generator.process_document(
        text="\n".join(all_combined_chunks),
        num_pairs=num_cot_questions,
        generation_type="cot",
    )
    qa_generator.save_pairs(cot_pairs, "combined", generation_type="cot")

    # STEP 4: TOOL USE GENERATION
    if config.get("tool_use", {}).get("enabled", False):
        logger.info("\n" + "=" * 50)
        logger.info("STEP 4: Tool-Use Generation")
        logger.info("=" * 50)

        try:
            tool_use_generator = ToolUseGenerator(provider)
            queries_per_chunk = config["tool_use"].get("queries_per_chunk", 3)

            # Limit to avoid too many API calls
            max_chunks_for_tools = 3  # Reduced further
            selected_chunks = all_combined_chunks[:max_chunks_for_tools]

            tool_examples = tool_use_generator.generate_from_chunks(
                chunks=selected_chunks,
                queries_per_chunk=queries_per_chunk,
            )

            tool_output_file = output_dir / "generated" / "combined_tool_use.jsonl"
            tool_output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(tool_output_file, "w") as f:
                for ex in tool_examples:
                    f.write(json.dumps(ex) + "\n")

            logger.info(f"✓ Generated {len(tool_examples)} tool-use examples")
            logger.info(f"✓ Saved to {tool_output_file}")
        except Exception as e:
            logger.error(f"Tool-use generation failed: {e}")
            logger.info("Continuing with curation...")
    else:
        logger.info("Tool-use generation skipped (disabled in config)")

    # STEP 5: CURATION - FIXED METHOD NAME
    logger.info("\n" + "=" * 50)
    logger.info("STEP 5: Quality Curation")
    logger.info("=" * 50)

    curator = QualityCurator(provider, config)

    # Use the correct method name 'curate' instead of 'curate_pairs'
    curated_qa, qa_metrics = curator.curate(qa_pairs, "combined", "qa")
    curated_cot, cot_metrics = curator.curate(cot_pairs, "combined", "cot")

    # FINAL SUMMARY
    logger.info("\n" + "=" * 50)
    logger.info("PIPELINE COMPLETE - SUMMARY")
    logger.info("=" * 50)
    logger.info(f"PDFs processed: {len(pdf_files)}")
    logger.info(f"Total chunks: {len(all_combined_chunks)}")
    logger.info(f"QA pairs generated: {len(qa_pairs)} → curated: {len(curated_qa)}")
    logger.info(f"COT pairs generated: {len(cot_pairs)} → curated: {len(curated_cot)}")
    logger.info(f"\nOutputs saved to {output_dir}")


if __name__ == "__main__":
    main()