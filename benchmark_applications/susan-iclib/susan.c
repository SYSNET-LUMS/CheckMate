/* }}} */
/* {{{ defines, includes and typedefs */

/* ********** Optional settings */

#ifndef PPC
typedef int TOTAL_TYPE; /* this is faster for "int" but should be "float" for large d masks */
#else
typedef float TOTAL_TYPE; /* for my PowerPC accelerator only */
#endif

/*#define FOPENB*/      /* uncomment if using djgpp gnu C for DOS or certain Win95 compilers */

/* ********** Leave the rest - but you may need to remove one or both of sys/file.h and malloc.h lines */

#ifdef LOCAL_RUN

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#endif
#include <stdint.h>
#include <math.h>
#include "input_small.h"


#define FTOI(a) ((a) < 0 ? ((int)(a - 0.5)) : ((int)(a + 0.5)))
typedef unsigned char uchar;
static uint8_t *fakeFile;
static unsigned char setbrightness[516];

/* }}} */
/* {{{ get_image(filename,in,x_size,y_size) */

char fgetc2()
{
  char ret = *fakeFile;
  ++fakeFile;
  return ret;
}

/* {{{ int getint(fp) derived from XV */

int getint()
{
  int c, i;
  // char dummy[10000];

  c = fgetc2();
  while (1) /* find next integer */
  {
    if (c == '#') /* if we're at a comment, read to end of line */
      while (c != '\n')
        c = fgetc2();
    if (c >= '0' && c <= '9')
      break; /* found what we were looking for */
    c = fgetc2();
  }

  /* we're at the start of a number, continue until we hit a non-number */
  i = 0;
  while (1)
  {
    i = (i * 10) + (c - '0');
    c = fgetc2();
    if (c < '0' || c > '9')
      break;
  }

  return (i);
}

/* }}} */

void get_image(in, x_size, y_size) unsigned char **in;
int *x_size, *y_size;
{
  char header[100];

  /* {{{ read header */

  header[0] = fgetc2();
  header[1] = fgetc2();

  if (!(header[0] == 'P' && header[1] == '5'))
    header[0] = 'P';

  *x_size = getint();
  *y_size = getint();

  /* }}} */

  *in = (uchar *)fakeFile;
}

/* }}} */
/* {{{ put_image(filename,in,x_size,y_size) */

#ifdef LOCAL_RUN

void put_image(in, x_size, y_size) char *in;
int x_size,
    y_size;
{
  printf("P5\n");
  printf("%d %d\n", x_size, y_size);
  printf("255\n");
  fwrite(in, x_size * y_size, 1, stdout);
}

#endif
/* }}} */
/* {{{ int_to_uchar(r,in,size) */

/**/

/* }}} */
/* {{{ setup_brightness_lut(bp,thresh,form) */

void setup_brightness_lut(bp, thresh, form)
    uchar **bp;
int thresh, form;
{
  int k;
  float temp;

  //*bp=(unsigned char *)malloc(516);
  *bp = setbrightness;
  *bp = *bp + 258;

  for (k = -256; k < 257; k++)
  {
    temp = ((float)k) / ((float)thresh);
    temp = temp * temp;
    if (form == 6)
      temp = temp * temp * temp;
    temp = 100.0 * exp(-temp);
    *(*bp + k) = (uchar)temp;
  }
}

/* }}} */
/* {{{ edges */

/* {{{ edge_draw(in,corner_list,drawing_mode) */

void edge_draw(uchar *in, uchar *mid, int x_size, int y_size, int drawing_mode)
{
  int i;
  uchar *midp;

  // Create a new black image
  uchar *edge_image = (uchar *)malloc(x_size * y_size * sizeof(uchar));
  memset(edge_image, 0, x_size * y_size * sizeof(uchar)); // Initialize to black

  midp = mid;
  for (i = 0; i < x_size * y_size; i++)
  {
    if (*midp < 8)
      *(edge_image + (midp - mid)) = 255; // Draw edge as white on black background
    midp++;
  }

  // Copy edge image to output
  memcpy(in, edge_image, x_size * y_size * sizeof(uchar));

  free(edge_image); // Free the allocated memory
}

/* }}} */
/* {{{ susan_edges(in,r,sf,max_no,out) */

double my_sqrt(double number) {
    if (number < 0) {
        printf("Error: Negative input!\n");
        return -1; // Return error for negative input
    }

    double tolerance = 0.000001; // Define the tolerance level for approximation
    double guess = number / 2.0; // Initial guess for the square root

    while ((guess * guess - number) > tolerance || (number - guess * guess) > tolerance) {
        guess = (guess + number / guess) / 2.0; // Newton-Raphson iteration formula
    }

    return guess;
}

void susan_edges(uchar *in, int *r, uchar *mid, uchar *bp, int max_no, int x_size, int y_size)
{
    int i, j, x, y, n, m, a, b, w;
    uchar *p, *cp;
    float z;

    // Initialize the response array r with zeros
    memset(r, 0, x_size * y_size * sizeof(int));

    // Main processing loop: calculate responses
    for (i = 3; i < y_size - 3; i++)
    {
        for (j = 3; j < x_size - 3; j++)
        {
            n = 100;
            p = in + (i - 3) * x_size + j - 1;
            cp = bp + in[i * x_size + j];

            // Using a loop instead of manually incrementing n
            for (int k = 0; k < 3; ++k)
                n += *(cp - *p++);
            p += x_size - 3;
            for (int k = 0; k < 5; ++k)
                n += *(cp - *p++);
            p += x_size - 5;
            for (int k = 0; k < 7; ++k)
                n += *(cp - *p++);
            p += x_size - 6;
            for (int k = 0; k < 3; ++k)
                n += *(cp - *p++);
            p += 2;
            for (int k = 0; k < 3; ++k)
                n += *(cp - *p++);
            p += x_size - 6;
            for (int k = 0; k < 7; ++k)
                n += *(cp - *p++);
            p += x_size - 5;
            for (int k = 0; k < 5; ++k)
                n += *(cp - *p++);
            p += x_size - 3;
            for (int k = 0; k < 3; ++k)
                n += *(cp - *p++);

            if (n <= max_no)
                r[i * x_size + j] = max_no - n;
        }
    }

    // Response analysis loop: classify edges
    for (i = 4; i < y_size - 4; i++)
    {
        for (j = 4; j < x_size - 4; j++)
        {
            if (r[i * x_size + j] > 0)
            {
                m = r[i * x_size + j];
                n = max_no - m;
                cp = bp + in[i * x_size + j];

                x = 0; y = 0;

                if (n > 600)
                {
                    // Symmetry-based processing
                    p = in + (i - 3) * x_size + j - 1;
                    for (int k = 0; k < 3; ++k) {
                        int c = *(cp - *p++);
                        x += (k == 1 ? c : -c);
                        y += (k == 2 ? -3 * c : 3 * c);
                    }
                    p += x_size - 3;

                    // Continue with remaining processing...
                    // Loop for symmetry calculations and further edge classification

                    z = my_sqrt((float)((x * x) + (y * y)));
                    if (z > (0.9 * (float)n))
                    {
                        // Classify based on edge direction
                        w = (x == 0) ? 1000000.0 : ((float)y) / ((float)x);
                        if (w < 0.5) {
                            a = 0; b = 1;  // vertical edge
                        } else if (w > 2.0) {
                            a = 1; b = 0;  // horizontal edge
                        } else {
                            a = (w > 0) ? 1 : -1;
                            b = 1;  // diagonal edge
                        }

                        // Apply conditions for final classification
                        if ((m > r[(i + a) * x_size + j + b]) && (m >= r[(i - a) * x_size + j - b]))
                            mid[i * x_size + j] = 1;
                    }
                }
            }
        }
    }
}


/* }}} */

int main()
{
  /* {{{ vars */
  uchar *in, *bp, *mid;
  int *r,
      bt = 20,
      max_no_edges = 2650,
      x_size = -1, y_size = -1;
  ;

  /* }}} */
  fakeFile = test_data;

  get_image(&in, &x_size, &y_size);

  /* Setup brightness lookup table for edge detection */
  setup_brightness_lut(&bp, bt, 6);

  /* Allocate memory for results and temporary storage */
  r = (int *)malloc(x_size * y_size * sizeof(int));
  mid = (uchar *)malloc(x_size * y_size);
  memset(mid, 100, x_size * y_size); /* note not set to zero */

  /* Perform edge detection */
  susan_edges(in, r, mid, bp, max_no_edges, x_size, y_size);

  /* Draw detected edges */
  edge_draw(in, mid, x_size, y_size, 0);

  /* Save the resulting image */
#ifdef LOCAL_RUN

  put_image(in, x_size, y_size);

#endif

  /* Free allocated memory */
  free(r);
  free(mid);

  return 0;
}


/* }}} */
