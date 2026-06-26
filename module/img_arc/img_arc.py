"""
Description: Do not edit
Author: HuPengcheng
Date: 2026-05-30 14:46:53
LastEditors: HuPengcheng hpc0813@outlook.com
LastEditTime: 2026-05-30 14:51:00
FilePath: /imgocr/module/img-arc/img_arc.py
"""

import os
import subprocess
from typing import Optional, Tuple

import cv2
import exiftool
import numpy as np
from osgeo import gdal, gdal_array


def get_normalized_params(bit_num=16):
    """normalized raw pixel value range: 0~(2^bit_num - 1)"""
    max_val = 2**bit_num
    return max_val


def black_level_correction(
    img: np.ndarray, bit_num: int = 16, black_level: int = 3200
) -> np.ndarray:
    """
    normalized black level value: DN_corrected = DN_raw - black_level (bitnum:16, black_level:3200)
    """
    max_val = get_normalized_params(bit_num)
    img_norm = img.astype(np.float32) / max_val
    bl_norm = black_level / max_val
    img_out = np.maximum(img_norm - bl_norm, 0.0)
    return img_out


def exposure_gain_normalization(
    img: np.ndarray, sensor_gain: float, exposure_time_us: int
) -> np.ndarray:
    """
    exposure and gain normalization: Camera = (I - BlackLevel) / (SensorGain × ExposureTime / 1e6)
    exposure_time_us: microseconds -> divide by 1e6 to convert to seconds
    """
    exp_s = exposure_time_us / 1_000_000.0
    img_normalized = img / (sensor_gain * exp_s)
    return img_normalized


def vignetting_correction(
    img: np.ndarray,
    center_x: float,
    center_y: float,
    vignetting_coeffs: list,  # [k0, k1, k2, k3, k4, k5] 来自XMP
) -> np.ndarray:
    """
    Vignetting Correction: I_corrected = I_original × (k5·r⁶ + k4·r⁵ + ... + k0·r + 1.0)
    """
    h, w = img.shape[:2]
    x = np.arange(w, dtype=np.float32)
    y = np.arange(h, dtype=np.float32)
    xx, yy = np.meshgrid(x, y)

    dx = xx - center_x
    dy = yy - center_y
    r = np.sqrt(dx**2 + dy**2)

    k0, k1, k2, k3, k4, k5 = vignetting_coeffs
    factor = (
        k5 * (r**6)
        + k4 * (r**5)
        + k3 * (r**4)
        + k2 * (r**3)
        + k1 * (r**2)
        + k0 * r
        + 1.0
    )

    img_vign = img * factor
    return img_vign


def distortion_correction(
    img: np.ndarray,
    fx: float,
    fy: float,
    cx: float,
    cy: float,
    k1: float,
    k2: float,
    p1: float,
    p2: float,
    k3: float,
) -> np.ndarray:
    """Distortion correction"""
    h, w = img.shape[:2]
    camera_matrix = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]], dtype=np.float32)
    dist_coeffs = np.array([k1, k2, p1, p2, k3], dtype=np.float32)
    img_undist = cv2.undistort(img, camera_matrix, dist_coeffs, None, camera_matrix)
    return img_undist


def band_alignment(img: np.ndarray, h_matrix: np.ndarray) -> np.ndarray:
    """
    Calibrated HMatrix correction for band alignment: img_aligned = warpPerspective(img, 3x3 HMatrix)
    h_matrix: 3×3 np.array
    """
    h, w = img.shape[:2]
    img_aligned = cv2.warpPerspective(img, h_matrix, (w, h))
    return img_aligned


def to_relative_reflectance(
    img: np.ndarray,
    irradiance: float,
    p_cam: float,
) -> np.ndarray:
    """
    absolute reflectance = (Camera / Irradiance) * pCam
    """
    reflectance = (img / irradiance) * p_cam
    reflectance = np.clip(reflectance, 0.0, 1.0)
    return reflectance


def to_radiance(
    file_path: str,
    output_dir: Optional[str] = None,
) -> float:
    """
    radiometric_correction: 0~1 absolute reflectance
    """
    output_path = (
        os.path.join(output_dir, os.path.basename(file_path))
        if output_dir
        else file_path
    )
    img_raw = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
    if img_raw is None:
        raise FileNotFoundError(f"图片读取失败，请检查路径：{file_path}")
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
                # "DewarpData",
                "CalibratedHMatrix",
                "Irradiance",
                # "SensorGainAdjustment",
            ],
        )

    exif = metadata[0]
    # EXIF: BitsPerSample
    bit_num = int(exif.get("EXIF:BitsPerSample"))
    # Xmp.drone-dji.BlackLevel
    black_level = int(exif.get("XMP:BlackLevel"))
    # Xmp.drone-dji.ExposureTime (微秒)
    exposure_time_us = int(exif.get("XMP:ExposureTime"))
    # Xmp.drone-dji.SensorGain
    sensor_gain = float(exif.get("XMP:SensorGain"))
    # Xmp.drone-dji.SensorGainAdjustment
    # p_cam = float(exif.get("XMP:SensorGainAdjustment"))

    center_x = float(exif.get("XMP:CalibratedOpticalCenterX"))
    center_y = float(exif.get("XMP:CalibratedOpticalCenterY"))
    # Xmp.drone-dji.VignettingData
    vign_str = exif.get("XMP:VignettingData")
    vignetting_coeffs = [float(v) for v in vign_str.split(",")]
    # DewarpData格式：date;fx,fy,cx,cy,k1,k2,p1,p2,k3
    # dewarp_str = exif.get("XMP:DewarpData")
    # dewarp_parts = dewarp_str.split(";")[-1].split(",")
    # fx = float(dewarp_parts[0])
    # fy = float(dewarp_parts[1])
    # cx = float(dewarp_parts[2])
    # cy = float(dewarp_parts[3])
    # k1 = float(dewarp_parts[4])
    # k2 = float(dewarp_parts[5])
    # p1 = float(dewarp_parts[6])
    # p2 = float(dewarp_parts[7])
    # k3 = float(dewarp_parts[8])

    h_str = exif.get("XMP:CalibratedHMatrix")
    h_vals = [float(v) for v in h_str.split(",")]
    h_matrix = np.array(h_vals).reshape(3, 3)

    irradiance = float(exif.get("XMP:Irradiance"))

    # 1 暗电平
    img = black_level_correction(img=img_raw, black_level=black_level, bit_num=bit_num)

    # 2 曝光+增益
    img = exposure_gain_normalization(
        img=img, sensor_gain=sensor_gain, exposure_time_us=exposure_time_us
    )

    # 3 渐晕
    img = vignetting_correction(
        img=img,
        center_x=center_x,
        center_y=center_y,
        vignetting_coeffs=vignetting_coeffs,
    )

    # # 4 畸变校正
    # img = distortion_correction(
    #     img=img, fx=fx, fy=fy, cx=cx, cy=cy, k1=k1, k2=k2, p1=p1, p2=p2, k3=k3
    # )

    # 5 波段配准（可选）
    if h_matrix is not None:
        img = band_alignment(img=img, h_matrix=h_matrix)

    cv2.imwrite(output_path, img)

    # with exiftool.ExifToolHelper() as et:
    #     et.execute(
    #         *[
    #             "-TagsFromFile",
    #             file_path,
    #             "-all:all",
    #             "-overwrite_original",
    #             output_path,
    #         ]
    #     )
    return irradiance


def to_relative_radiance_by_cam(
    file_path: str,
    output_dir: Optional[str] = None,
) -> None:
    """
    radiometric_correction: 0~1 absolute reflectance
    """
    output_path = (
        os.path.join(output_dir, os.path.basename(file_path))
        if output_dir
        else file_path
    )
    img_raw = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
    if img_raw is None:
        raise FileNotFoundError(f"图片读取失败，请检查路径：{file_path}")
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
    exif = metadata[0]
    # EXIF: BitsPerSample
    bit_num = int(exif.get("EXIF:BitsPerSample"))
    # Xmp.drone-dji.BlackLevel
    black_level = int(exif.get("XMP:BlackLevel"))
    # Xmp.drone-dji.ExposureTime (微秒)
    exposure_time_us = int(exif.get("XMP:ExposureTime"))
    # Xmp.drone-dji.SensorGain
    sensor_gain = float(exif.get("XMP:SensorGain"))
    # Xmp.drone-dji.SensorGainAdjustment
    p_cam = float(exif.get("XMP:SensorGainAdjustment"))

    center_x = float(exif.get("XMP:CalibratedOpticalCenterX"))
    center_y = float(exif.get("XMP:CalibratedOpticalCenterY"))
    # Xmp.drone-dji.VignettingData
    vign_str = exif.get("XMP:VignettingData")
    vignetting_coeffs = [float(v) for v in vign_str.split(",")]
    # DewarpData格式：date;fx,fy,cx,cy,k1,k2,p1,p2,k3
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

    h_str = exif.get("XMP:CalibratedHMatrix")
    h_vals = [float(v) for v in h_str.split(",")]
    h_matrix = np.array(h_vals).reshape(3, 3)

    irradiance = float(exif.get("XMP:Irradiance"))

    # 1 暗电平
    img = black_level_correction(img=img_raw, black_level=black_level, bit_num=bit_num)

    # 2 曝光+增益
    img = exposure_gain_normalization(
        img=img, sensor_gain=sensor_gain, exposure_time_us=exposure_time_us
    )

    # 3 渐晕
    img = vignetting_correction(
        img=img,
        center_x=center_x,
        center_y=center_y,
        vignetting_coeffs=vignetting_coeffs,
    )

    # # 4 畸变校正
    # img = distortion_correction(
    #     img=img, fx=fx, fy=fy, cx=cx, cy=cy, k1=k1, k2=k2, p1=p1, p2=p2, k3=k3
    # )

    # 5 波段配准（可选）
    if h_matrix is not None:
        img = band_alignment(img=img, h_matrix=h_matrix)

    # 6 转相对反射率
    reflectance = to_relative_reflectance(img=img, irradiance=irradiance, p_cam=p_cam)

    cv2.imwrite(output_path, reflectance)

    with exiftool.ExifToolHelper() as et:
        et.execute(
            *[
                "-TagsFromFile",
                file_path,
                "-all:all",
                "-overwrite_original",
                output_path,
            ]
        )


def to_absolute_radiance_by_panel(
    file_path: str,
    reflectance_function: Tuple[float, float, float, float],
    output_dir: Optional[str] = None,
) -> None:
    """
    absolute_radiometric_correction: 0~1 absolute reflectance
    """
    output_path = (
        os.path.join(output_dir, os.path.basename(file_path))
        if output_dir
        else file_path
    )
    # img_raw = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
    src_ds = gdal.Open(file_path, gdal.GA_ReadOnly)
    if src_ds is None:
        raise FileNotFoundError(f"图片读取失败，请检查路径：{file_path}")
    img_raw = gdal_array.DatasetReadAsArray(src_ds)  # type: ignore

    if img_raw is None:
        raise FileNotFoundError(f"图片读取失败，请检查路径：{file_path}")
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
                # "DewarpData",
                "CalibratedHMatrix",
                "Irradiance",
                # "SensorGainAdjustment",
            ],
        )
    exif = metadata[0]
    # EXIF: BitsPerSample
    bit_num = int(exif.get("EXIF:BitsPerSample"))
    # Xmp.drone-dji.BlackLevel
    black_level = int(exif.get("XMP:BlackLevel"))
    # Xmp.drone-dji.ExposureTime (微秒)
    exposure_time_us = int(exif.get("XMP:ExposureTime"))
    # Xmp.drone-dji.SensorGain
    sensor_gain = float(exif.get("XMP:SensorGain"))
    # Xmp.drone-dji.SensorGainAdjustment
    # p_cam = float(exif.get("XMP:SensorGainAdjustment"))

    center_x = float(exif.get("XMP:CalibratedOpticalCenterX"))
    center_y = float(exif.get("XMP:CalibratedOpticalCenterY"))
    # Xmp.drone-dji.VignettingData
    vign_str = exif.get("XMP:VignettingData")
    vignetting_coeffs = [float(v) for v in vign_str.split(",")]
    # DewarpData格式：date;fx,fy,cx,cy,k1,k2,p1,p2,k3
    # dewarp_str = exif.get("XMP:DewarpData")
    # dewarp_parts = dewarp_str.split(";")[-1].split(",")
    # fx = float(dewarp_parts[0])
    # fy = float(dewarp_parts[1])
    # cx = float(dewarp_parts[2])
    # cy = float(dewarp_parts[3])
    # k1 = float(dewarp_parts[4])
    # k2 = float(dewarp_parts[5])
    # p1 = float(dewarp_parts[6])
    # p2 = float(dewarp_parts[7])
    # k3 = float(dewarp_parts[8])

    h_str = exif.get("XMP:CalibratedHMatrix")
    h_vals = [float(v) for v in h_str.split(",")]
    h_matrix = np.array(h_vals).reshape(3, 3)

    irradiance = float(exif.get("XMP:Irradiance"))

    # 1 暗电平
    img = black_level_correction(img=img_raw, black_level=black_level, bit_num=bit_num)

    # 2 曝光+增益
    img = exposure_gain_normalization(
        img=img, sensor_gain=sensor_gain, exposure_time_us=exposure_time_us
    )

    # 3 渐晕
    img = vignetting_correction(
        img=img,
        center_x=center_x,
        center_y=center_y,
        vignetting_coeffs=vignetting_coeffs,
    )

    # # 4 畸变校正
    # img = distortion_correction(
    #     img=img, fx=fx, fy=fy, cx=cx, cy=cy, k1=k1, k2=k2, p1=p1, p2=p2, k3=k3
    # )

    # 5 波段配准（可选）
    if h_matrix is not None:
        img = band_alignment(img=img, h_matrix=h_matrix)

    # 6 转绝对反射率
    k, b, _, panel_irradiance = reflectance_function
    ref = img * panel_irradiance / irradiance * k + b
    # ref = np.clip(ref, 0, 1)
    # ref = ref.astype(np.float32)
    ref = np.round(ref * 65535.0).astype(np.uint16)
    # cv2.imwrite(output_path, ref.astype(np.float32))
    driver = gdal.GetDriverByName("GTiff")
    x_size = src_ds.RasterXSize
    y_size = src_ds.RasterYSize

    dst_ds = driver.Create(output_path, x_size, y_size, 1, gdal.GDT_UInt16)
    dst_ds.SetGeoTransform(src_ds.GetGeoTransform())
    dst_ds.SetProjection(src_ds.GetProjection())
    meta_domains = src_ds.GetMetadataDomainList()
    for domain in meta_domains:
        meta_dict = src_ds.GetMetadata(domain)
        dst_ds.SetMetadata(meta_dict, domain)

    band = dst_ds.GetRasterBand(1)
    band.WriteArray(ref)

    # band.SetNoDataValue(0.0)  # 你图像0为背景
    # dst_ds.SetMetadataItem("COMPRESSION", "DEFLATE", "IMAGE_STRUCTURE")

    dst_ds.FlushCache()
    src_ds = None
    dst_ds = None

    cmd = [
        "exiftool",
        "-tagsfromfile",
        file_path,
        "-all:all",
        "-preserve",
        "-overwrite_original_in_place",
        output_path,
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
