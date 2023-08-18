import numpy as np
import matplotlib.pyplot as plt

"""
RANGE + VELOCITY DETERMINATION OVER ONE CHIRP
"""

# CONSTANTS
c = 3e8  # Speed of light in meters per second

# TARGET PARAMETERS
r = 250  # (m) target range
v = 35  # (m/s) target velocity
rad = 0 * np.pi / 180  # (radians) angle of arrival

# RANGE PARAMETERS
Rmax = 500  # (m) max range

# DETECTOR (ADC + Signal Generator)
chirpPeriods = 64
Nchirp = 512
N = chirpPeriods * Nchirp  # sample period of measurement
BW = Nchirp * (c / (4 * Rmax))  # (Hz) Bandwidth (sets range resolution)

# SIGNAL PARAMETERS
fc = 77e9  # (Hz) carrier frequency
lambda_val = c / fc  # Radar wavelength
Tchirp = 6 * (2 * Rmax / c)  # (s) chirp period (sweep time)
f_slope = BW / Tchirp  # chirp slope (rise/run)

# DETECTOR CHARACTERISTICS
Rres = c / (2 * BW)  # (m) range resolution
Vmax = lambda_val / (4 * Tchirp)  # (m/s) max detectable velocity
Vres = 2 * Vmax / Nchirp  # (m/s) velocity resolution

# SAMPLING PARAMETERS
f_beat_max = (2 * BW * Rmax) / (c * Tchirp)  # (Hz) sampler rate
fs = 2 * f_beat_max  # (Hz) sampler rate
dt = 1 / fs  # time step

# Generate time vector
t = np.arange(0, chirpPeriods * Tchirp, dt)  # Time of Tx and Rx

# Local Oscillator of the detector
f_tx = fc + f_slope * (t % Tchirp)

# Reflected Signal
time_delay = (2 * r) / c
doppler_shift = (2 * v * fc) / c
f_rx = fc + f_slope * ((t - time_delay) % Tchirp) + doppler_shift

# Capture the beat frequency for each successive chirp in measurement window
IF_2DMatrix = np.zeros((chirpPeriods, Nchirp))
td = np.arange(Nchirp) / fs

for chirp_index in range(chirpPeriods):
    # left = chirp_index * Nchirp
    # right = left + Nchirp

    # # Perform the subtraction for the current interval
    # f_beat = f_tx[left:right] - f_rx[left:right]
    # signal_beat = np.cos(2 * np.pi * f_beat * t[left:right])

    #    a = (-2*pi*fc*2*V*i*tm/c ...    %phase shift
    #          -2*pi*(2*V*(fc+i*bw)/c + sweep_slope*td)*t);   %frequency
    step = chirp_index * Tchirp
    phase_shift = step * doppler_shift
    frequency_shift = step + (f_slope * time_delay) + phase_shift

    signal_beat = 0.5 * np.cos(-2*np.pi*(frequency_shift * td + phase_shift))

    IF_2DMatrix[chirp_index, :] = signal_beat

# construct Range-Doppler Image from dimmensional FFT
rdm = np.fft.fftshift(np.fft.fft2(IF_2DMatrix), axes=0)

rangeBin = np.arange(0, Rmax, Rres)
velocityBin = np.arange(-Vmax, Vmax, Vres/2)

# Plot the results
plt.figure(figsize=(10, 8))

# FREQUENCY SWEEP AS A FUNCTION OF TIME
plt.subplot(2, 1, 1)
plt.plot(t[0:  2*Nchirp] * 1e6, f_tx[0:  2*Nchirp] * 1e-9, label="TX Signal")
plt.plot(t[0:  2*Nchirp] * 1e6, f_rx[0:  2*Nchirp] * 1e-9, label="RX Signal")
plt.title("FMCW Chirp Frequency")
plt.xlabel("Time (us)")
plt.ylabel("Frequency (GHz)")
plt.legend()

# RANGE FFT OF  RAMP AS A FUNCTION OF TIME
chirp0 = rdm[0]
range_normalized = 2 * np.abs(chirp0) / len(chirp0)

plt.subplot(2, 2, 3)
plt.plot(rangeBin[0: Nchirp // 2], range_normalized[0: Nchirp // 2])
plt.xlabel("Range to Target (m)")
plt.ylabel("Amplitude")
plt.title("FFT of Beat Frequency")

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
plt.show()

# data
print("Number of chirps in image (chirpPeriods):", chirpPeriods)
print("Chirp sample length (Nchirp):", Nchirp)
print("meausrement capture window (N):", N)
print("measurement sample rate (fs):", fs)
print("")
print("Range Resolution (m):", Rres)
print("max Range (m):", Rmax)
print("Range Resolution (m):", Rres)
print("max Velcoity (m/s):", Vmax)
print("Velocity Resolution (m/s):", Vres)
