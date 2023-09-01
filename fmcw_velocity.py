import numpy as np
import matplotlib.pyplot as plt

"""
RANGE + VELOCITY DETERMINATION OVER ONE CHIRP
"""

# CONSTANTS
c = 3e8  # Speed of light in meters per second
fc = 77e9  # (Hz) carrier frequency

# TARGET PARAMETERS
r = 250  # (m) target range
v = 15  # (m/s) target velocity
rad = 0 * np.pi / 180  # (radians) angle of arrival

# DETECTOR (ADC + Signal Generator)
Nchirp = 512  # sample period of chirp
chirpPeriods = 64  # number of chirp periods in measurement
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
t_delay = (2 * r) / c
doppler_shift = (2 * v * fc) / c
f_rx = fc + m_slope * ((t - t_delay) % Tchirp) + doppler_shift

# Capture the beat frequency for each successive chirp in measurement window
IF_2DMatrix = np.zeros((chirpPeriods, Nchirp))  # 2D matrix of zeros
tr = np.arange(Nchirp) * dt  # time base

for chirp_index in range(chirpPeriods):
    fbeat = m_slope * t_delay * tr  # beat frequency

    offset = chirp_index * Tchirp  # time offset within the chirp sequence
    doppler_shift = (2 * v / c) * (fc * tr + offset * (fc + m_slope * tr))

    signal_beat = 0.5 * np.cos(2 * np.pi * (fbeat - doppler_shift))

    IF_2DMatrix[chirp_index, :] = signal_beat

# construct Range-Doppler Image from dimmensional FFT
rdm = np.fft.fftshift(np.fft.fft2(IF_2DMatrix, norm="backward"), axes=0)
rangeBin = np.arange(0, Rmax, Rres)
velocityBin = np.arange(-Vmax, Vmax, Vres / 2)

# Plot the results
plt.figure(figsize=(10, 8))

# FREQUENCY SWEEP AS A FUNCTION OF TIME
plt.subplot(2, 1, 1)
plt.plot(t[0: 2 * Nchirp] * 1e6, f_tx[0: 2 * Nchirp] * 1e-9, label="TX Signal")
plt.plot(t[0: 2 * Nchirp] * 1e6, f_rx[0: 2 * Nchirp] * 1e-9, label="RX Signal")
plt.title("FMCW Chirp Frequency")
plt.xlabel("Time (us)")
plt.ylabel("Frequency (GHz)")
plt.legend()

# RANGE FFT OF RAMP AS A FUNCTION OF TIME
chirp0 = rdm[:, : Nchirp // 2][0]

# additional factor of 2 to compensate for half the energy of the original signal
range_normalized = np.abs(chirp0) / np.max(np.abs(chirp0))

plt.subplot(2, 2, 3)
plt.plot(rangeBin, range_normalized)
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
    fontsize=6,
    fontfamily="monospace",
    verticalalignment="top",
)

# RANGE-DOPPLER DATA MAPPED TO IMAGE FRAME
rdm_image = 20 * np.log10(np.abs(rdm[:, : Nchirp // 2]))

plt.subplot(2, 2, 4)
plt.imshow(
    rdm_image,
    cmap="viridis",
    aspect="auto",
    extent=[rangeBin[0], rangeBin[-1], velocityBin[0], velocityBin[-1]],
)

plt.colorbar()  # Add a colorbar for reference
plt.title("Range-Doppler Map (RDM)")
plt.xlabel("Range (m)")
plt.ylabel("Velocity (m/s)")
plt.grid(True)

# PLOT
plt.tight_layout()
plt.savefig("range_doppler_map.png")
plt.show()

# data
print("Number of chirps in image (chirpPeriods):", chirpPeriods)
print("Chirp sample length (Nchirp):", Nchirp)
print("meausrement capture window (N):", N)
print("measurement sample rate (fs):", fs)
print("")
print("Bandwidth:", BW)
print("Range Resolution (m):", Rres)
print("max Range (m):", Rmax)
print("Range Resolution (m):", Rres)
print("max Velcoity (m/s):", Vmax)
print("Velocity Resolution (m/s):", Vres)
