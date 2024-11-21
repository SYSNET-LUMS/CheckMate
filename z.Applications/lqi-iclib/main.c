#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "struct.h"
#include "communication_trace_A.h"
#include "communication_trace_B.h"
#ifndef LOCAL_RUN
#include "support/msp430-support.h"
#endif


// extern PacketLog communication_trace_A[];
// extern PacketLog communication_trace_B[];
// extern PacketLog communication_trace_C[];

#define VECTOR_SIZE 100 // assuming a maximum size of the vector

double calculateDeliveryRatio(PacketLog logs[], int size)
{
    double total_packets = 0;
    double delivered_weight = 0;
    for (int i = 0; i < size; i++)
    {
        total_packets += 1.0;
        if (logs[i].status == 1)
        {
            delivered_weight += logs[i].weight;
        }
    }
    return (delivered_weight / total_packets);
}

void reverseArray(int arr[], int size) {
    int start = 0;
    int end = size - 1;
    while (start < end) {
        // Swap the elements at start and end
        int temp = arr[start];
        arr[start] = arr[end];
        arr[end] = temp;

        // Move the pointers towards the middle
        start++;
        end--;
    }
}

int main()
{
    double sum = 0;

    double delivery_ratio_A = calculateDeliveryRatio(communication_trace_A, VECTOR_SIZE);
   double delivery_ratio_B = calculateDeliveryRatio(communication_trace_B, VECTOR_SIZE);
   double delivery_ratio_C = calculateDeliveryRatio(communication_trace_A, VECTOR_SIZE);
   delivery_ratio_C = calculateDeliveryRatio(communication_trace_A, VECTOR_SIZE);
   delivery_ratio_C = calculateDeliveryRatio(communication_trace_A, VECTOR_SIZE);
   delivery_ratio_C = calculateDeliveryRatio(communication_trace_B, VECTOR_SIZE);
   delivery_ratio_C = calculateDeliveryRatio(communication_trace_A, VECTOR_SIZE);
   delivery_ratio_C = calculateDeliveryRatio(communication_trace_A, VECTOR_SIZE);
   delivery_ratio_C = calculateDeliveryRatio(communication_trace_A, VECTOR_SIZE);

    sum += (delivery_ratio_A * delivery_ratio_A);
   sum += (delivery_ratio_B * delivery_ratio_B);
   sum += (delivery_ratio_C * delivery_ratio_C);

   sum = sum / 3;

    double rmse = sqrt(sum);

#ifdef LOCAL_RUN
    printf("%.4f\n", rmse);
#else
    indicate_end();
#endif

    return 0;
}
