"""
Description: Do not edit
Author: HuPengcheng
Date: 2026-05-30 15:47:21
LastEditors: HuPengcheng hpc0813@outlook.com
LastEditTime: 2026-05-30 19:00:02
FilePath: /img-rc/test/test_arc.py
"""

import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)


def test_read_single_exif_metadata():
    """Test EXIF metadata reading functionality"""
    import exiftool

    file_path = "./data/cd/DJI_20260423090852_0001_MS_G.TIF"

    with exiftool.ExifToolHelper() as et:
        metadata = et.get_metadata(file_path)
        for d in metadata:
            print(f"{d['SourceFile']:>20.20} {d['EXIF:DateTimeOriginal']:>20.20}")


def test_read_multi_exif_metadata():
    """Test EXIF metadata reading functionality"""
    import exiftool
    import numpy as np

    file_path = ["./data/cd/DJI_20260423090852_0001_MS_G.TIF"]

    with exiftool.ExifToolHelper() as et:
        metadata = et.get_tags(
            file_path,
            tags=[
                "BitsPerSample",
                "BlackLevel",
                "SensorGain",
                "ExposureTime",
                "CalibratedOpticalCenterX",
                "CalibratedOpticalCenterY",
                "VignettingData",
                "DewarpData",
                "CalibratedHMatrix",
                "Irradiance",
                "SensorGainAdjustment",
            ],
        )
        for exif in metadata:

            # EXIF: BitsPerSample
            bit_num = int(exif.get("EXIF:BitsPerSample"))
            # Xmp.drone-dji.BlackLevel
            black_level = int(exif.get("XMP:BlackLevel"))
            # Xmp.drone-dji.ExposureTime (microseconds)
            exposure_time_us = int(exif.get("XMP:ExposureTime"))
            # Xmp.drone-dji.SensorGain
            sensor_gain = float(exif.get("XMP:SensorGain"))
            # Xmp.drone-dji.SensorGainAdjustment
            p_cam = float(exif.get("XMP:SensorGainAdjustment"))
            # Xmp.drone-dji.CalibratedOpticalCenterX
            center_x = float(exif.get("XMP:CalibratedOpticalCenterX"))
            center_y = float(exif.get("XMP:CalibratedOpticalCenterY"))
            # Xmp.drone-dji.VignettingData
            vign_str = exif.get("XMP:VignettingData")
            vignetting_coeffs = [float(v) for v in vign_str.split(",")]
            # DewarpData format: date;fx,fy,cx,cy,k1,k2,p1,p2,k3
            dewarp_str = exif.get("XMP:DewarpData")
            dewarp_parts = dewarp_str.split(";")[-1].split(",")
            fx = float(dewarp_parts[0])
            fy = float(dewarp_parts[1])
            cx = float(dewarp_parts[2])
            cy = float(dewarp_parts[3])
            k1 = float(dewarp_parts[4])
            k2 = float(dewarp_parts[5])
            p1 = float(dewarp_parts[6])
            p2 = float(dewarp_parts[7])
            k3 = float(dewarp_parts[8])
            # Xmp.drone-dji.CalibratedHMatrix
            h_str = exif.get("XMP:CalibratedHMatrix")
            h_vals = [float(v) for v in h_str.split(",")]
            h_matrix = np.array(h_vals).reshape(3, 3)
            # Xmp.drone-dji.Irradiance
            irradiance = float(exif.get("XMP:Irradiance"))

            return {
                "bit_num": bit_num,
                "black_level": black_level,
                "sensor_gain": sensor_gain,
                "exposure_time_us": exposure_time_us,
                "center_x": center_x,
                "center_y": center_y,
                "vignetting_coeffs": vignetting_coeffs,
                "fx": fx,
                "fy": fy,
                "cx": cx,
                "cy": cy,
                "k1": k1,
                "k2": k2,
                "p1": p1,
                "p2": p2,
                "k3": k3,
                "h_matrix": h_matrix,
                "irradiance": irradiance,
                "p_cam": p_cam,
            }


def test_copy_exif_metadata():
    """Test EXIF metadata copying functionality"""

    import cv2
    import exiftool

    output_path = "./data/cd/DJI_20260423090852_0001_MS_G.TIF"
    exif_file_path = "./data/Henan Zhoukou Wheat—20260423—80m—Original Image—CD/DJI_20260423090852_0001_MS_G.TIF"
    img_path = "./data/cd/DJI_20260423090852_0001_MS_G_1.TIF"
    with exiftool.ExifToolHelper() as et:
        et.execute(
            *[
                "-TagsFromFile",
                exif_file_path,
                "-all:all",
                "-overwrite_original",
                img_path,
            ]
        )
    img = cv2.imread(img_path)
    # Overwrite pixels: at this point output_file has complete metadata, imwrite won't clear it
    cv2.imwrite(output_path, img)
