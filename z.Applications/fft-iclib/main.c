#include "my_math.h"
#include <stdint.h>

#ifdef LOCAL_RUN
#include <stdio.h>
#else
#include "support/msp430-support.h"
#endif

#define PI 3.14159265358979323846
#define MAX_SIZE 8
struct FFTResults {
    double real[MAX_SIZE];
    double imag[MAX_SIZE];
};

static struct FFTResults result;

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

void main()
{
    int b[MAX_SIZE] = {7.1780364031,6.6925374084,0.0871675457,-1.6200835333,-0.3953061544,-3.9308192744,-1.1998727187,-0.1670252324};
    double complex B[MAX_SIZE];

    fft_radix2(b, B, MAX_SIZE, 1);

    for (int i = 0; i < MAX_SIZE; i++) {
    #ifdef LOCAL_RUN
        printf("%f,%f\n", creal(B[i]), cimag(B[i]));
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

double exp(double x) {
    double result = 1.0;
    double term = 1.0;
    int n = 1;

    // Taylor series: e^x = 1 + x + x^2/2! + x^3/3! + ...
    for (int i = 1; i <= 4; i++) {
        term *= x / n;  // term = x^n / n!
        result += term;
        n++;
    }

    return result;
}

double sin(double x) {
    double term = x;    // First term
    double sum = x;     // sin(x) starts with x
    int n = 3;          // Start from x^3

    for (int i = 1; i < 7; i++) {
        term *= -x * x / (n * (n - 1));  // Update term (-1)^i * x^(2i+1) / (2i+1)!
        sum += term;
        n += 2;
    }

    return sum;
}

double cos(double x) {
    double term = 1.0;  // First term
    double sum = 1.0;   // cos(x) starts with 1
    int n = 2;          // Start from x^2

    for (int i = 1; i < 7; i++) {
        term *= -x * x / (n * (n - 1));  // Update term (-1)^i * x^(2i) / (2i)!
        sum += term;
        n += 2;
    }

    return sum;
}

double complex cexp(double complex z)
{
	double complex w;
	double r, x, y;

	x = creal(z);
	y = cimag(z);
	r = exp(x);
	w = r * cos(y) + r * sin(y) * I;
	return w;
}