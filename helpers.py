import numpy as np

def get_dct(i, j, N):
    """
    If using with numpy from function, 
    use np.vectorize before use
    help: https://stackoverflow.com/questions/18702105/parameters-to-numpys-fromfunction
    """    
    if i == 0:
        return 1/np.sqrt(N)
    else:
        cos_ = np.cos((i*np.pi*(2*j+1))/(2*N))
        return np.sqrt(2/N) * cos_

QUANTIZATION_MATRIX_50 = [
    [16, 11, 10, 16, 24, 40, 51, 61], 
    [12, 12, 14, 19, 26, 58, 60, 55],
    [14, 13, 16, 24, 40, 57, 69, 56],
    [14, 17, 22, 29, 51, 87, 80, 62],
    [18, 22, 37, 56, 68, 109, 103, 77], 
    [24, 35, 55, 64, 81, 104, 113, 92],
    [49, 64, 78, 87, 103, 121, 120, 101], 
    [72, 92, 95, 98, 112, 100, 103, 99]
]

QUANTIZATION_MATRIX_90 = [
    [3, 2,  2,  3,  5,  8,  10, 12],
    [2, 2,  3,  4,  5,  12, 12, 11],
    [3, 3,  3,  5,  8,  11, 14, 11],
    [3, 3,  4,  6,  10, 17, 16, 12],
    [4, 4,  7,  11, 14, 22, 21, 15],
    [5, 7,  11, 13, 16, 12, 23, 18],
    [10,13, 16, 17, 21, 24, 24, 21],
    [14,18, 19, 20, 22, 20, 20, 20]
]