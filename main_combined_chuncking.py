import os
import yaml
import random
from pathlib import Path
from synthetic_data_kit.providers.bedrock_provider import BedrockProvider
from synthetic_data_kit.ingest.pdf_parser import PDFParser
from synthetic_data_kit.utils.chunker import chunk_text
from synthetic_data_kit.create.qa_generator import Generator
from synthetic_data_kit.curate.judge import QualityCurator


def load_config(path="configs/config.yaml"):
    """Load YAML config"""
    with open(path, "r") as f:
        return yaml.safe_load(f)


def ingest_all_pdfs(input_dir: str, config):
    """Step 4: Ingest all PDFs → combined chunks"""
    print("\n" + "=" * 60)
    print("STEP 4: PDF INGESTION (ALL FILES)")
    print("=" * 60)

    pdf_files = list(Path(input_dir).glob("*.pdf"))
    
    if not pdf_files:
        print(f"❌ No PDF files found in {input_dir}")
        return None, []
    
    print(f"📚 Found {len(pdf_files)} PDF file(s)")
    
    all_chunks = []
    total_chars = 0
    parser = PDFParser()
    
    for pdf_path in pdf_files:
        print(f"\n📄 Parsing: {pdf_path.name}")
        text = parser.parse(str(pdf_path))
        total_chars += len(text)
        print(f"   ✅ Extracted {len(text):,} characters")
        
        # Chunk this PDF
        chunks = chunk_text(
            text,
            chunk_size=config['generation']['chunk_size'],
            chunk_overlap=config['generation']['chunk_overlap']
        )
        
        # Convert chunks to dicts and tag with source PDF
        for chunk in chunks:
            if isinstance(chunk, str):
                chunk_dict = {"text": chunk, "source_pdf": pdf_path.stem}
            else:
                chunk_dict = chunk
                chunk_dict['source_pdf'] = pdf_path.stem
            
            all_chunks.append(chunk_dict)
    
    print(f"\n📊 Combined Stats:")
    print(f"   - Total characters: {total_chars:,}")
    print(f"   - Total chunks: {len(all_chunks)}")
    print(f"   - Chunks per PDF: {len(all_chunks) // len(pdf_files)} avg")
    
    return all_chunks


def generate_pairs_in_batches(all_chunks, num_total, generation_type, provider, config):
    """Generate QA or COT pairs in batches from combined chunks"""
    batch_size = config['generation']['batch_size']
    num_batches = (num_total + batch_size - 1) // batch_size  # ceiling division
    
    all_pairs = []
    generator = Generator(provider, config)
    
    print(f"\n🔄 Generating {num_total} {generation_type.upper()} pairs in {num_batches} batch(es) of ~{batch_size}")
    
    for batch_num in range(num_batches):
        pairs_needed = min(batch_size, num_total - len(all_pairs))
        
        # Sample random chunks for this batch
        sampled_chunks = random.sample(all_chunks, min(5, len(all_chunks)))
        combined_text = "\n\n".join([c["text"] for c in sampled_chunks])
        
        print(f"   Batch {batch_num + 1}/{num_batches}: generating {pairs_needed} pairs...")
        
        batch_pairs = generator.process_document(
            combined_text, 
            num_pairs=pairs_needed, 
            generation_type=generation_type
        )
        
        all_pairs.extend(batch_pairs)
        print(f"   ✅ Generated {len(batch_pairs)} pairs (total so far: {len(all_pairs)})")
        
        if len(all_pairs) >= num_total:
            break
    
    return all_pairs[:num_total]  # trim to exact count


def generate_qa_and_cot(all_chunks, provider, config):
    """Step 5: Generate QA & CoT from combined chunks"""
    
    print("\n" + "=" * 60)
    print("STEP 5A: QA GENERATION")
    print("=" * 60)
    
    qa_pairs = generate_pairs_in_batches(
        all_chunks,
        config['generation']['num_qa_pairs'],
        "qa",
        provider,
        config
    )
    
    # Save combined QA
    os.makedirs("data/generated", exist_ok=True)
    qa_file = "data/generated/combined_qa.json"
    import json
    with open(qa_file, "w", encoding="utf-8") as f:
        json.dump(qa_pairs, f, indent=2)
    print(f"\n💾 Saved {len(qa_pairs)} QA pairs → {qa_file}")
    
    print("\n" + "=" * 60)
    print("STEP 5B: COT GENERATION")
    print("=" * 60)
    
    cot_pairs = generate_pairs_in_batches(
        all_chunks,
        config['generation']['num_cot_pairs'],
        "cot",
        provider,
        config
    )
    
    # Save combined COT
    cot_file = "data/generated/combined_cot.json"
    with open(cot_file, "w", encoding="utf-8") as f:
        json.dump(cot_pairs, f, indent=2)
    print(f"\n💾 Saved {len(cot_pairs)} COT pairs → {cot_file}")
    
    return qa_pairs, cot_pairs


def curate_data(qa_pairs, cot_pairs, provider, config):
    """Step 6: Curate combined QA & CoT"""
    curator = QualityCurator(provider, config)

    print("\n" + "=" * 60)
    print("STEP 6: CURATION")
    print("=" * 60)

    curated_qa, qa_metrics = curator.curate(qa_pairs, "combined", "qa")
    curated_cot, cot_metrics = curator.curate(cot_pairs, "combined", "cot")

    print("\n✅ Curation complete!")
    
    print(f"\n📊 Final Dataset Summary:")
    print(f"   QA pairs:  {len(curated_qa)}/{len(qa_pairs)} kept")
    print(f"   COT pairs: {len(curated_cot)}/{len(cot_pairs)} kept")
    
    return curated_qa, curated_cot


if __name__ == "__main__":
    # ---- Setup ----
    config = load_config()
    provider = BedrockProvider(
        model_id=config["bedrock"]["model"],
        region=config["bedrock"]["region"]
    )

    input_dir = "data/input"
    
    if not os.path.exists(input_dir):
        print(f"❌ Input directory not found: {input_dir}")
        exit(1)

    # ---- Step 4: Ingest all PDFs ----
    all_chunks = ingest_all_pdfs(input_dir, config)
    
    if not all_chunks:
        print("❌ No chunks generated. Exiting.")
        exit(1)

    # ---- Step 5: Generate QA + COT (combined) ----
    qa_pairs, cot_pairs = generate_qa_and_cot(all_chunks, provider, config)

    # ---- Step 6: Curate ----
    curate_data(qa_pairs, cot_pairs, provider, config)
    
    print("\n🎉 Pipeline complete!")
    print("\n📁 Output files:")
    print("   - data/generated/combined_qa.json")
    print("   - data/generated/combined_cot.json")
    print("   - data/curated/combined_qa_curated.json")
    print("   - data/curated/combined_cot_curated.json")