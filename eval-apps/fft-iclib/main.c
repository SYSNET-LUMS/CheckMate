#include "my_math.h"
#include <stdint.h>

#ifdef LOCAL_RUN
#include <stdio.h>
#else
#include "support/msp430-support.h"
#endif

#define PI 3.14159265358979323846

struct FFTResults {
    double real[8];
    double imag[8];
};

static struct FFTResults result;


void fft_slow(int* x, double complex* X, unsigned int size_vec) {
    unsigned int n, k;

    // Iterate through, allowing X_K = sum_N of the complex frequencies.
    for (k = 0; k < size_vec; k++) {
        for (n = 0; n < size_vec; n++) {
            X[k] += x[n]
               * cexp(-2 * PI * I * n * k / size_vec)
            ;
        }
    }
}

void fft_radix2(int* x, double complex* X, unsigned int size_vec, unsigned int s) {
    unsigned int k;
    double complex t;

    // At the lowest level pass through (delta T=0 means no phase).
    if (size_vec == 1) {
        X[0] = x[0];
        return;
    }

    // Cooley-Tukey: recursively split in two, then combine beneath.
    fft_radix2(x, X, size_vec/2, 2*s);
    fft_radix2(x+s, X + size_vec/2, size_vec/2, 2*s);

    for (k = 0; k < size_vec/2; k++) {
        t = X[k];
        X[k] = t
         + cexp(-2 * PI * I * k / size_vec) * X[k + size_vec/2]
        ;
        X[k + size_vec/2] = t 
        - cexp(-2 * PI * I * k / size_vec) * X[k + size_vec/2]
        ;
    }
}

void fft(int* x, double complex* X, unsigned int size_vec) {
    fft_radix2(x, X, size_vec, 1);
}

void main()
{
    int b[8] = {0, 1, 0, 0, 0, 0, 0, 0};
    double complex B[8];

    fft(b, B, 8);

    for (int i = 0; i < 8; i++) {
    #ifdef LOCAL_RUN
        printf("%f%+fi\n", creal(B[i]), cimag(B[i]));
    #else
        // put in the results struct
        result.real[i] = creal(B[i]);
        result.imag[i] = cimag(B[i]);
    #endif
    }

    #ifndef LOCAL_RUN
    indicate_end();
    #endif
}