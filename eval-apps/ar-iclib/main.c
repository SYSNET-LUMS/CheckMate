/*
 * Copyright (c) 2019 Vito Kortbeek (v.kortbeek-1@tudelft.nl) TU Delft Embedded
 * and Networked Systems Group/Sustainable Systems Laboratory.
 *
 * Copyright (c) 2020 University of Southampton. All rights reserved.
 *
 * SPDX-License-Identifier: MIT
 */

/*
 * Modified 2020 for use with ICLib by Sivert Sliper, University of Southamption
 */
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#ifndef LOCAL_RUN
#include "support/msp430-support.h"
#endif

/* ------ Parameters ------ */
// Number of samples to discard before recording training set
#define NUM_WARMUP_SAMPLES 3
#define ACCEL_WINDOW_SIZE 3
#define MODEL_SIZE 16
#define SAMPLE_NOISE_FLOOR 10 // TODO: made up value
// Number of classifications to complete in one experiment
#define SAMPLES_TO_COLLECT 128

/* ------ Types ------ */
typedef struct {
  uint8_t x;
  uint8_t y;
  uint8_t z;
} threeAxis_t_8;

typedef threeAxis_t_8 accelReading;
typedef accelReading accelWindow[ACCEL_WINDOW_SIZE];

typedef struct {
  unsigned meanmag;
  unsigned stddevmag;
} features_t;

typedef enum {
  CLASS_STATIONARY,
  CLASS_MOVING,
} class_t;

typedef struct {
  features_t stationary[MODEL_SIZE];
  features_t moving[MODEL_SIZE];
} model_t;

typedef enum {
  MODE_IDLE = 3,
  MODE_TRAIN_STATIONARY = 2,
  MODE_TRAIN_MOVING = 1,
  MODE_RECOGNIZE = 0, // default
} run_mode_t;

typedef struct {
  unsigned totalCount;
  unsigned movingCount;
  unsigned stationaryCount;
} stats_t;

/* ------ Globals ------ */
static model_t model;
static void transform(accelWindow window);

/* ------ Function prototypes ------ */
//! Train model
void train(features_t *classModel);

//! Perform full sample->process->classify pipeline
void recognize(model_t *model);

//! Sample the accelerometer (emulated with random numbers)
static void ACCEL_singleSample(threeAxis_t_8 *result);

//! Sample a new window
static void acquire_window(accelWindow window);

//! Threshold (zero any samples < SAMPLE_NOISE_FLOOR)
static void transform(accelWindow window);

//! Feature extraction (mean and stddev)
static void featurize(features_t *features, accelWindow aWin);

//! Classify
static class_t classify(features_t *features, model_t *model);

//! Record classification statistics
static void record_stats(stats_t *stats, class_t class);

//! Warmup samples (discard NUM_WARMUP_SAMPLES samples)
static void warmup_sensor(void);

//! Square root by Newton's method
static uint16_t sqrt16(uint32_t x);

/* ------ Function definitions ------ */
static void ACCEL_singleSample(threeAxis_t_8 *result) {
  static unsigned int _v_seed = 4;

  unsigned int seed = _v_seed;
  result->x = (seed * 17) % 85;
  result->y = (seed * 17 * 17) % 85;
  result->z = (seed * 17 * 17 * 17) % 85;
  _v_seed = ++seed;
}

static void acquire_window(accelWindow window) {
  accelReading sample;
  unsigned samplesInWindow = 0;
  while (samplesInWindow < ACCEL_WINDOW_SIZE) {
    ACCEL_singleSample(&sample);
    window[samplesInWindow++] = sample;
  }
}

static void transform(accelWindow window) {
  for (unsigned i = 0; i < ACCEL_WINDOW_SIZE; i++) {
    accelReading *sample = &window[i];
    sample->x = (sample->x > SAMPLE_NOISE_FLOOR) ? sample->x : 0;
    sample->y = (sample->y > SAMPLE_NOISE_FLOOR) ? sample->y : 0;
    sample->z = (sample->z > SAMPLE_NOISE_FLOOR) ? sample->z : 0;
  }
}

static void featurize(features_t *features, accelWindow aWin) {
  accelReading mean;
  mean.x = mean.y = mean.z = 0;
  for (int i = 0; i < ACCEL_WINDOW_SIZE; i++) {
    mean.x += aWin[i].x; // x
    mean.y += aWin[i].y; // y
    mean.z += aWin[i].z; // z
  }
  /*
     mean.x = mean.x / ACCEL_WINDOW_SIZE;
     mean.y = mean.y / ACCEL_WINDOW_SIZE;
     mean.z = mean.z / ACCEL_WINDOW_SIZE;
     */
  mean.x >>= 2;
  mean.y >>= 2;
  mean.z >>= 2;

  accelReading stddev;
  stddev.x = stddev.y = stddev.z = 0;
  for (int i = 0; i < ACCEL_WINDOW_SIZE; i++) {
    stddev.x +=
        aWin[i].x > mean.x ? aWin[i].x - mean.x : mean.x - aWin[i].x; // x
    stddev.y +=
        aWin[i].y > mean.y ? aWin[i].y - mean.y : mean.y - aWin[i].y; // y
    stddev.z +=
        aWin[i].z > mean.z ? aWin[i].z - mean.z : mean.z - aWin[i].z; // z
  }
  /*
     stddev.x = stddev.x / (ACCEL_WINDOW_SIZE - 1);
     stddev.y = stddev.y / (ACCEL_WINDOW_SIZE - 1);
     stddev.z = stddev.z / (ACCEL_WINDOW_SIZE - 1);
     */
  stddev.x >>= 2;
  stddev.y >>= 2;
  stddev.z >>= 2;

  unsigned meanmag = mean.x * mean.x + mean.y * mean.y + mean.z * mean.z;
  unsigned stddevmag =
      stddev.x * stddev.x + stddev.y * stddev.y + stddev.z * stddev.z;

  features->meanmag = sqrt16(meanmag);
  features->stddevmag = sqrt16(stddevmag);
}

static class_t classify(features_t *features, model_t *model) {
  int move_less_error = 0;
  int stat_less_error = 0;
  features_t *model_features;

  for (int i = 0; i < MODEL_SIZE; ++i) {
    model_features = &model->stationary[i];

    long int stat_mean_err =
        (model_features->meanmag > features->meanmag)
            ? (model_features->meanmag - features->meanmag)
            : (features->meanmag - model_features->meanmag);

    long int stat_sd_err =
        (model_features->stddevmag > features->stddevmag)
            ? (model_features->stddevmag - features->stddevmag)
            : (features->stddevmag - model_features->stddevmag);

    model_features = &model->moving[i];

    long int move_mean_err =
        (model_features->meanmag > features->meanmag)
            ? (model_features->meanmag - features->meanmag)
            : (features->meanmag - model_features->meanmag);

    long int move_sd_err =
        (model_features->stddevmag > features->stddevmag)
            ? (model_features->stddevmag - features->stddevmag)
            : (features->stddevmag - model_features->stddevmag);

    if (move_mean_err < stat_mean_err) {
      move_less_error++;
    } else {
      stat_less_error++;
    }

    if (move_sd_err < stat_sd_err) {
      move_less_error++;
    } else {
      stat_less_error++;
    }
  }

  class_t class =
      move_less_error > stat_less_error ? CLASS_MOVING : CLASS_STATIONARY;
  return class;
}

static void record_stats(stats_t *stats, class_t class) {
  stats->totalCount++;
  switch (class) {
  case CLASS_MOVING:
    stats->movingCount++;
    break;

  case CLASS_STATIONARY:
    stats->stationaryCount++;
    break;
  }
}

static void warmup_sensor(void) {
  unsigned discardedSamplesCount = 0;
  accelReading sample;
  while (discardedSamplesCount++ < NUM_WARMUP_SAMPLES) {
    ACCEL_singleSample(&sample);
  }
}

void train(features_t *classModel) {
  accelWindow sampleWindow;
  features_t features;

  warmup_sensor();

  for (unsigned i = 0; i < MODEL_SIZE; ++i) {
    acquire_window(sampleWindow);
    transform(sampleWindow);
    featurize(&features, sampleWindow);
    classModel[i] = features;
  }
}

void recognize(model_t *model) {
  static stats_t stats;

  accelWindow sampleWindow;
  features_t features;
  class_t class;
  unsigned i;

  stats.totalCount = 0;
  stats.stationaryCount = 0;
  stats.movingCount = 0;

  for (i = 0; i < SAMPLES_TO_COLLECT; ++i) {
    acquire_window(sampleWindow);
    transform(sampleWindow);
    featurize(&features, sampleWindow);
    class = classify(&features, model);
    record_stats(&stats, class);
  }
#ifdef LOCAL_RUN
    printf("Total: %d, Moving: %d, Stationary: %d\n", stats.totalCount, stats.movingCount, stats.stationaryCount);
#endif
}

void main() {
    train(model.moving);
    train(model.stationary);
    recognize(&model);

#ifndef LOCAL_RUN
    indicate_end();
#endif
}

static uint16_t sqrt16(uint32_t x) {
  uint16_t hi = 0xffff;
  uint16_t lo = 0;
  uint16_t mid = ((uint32_t)hi + (uint32_t)lo) >> 1;
  uint32_t s = 0;

  while (s != x && hi - lo > 1) {
    mid = ((uint32_t)hi + (uint32_t)lo) >> 1;
    s = (uint32_t)mid * (uint32_t)mid;
    if (s < x)
      lo = mid;
    else
      hi = mid;
  }

  return mid;
}