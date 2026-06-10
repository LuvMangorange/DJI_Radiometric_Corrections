"""
Description: Do not edit
Author: HuPengcheng
Date: 2026-06-01 19:38:35
LastEditors: HuPengcheng hpc0813@outlook.com
LastEditTime: 2026-06-02 13:30:59
FilePath: /img-arc/module/detect_panel/__init__.py
"""

from ._version import __version__
from .detect_ocr_digit import detect_ocr_digit
from .detect_panel import detect_panels, fit_reflctance_fuctions, take_closest_image

__all__ = [
    "__version__",
    "detect_panels",
    "detect_ocr_digit",
    "take_closest_image",
    "fit_reflctance_fuctions",
]
