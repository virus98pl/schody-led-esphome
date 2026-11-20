#pragma once

#include "esphome/core/component.h"
#include "esphome/core/preferences.h"
#include "esphome/components/sensor/sensor.h"
#include "esphome/components/binary_sensor/binary_sensor.h"

#include <Wire.h>
#include <SparkFun_VL53L5CX_Library.h>

namespace esphome {
namespace vl53l5cx_presence {

static const int MAX_ZONES = 64;
static const int16_t NO_TARGET = 4000;  // „nic nie widać” w danej strefie [mm]

class VL53L5CXPresence : public Component {
 public:
  void set_pins(int sda, int scl) {
    this->sda_ = sda;
    this->scl_ = scl;
  }
  void set_frequency(uint32_t f) { this->freq_ = f; }
  void set_address(uint8_t a) { this->address_ = a; }
  void set_resolution(int r) { this->res_ = r; }
  void set_ranging_hz(int hz) { this->hz_ = hz; }
  void set_margin(int mm) { this->margin_ = mm; }
  void set_min_distance(int mm) { this->min_mm_ = mm; }
  void set_max_distance(int mm) { this->max_mm_ = mm; }
  void set_min_zones(int n) { this->min_zones_ = n; }
  void set_frames_on(int n) { this->frames_on_ = n; }
  void set_frames_off(int n) { this->frames_off_ = n; }
  void set_presence_sensor(binary_sensor::BinarySensor *b) { this->presence_ = b; }
  void set_distance_sensor(sensor::Sensor *s) { this->distance_ = s; }
  void set_zones_sensor(sensor::Sensor *s) { this->zones_ = s; }

  /// Zapamiętaj tło (puste schody): uśrednia kolejne ramki przez ok. 3 s.
  void calibrate();
  /// Usuń tło: wtedy ruch = cokolwiek bliżej niż max_distance - margines.
  void clear_calibration();
  bool is_calibrated() const { return this->base_.valid == 1; }

  void setup() override;
  void loop() override;
  void dump_config() override;
  float get_setup_priority() const override { return setup_priority::DATA; }

 protected:
  struct Baseline {
    int16_t mm[MAX_ZONES];
    uint8_t zones;
    uint8_t valid;
  };

  int16_t zone_mm_(int i) const;
  void finish_calibration_();

  SparkFun_VL53L5CX imager_;
  VL53L5CX_ResultsData data_;
  ESPPreferenceObject pref_;
  Baseline base_{};

  int sda_{-1}, scl_{-1};
  uint32_t freq_{400000};
  uint8_t address_{0x29};
  int res_{8};
  int hz_{10};
  int margin_{200};
  int min_mm_{40};
  int max_mm_{1500};
  int min_zones_{2};
  int frames_on_{2};
  int frames_off_{5};

  bool ok_{false};
  bool state_{false};
  int on_count_{0};
  int off_count_{0};

  int calib_left_{0};
  int32_t calib_sum_[MAX_ZONES];
  uint8_t calib_cnt_[MAX_ZONES];
  int calib_frames_{0};

  uint32_t last_dist_ms_{0};
  int last_dist_{-1};
  int last_zones_{-1};

  binary_sensor::BinarySensor *presence_{nullptr};
  sensor::Sensor *distance_{nullptr};
  sensor::Sensor *zones_{nullptr};
};

}  // namespace vl53l5cx_presence
}  // namespace esphome
