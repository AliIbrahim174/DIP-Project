import numpy as np

def compute_roi_stats(img: np.ndarray, x1: int, y1: int, x2: int, y2: int):
    """
    Extract ROI and compute comprehensive statistics.
    
    Returns dict with:
      - roi_array: extracted ROI as uint8 2D array
      - hist: 256-bin histogram
      - mean, std, min, max, median: pixel intensity statistics
      - entropy: Shannon entropy
      - area: pixel count in ROI
    """
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
        return {
            'roi_array': roi,
            'hist': hist,
            'mean': 0.0,
            'std': 0.0,
            'min': 0,
            'max': 0,
            'median': 0,
            'entropy': 0.0,
            'area': 0
        }

    # -------------------------
    # Mean (from scratch)
    # -------------------------
    mean = 0.0
    for i in range(256):
        mean += i * hist[i]
    mean /= total

    # -------------------------
    # Variance and Std Dev (from scratch)
    # -------------------------
    variance = 0.0
    for i in range(256):
        variance += ((i - mean) ** 2) * hist[i]
    variance /= total
    std = np.sqrt(variance)

    # -------------------------
    # Min and Max
    # -------------------------
    min_val = np.min(flat)
    max_val = np.max(flat)

    # -------------------------
    # Median (from scratch)
    # -------------------------
    cumsum = 0
    median = 0
    half_total = total // 2
    for i in range(256):
        cumsum += hist[i]
        if cumsum >= half_total:
            median = i
            break

    # -------------------------
    # Entropy (from scratch)
    # -------------------------
    entropy = 0.0
    for i in range(256):
        if hist[i] > 0:
            p = hist[i] / total
            entropy -= p * np.log2(p)

    return {
        'roi_array': roi,
        'hist': hist,
        'mean': mean,
        'std': std,
        'min': int(min_val),
        'max': int(max_val),
        'median': int(median),
        'entropy': entropy,
        'area': total
    }