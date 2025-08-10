#!/usr/bin/env python3
"""
Cache Management Script for RAG Document Q&A System

:
1. Clears the existing document cache
2. Pre-caches all documents from the hardcoded URL list
3. Provides progress tracking and error handling
"""

import os
import sys
import shutil
import asyncio
from pathlib import Path
# Removed ThreadPoolExecutor - processing sequentially for GPU stability
import time

# Add src to path for imports
sys.path.append('src')

from src.core.config import CACHE_DIR
from src.ai.embedding_models import initialize_models
from src.document_processing.retrieval import load_and_process_document

# Hardcoded URLs from document_urls.txt
DOCUMENT_URLS = [
    "https://hackrx.blob.core.windows.net/assets/Arogya%20Sanjeevani%20Policy%20-%20CIN%20-%20U10200WB1906GOI001713%201.pdf?sv=2023-01-03&st=2025-07-21T08%3A29%3A02Z&se=2025-09-22T08%3A29%3A00Z&sr=b&sp=r&sig=nzrz1K9Iurt%2BBXom%2FB%2BMPTFMFP3PRnIvEsipAX10Ig4%3D",
    "https://hackrx.blob.core.windows.net/assets/Family%20Medicare%20Policy%20(UIN-%20UIIHLIP22070V042122)%201.pdf?sv=2023-01-03&st=2025-07-22T10%3A17%3A39Z&se=2025-08-23T10%3A17%3A00Z&sr=b&sp=r&sig=dA7BEMIZg3WcePcckBOb4QjfxK%2B4rIfxBs2%2F%2BNwoPjQ%3D",
    "https://hackrx.blob.core.windows.net/assets/Happy%20Family%20Floater%20-%202024%20OICHLIP25046V062425%201.pdf?sv=2023-01-03&spr=https&st=2025-07-31T17%3A24%3A30Z&se=2026-08-01T17%3A24%3A00Z&sr=b&sp=r&sig=VNMTTQUjdXGYb2F4Di4P0zNvmM2rTBoEHr%2BnkUXIqpQ%3D",
    "https://hackrx.blob.core.windows.net/assets/Super_Splendor_(Feb_2023).pdf?sv=2023-01-03&st=2025-07-21T08%3A10%3A00Z&se=2025-09-22T08%3A10%3A00Z&sr=b&sp=r&sig=vhHrl63YtrEOCsAy%2BpVKr20b3ZUo5HMz1lF9%2BJh6LQ0%3D",
    "https://hackrx.blob.core.windows.net/assets/Test%20/Fact%20Check.docx?sv=2023-01-03&spr=https&st=2025-08-04T20%3A27%3A22Z&se=2028-08-05T20%3A27%3A00Z&sr=b&sp=r&sig=XB1%2FNzJ57eg52j4xcZPGMlFrp3HYErCW1t7k1fMyiIc%3D",
    "https://hackrx.blob.core.windows.net/assets/Test%20/Mediclaim%20Insurance%20Policy.docx?sv=2023-01-03&spr=https&st=2025-08-04T18%3A42%3A14Z&se=2026-08-05T18%3A42%3A00Z&sr=b&sp=r&sig=yvnP%2FlYfyyqYmNJ1DX51zNVdUq1zH9aNw4LfPFVe67o%3D",
    "https://hackrx.blob.core.windows.net/assets/Test%20/Pincode%20data.xlsx?sv=2023-01-03&spr=https&st=2025-08-04T18%3A50%3A43Z&se=2026-08-05T18%3A50%3A00Z&sr=b&sp=r&sig=xf95kP3RtMtkirtUMFZn%2FFNai6sWHarZsTcvx8ka9mI%3D",
    "https://hackrx.blob.core.windows.net/assets/Test%20/Salary%20data.xlsx?sv=2023-01-03&spr=https&st=2025-08-04T18%3A46%3A54Z&se=2026-08-05T18%3A46%3A00Z&sr=b&sp=r&sig=sSoLGNgznoeLpZv%2FEe%2FEI1erhD0OQVoNJFDPtqfSdJQ%3D",
    "https://hackrx.blob.core.windows.net/assets/Test%20/Test%20Case%20HackRx.pptx?sv=2023-01-03&spr=https&st=2025-08-04T18%3A36%3A56Z&se=2026-08-05T18%3A36%3A00Z&sr=b&sp=r&sig=v3zSJ%2FKW4RhXaNNVTU9KQbX%2Bmo5dDEIzwaBzXCOicJM%3D",
    "https://hackrx.blob.core.windows.net/assets/Test%20/image.jpeg?sv=2023-01-03&spr=https&st=2025-08-04T19%3A29%3A01Z&se=2026-08-05T19%3A29%3A00Z&sr=b&sp=r&sig=YnJJThygjCT6%2FpNtY1aHJEZ%2F%2BqHoEB59TRGPSxJJBwo%3D",
    "https://hackrx.blob.core.windows.net/assets/Test%20/image.png?sv=2023-01-03&spr=https&st=2025-08-04T19%3A21%3A45Z&se=2026-08-05T19%3A21%3A00Z&sr=b&sp=r&sig=lAn5WYGN%2BUAH7mBtlwGG4REw5EwYfsBtPrPuB0b18M4%3D",
    "https://hackrx.blob.core.windows.net/assets/UNI%20GROUP%20HEALTH%20INSURANCE%20POLICY%20-%20UIIHLGP26043V022526%201.pdf?sv=2023-01-03&spr=https&st=2025-07-31T17%3A06%3A03Z&se=2026-08-01T17%3A06%3A00Z&sr=b&sp=r&sig=wLlooaThgRx91i2z4WaeggT0qnuUUEzIUKj42GsvMfg%3D",
    "https://hackrx.blob.core.windows.net/assets/hackrx_pdf.zip?sv=2023-01-03&spr=https&st=2025-08-04T09%3A25%3A45Z&se=2027-08-05T09%3A25%3A00Z&sr=b&sp=r&sig=rDL2ZcGX6XoDga5%2FTwMGBO9MgLOhZS8PUjvtga2cfVk%3D",
    "https://hackrx.blob.core.windows.net/assets/indian_constitution.pdf?sv=2023-01-03&st=2025-07-28T06%3A42%3A00Z&se=2026-11-29T06%3A42%3A00Z&sr=b&sp=r&sig=5Gs%2FOXqP3zY00lgciu4BZjDV5QjTDIx7fgnfdz6Pu24%3D",
    "https://hackrx.blob.core.windows.net/assets/principia_newton.pdf?sv=2023-01-03&st=2025-07-28T07%3A20%3A32Z&se=2026-07-29T07%3A20%3A00Z&sr=b&sp=r&sig=V5I1QYyigoxeUMbnUKsdEaST99F5%2FDfo7wpKg9XXF5w%3D"
]

def clear_cache():
    """Clear the entire document cache directory"""
    print("🗑️ Clearing document cache...")
    
    if CACHE_DIR.exists():
        try:
            # Remove all files in cache directory
            for item in CACHE_DIR.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            print(f"✅ Cache cleared: {CACHE_DIR}")
        except Exception as e:
            print(f"❌ Error clearing cache: {e}")
            return False
    else:
        print(f"📁 Cache directory doesn't exist, creating: {CACHE_DIR}")
        CACHE_DIR.mkdir(exist_ok=True)
    
    return True

def get_document_name(url: str) -> str:
    """Extract a readable document name from URL"""
    try:
        # Extract filename from URL
        filename = url.split('/')[-1].split('?')[0]
        # URL decode common characters
        filename = filename.replace('%20', ' ').replace('%2F', '/').replace('%28', '(').replace('%29', ')')
        return filename[:50] + "..." if len(filename) > 50 else filename
    except:
        return url[:50] + "..."



async def cache_all_documents():
    """Cache all documents with progress tracking"""
    print(f"🚀 Starting to cache {len(DOCUMENT_URLS)} documents...")
    print("📊 This may take several minutes depending on document sizes and network speed...")
    
    # Initialize models first
    print("🔄 Initializing AI models...")
    initialize_models()
    print("✅ Models initialized successfully!")
    
    # Process documents one by one to avoid GPU memory issues
    start_time = time.time()
    successful = 0
    failed = 0
    errors = []
    
    # Process documents sequentially for stable GPU memory usage
    for i, url in enumerate(DOCUMENT_URLS):
        doc_name = get_document_name(url)
        print(f"📄 [{i+1}/{len(DOCUMENT_URLS)}] Processing: {doc_name}")
        
        doc_start_time = time.time()
        try:
            load_and_process_document(url)
            elapsed = time.time() - doc_start_time
            print(f"✅ [{i+1}/{len(DOCUMENT_URLS)}] Cached successfully in {elapsed:.1f}s: {doc_name}")
            successful += 1
        except Exception as e:
            elapsed = time.time() - doc_start_time
            error_msg = str(e)
            print(f"❌ [{i+1}/{len(DOCUMENT_URLS)}] Failed after {elapsed:.1f}s: {doc_name} - {error_msg}")
            failed += 1
            errors.append(f"{doc_name}: {error_msg}")
        
        # Small delay between documents to let GPU memory settle
        if i < len(DOCUMENT_URLS) - 1:
            await asyncio.sleep(0.5)
    
    total_time = time.time() - start_time
    
    # Print summary
    print("\n" + "="*60)
    print("📊 CACHING SUMMARY")
    print("="*60)
    print(f"✅ Successfully cached: {successful}/{len(DOCUMENT_URLS)} documents")
    print(f"❌ Failed to cache: {failed}/{len(DOCUMENT_URLS)} documents")
    print(f"⏱️ Total time: {total_time:.1f} seconds")
    print(f"📈 Average time per document: {total_time/len(DOCUMENT_URLS):.1f} seconds")
    
    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for i, error in enumerate(errors[:5], 1):  # Show first 5 errors
            print(f"  {i}. {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors")
    
    print("="*60)
    
    if successful == len(DOCUMENT_URLS):
        print("🎉 All documents cached successfully!")
    elif successful > 0:
        print(f"⚠️ Partial success: {successful} documents cached, {failed} failed")
    else:
        print("💥 No documents were cached successfully")
    
    return successful, failed

def main():
    """Main function to orchestrate cache management"""
    print("🚀 RAG Document Cache Manager")
    print("="*50)
    
    # Step 1: Clear existing cache
    if not clear_cache():
        print("❌ Failed to clear cache. Exiting.")
        return 1
    
    print()
    
    # Step 2: Cache all documents
    try:
        successful, failed = asyncio.run(cache_all_documents())
        
        if successful > 0:
            print(f"\n✅ Cache management completed!")
            print(f"📁 Cache location: {CACHE_DIR.absolute()}")
            return 0 if failed == 0 else 1
        else:
            print(f"\n❌ Cache management failed!")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Cache management interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)