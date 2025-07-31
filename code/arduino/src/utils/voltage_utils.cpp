#include "voltage_utils.h"

void VoltageUtils::showVoltage() {
    float vA0 = analogRead(VOLTAGE_PIN) * (MAX_VOLTAGE / VOLTAGE_VALUE_RANGE);
    float vBattery = vA0 * VOLTAGE_DIVIDER_RATIO; // Because of the voltage divider
    Serial.println("Battery voltage: " + String(vBattery, 1));
}