/* sobel.c */
#ifdef LOCAL_RUN
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#endif

#include <float.h>

#include "image_data.h"

/* Constant declaration */
#define MAX_BRIGHTNESS  255 /* Maximum gray level */
#define GRAYLEVEL       256 /* No. of gray levels */
#define MAX_FILENAME    256 /* Filename length limit */
#define MAX_BUFFERSIZE  256

// output image data
unsigned char image2[MAX_IMAGESIZE][MAX_IMAGESIZE];
int x_size2, y_size2;

#ifdef LOCAL_RUN
void save_image_data( )
/* Output of image2[ ][ ], x_size2, y_size2 in pgm format*/     
{
  char *file_name = "img.pgm";
  FILE *fp; /* File pointer */
  int x, y; /* Loop variable */
  
  /* Output file open */
  printf("-----------------------------------------------------\n");
  printf("Monochromatic image file output routine\n");
  printf("-----------------------------------------------------\n\n");
  fp = fopen(file_name, "wb");
  /* output of pgm file header information */
  fputs("P5\n", fp);
  fputs("# Created by Image Processing\n", fp);
  fprintf(fp, "%d %d\n", x_size2, y_size2);
  fprintf(fp, "%d\n", MAX_BRIGHTNESS);
  /* Output of image data */
  for (y = 0; y < y_size2; y++) {
    for (x = 0; x < x_size2; x++) {
      fputc((image2[y][x]), fp);
    }
  }
  printf("\n-----Image data output OK-----\n\n");
  printf("-----------------------------------------------------\n\n");
  fclose(fp);
}
#endif

void sobel_filtering( )
     /* Spatial filtering of image data */
     /* Sobel filter (horizontal differentiation */
     /* Input: image1[y][x] ---- Outout: image2[y][x] */
{
  /* Definition of Sobel filter in horizontal direction */
  int weight[3][3] = {{ -1,  0,  1 },
		      { -2,  0,  2 },
		      { -1,  0,  1 }};
  double pixel_value;
  double min, max;
  int x, y, i, j;  /* Loop variable */

  min = DBL_MAX;
  max = -DBL_MAX;
  for (y = 1; y < y_size1 - 1; y++) {
    for (x = 1; x < x_size1 - 1; x++) {
      pixel_value = 0.0;
      for (j = -1; j <= 1; j++) {
	    for (i = -1; i <= 1; i++) {
	      pixel_value += weight[j + 1][i + 1] * (image1[y + j][x + i]);
	    }
      }
      if (pixel_value < min) min = pixel_value;
      if (pixel_value > max) max = pixel_value;
    }
  }
  if ((int)(max - min) == 0) {
    return;
  }

  /* New loop variables */
  int xa;
  int ya;
  /* New pixel_value */
  double pixel_value_app;
  /* Initialization of image2[y][x] */
  x_size2 = x_size1;
  y_size2 = y_size1;
  for (ya = 0; (ya < y_size2); ya++) {
    for (xa = 0; (xa < x_size2); xa++) {
      image2[ya][xa] = 0;
    }
  }
  /* Generation of image2 after linear transformtion */
  for (ya = 1; (ya < y_size1 - 1); ya++) {
    for (xa = 1; (xa < x_size1 - 1); xa++) {
      pixel_value_app = 0.0;
      for (j = -1; j <= 1; j++) {
	    for (i = -1; i <= 1; i++) {
	      pixel_value_app += weight[j + 1][i + 1] * image1[ya + j][xa + i];
	    }
      }
      pixel_value_app = MAX_BRIGHTNESS * (pixel_value_app - min) / (max - min);
      image2[ya][xa] = (unsigned char)pixel_value_app;
    }
  }
}

int main(int argc, const char** argv)
{
  sobel_filtering( );

#ifdef LOCAL_RUN
  save_image_data( );
#endif

#ifndef LOCAL_RUN
  indicate_end();
#endif
  return 0;
}

