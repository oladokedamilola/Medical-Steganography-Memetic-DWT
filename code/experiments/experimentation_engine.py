# ============================================
# FILE: code/experiments/experimentation_engine.py
# ============================================

"""
Experimentation Engine for Medical Image Steganography
Runs all experiments systematically and collects data

Experiment Design:
- Automatically detects available images in color and grayscale folders
- Interactive prompts to configure experiment size
- 7 text sizes (15, 30, 45, 55, 100, 128, 256 bytes)
- Configurable repetitions
"""

import sys
import os
from pathlib import Path
import json
import csv
import logging
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import pandas as pd
import cv2
from tqdm import tqdm
import matplotlib.pyplot as plt
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import our modules
from code.integration.pipeline_orchestrator import SteganographyPipeline
from code.metrics.image_metrics import ImageQualityMetrics, DataMetrics, MetricsCollector
from code.encryption.memetic_encryption import MemeticEncryptor, MemeticDecryptor
from code.steganography.dwt_steganography import DWTEmbedder, DWTExtractor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/experimentation_engine.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ============================================
# Interactive Configuration
# ============================================

def get_user_config() -> Dict:
    """
    Interactive prompt to configure experiment parameters
    
    Returns:
        Dictionary with user choices
    """
    print("\n" + "=" * 60)
    print("EXPERIMENT CONFIGURATION")
    print("=" * 60)
    
    config = {}
    
    # Text sizes
    print("\n📄 Available text sizes: 15, 30, 45, 55, 100, 128, 256 bytes")
    choice = input("Use all text sizes? (y/n): ").strip().lower()
    if choice == 'y':
        config['text_sizes'] = [15, 30, 45, 55, 100, 128, 256]
    else:
        sizes = []
        print("Enter text sizes to test (comma-separated, e.g., 15,30,45):")
        size_input = input().strip()
        try:
            sizes = [int(s.strip()) for s in size_input.split(',')]
            # Validate sizes
            valid_sizes = [15, 30, 45, 55, 100, 128, 256]
            sizes = [s for s in sizes if s in valid_sizes]
            if not sizes:
                print("⚠️  No valid sizes selected. Using all sizes.")
                sizes = [15, 30, 45, 55, 100, 128, 256]
        except:
            print("⚠️  Invalid input. Using all sizes.")
            sizes = [15, 30, 45, 55, 100, 128, 256]
        config['text_sizes'] = sizes
    
    # Repetitions
    print(f"\n🔄 Default repetitions: 3")
    choice = input("Use default repetitions? (y/n): ").strip().lower()
    if choice == 'y':
        config['repetitions'] = 3
    else:
        try:
            reps = int(input("Enter number of repetitions (1-5): ").strip())
            config['repetitions'] = max(1, min(5, reps))  # Clamp between 1 and 5
        except:
            print("⚠️  Invalid input. Using 1 repetition.")
            config['repetitions'] = 1
    
    # Image selection
    print("\n🖼️  Image selection:")
    print("   1) All available images")
    print("   2) Only color images")
    print("   3) Only grayscale images")
    print("   4) Select specific images")
    
    choice = input("Choose (1-4): ").strip()
    
    if choice == '2':
        config['image_filter'] = 'color'
    elif choice == '3':
        config['image_filter'] = 'grayscale'
    elif choice == '4':
        config['image_filter'] = 'select'
    else:
        config['image_filter'] = 'all'
    
    # Quick test mode
    print("\n⚡ Quick test mode? (runs only 1 image × 1 size × 1 repetition)")
    choice = input("Run quick test? (y/n): ").strip().lower()
    config['quick_test'] = (choice == 'y')
    
    # Summary
    print("\n" + "=" * 60)
    print("CONFIGURATION SUMMARY")
    print("=" * 60)
    print(f"Text sizes: {config['text_sizes']}")
    print(f"Repetitions: {config['repetitions']}")
    print(f"Image filter: {config['image_filter']}")
    print(f"Quick test: {'Yes' if config.get('quick_test') else 'No'}")
    
    confirm = input("\nProceed with this configuration? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Experiment cancelled.")
        sys.exit(0)
    
    return config


# ============================================
# Step 1: Experiment Matrix Design
# ============================================

class ExperimentMatrix:
    """
    Designs and manages the experiment matrix
    Automatically detects available images
    """
    
    def __init__(self, user_config: Optional[Dict] = None):
        """
        Initialize experiment matrix with user configuration
        
        Args:
            user_config: Dictionary with user choices from interactive prompt
        """
        self.user_config = user_config or {}
        
        # Set parameters from user config or defaults
        self.text_sizes = self.user_config.get('text_sizes', [15, 30, 45, 55, 100, 128, 256])
        self.repetitions = self.user_config.get('repetitions', 3)
        self.image_filter = self.user_config.get('image_filter', 'all')
        self.quick_test = self.user_config.get('quick_test', False)
        
        # Discover available images
        self.all_color_images = self._discover_images('color')
        self.all_grayscale_images = self._discover_images('grayscale')
        
        # Filter images based on user choice
        self.color_images = self._filter_images(self.all_color_images)
        self.grayscale_images = self._filter_images(self.all_grayscale_images)
        
        # Combine selected images
        self.all_images = self.color_images + self.grayscale_images
        
        # Apply quick test mode if selected
        if self.quick_test:
            # Use only first image, first text size, one repetition
            if self.all_images:
                self.all_images = [self.all_images[0]]
                self.text_sizes = [self.text_sizes[0]] if self.text_sizes else [15]
                self.repetitions = 1
        
        # Calculate total combinations
        self.total_combinations = len(self.all_images) * len(self.text_sizes) * self.repetitions
        
        self._log_summary()
    
    def _filter_images(self, images: List[Dict]) -> List[Dict]:
        """Filter images based on user selection"""
        if self.image_filter == 'all':
            return images
        elif self.image_filter == 'select':
            return self._interactive_select(images)
        else:
            # Filter by type (already handled by caller)
            return images
    
    def _interactive_select(self, images: List[Dict]) -> List[Dict]:
        """Interactive selection of specific images"""
        if not images:
            return []
        
        print(f"\n📋 Available images in this category:")
        for i, img in enumerate(images, 1):
            print(f"  {i}. {img['name']} ({img['filename']})")
        
        print("\nEnter image numbers to include (comma-separated, e.g., 1,3,5)")
        print("Or press Enter to include all")
        
        choice = input().strip()
        if not choice:
            return images
        
        try:
            indices = [int(x.strip()) for x in choice.split(',')]
            selected = [images[i-1] for i in indices if 1 <= i <= len(images)]
            if selected:
                return selected
            else:
                print("⚠️  No valid selections. Using all.")
                return images
        except:
            print("⚠️  Invalid input. Using all.")
            return images
    
    def _discover_images(self, image_type: str) -> List[Dict]:
        """
        Discover available images in the specified directory
        
        Args:
            image_type: 'color' or 'grayscale'
            
        Returns:
            List of image dictionaries
        """
        images = []
        image_dir = Path(f"data/images/{image_type}")
        
        if not image_dir.exists():
            logger.warning(f"Directory not found: {image_dir}")
            return images
        
        # Supported image extensions
        extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff']
        
        for ext in extensions:
            for img_path in image_dir.glob(ext):
                # Verify image can be loaded
                if image_type == 'color':
                    img = cv2.imread(str(img_path))
                else:
                    img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
                
                if img is not None:
                    images.append({
                        'name': img_path.stem,
                        'filename': img_path.name,
                        'type': image_type,
                        'path': img_path,
                        'shape': img.shape,
                        'expected': True
                    })
                    logger.debug(f"Found {image_type} image: {img_path.name}")
                else:
                    logger.warning(f"Could not load image: {img_path}")
        
        # Sort for consistency
        images.sort(key=lambda x: x['name'])
        
        return images
    
    def _log_summary(self):
        """Log summary of experiment configuration"""
        logger.info(f"Experiment Matrix Designed:")
        logger.info(f"  - Color images available: {len(self.all_color_images)}")
        logger.info(f"  - Color images selected: {len(self.color_images)}")
        logger.info(f"  - Grayscale images available: {len(self.all_grayscale_images)}")
        logger.info(f"  - Grayscale images selected: {len(self.grayscale_images)}")
        logger.info(f"  - Total images: {len(self.all_images)}")
        logger.info(f"  - Text sizes: {len(self.text_sizes)} {self.text_sizes}")
        logger.info(f"  - Repetitions: {self.repetitions}")
        logger.info(f"  - Quick test: {self.quick_test}")
        logger.info(f"  - Total experiments: {self.total_combinations}")
    
    def get_all_combinations(self) -> List[Dict]:
        """
        Generate all experiment combinations
        
        Returns:
            List of dictionaries with experiment parameters
        """
        combinations = []
        experiment_id = 0
        
        for rep in range(self.repetitions):
            for img_idx, image in enumerate(self.all_images):
                for size_idx, text_size in enumerate(self.text_sizes):
                    experiment_id += 1
                    
                    # Generate unique seed for reproducibility
                    seed = (rep * 1000) + (img_idx * 100) + (size_idx * 10) + 42
                    
                    combination = {
                        'experiment_id': experiment_id,
                        'repetition': rep + 1,
                        'image_name': image['name'],
                        'image_filename': image['filename'],
                        'image_type': image['type'],
                        'image_index': img_idx,
                        'text_size': text_size,
                        'seed': seed,
                        'status': 'pending'
                    }
                    combinations.append(combination)
        
        logger.info(f"Generated {len(combinations)} experiment combinations")
        return combinations
    
    def get_summary(self) -> Dict:
        """
        Get summary of available images
        """
        return {
            'color_images': [img['name'] for img in self.color_images],
            'grayscale_images': [img['name'] for img in self.grayscale_images],
            'all_color_available': len(self.all_color_images),
            'all_grayscale_available': len(self.all_grayscale_images),
            'total_color': len(self.color_images),
            'total_grayscale': len(self.grayscale_images),
            'total_images': len(self.all_images),
            'text_sizes': self.text_sizes,
            'repetitions': self.repetitions,
            'quick_test': self.quick_test,
            'total_experiments': self.total_combinations
        }


# ============================================
# Step 2: Automated Experiment Runner
# ============================================

class ExperimentRunner:
    """
    Automated experiment runner that processes all combinations
    """
    
    def __init__(self, user_config: Optional[Dict] = None, output_dir: str = "data/experiment_results"):
        """
        Initialize the experiment runner
        
        Args:
            user_config: Dictionary with user configuration
            output_dir: Directory to save results
        """
        self.matrix = ExperimentMatrix(user_config)
        
        # Check if any images are available
        if len(self.matrix.all_images) == 0:
            raise RuntimeError("No images found in data/images/color or data/images/grayscale directories!")
        
        self.pipeline = SteganographyPipeline()
        self.metrics_calculator = ImageQualityMetrics()
        self.data_metrics = DataMetrics()
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.raw_data_dir = self.output_dir / "raw"
        self.processed_dir = self.output_dir / "processed"
        self.csv_dir = self.output_dir / "csv"
        self.failed_dir = self.output_dir / "failed"
        
        for dir_path in [self.raw_data_dir, self.processed_dir, 
                        self.csv_dir, self.failed_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Storage for results
        self.results = []
        self.failed_experiments = []
        self.progress_file = self.output_dir / "progress.json"
        
        # Load progress if exists
        self._load_progress()
        
        # Print summary of what will be run
        summary = self.matrix.get_summary()
        logger.info(f"Experiment Runner initialized. Found:")
        logger.info(f"  - {summary['total_color']} color images: {', '.join(summary['color_images'])}")
        logger.info(f"  - {summary['total_grayscale']} grayscale images: {', '.join(summary['grayscale_images'])}")
        logger.info(f"  - Text sizes: {summary['text_sizes']}")
        logger.info(f"  - Repetitions: {summary['repetitions']}")
        logger.info(f"  - Total experiments to run: {summary['total_experiments']}")
    
    def _load_progress(self):
        """Load previous progress if available"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    progress = json.load(f)
                    self.results = progress.get('completed', [])
                    self.failed_experiments = progress.get('failed', [])
                logger.info(f"Loaded progress: {len(self.results)} completed, "
                          f"{len(self.failed_experiments)} failed")
            except Exception as e:
                logger.warning(f"Could not load progress: {e}")
    
    def _save_progress(self):
        """Save current progress"""
        progress = {
            'completed': self.results,
            'failed': self.failed_experiments,
            'timestamp': datetime.now().isoformat()
        }
        with open(self.progress_file, 'w') as f:
            json.dump(progress, f, indent=2)
    
    def load_image(self, image_info: Dict) -> Optional[np.ndarray]:
        """
        Load image from file
        
        Args:
            image_info: Dictionary with image information (must contain 'image_filename' and 'image_type')
            
        Returns:
            Image array or None if not found
        """
        # Determine correct path based on image type
        if image_info['image_type'] == 'color':
            img_path = Path(f"data/images/color/{image_info['image_filename']}")
        else:
            img_path = Path(f"data/images/grayscale/{image_info['image_filename']}")
        
        if not img_path.exists():
            logger.warning(f"Image not found: {img_path}")
            return None
        
        # Load image
        if image_info['image_type'] == 'color':
            img = cv2.imread(str(img_path))
        else:
            img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            logger.error(f"Failed to load image: {img_path}")
            return None
        
        return img
    
    def load_payload(self, text_size: int) -> Optional[str]:
        """
        Load text payload of specified size
        
        Args:
            text_size: Size in bytes
            
        Returns:
            Payload text or None if not found
        """
        payload_path = Path(f"data/text_payloads/payload_{text_size}bytes.txt")
        
        if not payload_path.exists():
            logger.warning(f"Payload not found: {payload_path}")
            # Create a dummy payload
            return "X" * text_size
        
        with open(payload_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    
    def run_single_experiment(self, experiment: Dict) -> Optional[Dict]:
        """
        Run a single experiment
        
        Args:
            experiment: Dictionary with experiment parameters
            
        Returns:
            Dictionary with results or None if failed
        """
        logger.debug(f"Running experiment {experiment['experiment_id']}: "
                    f"{experiment['image_name']} - {experiment['text_size']} bytes")
        
        try:
            # Load image and payload
            image = self.load_image(experiment)
            if image is None:
                raise FileNotFoundError(f"Image not found: {experiment.get('image_filename', 'unknown')}")
            
            payload = self.load_payload(experiment['text_size'])
            if payload is None:
                raise FileNotFoundError(f"Payload not found for size {experiment['text_size']}")
            
            # Record start time
            start_time = time.time()
            
            # Run pipeline
            pipeline_result = self.pipeline.process_text_to_image(
                plaintext=payload,
                image=image,
                image_name=f"{experiment['image_name']}_{experiment['text_size']}bytes",
                seed=experiment['seed']
            )
            
            # Calculate additional metrics
            if 'stego_image' in pipeline_result:
                # Image quality metrics
                image_metrics = self.metrics_calculator.calculate_all_metrics(
                    image, pipeline_result['stego_image']
                )
                
                # Get decrypted text from pipeline result
                from code.steganography.dwt_steganography import DWTExtractor
                from code.encryption.memetic_encryption import MemeticDecryptor
                
                extractor = DWTExtractor()
                decryptor = MemeticDecryptor()
                
                extracted_text = extractor.extract(pipeline_result['stego_image'], pipeline_result['embed_info'])
                decrypted_text = decryptor.decrypt(extracted_text, pipeline_result['encrypt_metadata'])
                
                # Data metrics
                data_integrity = self.data_metrics.calculate_data_integrity(
                    payload, decrypted_text
                )
                
                # Payload capacity
                capacity = self.data_metrics.calculate_payload_capacity(image)
            else:
                image_metrics = {}
                data_integrity = {}
                capacity = {}
                decrypted_text = ''
            
            # Compile results with original plaintext included
            result = {
                'experiment_id': experiment['experiment_id'],
                'timestamp': datetime.now().isoformat(),
                'parameters': experiment.copy(),
                'plaintext': payload,
                'decrypted_text': decrypted_text,
                'pipeline_result': pipeline_result,
                'metrics': {
                    'image_metrics': image_metrics,
                    'data_integrity': data_integrity,
                    'capacity': capacity
                },
                'performance': {
                    'execution_time': time.time() - start_time,
                    'success': pipeline_result.get('verification', {}).get('full_cycle_success', False)
                }
            }
            
            logger.debug(f"Experiment {experiment['experiment_id']} completed in "
                        f"{result['performance']['execution_time']:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Experiment {experiment['experiment_id']} failed: {e}")
            return None
    
    def run_all_experiments(self, resume: bool = True, 
                           max_retries: int = 3) -> List[Dict]:
        """
        Run all experiments in the matrix
        
        Args:
            resume: Whether to resume from previous progress
            max_retries: Maximum number of retries for failed experiments
            
        Returns:
            List of all results
        """
        logger.info("=" * 60)
        logger.info("STARTING EXPERIMENT BATCH RUN")
        logger.info("=" * 60)
        
        # Get all experiment combinations
        all_combinations = self.matrix.get_all_combinations()
        
        # Filter out completed experiments if resuming
        if resume and self.results:
            completed_ids = {r['experiment_id'] for r in self.results}
            pending = [c for c in all_combinations 
                      if c['experiment_id'] not in completed_ids]
            logger.info(f"Resuming: {len(pending)} pending out of {len(all_combinations)}")
        else:
            pending = all_combinations
            self.results = []
            self.failed_experiments = []
        
        # Track statistics
        stats = {
            'total': len(pending),
            'successful': 0,
            'failed': 0,
            'retries': 0
        }
        
        # Create progress bar
        pbar = tqdm(pending, desc="Running experiments", unit="exp")
        
        for experiment in pbar:
            # Update progress bar description
            pbar.set_description(f"Exp {experiment['experiment_id']}: "
                                f"{experiment['image_name']} - {experiment['text_size']}B")
            
            # Run experiment with retries
            result = None
            for attempt in range(max_retries):
                result = self.run_single_experiment(experiment)
                if result is not None:
                    break
                stats['retries'] += 1
                logger.debug(f"Retry {attempt + 1} for experiment {experiment['experiment_id']}")
            
            if result is not None:
                self.results.append(result)
                stats['successful'] += 1
                
                # Save individual result
                self._save_individual_result(result)
            else:
                self.failed_experiments.append(experiment)
                stats['failed'] += 1
                logger.error(f"Experiment {experiment['experiment_id']} failed after {max_retries} retries")
            
            # Save progress periodically
            if len(self.results) % 5 == 0:
                self._save_progress()
                self._update_statistics(stats)
        
        pbar.close()
        
        # Final save
        self._save_progress()
        self._save_all_results()
        self._generate_csv_reports()
        
        # Print summary
        self._print_final_summary(stats)
        
        logger.info("=" * 60)
        logger.info("EXPERIMENT BATCH RUN COMPLETED")
        logger.info("=" * 60)
        
        return self.results
    
    def _save_individual_result(self, result: Dict):
        """Save individual experiment result"""
        exp_id = result['experiment_id']
        filename = self.raw_data_dir / f"experiment_{exp_id:04d}.json"
        
        # Create a copy without large image data for JSON
        save_result = result.copy()
        if 'stego_image' in save_result.get('pipeline_result', {}):
            del save_result['pipeline_result']['stego_image']
        if 'original_image' in save_result.get('pipeline_result', {}):
            del save_result['pipeline_result']['original_image']
        
        with open(filename, 'w') as f:
            json.dump(save_result, f, indent=2, default=str)
    
    def _save_all_results(self):
        """Save all results to a single file"""
        filename = self.processed_dir / f"all_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Create summary version without large data
        summary_results = []
        for result in self.results:
            summary = {
                'experiment_id': result['experiment_id'],
                'parameters': result['parameters'],
                'plaintext': result.get('plaintext', ''),
                'decrypted_text': result.get('decrypted_text', ''),
                'metrics': result['metrics'],
                'performance': result['performance']
            }
            summary_results.append(summary)
        
        with open(filename, 'w') as f:
            json.dump(summary_results, f, indent=2, default=str)
        
        logger.info(f"All results saved to {filename}")
    
    def _generate_csv_reports(self):
        """Generate CSV reports for analysis"""
        
        # Prepare data for CSV
        csv_data = []
        for result in self.results:
            # Get the correct BER from data_integrity
            ber = result['metrics']['data_integrity'].get('ber', 1.0)
            
            row = {
                'experiment_id': result['experiment_id'],
                'image_name': result['parameters']['image_name'],
                'image_type': result['parameters']['image_type'],
                'text_size': result['parameters']['text_size'],
                'repetition': result['parameters']['repetition'],
                'seed': result['parameters']['seed'],
                
                # Image metrics
                'psnr': result['metrics']['image_metrics'].get('psnr', ''),
                'mse': result['metrics']['image_metrics'].get('mse', ''),
                'ssim': result['metrics']['image_metrics'].get('ssim', ''),
                'structural_content': result['metrics']['image_metrics'].get('structural_content', ''),
                'correlation': result['metrics']['image_metrics'].get('correlation', ''),
                
                # Data metrics
                'ber': ber,
                'character_error_rate': result['metrics']['data_integrity'].get('character_error_rate', ''),
                'exact_match': result['metrics']['data_integrity'].get('exact_match', ''),
                
                # Capacity
                'usable_chars': result['metrics']['capacity'].get('usable_chars', ''),
                
                # Performance
                'execution_time': result['performance']['execution_time'],
                'success': result['performance']['success']
            }
            csv_data.append(row)
        
        # Save to CSV
        if csv_data:
            df = pd.DataFrame(csv_data)
            
            # Full report
            csv_path = self.csv_dir / f"experiment_results_full.csv"
            df.to_csv(csv_path, index=False)
            
            # Summary by image and text size
            summary = df.groupby(['image_name', 'text_size']).agg({
                'psnr': 'mean',
                'mse': 'mean',
                'ssim': 'mean',
                'ber': 'mean',
                'success': 'mean'
            }).round(4)
            
            summary_path = self.csv_dir / f"experiment_results_summary.csv"
            summary.to_csv(summary_path)
            
            logger.info(f"CSV reports saved to {self.csv_dir}")
    
    def _update_statistics(self, stats: Dict):
        """Update and save statistics"""
        stats_file = self.output_dir / "statistics.json"
        
        stats.update({
            'timestamp': datetime.now().isoformat(),
            'completed': len(self.results),
            'failed': len(self.failed_experiments),
            'success_rate': len(self.results) / (len(self.results) + len(self.failed_experiments) + 1) * 100
        })
        
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
    
    def _print_final_summary(self, stats: Dict):
        """Print final summary of the experiment run"""
        
        print("\n" + "=" * 60)
        print("EXPERIMENT RUN SUMMARY")
        print("=" * 60)
        
        print(f"\n📊 Overall Statistics:")
        print(f"  Total experiments: {stats['total']}")
        print(f"  Successful: {stats['successful']}")
        print(f"  Failed: {stats['failed']}")
        print(f"  Retries: {stats['retries']}")
        print(f"  Success rate: {stats['successful']/stats['total']*100:.1f}%")
        
        # Calculate average metrics
        if self.results:
            psnr_values = [r['metrics']['image_metrics'].get('psnr', 0) 
                          for r in self.results if r['metrics']['image_metrics'].get('psnr')]
            ber_values = [r['metrics']['data_integrity'].get('ber', 1) 
                         for r in self.results if 'ber' in r['metrics']['data_integrity']]
            
            print(f"\n📈 Average Metrics:")
            print(f"  PSNR: {np.mean(psnr_values):.2f} dB")
            print(f"  BER: {np.mean(ber_values):.6f}")
        
        print(f"\n📁 Output Files:")
        print(f"  Raw data: {self.raw_data_dir}")
        print(f"  CSV reports: {self.csv_dir}")
        print(f"  Processed data: {self.processed_dir}")




# ============================================
# Step 3: Validation Checks
# ============================================

class ExperimentValidator:
    """
    Validates experiment results and checks for consistency
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__ + ".Validator")
    
    def validate_ber_zero(self, results: List[Dict]) -> Dict:
        """
        Verify BER=0 for all successful runs
        
        Returns:
            Dictionary with validation results
        """
        validation = {
            'total_runs': len(results),
            'successful_runs': 0,
            'ber_zero_count': 0,
            'ber_non_zero': [],
            'ber_by_size': defaultdict(list)
        }
        
        for result in results:
            if result['performance']['success']:
                validation['successful_runs'] += 1
                
                ber = result['metrics']['data_integrity'].get('ber', 1.0)
                text_size = result['parameters']['text_size']
                
                validation['ber_by_size'][text_size].append(ber)
                
                if ber == 0:
                    validation['ber_zero_count'] += 1
                else:
                    validation['ber_non_zero'].append({
                        'experiment_id': result['experiment_id'],
                        'ber': ber,
                        'text_size': text_size,
                        'image': result['parameters']['image_name']
                    })
        
        # Calculate statistics
        validation['ber_zero_percentage'] = (
            validation['ber_zero_count'] / validation['successful_runs'] * 100 
            if validation['successful_runs'] > 0 else 0
        )
        
        return validation
    
    def validate_psnr_trend(self, results: List[Dict]) -> Dict:
        """
        Verify that PSNR decreases as text size increases
        
        Returns:
            Dictionary with trend analysis
        """
        # Group by image
        by_image = defaultdict(lambda: defaultdict(list))
        
        for result in results:
            if 'psnr' in result['metrics']['image_metrics']:
                image = result['parameters']['image_name']
                size = result['parameters']['text_size']
                psnr = result['metrics']['image_metrics']['psnr']
                
                by_image[image][size].append(psnr)
        
        # Analyze trend for each image
        trend_analysis = {}
        
        for image, size_data in by_image.items():
            # Calculate mean PSNR for each size
            mean_psnr = {}
            for size, values in size_data.items():
                mean_psnr[size] = np.mean(values)
            
            # Check if PSNR generally decreases with size
            sizes = sorted(mean_psnr.keys())
            psnr_values = [mean_psnr[s] for s in sizes]
            
            # Calculate correlation between size and PSNR
            if len(sizes) > 1:
                correlation = np.corrcoef(sizes, psnr_values)[0, 1]
                decreasing = correlation < 0  # Negative correlation means decreasing
            else:
                correlation = 0
                decreasing = None
            
            trend_analysis[image] = {
                'sizes': sizes,
                'psnr_values': psnr_values,
                'correlation': correlation,
                'decreasing_trend': decreasing,
                'psnr_drop': psnr_values[0] - psnr_values[-1] if len(psnr_values) > 1 else 0
            }
        
        # Overall statistics
        decreasing_count = sum(1 for v in trend_analysis.values() 
                              if v.get('decreasing_trend') == True)
        
        return {
            'by_image': trend_analysis,
            'total_images': len(trend_analysis),
            'images_with_decreasing_trend': decreasing_count,
            'trend_consistency': decreasing_count / len(trend_analysis) * 100 
                                if trend_analysis else 0
        }
    
    def validate_capacity(self, results: List[Dict]) -> Dict:
        """
        Verify that text size never exceeds capacity
        
        Returns:
            Dictionary with capacity validation
        """
        capacity_issues = []
        
        for result in results:
            text_size = result['parameters']['text_size']
            usable_chars = result['metrics']['capacity'].get('usable_chars', 0)
            
            if text_size > usable_chars:
                capacity_issues.append({
                    'experiment_id': result['experiment_id'],
                    'text_size': text_size,
                    'usable_chars': usable_chars,
                    'excess': text_size - usable_chars
                })
        
        return {
            'total_checked': len(results),
            'capacity_issues': len(capacity_issues),
            'issues_details': capacity_issues,
            'all_within_capacity': len(capacity_issues) == 0
        }
    
    def validate_reproducibility(self, results: List[Dict]) -> Dict:
        """
        Verify reproducibility across repetitions
        
        Returns:
            Dictionary with reproducibility analysis
        """
        # Group by image and text size
        groups = defaultdict(list)
        
        for result in results:
            key = (result['parameters']['image_name'], 
                   result['parameters']['text_size'])
            groups[key].append(result)
        
        reproducibility = {}
        
        for (image, size), group in groups.items():
            if len(group) >= 2:  # Need at least 2 repetitions
                psnr_values = [r['metrics']['image_metrics'].get('psnr', 0) 
                              for r in group if 'psnr' in r['metrics']['image_metrics']]
                
                if len(psnr_values) >= 2:
                    reproducibility[f"{image}_{size}"] = {
                        'repetitions': len(group),
                        'psnr_mean': np.mean(psnr_values),
                        'psnr_std': np.std(psnr_values),
                        'psnr_cv': np.std(psnr_values) / np.mean(psnr_values) if np.mean(psnr_values) > 0 else 0,
                        'consistent': np.std(psnr_values) < 1.0  # Less than 1dB variation
                    }
        
        return reproducibility
    
    def run_all_validations(self, results: List[Dict]) -> Dict:
        """
        Run all validation checks
        
        Args:
            results: List of experiment results
            
        Returns:
            Dictionary with all validation results
        """
        logger.info("Running all validation checks...")
        
        validations = {
            'ber_validation': self.validate_ber_zero(results),
            'psnr_trend': self.validate_psnr_trend(results),
            'capacity_validation': self.validate_capacity(results),
            'reproducibility': self.validate_reproducibility(results),
            'timestamp': datetime.now().isoformat()
        }
        
        # Overall validation status
        validations['overall_valid'] = (
            validations['ber_validation']['ber_zero_percentage'] == 100 and
            validations['capacity_validation']['all_within_capacity'] and
            validations['psnr_trend']['trend_consistency'] > 50
        )
        
        return validations

# ============================================
# Main Execution (UPDATED)
# ============================================

def main():
    """Main function to run the experimentation engine"""
    
    print("\n" + "=" * 60)
    print("EXPERIMENTATION ENGINE - PHASE 5")
    print("=" * 60)
    
    # Create necessary directories
    for dir_path in ["data/experiment_results", "logs"]:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    try:
        # Get user configuration FIRST (interactive)
        user_config = get_user_config()
        
        # Step 1: Initialize experiment runner with user config
        print("\n🚀 Initializing Experiment Runner...")
        runner = ExperimentRunner(user_config, output_dir="data/experiment_results")
        
        # Step 2: Run all experiments
        print("\n🧪 Running all experiments...")
        results = runner.run_all_experiments(resume=False, max_retries=3)
        
        # Step 3: Validate results
        print("\n✅ Validating results...")
        validator = ExperimentValidator()
        validation_results = validator.run_all_validations(results)
        
        # Print validation summary
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        
        print(f"\n📊 BER Validation:")
        print(f"  BER=0 runs: {validation_results['ber_validation']['ber_zero_count']}/"
              f"{validation_results['ber_validation']['successful_runs']} "
              f"({validation_results['ber_validation']['ber_zero_percentage']:.1f}%)")
        
        if validation_results['ber_validation']['ber_non_zero']:
            print(f"  ⚠️  {len(validation_results['ber_validation']['ber_non_zero'])} runs have BER > 0")
        
        print(f"\n📈 PSNR Trend:")
        print(f"  Images with decreasing trend: "
              f"{validation_results['psnr_trend']['images_with_decreasing_trend']}/"
              f"{validation_results['psnr_trend']['total_images']}")
        
        print(f"\n📦 Capacity Validation:")
        print(f"  All within capacity: {validation_results['capacity_validation']['all_within_capacity']}")
        
        print(f"\n🔄 Reproducibility:")
        reproducible = sum(1 for v in validation_results['reproducibility'].values() 
                          if v.get('consistent', False))
        total_groups = len(validation_results['reproducibility'])
        if total_groups > 0:
            print(f"  Consistent repetitions: {reproducible}/{total_groups}")
        
        print(f"\n{'✅' if validation_results['overall_valid'] else '⚠️'}  "
              f"Overall Validation: {'PASSED' if validation_results['overall_valid'] else 'PARTIAL'}")
        
        # Save validation results
        validation_file = Path("results/validation_results.json")
        validation_file.parent.mkdir(exist_ok=True)
        with open(validation_file, 'w') as f:
            json.dump(validation_results, f, indent=2, default=str)
        
        print(f"\n💾 Validation results saved to {validation_file}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Experiment interrupted by user.")
        return 1
    except Exception as e:
        logger.error(f"Experiment failed: {e}")
        print(f"\n❌ Error: {e}")
        return 1
    
    print("\n" + "=" * 60)
    print("PHASE 5 COMPLETE!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())