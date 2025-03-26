import numpy as np
import scipy.signal

def compute_lf_hf(rr_intervals):
    """Computes LF, HF, and LF/HF ratio from RR intervals using FFT"""
    
    if len(rr_intervals) < 30:
        return None, None, None  # Not enough data

    # Convert RR intervals to seconds
    rr_intervals = np.array(rr_intervals) / 1000.0  # Convert ms → sec

    # Interpolation to 4Hz (needed for FFT)
    time_stamps = np.cumsum(rr_intervals) - rr_intervals[0]  # Time series
    resampled_time = np.linspace(time_stamps[0], time_stamps[-1], len(rr_intervals) * 4)
    rr_interpolated = np.interp(resampled_time, time_stamps, rr_intervals)

    # Apply Fast Fourier Transform (FFT) for frequency analysis
    freqs, power_spectrum = scipy.signal.welch(rr_interpolated, fs=4.0, nperseg=len(rr_interpolated))

    # Integrate power in LF (0.04–0.15 Hz) and HF (0.15–0.4 Hz) bands
    lf_band = (freqs >= 0.04) & (freqs <= 0.15)
    hf_band = (freqs > 0.15) & (freqs <= 0.4)

    lf_power = np.trapz(power_spectrum[lf_band], freqs[lf_band])
    hf_power = np.trapz(power_spectrum[hf_band], freqs[hf_band])

    # Compute LF/HF ratio
    lf_hf_ratio = lf_power / hf_power if hf_power > 0 else None

    return lf_power, hf_power, lf_hf_ratio
