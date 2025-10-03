# # # # # # # main.py (temporary quick test)
# # # # # # from synthetic_data_kit.providers.bedrock_provider import BedrockProvider

# # # # # # if __name__ == "__main__":
# # # # # #     provider = BedrockProvider()
# # # # # #     result = provider.generate("Write a short haiku about synthetic data.")
# # # # # #     print(result)


# # # # # # main.py
# # # # # import yaml
# # # # # from synthetic_data_kit.providers.bedrock_provider import BedrockProvider

# # # # # def load_config(path="configs/config.yaml"):
# # # # #     with open(path, "r") as f:
# # # # #         return yaml.safe_load(f)

# # # # # if __name__ == "__main__":
# # # # #     config = load_config()
# # # # #     provider = BedrockProvider(model_id=config["bedrock"]["model"], region=config["bedrock"]["region"])

# # # # #     # Test using QA generation prompt from config
# # # # #     prompt_template = config["prompts"]["qa_generation"]
# # # # #     prompt = prompt_template.format(text="The Earth revolves around the Sun.", num_pairs=2)

# # # # #     result = provider.generate(prompt)
# # # # #     print(result)



# # # # # main.py
# # # # import yaml
# # # # import json
# # # # import os
# # # # from synthetic_data_kit.providers.bedrock_provider import BedrockProvider
# # # # from synthetic_data_kit.ingest.pdf_parser import PDFParser
# # # # from synthetic_data_kit.utils.chunker import chunk_text

# # # # def load_config(path="configs/config.yaml"):
# # # #     with open(path, "r") as f:
# # # #         return yaml.safe_load(f)

# # # # def test_ingestion(pdf_path: str):
# # # #     """Test PDF ingestion and chunking"""
# # # #     print("\n" + "="*60)
# # # #     print("STEP 4: PDF INGESTION SANITY CHECK")
# # # #     print("="*60 + "\n")
    
# # # #     # Load config
# # # #     config = load_config()
    
# # # #     # Parse PDF
# # # #     parser = PDFParser()
# # # #     text = parser.parse(pdf_path)
    
# # # #     print(f"\n📊 Document Stats:")
# # # #     print(f"   Total characters: {len(text):,}")
# # # #     print(f"   Total words: {len(text.split()):,}")
    
# # # #     # Chunk text
# # # #     chunk_size = config['generation']['chunk_size']
# # # #     chunk_overlap = config['generation']['chunk_overlap']
    
# # # #     chunks = chunk_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
# # # #     print(f"\n📦 Chunking Results:")
# # # #     print(f"   Chunk size: {chunk_size}")
# # # #     print(f"   Chunk overlap: {chunk_overlap}")
# # # #     print(f"   Number of chunks: {len(chunks)}")
    
# # # #     # Show first chunk preview
# # # #     if chunks:
# # # #         print(f"\n📝 First Chunk Preview (first 500 chars):")
# # # #         print("-" * 60)
# # # #         print(chunks[0][:500] + "...")
# # # #         print("-" * 60)
    
# # # #     # Save parsed output (SDK style)
# # # #     os.makedirs("data/parsed", exist_ok=True)
# # # #     output_file = "data/parsed/document.txt"
    
# # # #     with open(output_file, "w", encoding="utf-8") as f:
# # # #         f.write(text)
    
# # # #     print(f"\n💾 Saved parsed text to: {output_file}")
    
# # # #     # Save chunks as JSON (for inspection)
# # # #     chunks_file = "data/parsed/chunks.json"
# # # #     with open(chunks_file, "w", encoding="utf-8") as f:
# # # #         json.dump({
# # # #             "num_chunks": len(chunks),
# # # #             "chunk_size": chunk_size,
# # # #             "chunk_overlap": chunk_overlap,
# # # #             "chunks": chunks
# # # #         }, f, indent=2)
    
# # # #     print(f"💾 Saved chunks to: {chunks_file}")
    
# # # #     return text, chunks

# # # # if __name__ == "__main__":
# # # #     # Test ingestion with your PDF
# # # #     pdf_path = "data/input/sample.pdf"  # 👈 Put your PDF here
    
# # # #     if not os.path.exists(pdf_path):
# # # #         print(f"❌ PDF not found: {pdf_path}")
# # # #         print(f"👉 Please create 'data/input/' folder and place your PDF there as 'sample.pdf'")
# # # #     else:
# # # #         text, chunks = test_ingestion(pdf_path)
# # # #         print("\n✅ Ingestion sanity check complete!")
# # # import os
# # # if __name__ == "__main__":
# # #     # Pick any of your PDFs for testing
# # #     pdf_path = "data/input/Bank_Sweep_Terms_of_Use.pdf"

# # #     if not os.path.exists(pdf_path):
# # #         print(f"❌ PDF not found: {pdf_path}")
# # #     else:
# # #         text, chunks = test_ingestion(pdf_path)
# # #         print("\n✅ Ingestion sanity check complete!")


# # # main.py
# import os
# import yaml
# import json
# from synthetic_data_kit.providers.bedrock_provider import BedrockProvider
# from synthetic_data_kit.ingest.pdf_parser import PDFParser
# from synthetic_data_kit.utils.chunker import chunk_text

# def load_config(path="configs/config.yaml"):
#     with open(path, "r") as f:
#         return yaml.safe_load(f)

# def test_ingestion(pdf_path: str):
#     """Test PDF ingestion and chunking"""
#     print("\n" + "="*60)
#     print("STEP 4: PDF INGESTION SANITY CHECK")
#     print("="*60 + "\n")
    
#     # Load config
#     config = load_config()
    
#     # Parse PDF
#     parser = PDFParser()
#     text = parser.parse(pdf_path)
    
#     print(f"\n📊 Document Stats:")
#     print(f"   Total characters: {len(text):,}")
#     print(f"   Total words: {len(text.split()):,}")
    
#     # Chunk text
#     chunk_size = config['generation']['chunk_size']
#     chunk_overlap = config['generation']['chunk_overlap']
    
#     chunks = chunk_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
#     print(f"\n📦 Chunking Results for {os.path.basename(pdf_path)}:")
#     print(f"   Chunk size: {chunk_size}")
#     print(f"   Chunk overlap: {chunk_overlap}")
#     print(f"   Number of chunks: {len(chunks)}")
    
#     # Show first chunk preview
#     if chunks:
#         print(f"\n📝 First Chunk Preview (first 500 chars):")
#         print("-" * 60)
#         print(chunks[0][:500] + "...")
#         print("-" * 60)
    
#     # Save parsed output
#     os.makedirs("data/parsed", exist_ok=True)
#     base_name = os.path.splitext(os.path.basename(pdf_path))[0]
#     output_file = f"data/parsed/{base_name}.txt"
    
#     with open(output_file, "w", encoding="utf-8") as f:
#         f.write(text)
    
#     print(f"\n💾 Saved parsed text to: {output_file}")
    
#     return text, chunks

# if __name__ == "__main__":
#     # Pick one of your PDFs
#     pdf_path = "data/input/Bank_Sweep_Terms_of_Use.pdf"
    
#     if not os.path.exists(pdf_path):
#         print(f"❌ PDF not found: {pdf_path}")
#         print("👉 Please put a PDF under data/input/")
#     else:
#         text, chunks = test_ingestion(pdf_path)
#         print("\n✅ Ingestion sanity check complete!")


# # main.py (add after ingestion test)
# # import os
# # from synthetic_data_kit.create.qa_generator import QAGenerator

# # if __name__ == "__main__":
# #     pdf_path = "data/input/Bank_Sweep_Terms_of_Use.pdf"

# #     if not os.path.exists(pdf_path):
# #         print(f"❌ PDF not found: {pdf_path}")
# #     else:
# #         text, chunks = test_ingestion(pdf_path)

# #         # ------- QA GENERATION TEST -------
# #         print("\n" + "="*60)
# #         print("STEP 5: QA GENERATION SANITY CHECK")
# #         print("="*60 + "\n")

# #         config = load_config()
# #         provider = BedrockProvider(model_id=config["bedrock"]["model"], region=config["bedrock"]["region"])
# #         generator = QAGenerator(provider, config)

# #         qa_pairs = generator.process_document(text, num_pairs=5)  # 👈 generate 5 to test
# #         for i, pair in enumerate(qa_pairs, 1):
# #             print(f"Q{i}: {pair.get('question')}")
# #             print(f"A{i}: {pair.get('answer')}\n")

# #         generator.save_pairs(qa_pairs, "Bank_Sweep_Terms_of_Use")

# #         print("\n✅ QA Generation sanity check complete!")
        
# # main.py (bottom part)

# from synthetic_data_kit.create.qa_generator import Generator

# if __name__ == "__main__":
#     pdf_path = "data/input/Bank_Sweep_Terms_of_Use.pdf"

#     if not os.path.exists(pdf_path):
#         print(f"❌ PDF not found: {pdf_path}")
#     else:
#         # Step 4: Ingestion
#         text, chunks = test_ingestion(pdf_path)

#         # Load config + init generator
#         config = load_config()
#         provider = BedrockProvider(model_id=config["bedrock"]["model"],
#                                    region=config["bedrock"]["region"])
#         generator = Generator(provider, config)

#         # Step 5A: QA GENERATION
#         print("\n" + "="*60)
#         print("STEP 5A: QA GENERATION SANITY CHECK")
#         print("="*60 + "\n")

#         qa_pairs = generator.process_document(text, num_pairs=5, generation_type="qa")
#         for i, pair in enumerate(qa_pairs, 1):
#             print(f"Q{i}: {pair.get('question')}")
#             print(f"A{i}: {pair.get('answer')}\n")

#         base_name = os.path.splitext(os.path.basename(pdf_path))[0]
#         generator.save_pairs(qa_pairs, base_name, generation_type="qa")

#         # Step 5B: CoT GENERATION
#         print("\n" + "="*60)
#         print("STEP 5B: COT GENERATION SANITY CHECK")
#         print("="*60 + "\n")

#         cot_pairs = generator.process_document(text, num_pairs=3, generation_type="cot")
#         for i, pair in enumerate(cot_pairs, 1):
#             print(f"Q{i}: {pair.get('question')}")
#             print(f"Reasoning: {pair.get('reasoning')}")
#             print(f"A{i}: {pair.get('answer')}\n")

#         generator.save_pairs(cot_pairs, base_name, generation_type="cot")

#         print("\n✅ QA + CoT Generation sanity check complete!")



# main.py
import os
import yaml
from synthetic_data_kit.providers.bedrock_provider import BedrockProvider
from synthetic_data_kit.ingest.pdf_parser import PDFParser
from synthetic_data_kit.utils.chunker import chunk_text
from synthetic_data_kit.create.qa_generator import Generator
from synthetic_data_kit.curate.judge import QualityCurator


def load_config(path="configs/config.yaml"):
    """Load YAML config"""
    with open(path, "r") as f:
        return yaml.safe_load(f)


def ingest_pdf(pdf_path: str, config):
    """Step 4: Ingest PDF → raw text + chunks"""
    print("\n" + "=" * 60)
    print("STEP 4: PDF INGESTION")
    print("=" * 60)

    parser = PDFParser()
    text = parser.parse(pdf_path)

    print(f"\n📊 Document Stats: {len(text):,} characters, {len(text.split()):,} words")

    # Chunk text
    chunks = chunk_text(
        text,
        chunk_size=config['generation']['chunk_size'],
        chunk_overlap=config['generation']['chunk_overlap']
    )
    print(f"📦 Chunking → {len(chunks)} chunks")

    return text, chunks


def generate_qa_and_cot(text, base_name, provider, config):
    """Step 5: Generate QA & CoT"""
    generator = Generator(provider, config)

    print("\n" + "=" * 60)
    print("STEP 5A: QA GENERATION")
    print("=" * 60)
    qa_pairs = generator.process_document(text, num_pairs=5, generation_type="qa")
    generator.save_pairs(qa_pairs, base_name, "qa")

    print("\n" + "=" * 60)
    print("STEP 5B: COT GENERATION")
    print("=" * 60)
    cot_pairs = generator.process_document(text, num_pairs=3, generation_type="cot")
    generator.save_pairs(cot_pairs, base_name, "cot")

    return qa_pairs, cot_pairs


def curate_data(qa_pairs, cot_pairs, base_name, provider, config):
    """Step 6: Curate QA & CoT using Sonnet as judge"""
    curator = QualityCurator(provider, config)

    print("\n" + "=" * 60)
    print("STEP 6: CURATION")
    print("=" * 60)

    curated_qa, qa_metrics = curator.curate(qa_pairs, base_name, "qa")
    curated_cot, cot_metrics = curator.curate(cot_pairs, base_name, "cot")

    print("\n✅ Curation complete!")
    return curated_qa, curated_cot


if __name__ == "__main__":
    # ---- Setup ----
    config = load_config()
    provider = BedrockProvider(model_id=config["bedrock"]["model"],
                               region=config["bedrock"]["region"])

    # Pick PDF (adjust filename if needed)
    pdf_path = "data/input/Bank_Sweep_Terms_of_Use.pdf"
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]

    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        exit(1)

    # ---- Step 4: Ingestion ----
    text, chunks = ingest_pdf(pdf_path, config)

    # ---- Step 5: Generation (QA + CoT) ----
    qa_pairs, cot_pairs = generate_qa_and_cot(text, base_name, provider, config)

    # ---- Step 6: Curation ----
    curate_data(qa_pairs, cot_pairs, base_name, provider, config)