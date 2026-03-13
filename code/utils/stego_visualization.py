# ============================================
# FILE: code/utils/stego_visualization.py
# ============================================

"""
Visualization utilities for DWT steganography
Helps visualize sub-bands and embedding effects
"""

import numpy as np
import matplotlib.pyplot as plt
import pywt
import cv2
from pathlib import Path
from typing import Optional, List, Tuple

class DWTVisualizer:
    """Visualize DWT decomposition and steganography effects"""
    
    def __init__(self, wavelet: str = 'haar'):
        self.wavelet = wavelet
    
    def plot_subbands(self, image: np.ndarray, title: str = "DWT Subbands", 
                     save_path: Optional[str] = None):
        """Plot the four DWT subbands"""
        
        # Perform DWT
        coeffs = pywt.dwt2(image, self.wavelet)
        cA, (cH, cV, cD) = coeffs
        
        # Create figure
        fig, axes = plt.subplots(2, 2, figsize=(10, 10))
        
        # Plot each subband
        axes[0, 0].imshow(cA, cmap='gray')
        axes[0, 0].set_title('LL - Approximation')
        axes[0, 0].axis('off')
        
        axes[0, 1].imshow(cH, cmap='gray')
        axes[0, 1].set_title('LH - Horizontal')
        axes[0, 1].axis('off')
        
        axes[1, 0].imshow(cV, cmap='gray')
        axes[1, 0].set_title('HL - Vertical')
        axes[1, 0].axis('off')
        
        axes[1, 1].imshow(cD, cmap='gray')
        axes[1, 1].set_title('HH - Diagonal')
        axes[1, 1].axis('off')
        
        plt.suptitle(title)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved to {save_path}")
        
        plt.show()
    
    def compare_original_stego(self, original: np.ndarray, stego: np.ndarray,
                               title: str = "Original vs Stego", 
                               save_path: Optional[str] = None):
        """Compare original and stego images"""
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        
        # Original
        if len(original.shape) == 3:
            axes[0, 0].imshow(cv2.cvtColor(original, cv2.COLOR_BGR2RGB))
        else:
            axes[0, 0].imshow(original, cmap='gray')
        axes[0, 0].set_title('Original Image')
        axes[0, 0].axis('off')
        
        # Stego
        if len(stego.shape) == 3:
            axes[0, 1].imshow(cv2.cvtColor(stego, cv2.COLOR_BGR2RGB))
        else:
            axes[0, 1].imshow(stego, cmap='gray')
        axes[0, 1].set_title('Stego Image')
        axes[0, 1].axis('off')
        
        # Difference
        diff = np.abs(original.astype(float) - stego.astype(float))
        if len(diff.shape) == 3:
            diff = np.mean(diff, axis=2)
        
        axes[0, 2].imshow(diff, cmap='hot')
        axes[0, 2].set_title('Difference (hot = more change)')
        axes[0, 2].axis('off')
        
        # Histograms
        if len(original.shape) == 3:
            # Color image - show each channel
            colors = ['r', 'g', 'b']
            for i, color in enumerate(colors):
                axes[1, i].hist(original[:,:,i].ravel(), bins=50, alpha=0.5, 
                               label='Original', color=color, density=True)
                axes[1, i].hist(stego[:,:,i].ravel(), bins=50, alpha=0.5, 
                               label='Stego', color=color, linestyle='--', density=True)
                axes[1, i].set_title(f'{color.upper()} Channel')
                axes[1, i].legend()
        else:
            # Grayscale
            axes[1, 0].hist(original.ravel(), bins=50, alpha=0.5, 
                           label='Original', color='gray', density=True)
            axes[1, 0].hist(stego.ravel(), bins=50, alpha=0.5, 
                           label='Stego', color='red', linestyle='--', density=True)
            axes[1, 0].set_title('Pixel Value Distribution')
            axes[1, 0].legend()
            
            # Hide unused subplots
            for i in range(1, 3):
                axes[1, i].axis('off')
        
        plt.suptitle(title)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def plot_embedding_pattern(self, subband: np.ndarray, embedded_bits: int,
                              title: str = "Embedding Pattern", 
                              save_path: Optional[str] = None):
        """Visualize where bits are embedded in a subband"""
        
        # Create a mask of embedded positions
        mask = np.zeros_like(subband, dtype=bool)
        flat_mask = mask.flatten()
        
        # Mark positions where bits were embedded
        bits_per_coeff = 1  # Assuming 1 LSB bit
        num_coeffs_used = (embedded_bits + bits_per_coeff - 1) // bits_per_coeff
        flat_mask[:min(num_coeffs_used, len(flat_mask))] = True
        mask = flat_mask.reshape(subband.shape)
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        # Original subband
        axes[0].imshow(subband, cmap='gray')
        axes[0].set_title('Original Subband')
        axes[0].axis('off')
        
        # Embedding mask
        axes[1].imshow(mask, cmap='Reds')
        axes[1].set_title(f'Embedded Positions ({embedded_bits} bits)')
        axes[1].axis('off')
        
        # Overlay
        overlay = subband.copy()
        overlay = overlay.astype(float)
        overlay_max = np.max(overlay)
        if overlay_max > 0:
            overlay = overlay / overlay_max
        
        # Create RGB overlay
        overlay_rgb = np.stack([overlay, overlay, overlay], axis=2)
        overlay_rgb[mask, 0] = 1.0  # Red channel for embedded positions
        overlay_rgb[mask, 1] = 0.0
        overlay_rgb[mask, 2] = 0.0
        
        axes[2].imshow(overlay_rgb)
        axes[2].set_title('Overlay (red = embedded)')
        axes[2].axis('off')
        
        plt.suptitle(title)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()


# Example usage
def demo_visualization():
    """Demonstrate visualization utilities"""
    
    # Create a test image
    image = np.zeros((256, 256), dtype=np.uint8)
    for i in range(256):
        for j in range(256):
            image[i, j] = (i + j) // 2
    
    # Create visualizer
    vis = DWTVisualizer()
    
    # Plot subbands
    vis.plot_subbands(image, title="Test Image DWT Decomposition")
    
    # Create stego image (simulated)
    stego = image.copy()
    stego[100:150, 100:150] += np.random.randint(0, 2, (50, 50))
    
    # Compare
    vis.compare_original_stego(image, stego)
    
    # Plot embedding pattern
    vis.plot_embedding_pattern(image[100:150, 100:150], 500)


if __name__ == "__main__":
    demo_visualization()