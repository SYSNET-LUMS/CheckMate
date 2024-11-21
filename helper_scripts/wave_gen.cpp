#include <iostream>
#include <cmath>
#include <iomanip> // For setting precision

const int N = 8; // Number of samples
int main() {
    double b[N];
    double j = 0.0;

    // Set the precision to display more significant figures
    std::cout << std::fixed << std::setprecision(10);

    // Combine sine waves of different frequencies, amplitudes, and phases
    for (int i = 0; i < N; ++i) {
        b[i] = 3 * sin(2 * M_PI * j / N + M_PI / 6) 
             + 2 * sin(4 * M_PI * j / N + M_PI / 3) 
             + 1.5 * sin(6 * M_PI * j / N + M_PI / 4) 
             + 1 * sin(8 * M_PI * j / N + M_PI / 2) 
             + 2.5 * sin(3 * M_PI * j / N + M_PI / 8) 
             + 2 * sin(5 * M_PI * j / N + M_PI / 10) 
             + 1.2 * sin(7 * M_PI * j / N + M_PI / 12) 
             + 1 * sin(9 * M_PI * j / N);
        
        j += 1.0;
        std::cout << b[i] << ",";
    }
    
    return 0;
}
