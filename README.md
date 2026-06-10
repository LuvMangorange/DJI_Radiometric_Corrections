# DJi Radiometric Corrections

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

DJI Radiometric Corrections is a professional aerial image processing system focusing on radiometric calibration and geometric correction of multispectral images captured by drones (DJI Mavic 3M). The project provides a complete image processing pipeline including black level correction, gain and exposure normalization, vignetting correction, and calibration panel detection and recognition.

## Main Features

### 1. Image Radiometric Correction (img_arc)
- **Black Level Correction**: Remove black level offset from images
- **Gain and Exposure Normalization**: Normalize based on sensor gain and exposure time
- **Vignetting Correction**: Correct lens edge brightness attenuation
- **Bayer Array Demosaicing**: Convert Bayer array to RGB image
- **White Balance**: Automatic or manual white balance adjustment

### 2. Calibration Panel Detection (detect_panel)
- **Automatic Panel Detection**: Identify calibration panels in images using SAM segmentation
- **OCR Digit Recognition**: Automatically recognize numbers on panels using DDDDOCR
- **Advanced Segmentation**: Leverage Meta's Segment Anything Model for robust panel region extraction
- **EXIF Metadata Processing**: Extract and process camera metadata

### 3. Utility Functions (utils)
- **TIFF File Processing**: Support for reading, writing, and processing TIFF formats
- **Logging System**: Complete logging system
- **Data Validation**: Data type and range validation

## System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Linux, macOS, Windows
- **Memory**: Recommended 4GB or more

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/LuvMangorange/DJI_Radiometric_Corrections.git
cd DJI_Radiometric_Corrections
```

### 2. Create Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### Dependencies Description

Main dependencies include:
- **opencv-python**: Image processing
- **numpy**: Numerical computation
- **Pillow**: Image manipulation
- **PyTorch & TorchVision**: Deep learning framework (for object detection)
- **scikit-learn**: Machine learning algorithms
- **ddddocr**: OCR text recognition for automatic calibration panel digit recognition
- **pyexiftool**: EXIF metadata processing
- **segment-anything (SAM)**: Meta's Segment Anything Model for advanced image segmentation and panel region detection

## Usage Guide

### Basic Usage

#### 1. Image Radiometric Correction
```python
from module.img_arc import img_arc
import numpy as np
import cv2

# Read image
image = cv2.imread('raw_image.tiff', cv2.IMREAD_UNCHANGED)

# Black level correction
corrected = img_arc.black_level_correction(image, bit_num=16, black_level=3200)

# Gain and exposure normalization
normalized = img_arc.exposure_gain_normalization(
    corrected, 
    sensor_gain=1.0, 
    exposure_time_us=10000
)

# Vignetting correction
vignette_corrected = img_arc.vignetting_correction(normalized)
```

#### 2. Calibration Panel Detection
```python
from module.detect_panel import detect_panel

# Detect panels
result = detect_panel.detect_panels(image, downscale_height=600)
if result:
    digit, rect, confidence = result
    print(f"Detected panel number: {digit}")
    print(f"Location: {rect}")
```

### Complete Workflow

```python
from utils.tiff_tool import tiff_tool
from module.img_arc import img_arc
from module.detect_panel import detect_panel

# 1. Read raw TIFF image
image_path = 'raw_image.tiff'
image = tiff_tool.read_tiff(image_path)

# 2. Get EXIF metadata
with exiftool.ExifTool() as et:
    metadata = et.get_metadata(image_path)
    sensor_gain = float(metadata.get('IFD0:Make', 1.0))
    exposure_time = int(metadata.get('EXIF:ExposureTime', 10000))

# 3. Radiometric correction
corrected = img_arc.black_level_correction(image)
normalized = img_arc.exposure_gain_normalization(corrected, sensor_gain, exposure_time)
calibrated = img_arc.vignetting_correction(normalized)

# 4. Panel detection
panel_result = detect_panel.detect_panels(calibrated)

# 5. Save processed image
output_path = 'corrected_image.tiff'
tiff_tool.write_tiff(calibrated, output_path)
```

## Project Structure

```
DJI_Radiometric_Corrections/
├── module/                      # Core modules
│   ├── img_arc/                # Image radiometric correction module
│   │   ├── img_arc.py         # Main correction functions
│   │   └── _version.py        # Version information
│   └── detect_panel/          # Calibration panel detection module
│       ├── detect_panel.py    # Main detection functions
│       ├── detect_ocr_digit.py # OCR recognition
│       └── _version.py        # Version information
├── utils/                      # Utility functions
│   ├── tiff_tool.py          # TIFF file operations
│   └── logger.py             # Logging system
├── test/                       # Test cases
│   ├── test_img-arc.py       # Correction module tests
│   ├── test_detect_panel.py  # Detection module tests
│   └── test_exif.py          # EXIF processing tests
├── configs/                    # Configuration files
├── doc/                        # Documentation
│   └── Mavic_3M_Image_Processing_Guide_EN.pdf
├── logs/                       # Log file directory
├── requirements.txt            # Python dependencies
└── README.md                  # This file
```

## API Documentation

### img_arc Module

#### `black_level_correction(img, bit_num=16, black_level=3200)`
Remove black level offset.

**Parameters**:
- `img` (np.ndarray): Input image
- `bit_num` (int): Bit depth, default 16
- `black_level` (int): Black level value

**Returns**: Corrected image

#### `exposure_gain_normalization(img, sensor_gain, exposure_time_us)`
Normalize based on sensor gain and exposure time.

**Parameters**:
- `img` (np.ndarray): Input image
- `sensor_gain` (float): Sensor gain value
- `exposure_time_us` (int): Exposure time (microseconds)

**Returns**: Normalized image

#### `vignetting_correction(img, vignetting_params=None)`
Correct vignetting effect.

### detect_panel Module

#### `detect_panels(image, downscale_height=600)`
Detect calibration panels in image.

**Parameters**:
- `image` (np.ndarray): Input image
- `downscale_height` (int): Downsampling height during processing

**Returns**: Dictionary containing (digit, rect, rect_list) or None

## Testing

Run test cases:
```bash
pytest test/ -v
```

Or run individual tests:
```bash
pytest test/test_img-arc.py -v
pytest test/test_detect_panel.py -v
```

## Configuration

Project configuration files are stored in the `configs/` directory. Adjust parameters according to your hardware and requirements:

- **Black level value**: Adjust according to specific camera model
- **Downsampling height**: Balance speed and accuracy
- **OCR threshold**: Adjust recognition sensitivity

## Performance Optimization

1. **Batch Processing**: Use NumPy vectorized operations instead of loops
2. **Memory Management**: Release large arrays in time
3. **Multiprocessing**: Use multiprocessing to accelerate large image batches
4. **GPU Acceleration**: PyTorch portions support CUDA acceleration

## Known Limitations

### DDDDOCR (Digit Recognition)
- OCR recognition may be inaccurate in low light or blurry conditions
- Best performance requires clear, high-contrast digit images
- Panel digits should be at least 20×20 pixels for reliable recognition

### SAM Model (Panel Segmentation)
- SAM model requires significant GPU memory (~11GB for base model)
- First inference on a device may be slower due to model initialization
- Works best with clear panel boundaries; heavily obscured panels may fail detection
- Detection algorithm has certain requirements for panel size (recommended 5% or more of image area)

### General
- Some special EXIF data formats may not be correctly parsed
- Performance varies based on image quality, lighting conditions, and panel visibility

## Troubleshooting

### Problem 1: ImportError - Cannot import SAM model or segment_anything
**Solution**: Ensure SAM is installed correctly:
```bash
pip install git+https://github.com/facebookresearch/segment-anything.git
# For GPU support with CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

**Note**: SAM model files (checkpoint) are downloaded automatically on first use. Ensure you have internet connectivity and ~500MB disk space.

### Problem 2: SAM model OutOfMemoryError (CUDA)
**Solution**: 
- Reduce image size using `downscale_height` parameter
- Use CPU inference if GPU memory is insufficient (slower but avoids OOM)
- Close other GPU applications to free memory

### Problem 3: DDDDOCR recognition failure
**Solution**: 
- Check image quality and contrast
- Ensure calibration panel digits are clearly visible
- Try adjusting preprocessing parameters (blur, threshold)
- Ensure panel size is at least 5% of image area for detection

### Problem 4: Memory overflow
**Solution**: 
- Reduce `downscale_height` or use batch processing to split large images
- Monitor memory usage with system tools during processing

## Contributing Guide

Welcome to submit Issues and Pull Requests!

1. Fork this repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## References

- **DJI Mavic 3M Official Documentation**: `doc/Mavic_3M_Image_Processing_Guide_EN.pdf`
- OpenCV Documentation: https://docs.opencv.org/
- PyTorch Documentation: https://pytorch.org/docs/

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

## Author

- **HuPengcheng** - *Lead Developer* - [hpc0813@outlook.com](mailto:hpc0813@outlook.com)

## Contact

If you have any questions or suggestions, feel free to contact:
- 📧 Email: hpc0813@outlook.com
- 🐛 Issue Tracker: [GitHub Issues](https://github.com/LuvMangorange/DJI_Radiometric_Corrections/issues)

## Changelog

### v1.0.0 (2026-06-10)
- Initial version release
- Complete radiometric correction functionality
- Calibration panel detection and OCR recognition
- Complete test suite

---

**Last Updated**: 2026-06-10
