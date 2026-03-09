# ============================================
# PHASE 0: PROJECT SETUP AND INFRASTRUCTURE
# ============================================

# 1. First, let's create the folder structure and initial setup script
# Save this as 'setup_project.py'

import os
import json
import logging
from pathlib import Path
import random
import string

def create_project_structure(base_path="."):
    """Create the complete folder structure for the project"""
    
    folders = [
        # Code modules
        "code/encryption",
        "code/steganography", 
        "code/integration",
        "code/metrics",
        "code/experiments",
        "code/utils",
        
        # Data directories
        "data/images/color",
        "data/images/grayscale",
        "data/text_payloads",
        "data/raw_output",
        
        # Results directories
        "results/tables",
        "results/graphs",
        "results/histograms/color",
        "results/histograms/grayscale",
        
        # Figures directory
        "figures",
        
        # Logs directory
        "logs",
        
        # Test directory
        "tests/test_encryption",
        "tests/test_steganography",
        "tests/test_integration"
    ]
    
    for folder in folders:
        path = Path(base_path) / folder
        path.mkdir(parents=True, exist_ok=True)
        print(f"Created: {path}")
    
    # Create __init__.py files for Python packages
    init_locations = [
        "code/encryption",
        "code/steganography",
        "code/integration",
        "code/metrics",
        "code/experiments",
        "code/utils",
        "tests"
    ]
    
    for location in init_locations:
        init_file = Path(base_path) / location / "__init__.py"
        init_file.touch(exist_ok=True)
        print(f"Created: {init_file}")
    
    print("\n✅ Project structure created successfully!")

# ============================================
# 2. Requirements.txt file
# ============================================

requirements_content = """
# Core dependencies
numpy>=1.21.0
opencv-python>=4.5.3
pywavelets>=1.1.1
Pillow>=8.3.0
scipy>=1.7.0
matplotlib>=3.4.0
scikit-image>=0.18.0

# Utilities
tqdm>=4.62.0
pandas>=1.3.0
seaborn>=0.11.0
jupyter>=1.0.0

# Testing
pytest>=6.2.0
pytest-cov>=2.12.0

# Additional helpful packages
psutil>=5.8.0
colorama>=0.4.4
"""

with open("requirements.txt", "w") as f:
    f.write(requirements_content.strip())
print("\n✅ requirements.txt created!")

# ============================================
# 3. Text Payload Generator
# ============================================

class TextPayloadGenerator:
    """Generate text payloads of specific sizes for experiments"""
    
    def __init__(self, seed=42):
        self.seed = seed
        random.seed(seed)
        
        # Medical-themed text samples for realistic payloads
        self.medical_templates = [
            "PATIENT:{} AGE:{} SEX:{} DIAGNOSIS:{} MEDICATIONS:{}",
            "RECORD#{}: BP:{}/{} HR:{} TEMP:{} SPO2:{}",
            "NAME:{} DOB:{} MRN:{} PROCEDURE:{} NOTES:{}",
            "LABS: WBC:{} RBC:{} HGB:{} PLT:{} GLU:{}",
            "RADIOLOGY: STUDY:{} FINDINGS:{} IMPRESSION:{}"
        ]
        
        self.first_names = ["John", "Jane", "Robert", "Mary", "David", "Sarah", "Michael", "Lisa"]
        self.last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller"]
        self.diagnoses = ["Hypertension", "Diabetes", "Asthma", "UTI", "Pneumonia", "Fracture"]
        self.medications = ["Lisinopril", "Metformin", "Albuterol", "Amoxicillin", "Ibuprofen"]
    
    def generate_medical_payload(self, target_bytes):
        """Generate a medical-themed text of exactly target_bytes"""
        
        # Start with a template
        template = random.choice(self.medical_templates)
        
        while True:
            # Generate realistic medical data
            data = {
                'name': f"{random.choice(self.first_names)} {random.choice(self.last_names)}",
                'age': str(random.randint(18, 95)),
                'sex': random.choice(['M', 'F']),
                'diagnosis': random.choice(self.diagnoses),
                'medications': ', '.join(random.sample(self.medications, random.randint(1, 3))),
                'bp_sys': str(random.randint(100, 180)),
                'bp_dia': str(random.randint(60, 120)),
                'hr': str(random.randint(60, 100)),
                'temp': f"{random.randint(97, 100)}.{random.randint(0,9)}",
                'spo2': str(random.randint(95, 100)),
                'mrn': ''.join(random.choices(string.digits, k=8)),
                'dob': f"{random.randint(1,12)}/{random.randint(1,28)}/{random.randint(1940,2005)}"
            }
            
            # Fill template
            try:
                text = template.format(
                    data['name'], data['age'], data['sex'], 
                    data['diagnosis'], data['medications']
                )
            except:
                # If template doesn't match, use a simpler approach
                text = f"MEDICAL RECORD: Patient {data['name']}, Age {data['age']}, " \
                       f"Diagnosis: {data['diagnosis']}, Meds: {data['medications']}"
            
            # Adjust to exact size
            text_bytes = text.encode('utf-8')
            
            if len(text_bytes) == target_bytes:
                return text
            elif len(text_bytes) < target_bytes:
                # Pad with spaces or additional data
                padding_needed = target_bytes - len(text_bytes)
                text += " " * padding_needed
                return text
            else:
                # Truncate carefully (preserve whole words if possible)
                words = text.split()
                while len(' '.join(words).encode('utf-8')) > target_bytes:
                    words.pop()
                text = ' '.join(words)
                
                # Final padding if needed
                text_bytes = text.encode('utf-8')
                if len(text_bytes) < target_bytes:
                    text += " " * (target_bytes - len(text_bytes))
                return text
    
    def generate_payloads_for_all_sizes(self, sizes=[15, 30, 45, 55, 100, 128, 256], 
                                        output_dir="data/text_payloads"):
        """Generate payloads for all specified sizes and save to files"""
        
        payloads = {}
        
        for size in sizes:
            print(f"Generating {size}-byte payload...")
            payload = self.generate_medical_payload(size)
            payloads[size] = payload
            
            # Save to file
            filename = f"payload_{size}bytes.txt"
            filepath = Path(output_dir) / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(payload)
            
            # Verify size
            actual_size = len(payload.encode('utf-8'))
            print(f"  ✓ Saved to {filename} (actual size: {actual_size} bytes)")
        
        # Save metadata
        metadata = {
            "generator_seed": self.seed,
            "sizes": sizes,
            "files_generated": [f"payload_{size}bytes.txt" for size in sizes],
            "verification": {f"payload_{size}bytes.txt": 
                           len(payloads[size].encode('utf-8')) for size in sizes}
        }
        
        with open(Path(output_dir) / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n✅ All payloads saved to {output_dir}/")
        return payloads

# ============================================
# 4. Configuration Manager
# ============================================

class ConfigManager:
    """Manage experiment configurations"""
    
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self.load_or_create_config()
    
    def get_default_config(self):
        """Return default configuration"""
        return {
            "project": {
                "name": "Medical Image Steganography with Memetic Encryption",
                "version": "1.0.0",
                "seed": 42
            },
            "encryption": {
                "algorithm": "memetic",
                "mcg_modulus": 2147383648,
                "mcg_multiplier": 1664525,
                "max_iterations": 100,
                "convergence_threshold": 0.001,
                "mutation_rate": 0.1,
                "crossover_types": [0, 1, 2, 3]  # 0:1-point, 1:2-point, 2:uniform, 3:multi-point
            },
            "steganography": {
                "dwt_level": 1,
                "wavelet": "haar",
                "subbands": ["HL", "HH"],
                "embedding_strength": 1,
                "lsb_bits": 1
            },
            "experiments": {
                "text_sizes": [15, 30, 45, 55, 100, 128, 256],
                "repetitions": 3,
                "color_images": [
                    "fundus1.jpg", "fundus2.jpg", "fundus3.jpg", 
                    "fundus4.jpg", "fundus5.jpg"
                ],
                "grayscale_images": [
                    "xray1.jpg", "xray2.jpg", "xray3.jpg", 
                    "xray4.jpg", "xray5.jpg"
                ]
            },
            "metrics": {
                "calculate_psnr": True,
                "calculate_mse": True,
                "calculate_ssim": True,
                "calculate_sc": True,
                "calculate_correlation": True,
                "calculate_ber": True
            },
            "paths": {
                "data": "data",
                "images_color": "data/images/color",
                "images_grayscale": "data/images/grayscale",
                "text_payloads": "data/text_payloads",
                "raw_output": "data/raw_output",
                "results_tables": "results/tables",
                "results_graphs": "results/graphs",
                "results_histograms": "results/histograms",
                "figures": "figures",
                "logs": "logs"
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": "logs/experiment.log"
            }
        }
    
    def load_or_create_config(self):
        """Load existing config or create default"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            config = self.get_default_config()
            self.save_config(config)
            return config
    
    def save_config(self, config=None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get(self, key, default=None):
        """Get configuration value by dot notation key (e.g., 'encryption.max_iterations')"""
        keys = key.split('.')
        value = self.config
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

# ============================================
# 5. Logging System
# ============================================

def setup_logging(config):
    """Setup logging system based on configuration"""
    
    log_file = config.get('logging.file', 'logs/experiment.log')
    log_level = getattr(logging, config.get('logging.level', 'INFO'))
    log_format = config.get('logging.format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Also print to console
        ]
    )
    
    # Create logger for this project
    logger = logging.getLogger('MedicalSteganography')
    logger.info("="*50)
    logger.info("Logging system initialized")
    logger.info(f"Log file: {log_file}")
    logger.info("="*50)
    
    return logger

# ============================================
# 6. Main Setup Script
# ============================================

def main():
    """Main setup function to initialize the project"""
    
    print("="*60)
    print("MEDICAL IMAGE STEGANOGRAPHY PROJECT - PHASE 0 SETUP")
    print("="*60)
    print()
    
    # Step 1: Create folder structure
    print("📁 Step 1: Creating folder structure...")
    create_project_structure()
    print()
    
    # Step 2: Initialize configuration
    print("⚙️  Step 2: Initializing configuration manager...")
    config_manager = ConfigManager()
    config = config_manager.config
    print(f"✓ Configuration saved to {config_manager.config_file}")
    print()
    
    # Step 3: Setup logging
    print("📝 Step 3: Setting up logging system...")
    logger = setup_logging(config_manager)
    logger.info("Project setup started")
    print("✓ Logging system ready")
    print()
    
    # Step 4: Generate text payloads
    print("📄 Step 4: Generating text payloads...")
    generator = TextPayloadGenerator(seed=config['project']['seed'])
    payloads = generator.generate_payloads_for_all_sizes(
        sizes=config['experiments']['text_sizes']
    )
    print()
    
    # Step 5: Create placeholder for medical images
    print("🖼️  Step 5: Setting up image directories...")
    print("NOTE: You need to manually add medical images to:")
    print(f"  - Color images: {config['paths']['images_color']}/")
    print(f"  - Grayscale images: {config['paths']['images_grayscale']}/")
    print()
    
    # Create README files in image directories
    for img_dir in [config['paths']['images_color'], config['paths']['images_grayscale']]:
        readme_path = Path(img_dir) / "README.txt"
        with open(readme_path, 'w') as f:
            f.write("Place your medical images in this directory.\n")
            f.write("Required: 5 color images (fundus/eye preferred)\n")
            f.write("Required: 5 grayscale images (chest X-rays preferred)\n")
            f.write("Supported formats: .jpg, .png, .bmp\n")
    
    # Step 6: Final verification
    print("✅ Step 6: Verifying setup...")
    
    # Check all required directories exist
    required_dirs = [
        "code/encryption", "code/steganography", "code/integration",
        "code/metrics", "code/experiments", "code/utils",
        "data/images/color", "data/images/grayscale", "data/text_payloads",
        "results/tables", "results/graphs", "results/histograms",
        "logs", "figures"
    ]
    
    all_good = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"  ✓ {dir_path}")
        else:
            print(f"  ✗ {dir_path} - MISSING!")
            all_good = False
    
    # Check payload files
    for size in config['experiments']['text_sizes']:
        payload_file = Path(f"data/text_payloads/payload_{size}bytes.txt")
        if payload_file.exists():
            actual_size = len(payload_file.read_text(encoding='utf-8').encode('utf-8'))
            print(f"  ✓ payload_{size}bytes.txt ({actual_size} bytes)")
        else:
            print(f"  ✗ payload_{size}bytes.txt - MISSING!")
            all_good = False
    
    print()
    if all_good:
        print("🎉 SUCCESS! Phase 0 setup completed successfully!")
        print("\nNext steps:")
        print("  1. Add medical images to the image directories")
        print("  2. Run 'pip install -r requirements.txt' to install dependencies")
        print("  3. Proceed to Phase 1: Memetic Algorithm Encryption")
    else:
        print("⚠️  Setup incomplete. Please check the missing items above.")
    
    logger.info("Phase 0 setup completed" + (" successfully" if all_good else " with issues"))
    print("="*60)

if __name__ == "__main__":
    main()