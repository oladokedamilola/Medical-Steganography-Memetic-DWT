# ============================================
# FILE: code/metrics/image_metrics.py
# ============================================

"""
Image Quality Metrics Module
Calculates all required metrics for steganography evaluation:
- MSE (Mean Square Error)
- PSNR (Peak Signal-to-Noise Ratio)
- SSIM (Structural Similarity Index)
- SC (Structural Content)
- Correlation Coefficient
- BER (Bit Error Rate)
"""

import numpy as np
import cv2
import logging
from typing import Dict, List, Tuple, Optional, Union
from math import log10
import warnings

# Optional: Use scikit-image for SSIM if available
try:
    from skimage.metrics import structural_similarity as ssim
    from skimage.metrics import peak_signal_noise_ratio as skimage_psnr
    SKIMAGE_AVAILABLE = True
except ImportError:
    SKIMAGE_AVAILABLE = False
    warnings.warn("scikit-image not available. Using custom SSIM implementation (may be slower)")

# Setup module logger
logger = logging.getLogger(__name__)


# ============================================
# Step 1: Image Quality Metrics
# ============================================

class ImageQualityMetrics:
    """
    Calculate image quality metrics for steganography evaluation
    
    Metrics implemented:
    - MSE: Mean Square Error
    - PSNR: Peak Signal-to-Noise Ratio
    - SSIM: Structural Similarity Index
    - SC: Structural Content
    - Correlation Coefficient
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__ + ".ImageQualityMetrics")
    
    def calculate_mse(self, original: np.ndarray, stego: np.ndarray) -> float:
        """
        Calculate Mean Square Error (MSE)
        
        MSE = (1/(M*N)) * sum(sum((original - stego)^2))
        
        Args:
            original: Original image
            stego: Stego image (with hidden data)
            
        Returns:
            MSE value (lower is better)
        """
        if original.shape != stego.shape:
            raise ValueError(f"Image shape mismatch: {original.shape} vs {stego.shape}")
        
        # Ensure same data type
        original = original.astype(np.float64)
        stego = stego.astype(np.float64)
        
        # Calculate MSE
        if len(original.shape) == 3:  # Color image
            # Calculate per-channel MSE and average
            mse_per_channel = []
            for c in range(original.shape[2]):
                channel_mse = np.mean((original[:, :, c] - stego[:, :, c]) ** 2)
                mse_per_channel.append(channel_mse)
            mse = np.mean(mse_per_channel)
        else:  # Grayscale
            mse = np.mean((original - stego) ** 2)
        
        self.logger.debug(f"MSE calculated: {mse:.6f}")
        return float(mse)
    
    def calculate_psnr(self, original: np.ndarray, stego: np.ndarray, 
                       max_pixel: int = 255) -> float:
        """
        Calculate Peak Signal-to-Noise Ratio (PSNR)
        
        PSNR = 10 * log10(MAX^2 / MSE)
        
        Args:
            original: Original image
            stego: Stego image
            max_pixel: Maximum pixel value (255 for 8-bit images)
            
        Returns:
            PSNR value in dB (higher is better)
        """
        if SKIMAGE_AVAILABLE:
            # Use scikit-image implementation
            try:
                return float(skimage_psnr(original, stego, data_range=max_pixel))
            except:
                pass
        
        # Fallback to custom implementation
        mse = self.calculate_mse(original, stego)
        
        if mse == 0:
            return float('inf')  # Identical images
        
        psnr = 10 * log10((max_pixel ** 2) / mse)
        
        self.logger.debug(f"PSNR calculated: {psnr:.2f} dB")
        return float(psnr)
    
    def calculate_ssim(self, original: np.ndarray, stego: np.ndarray,
                       win_size: int = 7, k1: float = 0.01, k2: float = 0.03,
                       L: int = 255) -> float:
        """
        Calculate Structural Similarity Index (SSIM)
        
        Args:
            original: Original image
            stego: Stego image
            win_size: Window size for SSIM calculation
            k1, k2: Constants for SSIM calculation
            L: Dynamic range of pixel values
            
        Returns:
            SSIM value between -1 and 1 (1 means identical)
        """
        if SKIMAGE_AVAILABLE:
            # Use scikit-image implementation
            try:
                if len(original.shape) == 3:
                    # Multi-channel image
                    ssim_value = ssim(original, stego, 
                                     win_size=win_size,
                                     data_range=L,
                                     channel_axis=-1,
                                     gaussian_weights=True,
                                     sigma=1.5)
                else:
                    # Grayscale
                    ssim_value = ssim(original, stego,
                                     win_size=win_size,
                                     data_range=L,
                                     gaussian_weights=True,
                                     sigma=1.5)
                return float(ssim_value)
            except Exception as e:
                self.logger.warning(f"scikit-image SSIM failed: {e}. Using fallback.")
        
        # Custom SSIM implementation (fallback)
        return self._custom_ssim(original, stego, win_size, k1, k2, L)
    
    def _custom_ssim(self, img1: np.ndarray, img2: np.ndarray,
                     win_size: int = 7, k1: float = 0.01, k2: float = 0.03,
                     L: int = 255) -> float:
        """
        Custom SSIM implementation for when scikit-image is not available
        """
        # Handle color images by converting to grayscale for SSIM
        if len(img1.shape) == 3:
            # Convert to grayscale using luminance
            if img1.shape[2] == 3:
                img1_gray = 0.299 * img1[:, :, 0] + 0.587 * img1[:, :, 1] + 0.114 * img1[:, :, 2]
                img2_gray = 0.299 * img2[:, :, 0] + 0.587 * img2[:, :, 1] + 0.114 * img2[:, :, 2]
            else:
                img1_gray = np.mean(img1, axis=2)
                img2_gray = np.mean(img2, axis=2)
        else:
            img1_gray = img1
            img2_gray = img2
        
        # Constants
        C1 = (k1 * L) ** 2
        C2 = (k2 * L) ** 2
        
        # Calculate means
        mu1 = cv2.GaussianBlur(img1_gray.astype(np.float64), (win_size, win_size), 1.5)
        mu2 = cv2.GaussianBlur(img2_gray.astype(np.float64), (win_size, win_size), 1.5)
        
        # Calculate variances and covariance
        sigma1_sq = cv2.GaussianBlur(img1_gray.astype(np.float64) ** 2, (win_size, win_size), 1.5) - mu1 ** 2
        sigma2_sq = cv2.GaussianBlur(img2_gray.astype(np.float64) ** 2, (win_size, win_size), 1.5) - mu2 ** 2
        sigma12 = cv2.GaussianBlur(img1_gray.astype(np.float64) * img2_gray.astype(np.float64), 
                                  (win_size, win_size), 1.5) - mu1 * mu2
        
        # Calculate SSIM map
        ssim_map = ((2 * mu1 * mu2 + C1) * (2 * sigma12 + C2)) / \
                   ((mu1 ** 2 + mu2 ** 2 + C1) * (sigma1_sq + sigma2_sq + C2))
        
        # Return mean SSIM
        return float(np.mean(ssim_map))
    
    def calculate_structural_content(self, original: np.ndarray, stego: np.ndarray) -> float:
        """
        Calculate Structural Content (SC)
        
        SC = sum(sum(original^2)) / sum(sum(stego^2))
        
        Args:
            original: Original image
            stego: Stego image
            
        Returns:
            SC value (close to 1 means similar structure)
        """
        original = original.astype(np.float64)
        stego = stego.astype(np.float64)
        
        if len(original.shape) == 3:
            # Handle color images
            sc_per_channel = []
            for c in range(original.shape[2]):
                orig_sum = np.sum(original[:, :, c] ** 2)
                stego_sum = np.sum(stego[:, :, c] ** 2)
                
                if stego_sum == 0:
                    sc = float('inf')
                else:
                    sc = orig_sum / stego_sum
                sc_per_channel.append(sc)
            
            sc = np.mean(sc_per_channel)
        else:
            # Grayscale
            orig_sum = np.sum(original ** 2)
            stego_sum = np.sum(stego ** 2)
            
            if stego_sum == 0:
                sc = float('inf')
            else:
                sc = orig_sum / stego_sum
        
        self.logger.debug(f"SC calculated: {sc:.6f}")
        return float(sc)
    
    def calculate_correlation(self, original: np.ndarray, stego: np.ndarray) -> float:
        """
        Calculate Correlation Coefficient between original and stego images
        
        Args:
            original: Original image
            stego: Stego image
            
        Returns:
            Correlation coefficient between -1 and 1 (1 means perfectly correlated)
        """
        original = original.astype(np.float64)
        stego = stego.astype(np.float64)
        
        if len(original.shape) == 3:
            # Handle color images - flatten all channels
            orig_flat = original.flatten()
            stego_flat = stego.flatten()
        else:
            # Grayscale
            orig_flat = original.flatten()
            stego_flat = stego.flatten()
        
        # Calculate correlation coefficient
        correlation = np.corrcoef(orig_flat, stego_flat)[0, 1]
        
        self.logger.debug(f"Correlation calculated: {correlation:.6f}")
        return float(correlation)
    
    def calculate_all_metrics(self, original: np.ndarray, stego: np.ndarray) -> Dict[str, float]:
        """
        Calculate all image quality metrics
        
        Args:
            original: Original image
            stego: Stego image
            
        Returns:
            Dictionary with all metrics
        """
        metrics = {}
        
        try:
            metrics['mse'] = self.calculate_mse(original, stego)
        except Exception as e:
            self.logger.error(f"Failed to calculate MSE: {e}")
            metrics['mse'] = None
        
        try:
            metrics['psnr'] = self.calculate_psnr(original, stego)
        except Exception as e:
            self.logger.error(f"Failed to calculate PSNR: {e}")
            metrics['psnr'] = None
        
        try:
            metrics['ssim'] = self.calculate_ssim(original, stego)
        except Exception as e:
            self.logger.error(f"Failed to calculate SSIM: {e}")
            metrics['ssim'] = None
        
        try:
            metrics['structural_content'] = self.calculate_structural_content(original, stego)
        except Exception as e:
            self.logger.error(f"Failed to calculate SC: {e}")
            metrics['structural_content'] = None
        
        try:
            metrics['correlation'] = self.calculate_correlation(original, stego)
        except Exception as e:
            self.logger.error(f"Failed to calculate correlation: {e}")
            metrics['correlation'] = None
        
        return metrics


# ============================================
# Step 2: Data Metrics
# ============================================

class DataMetrics:
    """
    Calculate data-related metrics for steganography evaluation
    
    Metrics implemented:
    - BER: Bit Error Rate
    - Payload capacity tracking
    - Data integrity metrics
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__ + ".DataMetrics")
    
    def calculate_ber(self, original_data: Union[str, bytes, List], 
                      extracted_data: Union[str, bytes, List]) -> float:
        """
        Calculate Bit Error Rate (BER)
        
        BER = (Number of bit errors) / (Total number of bits)
        
        Args:
            original_data: Original data before embedding
            extracted_data: Data extracted from stego image
            
        Returns:
            BER value between 0 and 1 (0 means perfect recovery)
        """
        # Convert to binary strings for comparison
        original_bits = self._to_bits(original_data)
        extracted_bits = self._to_bits(extracted_data)
        
        # Pad to same length if necessary
        max_len = max(len(original_bits), len(extracted_bits))
        original_bits = original_bits.ljust(max_len, '0')
        extracted_bits = extracted_bits.ljust(max_len, '0')
        
        # Count bit errors
        errors = sum(1 for i in range(max_len) 
                    if original_bits[i] != extracted_bits[i])
        
        ber = errors / max_len if max_len > 0 else 0
        
        self.logger.debug(f"BER calculated: {ber:.6f} ({errors}/{max_len} bits)")
        return float(ber)
    
    def _to_bits(self, data: Union[str, bytes, List]) -> str:
        """Convert various data types to binary string"""
        if isinstance(data, str):
            # Convert string to bits
            bits = []
            for char in data:
                char_bits = format(ord(char), '08b')
                bits.append(char_bits)
            return ''.join(bits)
        
        elif isinstance(data, bytes):
            # Convert bytes to bits
            bits = []
            for byte in data:
                byte_bits = format(byte, '08b')
                bits.append(byte_bits)
            return ''.join(bits)
        
        elif isinstance(data, list):
            # Assume list of integers (ASCII values)
            bits = []
            for val in data:
                if isinstance(val, int):
                    val_bits = format(val, '08b')
                    bits.append(val_bits)
            return ''.join(bits)
        
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")
    
    def calculate_payload_capacity(self, image: np.ndarray, 
                                   lsb_bits: int = 1) -> Dict[str, int]:
        """
        Calculate payload capacity of an image
        
        Args:
            image: Image to analyze
            lsb_bits: Number of LSB bits used per coefficient
            
        Returns:
            Dictionary with capacity information
        """
        total_pixels = image.size if len(image.shape) == 2 else image.shape[0] * image.shape[1]
        
        # For DWT, we use HL and HH subbands (each 1/4 of image size)
        dwt_coeffs = total_pixels // 4
        usable_coeffs = dwt_coeffs * 2  # HL and HH
        
        # Calculate capacities
        max_bits = usable_coeffs * lsb_bits
        max_bytes = max_bits // 8
        max_chars = max_bytes  # Assuming 1 byte per character
        
        # Subtract header overhead (48 bits = 6 bytes)
        usable_bytes = (max_bits - 48) // 8
        usable_chars = max(0, usable_bytes)
        
        capacity_info = {
            'total_pixels': total_pixels,
            'dwt_coefficients': dwt_coeffs,
            'usable_coefficients': usable_coeffs,
            'max_bits': max_bits,
            'max_bytes': max_bytes,
            'max_chars': max_chars,
            'usable_bytes': usable_bytes,
            'usable_chars': usable_chars,
            'header_overhead_bytes': 6,
            'lsb_bits': lsb_bits
        }
        
        self.logger.debug(f"Capacity: {usable_chars} chars (with {lsb_bits} LSB bits)")
        return capacity_info
    
    def calculate_data_integrity(self, original_text: str, decrypted_text: str) -> Dict[str, float]:
        """
        Calculate data integrity metrics
        
        Args:
            original_text: Original plaintext
            decrypted_text: Decrypted text after extraction
            
        Returns:
            Dictionary with integrity metrics
        """
        metrics = {}
        
        # Exact match
        metrics['exact_match'] = (original_text == decrypted_text)
        
        # Character error rate
        if len(original_text) > 0:
            errors = sum(1 for i in range(min(len(original_text), len(decrypted_text)))
                        if original_text[i] != decrypted_text[i])
            errors += abs(len(original_text) - len(decrypted_text))
            metrics['character_error_rate'] = errors / max(len(original_text), 1)
        else:
            metrics['character_error_rate'] = 0
        
        # Length difference
        metrics['length_difference'] = abs(len(original_text) - len(decrypted_text))
        
        # BER
        metrics['ber'] = self.calculate_ber(original_text, decrypted_text)
        
        return metrics


# ============================================
# Step 3: Metrics Collector
# ============================================

class MetricsCollector:
    """
    Collect and aggregate metrics from experiments
    Formats results for tables and reports
    """
    
    def __init__(self):
        self.image_metrics = ImageQualityMetrics()
        self.data_metrics = DataMetrics()
        self.logger = logging.getLogger(__name__ + ".MetricsCollector")
        
        # Storage for collected metrics
        self.results = []
    
    def collect_experiment_results(self, original_image: np.ndarray,
                                   stego_image: np.ndarray,
                                   original_text: str,
                                   encrypted_text: str,
                                   extracted_text: str,
                                   decrypted_text: str,
                                   metadata: Optional[Dict] = None) -> Dict:
        """
        Collect all metrics from a single experiment
        
        Args:
            original_image: Original image
            stego_image: Image with hidden data
            original_text: Original plaintext
            encrypted_text: Text after encryption
            extracted_text: Text extracted from stego
            decrypted_text: Text after decryption
            metadata: Additional experiment metadata
            
        Returns:
            Dictionary with all metrics
        """
        self.logger.info("Collecting metrics for experiment")
        
        results = {
            'metadata': metadata or {},
            'image_metrics': {},
            'data_metrics': {},
            'summary': {}
        }
        
        # Image quality metrics
        results['image_metrics'] = self.image_metrics.calculate_all_metrics(
            original_image, stego_image
        )
        
        # Data metrics
        results['data_metrics']['encryption_ber'] = self.data_metrics.calculate_ber(
            original_text, encrypted_text
        )
        
        results['data_metrics']['extraction_ber'] = self.data_metrics.calculate_ber(
            encrypted_text, extracted_text
        )
        
        results['data_metrics']['decryption_ber'] = self.data_metrics.calculate_ber(
            original_text, decrypted_text
        )
        
        # Data integrity
        results['data_metrics']['integrity'] = self.data_metrics.calculate_data_integrity(
            original_text, decrypted_text
        )
        
        # Payload capacity
        if original_image is not None:
            results['data_metrics']['capacity'] = self.data_metrics.calculate_payload_capacity(
                original_image
            )
        
        # Summary metrics
        results['summary']['overall_success'] = (
            results['data_metrics']['integrity'].get('exact_match', False)
        )
        
        results['summary']['psnr'] = results['image_metrics'].get('psnr')
        results['summary']['mse'] = results['image_metrics'].get('mse')
        results['summary']['ssim'] = results['image_metrics'].get('ssim')
        results['summary']['ber'] = results['data_metrics']['decryption_ber']
        
        # Add to collection
        self.results.append(results)
        
        self.logger.info(f"Metrics collected: PSNR={results['summary']['psnr']:.2f}dB, "
                        f"BER={results['summary']['ber']:.6f}")
        
        return results
    
    def aggregate_results(self, results_list: Optional[List[Dict]] = None) -> Dict:
        """
        Aggregate multiple experiment results
        
        Args:
            results_list: List of result dictionaries (uses self.results if None)
            
        Returns:
            Dictionary with aggregated statistics
        """
        if results_list is None:
            results_list = self.results
        
        if not results_list:
            return {'error': 'No results to aggregate'}
        
        aggregated = {
            'total_experiments': len(results_list),
            'successful_experiments': sum(1 for r in results_list 
                                        if r['summary'].get('overall_success', False)),
            'image_metrics': {},
            'data_metrics': {},
            'by_text_size': {},
            'by_image_type': {'color': [], 'grayscale': []}
        }
        
        # Collect all metric values
        psnr_values = []
        mse_values = []
        ssim_values = []
        sc_values = []
        correlation_values = []
        ber_values = []
        
        for result in results_list:
            # Image metrics
            if result['image_metrics'].get('psnr') is not None:
                psnr_values.append(result['image_metrics']['psnr'])
            if result['image_metrics'].get('mse') is not None:
                mse_values.append(result['image_metrics']['mse'])
            if result['image_metrics'].get('ssim') is not None:
                ssim_values.append(result['image_metrics']['ssim'])
            if result['image_metrics'].get('structural_content') is not None:
                sc_values.append(result['image_metrics']['structural_content'])
            if result['image_metrics'].get('correlation') is not None:
                correlation_values.append(result['image_metrics']['correlation'])
            
            # Data metrics
            if result['summary'].get('ber') is not None:
                ber_values.append(result['summary']['ber'])
            
            # Group by text size if available
            if 'metadata' in result and 'text_size' in result['metadata']:
                size = result['metadata']['text_size']
                if size not in aggregated['by_text_size']:
                    aggregated['by_text_size'][size] = []
                aggregated['by_text_size'][size].append(result['summary'])
            
            # Group by image type if available
            if 'metadata' in result and 'image_type' in result['metadata']:
                img_type = result['metadata']['image_type']
                if img_type in aggregated['by_image_type']:
                    aggregated['by_image_type'][img_type].append(result['summary'])
        
        # Calculate statistics
        aggregated['image_metrics'] = {
            'psnr': self._calculate_stats(psnr_values),
            'mse': self._calculate_stats(mse_values),
            'ssim': self._calculate_stats(ssim_values),
            'structural_content': self._calculate_stats(sc_values),
            'correlation': self._calculate_stats(correlation_values)
        }
        
        aggregated['data_metrics'] = {
            'ber': self._calculate_stats(ber_values)
        }
        
        # Aggregate by text size
        for size in aggregated['by_text_size']:
            size_results = aggregated['by_text_size'][size]
            aggregated['by_text_size'][size] = {
                'count': len(size_results),
                'avg_psnr': np.mean([r.get('psnr', 0) for r in size_results if r.get('psnr')]),
                'avg_mse': np.mean([r.get('mse', 0) for r in size_results if r.get('mse')]),
                'avg_ber': np.mean([r.get('ber', 0) for r in size_results if r.get('ber')]),
                'success_rate': sum(1 for r in size_results if r.get('overall_success', False)) / len(size_results)
            }
        
        return aggregated
    
    def _calculate_stats(self, values: List[float]) -> Dict[str, float]:
        """Calculate statistics for a list of values"""
        if not values:
            return {'mean': None, 'std': None, 'min': None, 'max': None}
        
        return {
            'mean': float(np.mean(values)),
            'std': float(np.std(values)),
            'min': float(np.min(values)),
            'max': float(np.max(values))
        }
    
    def format_for_table1(self, results: List[Dict], image_names: List[str]) -> str:
        """
        Format results for Table 1: PSNR and MSE for color images
        
        Format:
        | Image | Text Size | DWT-1L PSNR | DWT-1L MSE |
        """
        table_lines = []
        table_lines.append("| Image | Text Size | DWT-1L PSNR (dB) | DWT-1L MSE |")
        table_lines.append("|-------|-----------|------------------|------------|")
        
        for img_name in image_names:
            first_row = True
            for result in results:
                if result.get('metadata', {}).get('image_name') == img_name:
                    text_size = result.get('metadata', {}).get('text_size', 'N/A')
                    psnr = result['summary'].get('psnr', 'N/A')
                    mse = result['summary'].get('mse', 'N/A')
                    
                    if psnr != 'N/A':
                        psnr = f"{psnr:.2f}"
                    if mse != 'N/A':
                        mse = f"{mse:.6f}"
                    
                    if first_row:
                        table_lines.append(f"| {img_name} | {text_size} | {psnr} | {mse} |")
                        first_row = False
                    else:
                        table_lines.append(f"| | {text_size} | {psnr} | {mse} |")
        
        return '\n'.join(table_lines)
    
    def format_for_table2(self, results: List[Dict], image_names: List[str]) -> str:
        """Format results for Table 2: PSNR and MSE for grayscale images"""
        # Same format as Table 1
        return self.format_for_table1(results, image_names)
    
    def format_for_table3(self, results: List[Dict], image_names: List[str]) -> str:
        """
        Format results for Table 3: BER, SSIM, SC, Correlation
        
        Format:
        | Image | Text Size | BER | SSIM | SC | Correlation |
        """
        table_lines = []
        table_lines.append("| Image | Text Size | BER | SSIM | SC | Correlation |")
        table_lines.append("|-------|-----------|-----|------|-----|-------------|")
        
        for img_name in image_names:
            first_row = True
            for result in results:
                if result.get('metadata', {}).get('image_name') == img_name:
                    text_size = result.get('metadata', {}).get('text_size', 'N/A')
                    ber = result['summary'].get('ber', 'N/A')
                    ssim = result['image_metrics'].get('ssim', 'N/A')
                    sc = result['image_metrics'].get('structural_content', 'N/A')
                    corr = result['image_metrics'].get('correlation', 'N/A')
                    
                    if ber != 'N/A':
                        ber = f"{ber:.6f}"
                    if ssim != 'N/A':
                        ssim = f"{ssim:.4f}"
                    if sc != 'N/A':
                        sc = f"{sc:.4f}"
                    if corr != 'N/A':
                        corr = f"{corr:.4f}"
                    
                    if first_row:
                        table_lines.append(f"| {img_name} | {text_size} | {ber} | {ssim} | {sc} | {corr} |")
                        first_row = False
                    else:
                        table_lines.append(f"| | {text_size} | {ber} | {ssim} | {sc} | {corr} |")
        
        return '\n'.join(table_lines)
    
    def format_for_table4(self, your_results: Dict, comparison_results: List[Dict]) -> str:
        """
        Format results for Table 4: Comparison with existing approaches
        
        Format:
        | Model | PSNR | MSE |
        """
        table_lines = []
        table_lines.append("| Model | PSNR (dB) | MSE |")
        table_lines.append("|-------|-----------|-----|")
        
        # Add comparison models
        for model in comparison_results:
            table_lines.append(f"| {model['name']} | {model['psnr']} | {model['mse']} |")
        
        # Add your results
        table_lines.append(f"| Memetic Algorithm | {your_results['psnr']:.2f} | {your_results['mse']:.6f} |")
        
        return '\n'.join(table_lines)
    
    def save_tables(self, output_dir: str = "results/tables"):
        """Save all formatted tables to files"""
        import os
        from pathlib import Path
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Group results by image type
        color_results = [r for r in self.results 
                        if r.get('metadata', {}).get('image_type') == 'color']
        gray_results = [r for r in self.results 
                       if r.get('metadata', {}).get('image_type') == 'grayscale']
        
        # Get unique image names
        color_names = sorted(list(set(r.get('metadata', {}).get('image_name', '') 
                                     for r in color_results)))
        gray_names = sorted(list(set(r.get('metadata', {}).get('image_name', '') 
                                    for r in gray_results)))
        
        # Generate tables
        table1 = self.format_for_table1(color_results, color_names)
        table2 = self.format_for_table2(gray_results, gray_names)
        table3 = self.format_for_table3(self.results, color_names + gray_names)
        
        # Save to files
        with open(output_dir / "table1_color_images.txt", 'w') as f:
            f.write(table1)
        
        with open(output_dir / "table2_grayscale_images.txt", 'w') as f:
            f.write(table2)
        
        with open(output_dir / "table3_all_metrics.txt", 'w') as f:
            f.write(table3)
        
        self.logger.info(f"Tables saved to {output_dir}")


# ============================================
# Testing Module
# ============================================

class MetricsTester:
    """Test the metrics implementations"""
    
    def __init__(self):
        self.metrics = ImageQualityMetrics()
        self.data_metrics = DataMetrics()
        self.collector = MetricsCollector()
        self.logger = logging.getLogger(__name__ + ".MetricsTester")
    
    def test_image_metrics(self):
        """Test image quality metrics"""
        self.logger.info("Testing image quality metrics...")
        
        # Create test images
        original = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        identical = original.copy()
        different = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        
        # Test MSE
        mse_identical = self.metrics.calculate_mse(original, identical)
        assert mse_identical == 0, f"MSE for identical images should be 0, got {mse_identical}"
        
        mse_diff = self.metrics.calculate_mse(original, different)
        assert mse_diff > 0, f"MSE for different images should be >0, got {mse_diff}"
        
        # Test PSNR
        psnr_identical = self.metrics.calculate_psnr(original, identical)
        assert psnr_identical == float('inf'), f"PSNR for identical images should be inf"
        
        psnr_diff = self.metrics.calculate_psnr(original, different)
        assert psnr_diff > 0, f"PSNR should be positive, got {psnr_diff}"
        
        # Test correlation
        corr_identical = self.metrics.calculate_correlation(original, identical)
        assert abs(corr_identical - 1.0) < 1e-10, f"Correlation for identical images should be 1"
        
        self.logger.info("✓ Image metrics tests passed")
        return True
    
    def test_data_metrics(self):
        """Test data metrics"""
        self.logger.info("Testing data metrics...")
        
        # Test BER
        identical_text = "Hello World"
        ber_identical = self.data_metrics.calculate_ber(identical_text, identical_text)
        assert ber_identical == 0, f"BER for identical text should be 0"
        
        different_text = "Hello World!"
        ber_diff = self.data_metrics.calculate_ber(identical_text, different_text)
        assert ber_diff > 0, f"BER for different text should be >0"
        
        # Test capacity
        test_image = np.zeros((256, 256), dtype=np.uint8)
        capacity = self.data_metrics.calculate_payload_capacity(test_image, lsb_bits=1)
        assert capacity['usable_chars'] > 0, f"Capacity should be >0"
        
        self.logger.info("✓ Data metrics tests passed")
        return True
    
    def run_all_tests(self):
        """Run all tests"""
        self.logger.info("=" * 50)
        self.logger.info("Running Metrics Module Tests")
        self.logger.info("=" * 50)
        
        tests = [
            self.test_image_metrics,
            self.test_data_metrics
        ]
        
        results = []
        for test in tests:
            try:
                result = test()
                results.append(True)
            except AssertionError as e:
                self.logger.error(f"Test failed: {test.__name__} - {str(e)}")
                results.append(False)
            except Exception as e:
                self.logger.error(f"Test error: {test.__name__} - {str(e)}")
                results.append(False)
        
        self.logger.info("=" * 50)
        if all(results):
            self.logger.info("✅ ALL TESTS PASSED!")
            return True
        else:
            self.logger.error(f"❌ {sum(results)}/{len(results)} tests passed")
            return False


# ============================================
# Main execution
# ============================================

def main():
    """Main function to test metrics module"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\n" + "="*60)
    print("METRICS MODULE - PHASE 4")
    print("="*60 + "\n")
    
    # Run tests
    tester = MetricsTester()
    tests_passed = tester.run_all_tests()
    
    if tests_passed:
        print("\n📊 Demonstration:")
        print("-" * 40)
        
        # Create test data
        original_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        stego_img = original_img + np.random.randint(0, 2, (100, 100, 3), dtype=np.uint8)
        original_text = "Test medical data"
        encrypted_text = "!@#$%^&*()"  # Simulated encrypted text
        extracted_text = encrypted_text
        decrypted_text = original_text
        
        # Collect metrics
        collector = MetricsCollector()
        results = collector.collect_experiment_results(
            original_image=original_img,
            stego_image=stego_img,
            original_text=original_text,
            encrypted_text=encrypted_text,
            extracted_text=extracted_text,
            decrypted_text=decrypted_text,
            metadata={'image_name': 'test_img', 'text_size': len(original_text)}
        )
        
        print(f"\nCollected metrics for test experiment:")
        print(f"  PSNR: {results['summary']['psnr']:.2f} dB")
        print(f"  MSE: {results['summary']['mse']:.6f}")
        print(f"  SSIM: {results['summary']['ssim']:.4f}")
        print(f"  BER: {results['summary']['ber']:.6f}")
        print(f"  Success: {'✅' if results['summary']['overall_success'] else '❌'}")
        
        # Format tables
        print("\n📋 Sample Table Format:")
        table = collector.format_for_table1(
            [results], 
            ['test_img']
        )
        print(table)
    
    print("\n" + "="*60)
    print("Phase 4 implementation complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()