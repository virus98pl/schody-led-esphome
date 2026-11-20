#include "vl53l5cx_presence.h"
#include "esphome/core/log.h"
#include "esphome/core/hal.h"
#include "esphome/core/helpers.h"

#include <algorithm>
#include <cstdio>
#include <cstdlib>

namespace esphome {
namespace vl53l5cx_presence {

static const char *const TAG = "vl53l5cx_presence";

void VL53L5CXPresence::setup() {
  ESP_LOGCONFIG(TAG, "Start VL53L5CX (wgrywanie firmware do czujnika trwa 1-3 s)...");
  Wire.begin(this->sda_, this->scl_, this->freq_);
  this->imager_.setWireMaxPacketSize(128);  // bufor Wire na ESP32 ma 128 B

  if (!this->imager_.begin(this->address_, Wire)) {
    ESP_LOGE(TAG, "Brak VL53L5CX pod adresem 0x%02X (sprawdź SDA/SCL, zasilanie i pin LPn)", this->address_);
    this->mark_failed();
    return;
  }
  if (!this->imager_.setResolution(this->res_ * this->res_)) {
    ESP_LOGE(TAG, "Nie udało się ustawić rozdzielczości %dx%d", this->res_, this->res_);
    this->mark_failed();
    return;
  }
  if (!this->imager_.setRangingFrequency(this->hz_)) {
    ESP_LOGW(TAG, "Nie udało się ustawić %d Hz, zostaje domyślna częstotliwość", this->hz_);
  }
  if (!this->imager_.startRanging()) {
    ESP_LOGE(TAG, "Nie udało się uruchomić pomiarów");
    this->mark_failed();
    return;
  }

  this->pref_ = global_preferences->make_preference<Baseline>(fnv1_hash("vl53l5cx_presence_tlo"));
  if (!this->pref_.load(&this->base_) || this->base_.zones != this->res_ * this->res_) {
    this->base_.valid = 0;
  }
  ESP_LOGI(TAG, "VL53L5CX gotowy, %dx%d @ %d Hz, tło %s", this->res_, this->res_, this->hz_,
           this->is_calibrated() ? "wczytane" : "brak (zrób kalibrację pustych schodów)");
  this->ok_ = true;
}

int16_t VL53L5CXPresence::zone_mm_(int i) const {
  // statusy 5 i 9 = pomiar pewny, 6 = pewny z mniejszą dokładnością
  uint8_t st = this->data_.target_status[i];
  if (this->data_.nb_target_detected[i] == 0 || !(st == 5 || st == 6 || st == 9))
    return NO_TARGET;
  int16_t d = this->data_.distance_mm[i];
  if (d < this->min_mm_)
    return NO_TARGET;  // zabrudzone okienko / odbicie od szybki
  return d;
}

void VL53L5CXPresence::loop() {
  if (!this->ok_ || !this->imager_.isDataReady())
    return;
  if (!this->imager_.getRangingData(&this->data_))
    return;

  const int n = this->res_ * this->res_;

  // --- kalibracja tła ---
  if (this->calib_left_ > 0) {
    for (int i = 0; i < n; i++) {
      int16_t d = this->zone_mm_(i);
      if (d != NO_TARGET) {
        this->calib_sum_[i] += d;
        this->calib_cnt_[i]++;
      }
    }
    if (--this->calib_left_ == 0)
      this->finish_calibration_();
    return;
  }

  // --- wykrywanie ---
  int active = 0;
  int nearest = NO_TARGET;
  for (int i = 0; i < n; i++) {
    int16_t d = this->zone_mm_(i);
    if (d == NO_TARGET || d > this->max_mm_)
      continue;
    int16_t bg = this->is_calibrated() ? this->base_.mm[i] : NO_TARGET;
    if (bg > this->max_mm_)
      bg = this->max_mm_;
    if (d < bg - this->margin_) {
      active++;
      if (d < nearest)
        nearest = d;
    }
  }

  bool hit = active >= this->min_zones_;
  if (hit) {
    this->off_count_ = 0;
    if (++this->on_count_ >= this->frames_on_ && !this->state_) {
      this->state_ = true;
      if (this->presence_ != nullptr)
        this->presence_->publish_state(true);
    }
  } else {
    this->on_count_ = 0;
    if (++this->off_count_ >= this->frames_off_ && this->state_) {
      this->state_ = false;
      if (this->presence_ != nullptr)
        this->presence_->publish_state(false);
    }
  }

  // odległość i liczbę stref wysyłamy najwyżej 2x na sekundę i tylko po zmianie
  uint32_t now = millis();
  if (now - this->last_dist_ms_ >= 500) {
    int dist = nearest == NO_TARGET ? 0 : nearest;
    if (this->distance_ != nullptr && std::abs(dist - this->last_dist_) >= 20) {
      this->distance_->publish_state(dist);
      this->last_dist_ = dist;
    }
    if (this->zones_ != nullptr && active != this->last_zones_) {
      this->zones_->publish_state(active);
      this->last_zones_ = active;
    }
    this->last_dist_ms_ = now;
  }
}

void VL53L5CXPresence::calibrate() {
  if (!this->ok_)
    return;
  for (int i = 0; i < MAX_ZONES; i++) {
    this->calib_sum_[i] = 0;
    this->calib_cnt_[i] = 0;
  }
  this->calib_frames_ = std::max(10, this->hz_ * 3);
  this->calib_left_ = this->calib_frames_;
  ESP_LOGI(TAG, "Kalibracja tła: %d ramek, nikt nie może stać przed czujnikiem", this->calib_frames_);
}

void VL53L5CXPresence::finish_calibration_() {
  const int n = this->res_ * this->res_;
  for (int i = 0; i < n; i++) {
    // strefa musi widzieć tło w co najmniej połowie ramek, inaczej traktujemy ją jako pustą
    if (this->calib_cnt_[i] * 2 >= this->calib_frames_)
      this->base_.mm[i] = this->calib_sum_[i] / this->calib_cnt_[i];
    else
      this->base_.mm[i] = NO_TARGET;
  }
  this->base_.zones = n;
  this->base_.valid = 1;
  this->pref_.save(&this->base_);
  global_preferences->sync();
  ESP_LOGI(TAG, "Kalibracja zapisana");
  for (int r = 0; r < this->res_; r++) {
    char line[8 * 6 + 1];
    int p = 0;
    for (int c = 0; c < this->res_; c++)
      p += snprintf(line + p, sizeof(line) - p, "%5d", this->base_.mm[r * this->res_ + c]);
    ESP_LOGI(TAG, "  tło[%d]:%s", r, line);
  }
}

void VL53L5CXPresence::clear_calibration() {
  this->base_.valid = 0;
  this->pref_.save(&this->base_);
  global_preferences->sync();
  ESP_LOGI(TAG, "Tło usunięte");
}

void VL53L5CXPresence::dump_config() {
  ESP_LOGCONFIG(TAG, "VL53L5CX presence:");
  ESP_LOGCONFIG(TAG, "  SDA: GPIO%d, SCL: GPIO%d, %u Hz, adres 0x%02X", this->sda_, this->scl_, this->freq_,
                this->address_);
  ESP_LOGCONFIG(TAG, "  Siatka %dx%d @ %d Hz", this->res_, this->res_, this->hz_);
  ESP_LOGCONFIG(TAG, "  Margines %d mm, zakres %d-%d mm, min. stref %d", this->margin_, this->min_mm_, this->max_mm_,
                this->min_zones_);
  ESP_LOGCONFIG(TAG, "  Tło: %s", this->is_calibrated() ? "skalibrowane" : "brak");
  if (this->is_failed())
    ESP_LOGE(TAG, "  Czujnik nie odpowiada!");
}

}  // namespace vl53l5cx_presence
}  // namespace esphome
