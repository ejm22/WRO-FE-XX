#ifndef VOLTAGE_UTILS_H
#define VOLTAGE_UTILS_H
#include <Arduino.h>

const int VOLTAGE_PIN = A5;  // Pin for battery voltage measurement
const double VOLTAGE_VALUE_RANGE = 1023.0;
const double VOLTAGE_DIVIDER_RATIO = 3.0;
const double MAX_VOLTAGE = 5.0;

class VoltageUtils {
public:
    static void showVoltage();
};

#endif