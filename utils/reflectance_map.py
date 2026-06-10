"""
Description: Do not edit
Author: HuPengcheng
Date: 2026-06-01 19:49:40
LastEditors: HuPengcheng hpc0813@outlook.com
LastEditTime: 2026-06-01 19:56:18
FilePath: /img-arc/utils/type.py
"""

from pathlib import Path
from typing import Dict, Optional, Tuple

from utils.config_loader import ConfigLoader
from utils.logger import logger


class ReflectanceMap:
    """Manages reflectance calibration values for OCR-detected panel numbers."""

    BANDS = ["blue_450nm", "green_560nm", "red_650nm", "red_edge_730nm", "nir_840nm"]

    def __init__(self, calibration_yaml_path: Optional[str] = None):
        """
        Initialize reflectance map from YAML file.

        Args:
            calibration_yaml_path: Path to spectral_reflectance.yaml.
                                If None, uses default path relative to module.
        """
        if calibration_yaml_path is None:
            # Default to cfg directory
            calibration_yaml_path = (
                "/home/algorithm/projects/img-arc/configs/spectral_reflectance.yaml"
            )

        self.calibration_path = Path(calibration_yaml_path)

        if not self.calibration_path.exists():
            raise FileNotFoundError(
                f"Reflectance calibration YAML not found: {self.calibration_path}"
            )

        self.config_data = ConfigLoader.yaml(str(self.calibration_path))
        logger.info(f"Loaded reflectance calibration from {self.calibration_path}")

        # Build lookup: panel_number -> list of 3 reflectance dicts
        self._build_lookup_table()

    def _build_lookup_table(self):
        """Build internal lookup table for fast panel number access."""
        self.panel_lookup = {}

        if "panels" not in self.config_data:
            raise ValueError("YAML file must contain 'panels' key")

        for panel_data in self.config_data["panels"]:
            panel_num = panel_data.get("panel_number")
            products = panel_data.get("products", [])

            if len(products) != 3:
                logger.warning(
                    f"Panel {panel_num} has {len(products)} entries, expected 3"
                )

            level_order = {"low": 0, "mid": 1, "high": 2}
            sorted_products = sorted(
                products, key=lambda x: level_order.get(x.get("reflectance_level"), 3)
            )

            reflectance_list = []
            for product in sorted_products:
                spectral_data = product.get("spectral_data", {})
                reflectance_dict = {
                    "product_code": product.get("product_code"),
                    "reflectance_level": product.get("reflectance_level"),
                    "blue_450nm": spectral_data.get("blue_450nm"),
                    "green_560nm": spectral_data.get("green_560nm"),
                    "red_650nm": spectral_data.get("red_650nm"),
                    "red_edge_730nm": spectral_data.get("red_edge_730nm"),
                    "nir_840nm": spectral_data.get("nir_840nm"),
                    "rgb_380_780nm": spectral_data.get("rgb_380_780nm"),
                }
                reflectance_list.append(reflectance_dict)

            self.panel_lookup[panel_num] = reflectance_list

    def get_reflectance_by_panel_number(self, panel_number: int) -> Optional[list]:
        """
        Get reflectance values for a specific panel number.

        Args:
            panel_number: Panel identifier (1, 2, 3, or 4)

        Returns:
            List of 3 reflectance dicts [low, mid, high], or None if not found
        """
        if panel_number not in self.panel_lookup:
            logger.warning(
                f"Panel number {panel_number} not found in calibration table"
            )
            return None

        return self.panel_lookup[panel_number]

    def get_band_reflectances(
        self, panel_number: int, band: str
    ) -> Optional[Tuple[float, float, float]]:
        """
        Get reflectance values for a specific band across all 3 panels.

        Args:
            panel_number: Panel identifier (1, 2, 3, or 4)
            band: Band name (e.g., 'red_650nm', 'blue_450nm')

        Returns:
            Tuple of (low, mid, high) reflectance values, or None if not found
        """
        panels = self.get_reflectance_by_panel_number(panel_number)
        if panels is None:
            return None

        if band not in panels[0]:
            logger.warning(f"Band {band} not found in reflectance data")
            return None

        return (panels[0][band], panels[1][band], panels[2][band])

    def get_all_panel_numbers(self) -> list:
        """Get list of available panel numbers."""
        return sorted(self.panel_lookup.keys())

    def get_panel_info(self, panel_number: int) -> Optional[Dict]:
        """
        Get comprehensive info for a panel number.

        Args:
            panel_number: Panel identifier

        Returns:
            Dict with panel information
        """
        panels = self.get_reflectance_by_panel_number(panel_number)
        if panels is None:
            return None

        return {
            "panel_number": panel_number,
            "low": panels[0],
            "mid": panels[1],
            "high": panels[2],
            "available_bands": self.BANDS,
        }


reflectance_map = ReflectanceMap()
