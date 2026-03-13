# ============================================
# FILE: code/experiments/run_complete_experiment.py
# ============================================

"""
Complete Experiment Runner
Integrates Phase 1-4 to run full experiments and collect metrics
"""

import sys
from pathlib import Path
import json
import logging
from datetime import datetime
import cv2
import numpy as np

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Import all modules
from code.integration.pipeline_orchestrator import SteganographyPipeline, BatchProcessor
from code.metrics.integrated_collector import IntegratedMetricsCollector
from code.metrics.image_metrics import MetricsCollector
from code.utils.stego_visualization import DWTVisualizer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/complete_experiment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CompleteExperimentRunner:
    """
    Runs the complete experiment pipeline and collects all metrics
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the complete experiment runner
        
        Args:
            config_path: Path to configuration file (optional)
        """
        self.pipeline = SteganographyPipeline()
        self.metrics_collector = IntegratedMetricsCollector()
        self.visualizer = DWTVisualizer()
        
        # Load config if provided
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = self._get_default_config()
        
        self.experiment_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        logger.info(f"Experiment Runner initialized with ID: {self.experiment_id}")
    
    def _get_default_config(self):
        """Get default experiment configuration"""
        return {
            "text_sizes": [15, 30, 45, 55, 100, 128, 256],
            "repetitions": 3,
            "color_images": [
                "fundus1.jpg", "fundus2.jpg", "fundus3.jpg", 
                "fundus4.jpg", "fundus5.jpg"
            ],
            "grayscale_images": [
                "xray1.jpg", "xray2.jpg", "xray3.jpg", 
                "xray4.jpg", "xray5.jpg"
            ],
            "output": {
                "raw_data": "data/raw_output",
                "tables": "results/tables",
                "graphs": "results/graphs",
                "histograms": "results/histograms",
                "figures": "figures"
            }
        }
    
    def run_complete_experiment(self):
        """
        Run the complete experiment:
        1. Process all images with all text sizes
        2. Collect metrics
        3. Generate tables
        4. Create visualizations
        """
        logger.info("=" * 60)
        logger.info("STARTING COMPLETE EXPERIMENT")
        logger.info("=" * 60)
        
        # Step 1: Load all payloads
        logger.info("\n📄 Step 1: Loading text payloads...")
        payloads = self._load_all_payloads()
        
        # Step 2: Load all images
        logger.info("\n🖼️ Step 2: Loading images...")
        color_images, grayscale_images = self._load_all_images()
        
        # Step 3: Run experiments
        logger.info("\n🧪 Step 3: Running experiments...")
        all_results = self._run_all_experiments(
            color_images, grayscale_images, payloads
        )
        
        # Step 4: Collect metrics
        logger.info("\n📊 Step 4: Collecting metrics...")
        aggregated_metrics = self.metrics_collector.process_pipeline_results(all_results)
        
        # Step 5: Generate tables
        logger.info("\n📋 Step 5: Generating tables...")
        self._generate_all_tables(aggregated_metrics)
        
        # Step 6: Generate histograms
        logger.info("\n📈 Step 6: Generating histograms...")
        self._generate_histograms(color_images, grayscale_images, all_results)
        
        # Step 7: Save complete results
        logger.info("\n💾 Step 7: Saving complete results...")
        self._save_complete_results(all_results, aggregated_metrics)
        
        # Step 8: Print summary
        self._print_summary(aggregated_metrics)
        
        logger.info("\n" + "=" * 60)
        logger.info("EXPERIMENT COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        
        return all_results, aggregated_metrics
    
    def _load_all_payloads(self):
        """Load all text payloads"""
        payload_dir = Path("data/text_payloads")
        payloads = {}
        
        for size in self.config["text_sizes"]:
            file_path = payload_dir / f"payload_{size}bytes.txt"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    payloads[size] = f.read().strip()
                logger.info(f"  Loaded {size} byte payload")
            else:
                logger.warning(f"  Payload file not found: {file_path}")
                # Create a dummy payload if file doesn't exist
                payloads[size] = "X" * size
        
        return payloads
    
    def _load_all_images(self):
        """Load all color and grayscale images"""
        color_images = []
        grayscale_images = []
        
        # Load color images
        color_dir = Path("data/images/color")
        for img_name in self.config["color_images"]:
            img_path = color_dir / img_name
            if img_path.exists():
                img = cv2.imread(str(img_path))
                if img is not None:
                    color_images.append({
                        'name': img_name.replace('.jpg', '').replace('.png', ''),
                        'data': img,
                        'path': img_path
                    })
                    logger.info(f"  Loaded color image: {img_name}")
                else:
                    logger.warning(f"  Could not read color image: {img_path}")
            else:
                logger.warning(f"  Color image not found: {img_path}")
                # Create dummy image if file doesn't exist
                dummy = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
                color_images.append({
                    'name': f"dummy_color_{img_name}",
                    'data': dummy,
                    'path': None
                })
        
        # Load grayscale images
        gray_dir = Path("data/images/grayscale")
        for img_name in self.config["grayscale_images"]:
            img_path = gray_dir / img_name
            if img_path.exists():
                img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    grayscale_images.append({
                        'name': img_name.replace('.jpg', '').replace('.png', ''),
                        'data': img,
                        'path': img_path
                    })
                    logger.info(f"  Loaded grayscale image: {img_name}")
                else:
                    logger.warning(f"  Could not read grayscale image: {img_path}")
            else:
                logger.warning(f"  Grayscale image not found: {img_path}")
                # Create dummy image if file doesn't exist
                dummy = np.random.randint(0, 255, (512, 512), dtype=np.uint8)
                grayscale_images.append({
                    'name': f"dummy_gray_{img_name}",
                    'data': dummy,
                    'path': None
                })
        
        return color_images, grayscale_images
    
    def _run_all_experiments(self, color_images, grayscale_images, payloads):
        """Run all experiment combinations"""
        all_results = []
        
        # Process color images
        logger.info("\n  Processing color images...")
        for img in color_images:
            for size, text in payloads.items():
                for rep in range(self.config["repetitions"]):
                    logger.info(f"    {img['name']} - {size} bytes - repetition {rep+1}")
                    
                    try:
                        # Run pipeline
                        result = self.pipeline.process_text_to_image(
                            plaintext=text,
                            image=img['data'],
                            image_name=f"{img['name']}_{size}bytes",
                            seed=42 + rep * 100
                        )
                        
                        # Add metadata
                        result['image_type'] = 'color'
                        result['payload_size'] = size
                        result['repetition'] = rep
                        result['original_image'] = img['data']
                        
                        all_results.append(result)
                        
                    except Exception as e:
                        logger.error(f"    Error: {e}")
        
        # Process grayscale images
        logger.info("\n  Processing grayscale images...")
        for img in grayscale_images:
            for size, text in payloads.items():
                for rep in range(self.config["repetitions"]):
                    logger.info(f"    {img['name']} - {size} bytes - repetition {rep+1}")
                    
                    try:
                        # Run pipeline
                        result = self.pipeline.process_text_to_image(
                            plaintext=text,
                            image=img['data'],
                            image_name=f"{img['name']}_{size}bytes",
                            seed=42 + rep * 100
                        )
                        
                        # Add metadata
                        result['image_type'] = 'grayscale'
                        result['payload_size'] = size
                        result['repetition'] = rep
                        result['original_image'] = img['data']
                        
                        all_results.append(result)
                        
                    except Exception as e:
                        logger.error(f"    Error: {e}")
        
        logger.info(f"\n  Total experiments run: {len(all_results)}")
        return all_results
    
    def _generate_all_tables(self, aggregated_metrics):
        """Generate all required tables"""
        
        # Tables are automatically saved by IntegratedMetricsCollector
        # But we'll also print them
        
        tables_dir = Path("results/tables")
        
        # Read and display tables
        table_files = [
            "table1_color_images.txt",
            "table2_grayscale_images.txt", 
            "table3_all_metrics.txt"
        ]
        
        for table_file in table_files:
            file_path = tables_dir / table_file
            if file_path.exists():
                print(f"\n📋 {table_file}:")
                print("-" * 80)
                with open(file_path, 'r') as f:
                    print(f.read())
        
        # Generate comparison table
        comparison_table = self.metrics_collector.generate_comparison_table(
            your_avg_psnr=aggregated_metrics['image_metrics']['psnr']['mean'],
            your_avg_mse=aggregated_metrics['image_metrics']['mse']['mean']
        )
        
        print("\n📋 Table 4: Comparison with Existing Approaches:")
        print("-" * 80)
        print(comparison_table)
        
        # Save comparison table
        with open(tables_dir / "table4_comparison.txt", 'w') as f:
            f.write(comparison_table)
    
    def _generate_histograms(self, color_images, grayscale_images, all_results):
        """Generate histogram figures (Figures 4-7)"""
        
        # Group results by image type and text size
        color_results_by_size = {size: [] for size in self.config["text_sizes"]}
        gray_results_by_size = {size: [] for size in self.config["text_sizes"]}
        
        for result in all_results:
            size = result['payload_size']
            if result['image_type'] == 'color':
                color_results_by_size[size].append(result)
            else:
                gray_results_by_size[size].append(result)
        
        # Figure 4: Color images before/after (15,30,45,55 bytes)
        self._create_histogram_figure(
            images=color_images,
            results_by_size=color_results_by_size,
            sizes=[15, 30, 45, 55],
            title="Figure 4: Color Images - Before/After (15-55 bytes)",
            filename="figures/figure4_color_small.png"
        )
        
        # Figure 5: Color images before/after (100,128,256 bytes)
        self._create_histogram_figure(
            images=color_images,
            results_by_size=color_results_by_size,
            sizes=[100, 128, 256],
            title="Figure 5: Color Images - Before/After (100-256 bytes)",
            filename="figures/figure5_color_large.png"
        )
        
        # Figure 6: Grayscale images before/after (15,30,45,55 bytes)
        self._create_histogram_figure(
            images=grayscale_images,
            results_by_size=gray_results_by_size,
            sizes=[15, 30, 45, 55],
            title="Figure 6: Grayscale Images - Before/After (15-55 bytes)",
            filename="figures/figure6_gray_small.png"
        )
        
        # Figure 7: Grayscale images before/after (100,128,256 bytes)
        self._create_histogram_figure(
            images=grayscale_images,
            results_by_size=gray_results_by_size,
            sizes=[100, 128, 256],
            title="Figure 7: Grayscale Images - Before/After (100-256 bytes)",
            filename="figures/figure7_gray_large.png"
        )
        
        logger.info("  Histograms saved to figures/ directory")
    
    def _create_histogram_figure(self, images, results_by_size, sizes, title, filename):
        """Create a histogram figure for specified sizes"""
        import matplotlib.pyplot as plt
        
        # Create subplot grid
        n_sizes = len(sizes)
        n_images = min(2, len(images))  # Show up to 2 images per figure
        
        fig, axes = plt.subplots(n_sizes, n_images * 2, figsize=(15, 3*n_sizes))
        fig.suptitle(title, fontsize=14, fontweight='bold')
        
        for row, size in enumerate(sizes):
            for col, img_idx in enumerate(range(min(2, len(images)))):
                if n_images == 1:
                    # Handle single image case
                    ax_orig = axes[row, 0] if n_sizes > 1 else axes[0]
                    ax_stego = axes[row, 1] if n_sizes > 1 else axes[1]
                else:
                    # Multiple images
                    ax_orig = axes[row, col*2] if n_sizes > 1 else axes[col*2]
                    ax_stego = axes[row, col*2 + 1] if n_sizes > 1 else axes[col*2 + 1]
                
                # Get image and result
                img = images[img_idx]
                
                # Find result for this image and size
                result = None
                for r in results_by_size.get(size, []):
                    if r['image_name'].startswith(img['name']):
                        result = r
                        break
                
                if result and 'stego_image' in result:
                    # Plot original histogram
                    if len(img['data'].shape) == 3:
                        # Color image - show first channel
                        ax_orig.hist(img['data'][:,:,0].ravel(), bins=50, 
                                   color='blue', alpha=0.7, density=True)
                        ax_orig.set_title(f"{img['name']} - Original")
                    else:
                        # Grayscale
                        ax_orig.hist(img['data'].ravel(), bins=50, 
                                   color='gray', alpha=0.7, density=True)
                        ax_orig.set_title(f"{img['name']} - Original")
                    
                    # Plot stego histogram
                    if len(result['stego_image'].shape) == 3:
                        ax_stego.hist(result['stego_image'][:,:,0].ravel(), bins=50,
                                     color='red', alpha=0.7, density=True)
                        ax_stego.set_title(f"{img['name']} - Stego ({size} bytes)")
                    else:
                        ax_stego.hist(result['stego_image'].ravel(), bins=50,
                                     color='red', alpha=0.7, density=True)
                        ax_stego.set_title(f"{img['name']} - Stego ({size} bytes)")
                    
                    # Add size label on the left
                    if col == 0:
                        ax_orig.set_ylabel(f'Size: {size}B', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _save_complete_results(self, all_results, aggregated_metrics):
        """Save all results to files"""
        
        # Save raw results
        results_file = Path(f"data/raw_output/complete_results_{self.experiment_id}.json")
        
        # Convert numpy arrays to lists for JSON serialization
        serializable_results = []
        for result in all_results:
            r = result.copy()
            # Remove large image arrays for JSON
            if 'stego_image' in r:
                del r['stego_image']
            if 'original_image' in r:
                del r['original_image']
            serializable_results.append(r)
        
        with open(results_file, 'w') as f:
            json.dump(serializable_results, f, indent=2, default=str)
        
        # Save aggregated metrics
        metrics_file = Path(f"results/aggregated_metrics_{self.experiment_id}.json")
        with open(metrics_file, 'w') as f:
            json.dump(aggregated_metrics, f, indent=2, default=str)
        
        logger.info(f"  Results saved to: {results_file}")
        logger.info(f"  Metrics saved to: {metrics_file}")
    
    def _print_summary(self, aggregated_metrics):
        """Print experiment summary"""
        
        print("\n" + "=" * 60)
        print("EXPERIMENT SUMMARY")
        print("=" * 60)
        
        print(f"\n📊 Overall Statistics:")
        print(f"  Total experiments: {aggregated_metrics.get('total_experiments', 0)}")
        print(f"  Successful: {aggregated_metrics.get('successful_experiments', 0)}")
        print(f"  Success rate: {aggregated_metrics.get('successful_experiments', 0)/aggregated_metrics.get('total_experiments', 1)*100:.1f}%")
        
        print(f"\n📈 Image Quality Metrics:")
        print(f"  PSNR (dB): {aggregated_metrics['image_metrics']['psnr']['mean']:.2f} ± {aggregated_metrics['image_metrics']['psnr']['std']:.2f}")
        print(f"  MSE: {aggregated_metrics['image_metrics']['mse']['mean']:.6f} ± {aggregated_metrics['image_metrics']['mse']['std']:.6f}")
        print(f"  SSIM: {aggregated_metrics['image_metrics']['ssim']['mean']:.4f} ± {aggregated_metrics['image_metrics']['ssim']['std']:.4f}")
        print(f"  Correlation: {aggregated_metrics['image_metrics']['correlation']['mean']:.4f} ± {aggregated_metrics['image_metrics']['correlation']['std']:.4f}")
        
        print(f"\n🔢 Data Metrics:")
        print(f"  BER: {aggregated_metrics['data_metrics']['ber']['mean']:.6f}")
        
        print(f"\n📁 Output Files:")
        print(f"  Tables: results/tables/")
        print(f"  Figures: figures/")
        print(f"  Raw data: data/raw_output/")
        print(f"  Logs: logs/complete_experiment.log")


def main():
    """Main function to run the complete experiment"""
    
    print("\n" + "=" * 60)
    print("COMPLETE MEDICAL IMAGE STEGANOGRAPHY EXPERIMENT")
    print("=" * 60)
    
    # Check if images exist
    color_dir = Path("data/images/color")
    gray_dir = Path("data/images/grayscale")
    
    if not color_dir.exists() or len(list(color_dir.glob("*.jpg"))) == 0:
        print("\n⚠️  Warning: No color images found in data/images/color/")
        print("   Will create dummy images for testing.")
    
    if not gray_dir.exists() or len(list(gray_dir.glob("*.jpg"))) == 0:
        print("\n⚠️  Warning: No grayscale images found in data/images/grayscale/")
        print("   Will create dummy images for testing.")
    
    # Create necessary directories
    for dir_path in ["data/raw_output", "results/tables", "results/graphs", 
                    "results/histograms", "figures", "logs"]:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # Run experiment
    runner = CompleteExperimentRunner()
    
    try:
        results, metrics = runner.run_complete_experiment()
        
        print("\n" + "=" * 60)
        print("✅ EXPERIMENT COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"Experiment failed: {e}", exc_info=True)
        print(f"\n❌ Experiment failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())