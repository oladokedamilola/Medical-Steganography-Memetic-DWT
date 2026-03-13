# ============================================
# FILE: code/metrics/integrated_collector.py
# ============================================

"""
Integrated Metrics Collector
Connects with the pipeline to automatically collect and save metrics
"""

import json
from pathlib import Path
import logging
from typing import Dict, List, Optional
import numpy as np
from datetime import datetime

from code.metrics.image_metrics import MetricsCollector, ImageQualityMetrics, DataMetrics

logger = logging.getLogger(__name__)

class IntegratedMetricsCollector:
    """
    Collects metrics during pipeline execution and saves results
    """
    
    def __init__(self, output_dir: str = "results"):
        self.collector = MetricsCollector()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.tables_dir = self.output_dir / "tables"
        self.graphs_dir = self.output_dir / "graphs"
        self.histograms_dir = self.output_dir / "histograms"
        
        for dir_path in [self.tables_dir, self.graphs_dir, self.histograms_dir]:
            dir_path.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
    
    def process_pipeline_results(self, pipeline_results: List[Dict]) -> Dict:
        """
        Process results from pipeline and collect metrics
        
        Args:
            pipeline_results: List of results from pipeline_orchestrator
            
        Returns:
            Aggregated metrics
        """
        self.logger.info(f"Processing {len(pipeline_results)} pipeline results")
        
        for result in pipeline_results:
            # Extract data from pipeline result
            # Note: This assumes pipeline results contain the necessary fields
            
            # For now, we'll create a placeholder
            # In practice, you'd extract actual images and text from the pipeline result
            
            # Collect metrics
            metrics_result = self.collector.collect_experiment_results(
                original_image=result.get('original_image'),  # Need to ensure these are stored
                stego_image=result.get('stego_image'),
                original_text=result.get('plaintext'),
                encrypted_text=result.get('encrypted_text'),
                extracted_text=result.get('extracted_text'),
                decrypted_text=result.get('decrypted_text'),
                metadata={
                    'image_name': result.get('image_name'),
                    'image_type': result.get('image_type'),
                    'text_size': result.get('plaintext_length'),
                    'repetition': result.get('repetition', 0)
                }
            )
        
        # Aggregate results
        aggregated = self.collector.aggregate_results()
        
        # Save tables
        self.collector.save_tables(str(self.tables_dir))
        
        # Save aggregated results
        self._save_aggregated(aggregated)
        
        return aggregated
    
    def _save_aggregated(self, aggregated: Dict):
        """Save aggregated results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / f"aggregated_metrics_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(aggregated, f, indent=2, default=str)
        
        self.logger.info(f"Aggregated metrics saved to {filename}")
    
    def generate_comparison_table(self, your_avg_psnr: float, your_avg_mse: float) -> str:
        """
        Generate Table 4 comparing with existing approaches
        
        Args:
            your_avg_psnr: Your average PSNR across experiments
            your_avg_mse: Your average MSE across experiments
        """
        comparison_results = [
            {'name': 'Anwar et al.', 'psnr': '56.76', 'mse': '0.1338'},
            {'name': 'AES & RSA', 'psnr': '57.02', 'mse': '0.1288'}
        ]
        
        your_results = {
            'psnr': your_avg_psnr,
            'mse': your_avg_mse
        }
        
        return self.collector.format_for_table4(your_results, comparison_results)
    
    def export_for_visualization(self) -> Dict:
        """Export metrics in format suitable for visualization"""
        
        export_data = {
            'psnr_by_size': {},
            'mse_by_size': {},
            'ber_by_size': {},
            'ssim_by_size': {}
        }
        
        # Group by text size
        for size, results in self.collector.aggregated_results.get('by_text_size', {}).items():
            export_data['psnr_by_size'][size] = results.get('avg_psnr')
            export_data['mse_by_size'][size] = results.get('avg_mse')
            export_data['ber_by_size'][size] = results.get('avg_ber')
        
        # Group by image type
        export_data['by_image_type'] = self.collector.aggregated_results.get('by_image_type', {})
        
        return export_data


# Simple test
if __name__ == "__main__":
    collector = IntegratedMetricsCollector()
    
    # Simulate some results
    sample_results = [
        {
            'image_name': 'fundus1',
            'image_type': 'color',
            'plaintext_length': 15,
            'plaintext': 'Test message',
            'encrypted_text': '!@#$%^',
            'extracted_text': '!@#$%^',
            'decrypted_text': 'Test message',
            'original_image': np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8),
            'stego_image': np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
        }
    ]
    
    collector.process_pipeline_results(sample_results)
    
    print("\nComparison Table:")
    print(collector.generate_comparison_table(57.15, 0.1250))