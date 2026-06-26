"""
Description: Do not edit
Author: HuPengcheng
Date: 2026-06-11 15:38:59
LastEditors: HuPengcheng hpc0813@outlook.com
LastEditTime: 2026-06-26 18:10:23
FilePath: /DJI_Radiometric_Corrections/module/detect_panel/detect_ocr_digit.py
"""

"""
Description: Do not edit
Author: HuPengcheng
Date: 2026-06-01 19:38:35
LastEditors: HuPengcheng hpc0813@outlook.com
LastEditTime: 2026-06-02 20:59:47
FilePath: /img-arc/module/detect_panel/detect_ocr_digit.py
"""

from typing import Optional

import ddddocr
import imutils
import numpy as np

from utils.logger import logger
from utils.tiff_tool import tiff_tool


def detect_ocr_digit(
    image: np.ndarray, downscale_height: int = 600
) -> Optional[tuple[str, dict, list]]:
    """
    Detect and recognize the panel number digit in an image.
    """
    image_original = image.copy()
    orig_h, orig_w = image_original.shape[:2]

    image_scaled = imutils.resize(image_original, height=downscale_height)
    height, width = image_scaled.shape[:2]
    scale = orig_h / height

    rect_list = tiff_tool.detect_rectangles(image=image_scaled, scale=scale)
    for rect in rect_list:
        logger.info(f"Detected rectangle: {rect}")
        bg = image_scaled.copy()
        tiff_tool.show_image(bg, rect["cnt"])
    logger.info(f"Detected {len(rect_list)} rectangles")

    if len(rect_list) < 1:
        logger.warning("No rectangles detected")
        return None

    # Initialize OCR
    ocr = ddddocr.DdddOcr(show_ad=False)

    # Try to recognize digit in each rectangle
    for rect in sorted(rect_list, key=lambda r: r["area"], reverse=True)[:5]:
        x, y, w, h = rect["x"], rect["y"], rect["w"], rect["h"]

        # Extract ROI from original image
        roi = image_original[y : y + h, x : x + w]

        if roi.size == 0:
            continue

        digit = tiff_tool.recognize_digit_in_roi(roi, ocr)

        if digit and digit in "1234567890":
            logger.info(f"Recognized panel number digit: {digit}")
            return digit, rect, rect_list

    logger.warning("Could not recognize panel number digit")
    return None
