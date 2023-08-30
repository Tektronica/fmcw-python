import numpy as np
import matplotlib.pyplot as plt

"""
RANGE DETERMINATION OVER ONE CHIRP
"""

# CONSTANTS
c = 3e8  # Speed of light in meters per second
fc = 48e6  # (Hz) carrier frequency

# TARGET PARAMETERS
r = 250  # (m) target range
v = 15  # (m/s) target velocity
rad = 0 * np.pi / 180  # (radians) angle of arrival

# DETECTOR (ADC + Signal Generator)
Nchirp = 512  # sample period of chirp
chirpPeriods = 2  # number of chirp periods in measurement
N = Nchirp * chirpPeriods  # sample period of measurement

# RANGE PARAMETERS
Rmax = 500  # (m) max range
Rres = 2 * Rmax / Nchirp  # (m) range resolution

BW = c / (2 * Rres)  # (Hz) Bandwidth (sets range resolution)
Tchirp = 6 * (2 * Rmax / c)  # (s) chirp period (sweep time)
m_slope = BW / Tchirp  # chirp slope (rise/run)

# VELOCITY CHARACTERISTICS
Vmax = c / (4 * fc * Tchirp)  # (m/s) max detectable velocity
Vres = 2 * Vmax / Nchirp  # (m/s) velocity resolution

# SAMPLING PARAMETERS
f_beat_max = (2 * BW * Rmax) / (c * Tchirp)  # (Hz) sampler rate
fs = 2 * f_beat_max  # (Hz) sampler rate
dt = 1 / fs  # time step

# Generate time vector
t = np.arange(0, chirpPeriods * Tchirp, dt)  # Time of Tx and Rx

# Local Oscillator of the detector
f_tx = fc + m_slope * (t % Tchirp)

# Reflected Signal
time_delay = 2 * r / c
doppler_shift = 2 * v * fc / c
f_rx = fc + m_slope * ((t - time_delay) % Tchirp) - doppler_shift

# Calculate the beat signal (difference between RX and TX frequencies)
f_beat = f_rx - f_tx  # f2(t) - f1(t)

signal_beat = np.cos(2 * np.pi * f_beat * t)

# Perform FFT on the beat signal
fft_result = np.fft.fft(signal_beat)
fft_normalize = 2 * np.abs(fft_result) / len(fft_result)
frequency_bins = np.fft.fftfreq(len(fft_normalize), d=dt)

# convert spectrum to range distance
range_target = np.abs(((c / 2) * (frequency_bins / m_slope)))

# Plot the results
plt.figure(figsize=(10, 8))

plt.subplot(2, 1, 1)
plt.plot(t * 1e6, f_tx * 1e-6, label="TX Signal")
plt.plot(t * 1e6, f_rx * 1e-6, label="RX Signal")
plt.title("FMCW Chirp Frequency")
plt.xlabel("Time (us)")
plt.ylabel("Frequency (MHz)")
plt.legend()

# Plot the FFT results
plt.subplot(2, 1, 2)
plt.plot(range_target, fft_normalize)
plt.xlabel("Range to Target (m)")
plt.ylabel("Amplitude")
plt.title("FFT of Beat Frequency")
text_str = (
    f"{'{:<22}'.format('Max Range:')}{Rmax:.1f} m\n"
    f"{'{:<22}'.format('Range Resolution:')}{Rres:.2f} m\n"
    f"{'{:<22}'.format('Max Velocity:')}{Vmax:.1f} m/s\n"
    f"{'{:<22}'.format('Velocity Resolution:')}{Vres:.1f} m/s"
)
plt.annotate(
    text_str,
    xy=(0.05, 0.95),
    xycoords="axes fraction",
    fontsize=10,
    fontfamily="monospace",
    verticalalignment="top",
)

plt.tight_layout()
plt.savefig("range.png")
plt.show()
