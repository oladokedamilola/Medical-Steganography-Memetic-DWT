# ============================================
# FILE: code/integration/run_experiment.py
# ============================================

"""
Simple wrapper script to run experiments with the integrated pipeline
"""

import sys
from pathlib import Path
import argparse
import json
import logging

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from code.integration.pipeline_orchestrator import SteganographyPipeline, BatchProcessor

def setup_logging(level=logging.INFO):
    """Setup logging configuration"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/experiment.log'),
            logging.StreamHandler()
        ]
    )

def main():
    parser = argparse.ArgumentParser(description='Run medical image steganography experiment')
    
    parser.add_argument('--mode', type=str, choices=['single', 'batch'], default='single',
                       help='Run mode: single image or batch experiment')
    
    parser.add_argument('--image', type=str, help='Path to image file (for single mode)')
    parser.add_argument('--text', type=str, help='Text to hide (for single mode)')
    parser.add_argument('--text-file', type=str, help='File containing text to hide')
    
    parser.add_argument('--image-dir', type=str, default='data/images',
                       help='Directory containing images (for batch mode)')
    parser.add_argument('--payload-dir', type=str, default='data/text_payloads',
                       help='Directory containing text payloads (for batch mode)')
    parser.add_argument('--sizes', type=int, nargs='+', 
                       default=[15, 30, 45, 55, 100, 128, 256],
                       help='Text sizes to test (for batch mode)')
    
    parser.add_argument('--output-dir', type=str, default='data/raw_output',
                       help='Output directory for results')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level)
    
    # Create pipeline
    pipeline = SteganographyPipeline()
    
    if args.mode == 'single':
        # Single image mode
        if not args.image:
            print("Error: --image required for single mode")
            return
        
        # Load image
        import cv2
        image = cv2.imread(args.image)
        if image is None:
            print(f"Error: Could not load image from {args.image}")
            return
        
        # Get text
        if args.text_file:
            with open(args.text_file, 'r', encoding='utf-8') as f:
                text = f.read()
        elif args.text:
            text = args.text
        else:
            text = "CONFIDENTIAL: Test message"
        
        print(f"\n🚀 Running single experiment...")
        print(f"  Image: {args.image}")
        print(f"  Text: '{text[:50]}...' ({len(text)} chars)")
        
        # Process
        result = pipeline.process_text_to_image(
            plaintext=text,
            image=image,
            image_name=Path(args.image).stem,
            seed=args.seed
        )
        
        # Save
        save_dir = pipeline.save_pipeline_result(result, args.output_dir)
        print(f"\n✅ Results saved to: {save_dir}")
        
        # Print summary
        print(f"\n📊 Summary:")
        print(f"  Encryption iterations: {result['encryption_iterations']}")
        print(f"  Bits embedded: {result['embedding_bits']}")
        print(f"  Processing time: {result['processing_time']:.2f}s")
        
        if result.get('verification', {}).get('full_cycle_success'):
            print("  ✅ Full cycle successful!")
        else:
            print("  ⚠️  Verification issues detected")
    
    elif args.mode == 'batch':
        # Batch mode
        print(f"\n📦 Running batch experiment...")
        print(f"  Image directory: {args.image_dir}")
        print(f"  Payload directory: {args.payload_dir}")
        print(f"  Text sizes: {args.sizes}")
        
        batch_processor = BatchProcessor(pipeline, args.output_dir)
        
        results = batch_processor.run_batch_experiment(
            image_dir=args.image_dir,
            payload_dir=args.payload_dir,
            text_sizes=args.sizes,
            repetitions=1
        )
        
        print(f"\n✅ Batch experiment completed!")
        print(f"  Processed {len(results)} combinations")
        print(f"  Report saved to: {args.output_dir}/batch_report_*.json")

if __name__ == "__main__":
    main()