import numpy as np

def compute_roi_stats(img: np.ndarray, x1: int, y1: int, x2: int, y2: int):

    # Ensure correct ordering
    x1, x2 = min(x1, x2), max(x1, x2)
    y1, y2 = min(y1, y2), max(y1, y2)

    # Extract ROI
    roi = img[y1:y2, x1:x2]

    # Convert to grayscale if RGB
    if roi.ndim == 3:
        roi = (
            0.299 * roi[:, :, 0] +
            0.587 * roi[:, :, 1] +
            0.114 * roi[:, :, 2]
        ).astype(np.uint8)

    flat = roi.flatten()

    # -------------------------
    # Histogram (from scratch)
    # -------------------------
    hist = np.zeros(256, dtype=np.int64)

    for px in flat:
        hist[px] += 1

    total = len(flat)

    if total == 0:
        return hist, 0.0, 0.0

    # -------------------------
    # Mean (from scratch)
    # -------------------------
    mean = 0.0
    for i in range(256):
        mean += i * hist[i]
    mean /= total

    # -------------------------
    # Variance (from scratch)
    # -------------------------
    variance = 0.0
    for i in range(256):
        variance += ((i - mean) ** 2) * hist[i]
    variance /= total

    return hist, mean, variance