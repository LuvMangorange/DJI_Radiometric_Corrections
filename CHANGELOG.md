# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-06-10

### Added
- Initial release of DJI Radiometric Corrections
- **Image Radiometric Correction Module (img_arc)**:
  - Black level correction for sensor offset removal
  - Gain and exposure normalization based on sensor parameters
  - Vignetting correction for lens edge brightness attenuation
  - Bayer array demosaicing support
  - White balance adjustment (automatic and manual)
  
- **Calibration Panel Detection Module (detect_panel)**:
  - Automatic detection of calibration panels in aerial images
  - OCR digit recognition for panel number identification
  - Advanced rectangle detection algorithms
  - EXIF metadata extraction and processing
  
- **Utility Functions**:
  - TIFF file processing and I/O operations
  - Comprehensive logging system
  - Data validation utilities
  
- **Testing Suite**:
  - Test cases for image radiometric correction
  - Test cases for calibration panel detection
  - EXIF metadata processing tests
  
- **Documentation**:
  - Comprehensive README with installation and usage guides
  - API documentation for all modules
  - DJI Mavic 3M image processing guide (PDF)
  - Contributing guidelines
  - This changelog

### Technical Details
- Supports Python 3.8+
- Compatible with Linux, macOS, and Windows
- GPU acceleration support via PyTorch and CUDA
- Batch processing capabilities for handling large image datasets
- Optimized memory management for processing large multispectral images

### Dependencies
- opencv-python for image processing
- numpy for numerical computations
- Pillow for image manipulation
- PyTorch and TorchVision for deep learning
- scikit-learn for machine learning algorithms
- ddddocr for OCR text recognition
- pyexiftool for EXIF metadata processing
- segment-anything (SAM) for segmentation

---

## Unreleased

### Planned Features
- Multi-band image processing support
- Real-time streaming image correction
- Advanced panel recognition with multiple languages
- GPU-optimized processing pipeline
- Distributed processing support
- Web API interface

### Known Issues
- OCR recognition may have reduced accuracy in low-light conditions
- Panel detection requires minimum panel size (5% of image area)
- Some specialized EXIF formats may not parse correctly

---

## Guidelines for Contributors

When submitting changes, please update this changelog by:
1. Adding your changes under the "Unreleased" section
2. Using these categories: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`
3. Including the PR number when applicable
4. Keeping entries concise and clear

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.
