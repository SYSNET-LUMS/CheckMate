#include <complex.h>

double exp(double x) {
    double result = 1.0;
    double term = 1.0;
    int n = 1;

    // Taylor series: e^x = 1 + x + x^2/2! + x^3/3! + ...
    for (int i = 1; i <= 20; i++) {
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

    for (int i = 1; i < 20; i++) {
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

    for (int i = 1; i < 20; i++) {
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