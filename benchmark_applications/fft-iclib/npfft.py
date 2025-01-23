import numpy as np

# Define the input arrays
n = 8
real = np.array([0, 1, 0, 0, 0, 0, 0, 0])
imag = np.zeros(n)  # Imaginary part starts at 0

# Combine real and imaginary parts into a complex array
wave = real + 1j * imag

# Compute the FFT
fft_result = np.fft.fft(wave)

# Print the result
for i, val in enumerate(fft_result):
    print(f"FFT[{i}]: {val.real:.5f} + {val.imag:.5f}j")
