"""
Description: Do not edit
Author: HuPengcheng
Date: 2026-06-01 19:41:15
LastEditors: HuPengcheng hpc0813@outlook.com
LastEditTime: 2026-06-02 13:51:21
FilePath: /img-arc/test/test_detect_panel.py
"""

import os
import sys

import cv2
import numpy as np
from osgeo import gdal

from module.detect_panel import (
    detect_ocr_digit,
    detect_panels,
    fit_reflctance_fuctions,
    take_closest_image,
)
from utils.logger import logger
from utils.reflectance_map import reflectance_map

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)


def test_detect_ocr_digit():
    """Test digit detection functionality"""

    image_path = "./data/DJI_202606021825_007/DJI_20260602182927_0002_MS_RE.TIF"

    if not os.path.exists(image_path):
        logger.error(f"Image file does not exist: {image_path}")
        return

    result = detect_ocr_digit(cv2.imread(image_path))
    logger.info(f"Recognition result: {result}")
    print(result)


def test_detect_panel():
    """Test panel detection functionality"""

    image_path = "./data/DJI_202606021825_007/DJI_20260602182927_0002_MS_NIR.TIF"

    if not os.path.exists(image_path):
        logger.error(f"Image file does not exist: {image_path}")
        return

    result = detect_panels(cv2.imread(image_path))
    logger.info(f"Detection result: {result}")
    print(result)


def test_get_reflectance():
    """Test reflectance retrieval functionality"""

    image_path = "./data/DJI_202606021825_007/DJI_20260602182924_0001_MS_G.TIF"

    if not os.path.exists(image_path):
        logger.error(f"Image file does not exist: {image_path}")
        return

    result = detect_panels(cv2.imread(image_path))
    logger.info(f"Detection result: {result}")
    if result is None:
        logger.error("Panel not detected")
        return

    reflectance = reflectance_map.get_band_reflectances(
        result["panel_number"], band="red_650nm"
    )
    logger.info(f"Reflectance: {reflectance}")


def test_take_closest_image():
    """Test closest target irradiance image retrieval functionality"""

    data_dir = "./data/cd"
    closest_image = take_closest_image(data_dir)
    print(closest_image)


def test_fit_reflectance_functions():
    """Test reflectance function fitting functionality"""

    data_dir = "./data/DJI_202606021825_007"
    closest_image = take_closest_image(data_dir)
    print(closest_image)

    band_map = {
        "B": "blue_450nm",
        "G": "green_560nm",
        "R": "red_650nm",
        "RE": "red_edge_730nm",
        "NIR": "nir_840nm",
        "D": "rgb_380_780nm",
    }
    multi_reflectance = {}
    for band_name, band_path in closest_image.items():
        logger.info(f"Processing band {band_name} with image {band_path}")
        image = cv2.imread(band_path)
        ocr_result = detect_panels(image)
        if ocr_result is None:
            logger.error("Panel not detected")
            return
        ref_reflectance = reflectance_map.get_band_reflectances(
            ocr_result["panel_number"], band=band_map[band_name]
        )

        if ref_reflectance is None:
            logger.error("Reflectance not obtained")
            return

        ds = gdal.Open(band_path, gdal.GA_ReadOnly)
        band = ds.GetRasterBand(1)
        dn_data = band.ReadAsArray()
        h, w = dn_data.shape
        mask = np.zeros((h, w), np.uint8)
        nir_dn_list = []
        for rect in ocr_result["rectangles"]:

            cv2.drawContours(mask, [rect["cnt"]], -1, (255,), -1)

            roi_dn = dn_data[mask > 0]
            mean_dn = np.mean(roi_dn)
            nir_dn_list.append(mean_dn)

        fit_result = fit_reflctance_fuctions(
            sorted(nir_dn_list, reverse=False), ref_reflectance
        )
        logger.info(f"{band_name} fitting result: {fit_result}")
        multi_reflectance[band_name] = fit_result
    print(multi_reflectance)
