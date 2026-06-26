"""
Description: Do not edit
Author: HuPengcheng
Date: 2026-05-25 14:05:49
LastEditors: HuPengcheng hpc0813@outlook.com
LastEditTime: 2026-05-25 14:22:34
FilePath: /ocr-panel/utils/tiff_tool.py
"""

import itertools
import os
from typing import Dict, List, Optional

import cv2
import imutils
import matplotlib.pyplot as plt
import numpy as np
import torch
from segment_anything import SamAutomaticMaskGenerator, sam_model_registry

from utils.logger import logger


class TiffTool:

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    sam = sam_model_registry["vit_b"](checkpoint="./utils/sam_vit_b_01ec64.pth").to(
        device
    )
    mask_generator = SamAutomaticMaskGenerator(
        sam,
        min_mask_region_area=4000,
        pred_iou_thresh=0.78,
    )

    def __init__(self):
        self.metadata = {}
        self.tiff_meta = {}
        self.band_count = 0
        self.transform = None

    @staticmethod
    def show_image(bg: np.ndarray, cnt: np.ndarray) -> None:
        cv2.drawContours(bg, [cnt], -1, (0, 0, 255), 2)
        plt.imshow(cv2.cvtColor(bg, cv2.COLOR_BGR2RGB))
        plt.show()

    def detect_rectangles(self, image: np.ndarray, scale: float = 1.0) -> List[dict]:
        """
        Detect all rectangular regions in an image.
        """
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        masks = self.mask_generator.generate(img_rgb)
        rect_list = []

        for mask_info in masks:
            mask = mask_info["segmentation"].astype(np.uint8)
            area = mask_info["area"]

            cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)

            for cnt in cnts:
                cnt = cv2.convexHull(cnt)

                peri = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
                if len(approx) != 4:
                    continue

                pts = approx.reshape(-1, 2)
                edge = []
                for i in range(4):
                    p1 = pts[i]
                    p2 = pts[(i + 1) % 4]
                    dist = np.hypot(p1[0] - p2[0], p1[1] - p2[1])
                    edge.append(dist)
                edge = np.array(edge)
                mean_e = edge.mean()
                std_e = edge.std()
                coeff = std_e / mean_e
                if coeff > 0.2:
                    continue

                x, y, w, h = cv2.boundingRect(cnt)
                area = cv2.contourArea(cnt)

                if w == 0 or h == 0:
                    continue

                aspect = w / h
                if 0.8 < aspect < 1.2:
                    cx = x + w // 2
                    cy = y + h // 2

                    duplicate = False
                    for exist in rect_list:
                        ecx, ecy = exist["cx"], exist["cy"]
                        if (
                            abs(cx - ecx / scale) / w < 0.2
                            and abs(cy - ecy / scale) / h < 0.2
                            and abs(area - exist["area"]) / max(area, exist["area"])
                            < 0.1
                        ):
                            duplicate = True
                            break

                    if duplicate:
                        continue
                    # bg = image.copy()
                    # self.show_image(bg, cnt)

                    rect_list.append(
                        {
                            "cnt": cnt,
                            "area": area,
                            "x": int(x * scale),
                            "y": int(y * scale),
                            "w": int(w * scale),
                            "h": int(h * scale),
                            "cx": int(cx * scale),
                            "cy": int(cy * scale),
                        }
                    )

        best_group = []
        min_total_diff = float("inf")
        for group in itertools.combinations(rect_list, 4):
            areas = [p["area"] for p in group]
            total_diff = max(areas) - min(areas)
            if total_diff < min_total_diff:
                min_total_diff = total_diff
                best_group = list(group)

        return best_group

    @staticmethod
    def recognize_digit_in_roi(
        roi: np.ndarray, ocr, angles: Optional[List[int]] = None
    ) -> str:
        """
        Recognize a single digit in a region of interest using OCR.
        """
        if angles is None:
            angles = [0, 90, 180, 270]

        TARGET_DIGITS = {"1", "2", "3", "4", "5"}

        # Convert to RGB if needed
        if len(roi.shape) == 2:  # Grayscale
            roi_rgb = cv2.cvtColor(roi, cv2.COLOR_GRAY2RGB)
        elif roi.shape[2] == 4:  # RGBA
            roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGRA2RGB)
        else:  # BGR
            roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)

        for angle in angles:
            if angle != 0:
                h, w = roi_rgb.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                rotated = cv2.warpAffine(roi_rgb, M, (w, h))
            else:
                rotated = roi_rgb

            try:
                res = ocr.classification(rotated).strip()
                if res in TARGET_DIGITS:
                    logger.debug(f"Recognized digit '{res}' at angle {angle}")
                    return res
            except Exception as e:
                logger.debug(f"OCR recognition failed at angle {angle}: {e}")
                continue

        return ""

    @staticmethod
    def group_tiffs(data_dir: str) -> Dict:
        """
        Group TIFF files by band.
        """
        bands = ["D", "G", "NIR", "R", "RE"]
        band_paths = {band: [] for band in bands}

        for filename in os.listdir(data_dir):
            if filename.endswith((".JPG", ".TIF")):
                for band in bands:
                    if f"_{band}." in filename:
                        full_path = os.path.join(data_dir, filename)
                        band_paths[band].append(full_path)
                        break

        # logger.info(f"Grouped TIFF files by band: {band_paths}")
        return band_paths


tiff_tool = TiffTool()
