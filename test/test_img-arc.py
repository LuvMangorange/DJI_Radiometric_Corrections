"""
Description: Do not edit
Author: HuPengcheng
Date: 2026-06-02 21:19:46
LastEditors: HuPengcheng hpc0813@outlook.com
LastEditTime: 2026-06-03 13:28:29
FilePath: /img-arc/test/test_img-arc.py
"""

import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)


def test_relative_radiance_by_cam():
    """Test Mavic 3M image processing functionality"""

    from module.img_arc import to_relative_radiance_by_cam

    output_dir = "./output"
    for file in os.listdir(output_dir):
        if file.endswith(".TIF"):
            file_path = os.path.join(output_dir, file)
            to_relative_radiance_by_cam(file_path, output_dir)


def test_absolute_radiance_by_panel():
    """Test Mavic 3M image processing functionality"""

    import cv2
    import numpy as np
    from osgeo import gdal

    from module.detect_panel import (
        detect_panels,
        fit_reflctance_fuctions,
        take_closest_image,
    )
    from module.img_arc import to_absolute_radiance_by_panel, to_radiance
    from utils.logger import logger
    from utils.reflectance_map import reflectance_map
    from utils.tiff_tool import tiff_tool

    band_map = {
        "B": "blue_450nm",
        "G": "green_560nm",
        "R": "red_650nm",
        "RE": "red_edge_730nm",
        "NIR": "nir_840nm",
        "D": "rgb_380_780nm",
    }

    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)

    cd_data_dir = "/home/algorithm/Data/TMP/河南周口玉米—20260625—110米—原始影像/河南周口玉米—20260625—110米—原始影像—CD"
    cd_output_dir = "/home/algorithm/Data/TMP/output"
    closest_image = take_closest_image(cd_data_dir)
    print(closest_image)

    multi_reflectance_functions = {}
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

        panel_irradiance = to_radiance(band_path, cd_output_dir)

        ds = gdal.Open(
            os.path.join(cd_output_dir, os.path.basename(band_path)), gdal.GA_ReadOnly
        )
        band = ds.GetRasterBand(1)
        dn_data = band.ReadAsArray()
        # h, w = dn_data.shape
        # mask = np.zeros((h, w), np.uint8)
        dn_list = []
        for rect in ocr_result["rectangles"]:

            # cv2.drawContours(mask, [rect["cnt"]], -1, (255,), -1)
            # Read pre-calculated center and width/height directly, no need to recalculate with boundingRect
            cx = rect["cx"]
            cy = rect["cy"]
            w = rect["w"]
            h = rect["h"]
            scale = 0.7  # Keep 70% of center size, can be adjusted to 0.6~0.9 as needed

            # Calculate shrunk half-width and half-height
            half_w = int((w * scale) / 2)
            half_h = int((h * scale) / 2)
            # Center rectangle corners
            x1 = cx - half_w
            y1 = cy - half_h
            x2 = cx + half_w
            y2 = cy + half_h

            # Generate mask to fill only center area
            mask = np.zeros_like(dn_data, dtype=np.uint8)
            cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)
            roi_dn = dn_data[mask > 0]
            mu, std = np.mean(roi_dn), np.std(roi_dn)
            roi_clean = roi_dn[(roi_dn >= mu - 3 * std) & (roi_dn <= mu + 3 * std)]
            mean_dn = np.mean(roi_clean)
            dn_list.append(mean_dn)

        fit_result = fit_reflctance_fuctions(
            sorted(dn_list, reverse=False), ref_reflectance
        )
        logger.info(f"{band_name} fitting result: {fit_result}")
        multi_reflectance_functions[band_name] = (*fit_result, panel_irradiance)

    logger.info(f"multi_reflectance_functions: {multi_reflectance_functions}")

    data_dir = "./Downloads/147DaNorthAg Base Cotton-20260603-118m-Original Image/DJI_202606031455_010_147DaNorthAg Base"
    output_dir = "./output/DJI_202606031455_010_147DaNorthAg Base"
    group_image = tiff_tool.group_tiffs(data_dir)
    for band_name, band_path in group_image.items():
        if band_name not in multi_reflectance_functions.keys():
            continue
        for file_path in band_path:
            to_absolute_radiance_by_panel(
                file_path=file_path,
                output_dir=output_dir,
                reflectance_function=multi_reflectance_functions[band_name],
            )
