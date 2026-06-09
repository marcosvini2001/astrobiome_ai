#!/usr/bin/env python3
"""
Visão computacional headless para detecção de estresse foliar em plantas.
Dependências: opencv-python, numpy
"""

import os

import cv2
import numpy as np

IMAGE_PATH = os.path.join(os.path.dirname(__file__), "plant_sample.jpg")

# Ranges HSV (H: 0-179, S: 0-255, V: 0-255 no OpenCV)
HSV_CHLOROTIC_LOW  = np.array([15, 40, 40],  dtype=np.uint8)
HSV_CHLOROTIC_HIGH = np.array([35, 255, 255], dtype=np.uint8)

HSV_HEALTHY_LOW    = np.array([35, 40, 40],  dtype=np.uint8)
HSV_HEALTHY_HIGH   = np.array([85, 255, 255], dtype=np.uint8)


def analyze_plant_image(image_path: str) -> dict:
    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        raise FileNotFoundError(f"Imagem não encontrada: {image_path}")

    total_pixels = img_bgr.shape[0] * img_bgr.shape[1]

    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

    mask_chlorotic = cv2.inRange(hsv, HSV_CHLOROTIC_LOW, HSV_CHLOROTIC_HIGH)
    mask_healthy   = cv2.inRange(hsv, HSV_HEALTHY_LOW,   HSV_HEALTHY_HIGH)

    chlorotic_px = int(cv2.countNonZero(mask_chlorotic))
    healthy_px   = int(cv2.countNonZero(mask_healthy))

    chlorotic_pct = round(chlorotic_px / total_pixels * 100, 2)
    healthy_pct   = round(healthy_px   / total_pixels * 100, 2)

    # NDVI proxy: razão de pixels saudáveis sobre tecido fotossintético detectado,
    # normalizado para o intervalo [0.3, 0.9]
    raw_ratio = healthy_pct / (healthy_pct + chlorotic_pct + 0.001)
    ndvi_proxy = round(0.3 + raw_ratio * 0.6, 3)

    if chlorotic_pct > 20:
        stress_level = "CRITICO"
    elif chlorotic_pct > 10:
        stress_level = "ALTO"
    elif chlorotic_pct > 5:
        stress_level = "MODERADO"
    else:
        stress_level = "NORMAL"

    return {
        "chlorotic_pct": chlorotic_pct,
        "healthy_pct": healthy_pct,
        "ndvi_proxy": ndvi_proxy,
        "stress_level": stress_level,
        "chlorotic_pixels": chlorotic_px,
        "healthy_pixels": healthy_px,
        "total_pixels": total_pixels,
    }


if __name__ == "__main__":
    print("=" * 50)
    print("ASTROBIOME AI — CV Plant Stress Analyzer")
    print("=" * 50)
    print(f"Imagem: {IMAGE_PATH}\n")

    try:
        result = analyze_plant_image(IMAGE_PATH)
    except FileNotFoundError as e:
        print(f"ERRO: {e}")
        print("Coloque uma imagem em simulator/plant_sample.jpg e tente novamente.")
        raise SystemExit(1)

    print(f"Pixels totais       : {result['total_pixels']:,}")
    print(f"Pixels saudáveis    : {result['healthy_pixels']:,}  ({result['healthy_pct']}%)")
    print(f"Pixels cloróticos   : {result['chlorotic_pixels']:,}  ({result['chlorotic_pct']}%)")
    print(f"NDVI proxy          : {result['ndvi_proxy']}")
    print(f"Nível de estresse   : {result['stress_level']}")
    print("=" * 50)
