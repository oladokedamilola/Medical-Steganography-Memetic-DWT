# ============================================
# FILE: code/integration/pipeline_orchestrator.py
# ============================================

"""
Integration Layer for Medical Image Steganography Pipeline
Connects Memetic Encryption with DWT Steganography

Pipeline Flow:
1. Encryption: Plaintext → Memetic Algorithm → Encrypted Text
2. Steganography: Encrypted Text → DWT Embedding → Stego Image
3. Extraction: Stego Image → DWT Extraction → Encrypted Text
4. Decryption: Encrypted Text → Memetic Algorithm → Plaintext
"""

import sys
import os
from pathlib import Path
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Union, Any
import numpy as np
import cv2
from tqdm import tqdm
import hashlib

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Import our modules
from code.encryption.memetic_encryption import MemeticEncryptor, MemeticDecryptor
from code.steganography.dwt_steganography import DWTEmbedder, DWTExtractor
from code.metrics.image_metrics import ImageQualityMetrics

# Setup logging
logger = logging.getLogger(__name__)


# ============================================
# Step 1: Pipeline Orchestrator
# ============================================

class SteganographyPipeline:
    """
    Main pipeline orchestrator connecting encryption and steganography
    
    Handles the complete workflow:
    - Text → Encrypt → Embed → Save
    - Load → Extract → Decrypt → Text
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the pipeline with configuration
        
        Args:
            config: Configuration dictionary (optional)
        """
        self.config = config or self._get_default_config()
        
        # Initialize components - using simplified DWT embedder (no parameters needed)
        self.encryptor = MemeticEncryptor(self.config.get('encryption', {}))
        self.decryptor = MemeticDecryptor(self.config.get('encryption', {}))
        self.embedder = DWTEmbedder()  # Simplified - no parameters
        self.extractor = DWTExtractor()  # Simplified - no parameters
        self.metrics_calculator = ImageQualityMetrics()
        
        # Track pipeline state
        self.pipeline_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = []
        self.errors = []
        
        logger.info(f"Pipeline initialized with ID: {self.pipeline_id}")
        logger.debug(f"Configuration: {json.dumps(self.config, indent=2)}")
    
    def _get_default_config(self) -> Dict:
        """Get default pipeline configuration"""
        return {
            'encryption': {
                'max_iterations': 100,
                'mutation_rate': 0.1,
                'mcg_modulus': 2147383648,
                'mcg_multiplier': 1664525
            },
            'steganography': {
                'wavelet': 'haar',
                'level': 1
            },
            'pipeline': {
                'save_intermediate': True,
                'verify_extraction': True,
                'calculate_metrics': True,
                'output_dir': 'data/raw_output',
                'results_dir': 'results'
            }
        }
    
    def process_text_to_image(self, plaintext: str, image: np.ndarray, 
                              image_name: str = "image", 
                              seed: Optional[int] = None) -> Dict:
        """
        Complete pipeline: Text → Encrypt → Embed → Save
        
        Args:
            plaintext: Original text to hide
            image: Original image
            image_name: Name of the image (for logging)
            seed: Random seed for encryption (for reproducibility)
            
        Returns:
            Dictionary with pipeline results
        """
        start_time = time.time()
        
        logger.info(f"Starting text-to-image pipeline for {image_name}")
        logger.debug(f"Plaintext length: {len(plaintext)} chars")
        
        try:
            # Stage 1: Encryption
            logger.debug("Stage 1: Encrypting text...")
            encrypted_text, encrypt_metadata = self.encryptor.encrypt(plaintext, seed)
            
            # Stage 2: Embedding
            logger.debug("Stage 2: Embedding encrypted text into image...")
            stego_image, embed_info = self.embedder.embed(image, encrypted_text)
            
            # Stage 3: Verification (optional)
            if self.config['pipeline']['verify_extraction']:
                logger.debug("Stage 3: Verifying extraction...")
                extracted_text = self.extractor.extract(stego_image, embed_info)
                decrypted_text = self.decryptor.decrypt(extracted_text, encrypt_metadata)
                
                verification = {
                    'extraction_success': (encrypted_text == extracted_text),
                    'decryption_success': (plaintext == decrypted_text),
                    'full_cycle_success': (plaintext == decrypted_text)
                }
            else:
                verification = {
                    'extraction_success': None,
                    'decryption_success': None,
                    'full_cycle_success': None
                }
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Compile results
            result = {
                'pipeline_id': self.pipeline_id,
                'timestamp': datetime.now().isoformat(),
                'image_name': image_name,
                'plaintext_length': len(plaintext),
                'encrypted_length': len(encrypted_text),
                'encryption_iterations': encrypt_metadata['iterations_performed'],
                'embedding_bits': embed_info['total_bits'],
                'bits_in_hl': embed_info.get('bits_in_hl', embed_info['total_bits']),
                'bits_in_hh': embed_info.get('bits_in_hh', 0),
                'processing_time': processing_time,
                'seed': encrypt_metadata['seed'],
                'verification': verification,
                'encrypt_metadata': encrypt_metadata,
                'embed_info': embed_info,
                'stego_image': stego_image if self.config['pipeline']['save_intermediate'] else None
            }
            
            # Log success
            if verification.get('full_cycle_success'):
                logger.info(f"✅ Pipeline completed successfully for {image_name} "
                          f"in {processing_time:.2f}s")
            else:
                logger.warning(f"⚠️ Pipeline completed with verification issues for {image_name}")
            
            self.results.append(result)
            return result
            
        except Exception as e:
            error_msg = f"Pipeline failed for {image_name}: {str(e)}"
            logger.error(error_msg)
            self.errors.append({
                'image_name': image_name,
                'error': str(e),
                'stage': 'text_to_image'
            })
            raise
    
    def process_image_to_text(self, stego_image: np.ndarray, 
                             embed_info: Dict,
                             encrypt_metadata: Dict,
                             image_name: str = "stego_image") -> Dict:
        """
        Reverse pipeline: Load → Extract → Decrypt → Text
        
        Args:
            stego_image: Image with hidden data
            embed_info: Embedding information from embedding process
            encrypt_metadata: Encryption metadata
            image_name: Name of the image (for logging)
            
        Returns:
            Dictionary with extraction results
        """
        start_time = time.time()
        
        logger.info(f"Starting image-to-text pipeline for {image_name}")
        
        try:
            # Stage 1: Extraction
            logger.debug("Stage 1: Extracting encrypted text from image...")
            extracted_text = self.extractor.extract(stego_image, embed_info)
            
            # Stage 2: Decryption
            logger.debug("Stage 2: Decrypting text...")
            decrypted_text = self.decryptor.decrypt(extracted_text, encrypt_metadata)
            
            processing_time = time.time() - start_time
            
            result = {
                'pipeline_id': self.pipeline_id,
                'timestamp': datetime.now().isoformat(),
                'image_name': image_name,
                'extracted_length': len(extracted_text),
                'decrypted_length': len(decrypted_text),
                'processing_time': processing_time,
                'extracted_text': extracted_text,
                'decrypted_text': decrypted_text
            }
            
            logger.info(f"✅ Image-to-text pipeline completed in {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            error_msg = f"Extraction pipeline failed for {image_name}: {str(e)}"
            logger.error(error_msg)
            self.errors.append({
                'image_name': image_name,
                'error': str(e),
                'stage': 'image_to_text'
            })
            raise
    
    def save_pipeline_result(self, result: Dict, output_dir: Optional[Path] = None):
        """
        Save pipeline results to files
        
        Args:
            result: Pipeline result dictionary
            output_dir: Output directory (uses config if None)
        """
        if output_dir is None:
            output_dir = Path(self.config['pipeline']['output_dir'])
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectory for this pipeline run
        run_dir = output_dir / f"pipeline_{self.pipeline_id}"
        run_dir.mkdir(exist_ok=True)
        
        # Save metadata
        metadata_path = run_dir / f"{result['image_name']}_metadata.json"
        
        # Remove stego_image from metadata before saving (too large for JSON)
        metadata = result.copy()
        if 'stego_image' in metadata:
            # Save stego image separately
            stego_path = run_dir / f"{result['image_name']}_stego.png"
            cv2.imwrite(str(stego_path), metadata['stego_image'])
            metadata['stego_image_path'] = str(stego_path)
            del metadata['stego_image']
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        logger.debug(f"Pipeline result saved to {run_dir}")
        
        return run_dir
    
    def load_pipeline_result(self, metadata_path: Path) -> Dict:
        """
        Load previously saved pipeline result
        
        Args:
            metadata_path: Path to metadata JSON file
            
        Returns:
            Loaded pipeline result
        """
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        # Load stego image if path exists
        if 'stego_image_path' in metadata:
            stego_path = Path(metadata['stego_image_path'])
            if stego_path.exists():
                metadata['stego_image'] = cv2.imread(str(stego_path))
        
        return metadata
    
    def generate_report(self) -> Dict:
        """Generate summary report of all pipeline runs"""
        
        if not self.results:
            return {"error": "No pipeline results to report"}
        
        successful = sum(1 for r in self.results 
                        if r.get('verification', {}).get('full_cycle_success', False))
        
        report = {
            'pipeline_id': self.pipeline_id,
            'total_runs': len(self.results),
            'successful_runs': successful,
            'failed_runs': len(self.results) - successful,
            'errors': self.errors,
            'average_processing_time': np.mean([r['processing_time'] for r in self.results]),
            'total_bits_embedded': sum(r['embedding_bits'] for r in self.results),
            'results_by_image': [
                {
                    'image_name': r['image_name'],
                    'text_length': r['plaintext_length'],
                    'success': r.get('verification', {}).get('full_cycle_success', False),
                    'processing_time': r['processing_time'],
                    'bits_embedded': r['embedding_bits']
                }
                for r in self.results
            ]
        }
        
        return report


# ============================================
# Step 2: Batch Processing
# ============================================

class BatchProcessor:
    """
    Process multiple images with varying text sizes
    Handles batch execution of the pipeline
    """
    
    def __init__(self, pipeline: SteganographyPipeline, 
                 output_dir: Union[str, Path] = "data/raw_output"):
        """
        Initialize batch processor
        
        Args:
            pipeline: Configured pipeline instance
            output_dir: Directory for output files
        """
        self.pipeline = pipeline
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.batch_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.logger = logging.getLogger(__name__ + ".BatchProcessor")
        
        self.logger.info(f"Batch processor initialized with ID: {self.batch_id}")
    
    def load_payloads(self, payload_dir: Union[str, Path]) -> Dict[int, str]:
        """
        Load text payloads from directory
        
        Args:
            payload_dir: Directory containing payload files
            
        Returns:
            Dictionary mapping size -> payload text
        """
        payload_dir = Path(payload_dir)
        payloads = {}
        
        for payload_file in sorted(payload_dir.glob("payload_*bytes.txt")):
            # Extract size from filename
            size = int(payload_file.stem.split('_')[1].replace('bytes', ''))
            
            with open(payload_file, 'r', encoding='utf-8') as f:
                payloads[size] = f.read()
            
            self.logger.debug(f"Loaded payload: {size} bytes")
        
        self.logger.info(f"Loaded {len(payloads)} payloads: {list(payloads.keys())}")
        return payloads
    
    def load_images(self, image_dir: Union[str, Path], color: bool = True) -> List[Dict]:
        """
        Load images from directory
        
        Args:
            image_dir: Directory containing images
            color: True for color images, False for grayscale
            
        Returns:
            List of dictionaries with image data and metadata
        """
        image_dir = Path(image_dir)
        images = []
        
        # Supported extensions
        extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff']
        
        for ext in extensions:
            for img_path in image_dir.glob(ext):
                # Read image
                img = cv2.imread(str(img_path))
                if img is None:
                    self.logger.warning(f"Could not read image: {img_path}")
                    continue
                
                # Convert to grayscale if needed
                if not color and len(img.shape) == 3:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                
                images.append({
                    'path': img_path,
                    'name': img_path.stem,
                    'data': img,
                    'shape': img.shape,
                    'color': color and len(img.shape) == 3
                })
                
                self.logger.debug(f"Loaded image: {img_path.name} - shape={img.shape}")
        
        self.logger.info(f"Loaded {len(images)} images from {image_dir}")
        return images
    
    def run_batch_experiment(self, image_dir: Union[str, Path], 
                            payload_dir: Union[str, Path],
                            text_sizes: Optional[List[int]] = None,
                            repetitions: int = 1) -> List[Dict]:
        """
        Run complete batch experiment
        
        Args:
            image_dir: Directory containing images
            payload_dir: Directory containing payloads
            text_sizes: List of text sizes to test (None for all available)
            repetitions: Number of repetitions per combination
            
        Returns:
            List of all results
        """
        # Load payloads and images
        all_payloads = self.load_payloads(payload_dir)
        color_images = self.load_images(Path(image_dir) / "color", color=True)
        grayscale_images = self.load_images(Path(image_dir) / "grayscale", color=False)
        
        # Filter text sizes if specified
        if text_sizes:
            payloads = {size: all_payloads[size] for size in text_sizes if size in all_payloads}
        else:
            payloads = all_payloads
        
        all_images = color_images + grayscale_images
        
        self.logger.info(f"Starting batch experiment with {len(all_images)} images "
                        f"and {len(payloads)} payload sizes")
        
        total_combinations = len(all_images) * len(payloads) * repetitions
        self.logger.info(f"Total combinations to process: {total_combinations}")
        
        all_results = []
        
        # Create progress bar
        pbar = tqdm(total=total_combinations, desc="Processing batch")
        
        for repetition in range(repetitions):
            for seed_offset, image in enumerate(all_images):
                for size, payload in payloads.items():
                    try:
                        # Use different seed for each run
                        seed = (repetition * 1000) + seed_offset + 42
                        
                        # Process
                        result = self.pipeline.process_text_to_image(
                            plaintext=payload,
                            image=image['data'],
                            image_name=f"{image['name']}_{size}bytes_rep{repetition}",
                            seed=seed
                        )
                        
                        # Add metadata
                        result['image_type'] = 'color' if image['color'] else 'grayscale'
                        result['payload_size'] = size
                        result['repetition'] = repetition
                        
                        # Save result
                        self.pipeline.save_pipeline_result(result, self.output_dir)
                        
                        all_results.append(result)
                        
                    except Exception as e:
                        self.logger.error(f"Failed: {image['name']}, size={size}, rep={repetition}: {e}")
                    
                    pbar.update(1)
        
        pbar.close()
        
        # Generate and save batch report
        report = self.generate_batch_report(all_results)
        self.save_batch_report(report)
        
        self.logger.info(f"Batch experiment completed. Processed {len(all_results)} combinations")
        
        return all_results
    
    def generate_batch_report(self, results: List[Dict]) -> Dict:
        """Generate comprehensive batch report"""
        
        # Group by image type
        color_results = [r for r in results if r.get('image_type') == 'color']
        gray_results = [r for r in results if r.get('image_type') == 'grayscale']
        
        # Group by payload size
        by_size = {}
        for r in results:
            size = r['payload_size']
            if size not in by_size:
                by_size[size] = []
            by_size[size].append(r)
        
        report = {
            'batch_id': self.batch_id,
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_combinations': len(results),
                'color_images': len(color_results),
                'grayscale_images': len(gray_results),
                'successful_runs': sum(1 for r in results 
                                      if r.get('verification', {}).get('full_cycle_success', False)),
                'payload_sizes': list(by_size.keys())
            },
            'by_payload_size': {
                size: {
                    'count': len(items),
                    'avg_processing_time': np.mean([r['processing_time'] for r in items]),
                    'avg_encryption_iterations': np.mean([r['encryption_iterations'] for r in items]),
                    'avg_bits_embedded': np.mean([r['embedding_bits'] for r in items])
                }
                for size, items in by_size.items()
            },
            'errors': self.pipeline.errors
        }
        
        return report
    
    def save_batch_report(self, report: Dict):
        """Save batch report to file"""
        report_path = self.output_dir / f"batch_report_{self.batch_id}.json"
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        self.logger.info(f"Batch report saved to {report_path}")
        
        return report_path


# ============================================
# Step 3: Error Handling and Validation
# ============================================

class PipelineValidator:
    """
    Validation utilities for the pipeline
    Ensures data integrity throughout the process
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__ + ".Validator")
    
    def calculate_checksum(self, data: Union[str, bytes, np.ndarray]) -> str:
        """Calculate SHA-256 checksum of data"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        elif isinstance(data, np.ndarray):
            data = data.tobytes()
        
        return hashlib.sha256(data).hexdigest()
    
    def validate_cycle(self, original_text: str, original_image: np.ndarray,
                      stego_image: np.ndarray, extracted_text: str,
                      decrypted_text: str) -> Dict:
        """
        Comprehensive validation of the entire cycle
        
        Args:
            original_text: Original plaintext
            original_image: Original image
            stego_image: Stego image
            extracted_text: Extracted encrypted text
            decrypted_text: Decrypted text
            
        Returns:
            Validation results dictionary
        """
        validation = {
            'text_recovery': {
                'original_length': len(original_text),
                'decrypted_length': len(decrypted_text),
                'exact_match': original_text == decrypted_text,
                'original_checksum': self.calculate_checksum(original_text),
                'decrypted_checksum': self.calculate_checksum(decrypted_text)
            },
            'encryption_integrity': {
                'original_encrypted': self.calculate_checksum(extracted_text)
            },
            'image_integrity': {
                'original_shape': original_image.shape,
                'stego_shape': stego_image.shape,
                'dimensions_match': original_image.shape == stego_image.shape,
                'original_checksum': self.calculate_checksum(original_image),
                'stego_checksum': self.calculate_checksum(stego_image)
            }
        }
        
        # Calculate image difference metrics
        if original_image.shape == stego_image.shape:
            diff = np.abs(original_image.astype(float) - stego_image.astype(float))
            validation['image_integrity']['mean_pixel_change'] = float(np.mean(diff))
            validation['image_integrity']['max_pixel_change'] = float(np.max(diff))
            validation['image_integrity']['pixels_changed'] = int(np.sum(diff > 0))
        
        # Overall success
        validation['overall_success'] = (
            validation['text_recovery']['exact_match'] and
            validation['image_integrity']['dimensions_match']
        )
        
        return validation
    
    def verify_extraction_capacity(self, image: np.ndarray, text_length: int) -> Tuple[bool, int]:
        """
        Verify if image has enough capacity for text
        
        Args:
            image: Image to check
            text_length: Length of text to embed
            
        Returns:
            Tuple of (has_capacity, max_capacity_bytes)
        """
        total_pixels = image.size
        max_bits = total_pixels  # 1 bit per pixel
        max_bytes = (max_bits - 16) // 8  # Subtract 16-bit header
        
        has_capacity = text_length <= max_bytes
        
        self.logger.debug(f"Capacity check: need={text_length} bytes, "
                         f"max={max_bytes} bytes -> {'OK' if has_capacity else 'INSUFFICIENT'}")
        
        return has_capacity, max_bytes
    
    def validate_pipeline_result(self, result: Dict) -> Dict:
        """Validate a single pipeline result"""
        
        # Check for required fields
        required_fields = ['plaintext_length', 'encrypted_length', 'embedding_bits']
        missing = [f for f in required_fields if f not in result]
        
        if missing:
            return {
                'valid': False,
                'errors': [f"Missing required fields: {missing}"]
            }
        
        errors = []
        warnings = []
        
        # Check text length consistency
        if result.get('plaintext_length', 0) > 0:
            if result.get('encrypted_length', 0) == 0:
                errors.append("Encrypted text is empty")
        
        # Check embedding
        if result.get('embedding_bits', 0) == 0:
            warnings.append("No bits were embedded")
        
        # Check verification if available
        verification = result.get('verification', {})
        if verification.get('extraction_success') is False:
            errors.append("Extraction failed")
        if verification.get('decryption_success') is False:
            errors.append("Decryption failed")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }


# ============================================
# Main execution and testing
# ============================================

def main():
    """Main function to test the integration pipeline"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\n" + "="*60)
    print("INTEGRATION LAYER - PHASE 3")
    print("="*60 + "\n")
    
    # Create test data
    print("📝 Creating test data...")
    
    # Test text
    test_text = "CONFIDENTIAL: Patient medical record #12345"
    
    # Test image (create a simple gradient)
    test_image = np.zeros((256, 256, 3), dtype=np.uint8)
    for i in range(256):
        for j in range(256):
            test_image[i, j] = [i % 256, j % 256, (i+j) % 256]
    
    print(f"  Text: '{test_text}' ({len(test_text)} chars)")
    print(f"  Image: 256x256 color gradient")
    
    # Initialize pipeline
    print("\n🔧 Initializing pipeline...")
    pipeline = SteganographyPipeline()
    
    # Test full cycle
    print("\n🔄 Testing full encryption-embedding-extraction-decryption cycle...")
    
    try:
        # Text → Image
        result = pipeline.process_text_to_image(
            plaintext=test_text,
            image=test_image,
            image_name="test_image",
            seed=42
        )
        
        print(f"  ✓ Encryption: {result['encryption_iterations']} iterations")
        print(f"  ✓ Embedding: {result['embedding_bits']} bits embedded")
        
        # Validate
        validator = PipelineValidator()
        
        if 'stego_image' in result:
            # Image → Text (simulate full cycle)
            extract_result = pipeline.process_image_to_text(
                stego_image=result['stego_image'],
                embed_info=result['embed_info'],
                encrypt_metadata=result['encrypt_metadata'],
                image_name="test_image_extract"
            )
            
            # Validate
            validation = validator.validate_cycle(
                original_text=test_text,
                original_image=test_image,
                stego_image=result['stego_image'],
                extracted_text=extract_result['extracted_text'],
                decrypted_text=extract_result['decrypted_text']
            )
            
            print(f"\n📊 Validation Results:")
            print(f"  Text recovery: {'✅' if validation['text_recovery']['exact_match'] else '❌'}")
            print(f"  Image dimensions: {'✅' if validation['image_integrity']['dimensions_match'] else '❌'}")
            print(f"  Mean pixel change: {validation['image_integrity'].get('mean_pixel_change', 0):.2f}")
            print(f"  Overall success: {'✅' if validation['overall_success'] else '❌'}")
        
        # Save result
        save_dir = pipeline.save_pipeline_result(result)
        print(f"\n💾 Results saved to: {save_dir}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test batch processing (if images available)
    print("\n📦 Testing batch processor...")
    
    batch_processor = BatchProcessor(pipeline)
    
    # Check if we have payload files
    payload_dir = Path("data/text_payloads")
    if payload_dir.exists():
        payloads = batch_processor.load_payloads(payload_dir)
        print(f"  Found {len(payloads)} payloads: {list(payloads.keys())} bytes")
    else:
        print("  ⚠️  No payload directory found. Skipping batch test.")
    
    print("\n" + "="*60)
    print("Phase 3 implementation complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()