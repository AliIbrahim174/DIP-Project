import numpy as np
import time

# -------------------------------
# Simple Linear Congruential Generator (LCG)
# -------------------------------
class SimpleRNG:
    def __init__(self, seed=None):
        if seed is None:
            seed = int(time.time()) % 2**31
        self.state = seed

    def rand(self):
        self.state = (1103515245 * self.state + 12345) % (2**31)
        return self.state / (2**31)

    def rand_uniform(self, low=0.0, high=1.0):
        return low + (high - low) * self.rand()


# -------------------------------
# Box-Muller Gaussian
# -------------------------------
def box_muller(rng):
    u1 = max(rng.rand(), 1e-10)
    u2 = rng.rand()

    return (-2.0 * np.log(u1)) ** 0.5 * np.cos(2 * np.pi * u2)


# -------------------------------
# Gaussian Noise (from scratch)
# -------------------------------
def inject_gaussian_noise(img, mean=0.0, std=25.0):
    rng = SimpleRNG()

    h, w = img.shape[:2]
    noisy = np.zeros_like(img, dtype=np.float32)

    for i in range(h):
        for j in range(w):
            noise = box_muller(rng) * std + mean

            if img.ndim == 2:
                noisy[i, j] = img[i, j] + noise
            else:
                noisy[i, j, 0] = img[i, j, 0] + noise
                noisy[i, j, 1] = img[i, j, 1] + noise
                noisy[i, j, 2] = img[i, j, 2] + noise

    return np.clip(noisy, 0, 255).astype(np.uint8)


# -------------------------------
# Uniform Noise (from scratch)
# -------------------------------
def inject_uniform_noise(img, low=-40.0, high=40.0):
    rng = SimpleRNG()

    h, w = img.shape[:2]
    noisy = np.zeros_like(img, dtype=np.float32)

    for i in range(h):
        for j in range(w):
            noise = rng.rand_uniform(low, high)

            if img.ndim == 2:
                noisy[i, j] = img[i, j] + noise
            else:
                noisy[i, j, 0] = img[i, j, 0] + noise
                noisy[i, j, 1] = img[i, j, 1] + noise
                noisy[i, j, 2] = img[i, j, 2] + noise

    return np.clip(noisy, 0, 255).astype(np.uint8)