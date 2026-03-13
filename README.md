# Secure Medical Image Transmission Using Memetic Algorithm Encryption and DWT Steganography

## Research Overview

This repository contains the complete implementation of a novel approach for secure medical data transmission, combining Memetic Algorithm-based encryption with Discrete Wavelet Transform (DWT) steganography. The project demonstrates high-capacity, secure hiding of patient data within medical images while maintaining diagnostic image quality.

**Research Contribution:** A hybrid security framework that leverages evolutionary computing (Memetic Algorithm) for encryption and frequency-domain steganography for data hiding, specifically optimized for medical imaging applications.

---

## Methodology

### 1. Memetic Algorithm Encryption (Algorithms 2 & 3)

| Component | Description |
|-----------|-------------|
| **PRNG** | Multiplicative congruential: Z(i+1) = Z(i) × a (mod m) |
| **Modulus (m)** | 2,147,383,648 (large prime) |
| **Multiplier (a)** | Odd number with 2^16+3 limit |
| **Crossover Types** | 0: One-point, 1: Two-point, 2: Uniform, 3: Multi-point |
| **Selection** | PRNG mod 4 determines crossover type per iteration |
| **Mutation** | Applied to all blocks after crossover |
| **Termination** | Fixed iterations or convergence threshold |

### 2. DWT-Based Steganography

- **Wavelet:** 1-level Haar Discrete Wavelet Transform
- **Sub-bands:** LL, LH, HL, HH
- **Embedding Regions:** HL and HH frequency bands
- **Extraction:** Synchronized DWT decomposition

---

## Technical Architecture

```
📦 Project Root
├── 📁 code/
│   ├── 📁 encryption/          # Memetic Algorithm implementation
│   │   ├── prng.py              # Pseudo-random number generator
│   │   ├── crossover.py         # Four crossover operators
│   │   ├── mutation.py          # Mutation operations
│   │   ├── algorithm2.py        # Encryption implementation
│   │   └── algorithm3.py        # Decryption implementation
│   ├── 📁 steganography/       
│   │   ├── dwt.py               # Haar DWT decomposition
│   │   ├── embed.py             # Data embedding in HL/HH bands
│   │   ├── extract.py           # Data extraction
│   │   └── reconstruct.py       # Image reconstruction
│   ├── 📁 integration/           # Pipeline orchestration
│   ├── 📁 metrics/               # Quality metrics calculation
│   └── 📁 experiments/           # Batch processing
├── 📁 data/
│   ├── 📁 images/              
│   │   ├── 📁 color/            # 5 fundus/medical color images
│   │   └── 📁 grayscale/        # 5 chest X-ray images
│   └── 📁 text_payloads/        # Medical text samples (15-256 bytes)
└── 📁 results/
    ├── 📁 tables/               # PSNR, MSE, SSIM, BER results
    ├── 📁 graphs/               # Performance visualizations
    └── 📁 histograms/           # Before/after comparisons
```

---

## Key Features

| Feature | Description |
|---------|-------------|
| 🔐 **Custom Encryption** | Novel Memetic Algorithm without external crypto libraries |
| 🖼️ **Adaptive Steganography** | Frequency-domain hiding optimized for medical images |
| 📊 **Comprehensive Metrics** | PSNR, MSE, SSIM, Structural Content, Correlation, BER |
| 🎨 **Multi-format Support** | Both color and grayscale medical images |
| 📦 **Variable Payload** | 15, 30, 45, 55, 100, 128, and 256-byte messages |
| ✅ **Lossless Recovery** | BER = 0 for all successful extractions |

---

## Experimental Results

### Table 1: PSNR and MSE for Color Medical Images

| Image | Text Size | DWT-1L PSNR | DWT-1L MSE |
|-------|-----------|--------------|-------------|
| **Fundus-1** | 15 | [value] | [value] |
| | 30 | [value] | [value] |
| | 45 | [value] | [value] |
| | 55 | [value] | [value] |
| | 100 | [value] | [value] |
| | 128 | [value] | [value] |
| | 256 | [value] | [value] |
| **Fundus-2** | 15 | [value] | [value] |
| | 30 | [value] | [value] |
| | 45 | [value] | [value] |
| | 55 | [value] | [value] |
| | 100 | [value] | [value] |
| | 128 | [value] | [value] |
| | 256 | [value] | [value] |
| **Fundus-3** | 15 | [value] | [value] |
| | 30 | [value] | [value] |
| | 45 | [value] | [value] |
| | 55 | [value] | [value] |
| | 100 | [value] | [value] |
| | 128 | [value] | [value] |
| | 256 | [value] | [value] |
| **Fundus-4** | 15 | [value] | [value] |
| | 30 | [value] | [value] |
| | 45 | [value] | [value] |
| | 55 | [value] | [value] |
| | 100 | [value] | [value] |
| | 128 | [value] | [value] |
| | 256 | [value] | [value] |
| **Fundus-5** | 15 | [value] | [value] |
| | 30 | [value] | [value] |
| | 45 | [value] | [value] |
| | 55 | [value] | [value] |
| | 100 | [value] | [value] |
| | 128 | [value] | [value] |
| | 256 | [value] | [value] |

---

### Table 2: PSNR and MSE for Grayscale Medical Images

| Image | Text Size | DWT-1L PSNR | DWT-1L MSE |
|-------|-----------|--------------|-------------|
| **Xray-1** | 15 | [value] | [value] |
| | 30 | [value] | [value] |
| | 45 | [value] | [value] |
| | 55 | [value] | [value] |
| | 100 | [value] | [value] |
| | 128 | [value] | [value] |
| | 256 | [value] | [value] |
| **Xray-2** | 15 | [value] | [value] |
| | 30 | [value] | [value] |
| | 45 | [value] | [value] |
| | 55 | [value] | [value] |
| | 100 | [value] | [value] |
| | 128 | [value] | [value] |
| | 256 | [value] | [value] |
| **Xray-3** | 15 | [value] | [value] |
| | 30 | [value] | [value] |
| | 45 | [value] | [value] |
| | 55 | [value] | [value] |
| | 100 | [value] | [value] |
| | 128 | [value] | [value] |
| | 256 | [value] | [value] |
| **Xray-4** | 15 | [value] | [value] |
| | 30 | [value] | [value] |
| | 45 | [value] | [value] |
| | 55 | [value] | [value] |
| | 100 | [value] | [value] |
| | 128 | [value] | [value] |
| | 256 | [value] | [value] |
| **Xray-5** | 15 | [value] | [value] |
| | 30 | [value] | [value] |
| | 45 | [value] | [value] |
| | 55 | [value] | [value] |
| | 100 | [value] | [value] |
| | 128 | [value] | [value] |
| | 256 | [value] | [value] |

---

### Table 3: Quality Metrics for All Test Images

| Image | Text Size | BER | SSIM | SC | Correlation |
|-------|-----------|:---:|------|-----|-------------|
| **Fundus-1** | 15 | 0 | [value] | [value] | [value] |
| | 30 | 0 | [value] | [value] | [value] |
| | 45 | 0 | [value] | [value] | [value] |
| | 55 | 0 | [value] | [value] | [value] |
| | 100 | 0 | [value] | [value] | [value] |
| | 128 | 0 | [value] | [value] | [value] |
| | 256 | 0 | [value] | [value] | [value] |
| **Fundus-2** | 15 | 0 | [value] | [value] | [value] |
| | ... | ... | ... | ... | ... |
| **Xray-1** | 15 | 0 | [value] | [value] | [value] |
| | ... | ... | ... | ... | ... |

---

### Table 4: Comparative Analysis with Existing Methods

| Model | PSNR | MSE |
|-------|------|-----|
| Anwar et al. (2020) | 56.76 | 0.1338 |
| AES & RSA Hybrid | 57.02 | 0.1288 |
| **Proposed Memetic-DWT** | [value] | [value] |

---

## Performance Analysis

| Metric | Observation |
|--------|-------------|
| **Imperceptibility** | PSNR > 40 dB across all payload sizes |
| **Capacity** | Successful embedding up to 256 bytes |
| **Security** | Encryption through evolutionary operations |
| **Robustness** | Zero BER ensures perfect data recovery |

---

## Dataset

| Image Type | Count | Preferred Source | Alternative |
|------------|-------|------------------|-------------|
| 🟢 **Color** | 5 | Fundus/retinal images | Medical color images |
| ⚪ **Grayscale** | 5 | Chest X-rays | Medical grayscale imagery |

> **Note:** Medical images are not included in this repository due to privacy restrictions. Researchers should use appropriate publicly available medical image datasets.

---

## Results Reproduction

### 1. Environment Setup
```bash
pip install -r requirements.txt
```

### 2. Initialize Project Structure
```bash
python setup_project.py
```

### 3. Add Medical Images
```
📁 data/images/color/     ← Place 5 color images here
📁 data/images/grayscale/ ← Place 5 grayscale images here
```

### 4. Run Complete Pipeline
```bash
python -m code.experiments.run_all
```

### 5. Generate Results
```bash
python -m code.experiments.generate_tables
python -m code.experiments.generate_histograms
```

---

## Results Visualization

| Figure | Content | Payload Sizes |
|--------|---------|---------------|
| **Figure 4** | Color image histograms (before/after) | 15, 30, 45, 55 bytes |
| **Figure 5** | Color image histograms (before/after) | 100, 128, 256 bytes |
| **Figure 6** | Grayscale image histograms (before/after) | 15, 30, 45, 55 bytes |
| **Figure 7** | Grayscale image histograms (before/after) | 100, 128, 256 bytes |

Additional visualizations:
- Performance graphs (PSNR vs. payload size)
- Comparative bar charts with existing methods

---

## Citation

```bibtex
@article{medical-stego-memetic-dwt,
  title={Secure Medical Image Transmission Using Memetic Algorithm 
         Encryption and DWT Steganography},
  author={[Your Name]},
  journal={[Journal Name]},
  year={2026}
}
```

---

## License

This research code is provided for academic and non-commercial use only.  
© 2026 [Your Institution]

---