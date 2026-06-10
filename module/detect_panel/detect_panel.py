"""
Description: Do not edit
Author: HuPengcheng
Date: 2026-06-01 15:18:07
LastEditors: HuPengcheng hpc0813@outlook.com
LastEditTime: 2026-06-01 16:22:21
FilePath: /detect-panel/module/detect_panel/detect_panel.py
"""

from typing import Dict, Optional, Tuple

import exiftool
import imutils
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

from utils.logger import logger
from utils.tiff_tool import tiff_tool

from .detect_ocr_digit import detect_ocr_digit


def detect_panels(image: np.ndarray, downscale_height: int = 600) -> Optional[Dict]:
    """
    Detect calibration panels and attempt to recognize panel number.
    """
    image_original = image.copy()
    orig_h, orig_w = image_original.shape[:2]

    # Downscale for faster processing
    image_scaled = imutils.resize(image_original, height=downscale_height)
    height, width = image_scaled.shape[:2]
    scale = orig_h / height

    # Recognize digit
    digit_detect = detect_ocr_digit(image_original, downscale_height)
    if not digit_detect:
        logger.warning("digit_detect is False")
        return None
    digit, rect, rect_list = digit_detect

    # Detect rectangles (calibration panels)
    # rect_list = tiff_tool.detect_rectangles(image_scaled, scale)

    epsilon = 0.01
    target_rects = []
    for n in range(1, 30):

        target_rects = [
            {**x, "cnt": (x["cnt"] * scale).astype(np.int32)}
            for x in rect_list
            if abs(x["area"] - rect["area"]) / max(rect["area"], x["area"])
            < 0.05 + n * epsilon
        ]
        logger.info(f"{len(target_rects)} potential calibration panels")
        if len(target_rects) == 4:
            break

    target_rects = [
        d for d in target_rects if not (d["x"] == rect["x"] and d["y"] == rect["y"])
    ]
    # bg = image_original.copy()
    # for rect in target_rects:
    #     tiff_tool.show_image(bg, rect["cnt"])

    panel_info = {
        "panel_number": int(digit),
        "rectangles": target_rects,
    }

    # logger.info(f"Panel detection result: {panel_info}")
    return panel_info


def take_closest_image(data_dir: str) -> Dict[str, str]:
    """Per band, return image with mean reflectance closest to target."""
    grouped_by_band = tiff_tool.group_tiffs(data_dir)
    calibration_data = {}

    for band, paths in grouped_by_band.items():
        if band in ["D"]:
            continue
        with exiftool.ExifToolHelper() as et:
            metadata = et.get_tags(
                paths,
                tags=["Irradiance", "BitsPerSample"],
            )
        # target = 2 ** metadata[0]["EXIF:BitsPerSample"] / 2
        irradiances = [float(d["XMP:Irradiance"]) for d in metadata]
        target = np.array(irradiances).mean()
        closest_index = np.argmin(np.abs(np.array(irradiances) - target))
        calibration_data[band] = paths[closest_index]

    return calibration_data


def fit_reflctance_fuctions(
    panel_dn_list: list, panel_reflectance: Tuple[float, ...]
) -> tuple:
    """
    Fit reflectance functions for each band using BandFitter
    """
    panel_dn = np.array(panel_dn_list).reshape(-1, 1)
    rho_true = np.array(panel_reflectance)

    lr = LinearRegression(fit_intercept=False)
    lr.fit(panel_dn, rho_true)
    k = lr.coef_[0]
    b = lr.intercept_

    rho_pred = lr.predict(panel_dn)
    r2 = r2_score(rho_true, rho_pred)

    logger.info(f"formula: rho_pred = {k:.6f} * DN + {b:.6f}")
    logger.info(f"R² = {r2:.4f}")

    return k, b, r2
