"""VL53L5CX (8x8 ToF) jako czujnik obecności na schodach.

Używa biblioteki SparkFun VL53L5CX (Arduino). Porównuje każdą strefę z zapamiętanym
tłem (kalibracja pustych schodów): strefa „widzi ruch”, gdy coś jest bliżej niż tło
minus margines. Obecność = co najmniej `min_zones` takich stref przez `frames_on` ramek.
"""
import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import binary_sensor, sensor
from esphome.const import (
    CONF_ADDRESS,
    CONF_FREQUENCY,
    CONF_ID,
    DEVICE_CLASS_DISTANCE,
    DEVICE_CLASS_OCCUPANCY,
    STATE_CLASS_MEASUREMENT,
)

CODEOWNERS = ["@virus98pl"]
AUTO_LOAD = ["sensor", "binary_sensor"]

CONF_SDA = "sda"
CONF_SCL = "scl"
CONF_RESOLUTION = "resolution"
CONF_RANGING_HZ = "ranging_hz"
CONF_MARGIN = "margin"
CONF_MIN_DISTANCE = "min_distance"
CONF_MAX_DISTANCE = "max_distance"
CONF_MIN_ZONES = "min_zones"
CONF_FRAMES_ON = "frames_on"
CONF_FRAMES_OFF = "frames_off"
CONF_PRESENCE = "presence"
CONF_DISTANCE = "distance"
CONF_ZONES = "zones"

ns = cg.esphome_ns.namespace("vl53l5cx_presence")
VL53L5CXPresence = ns.class_("VL53L5CXPresence", cg.Component)


def _validate_hz(config):
    limit = 60 if config[CONF_RESOLUTION] == 4 else 15
    if config[CONF_RANGING_HZ] > limit:
        raise cv.Invalid(f"ranging_hz dla {config[CONF_RESOLUTION]}x{config[CONF_RESOLUTION]} to maks. {limit}")
    return config


CONFIG_SCHEMA = cv.All(
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(VL53L5CXPresence),
            cv.Required(CONF_SDA): cv.int_range(min=0, max=48),
            cv.Required(CONF_SCL): cv.int_range(min=0, max=48),
            cv.Optional(CONF_FREQUENCY, default=400000): cv.int_range(min=100000, max=1000000),
            cv.Optional(CONF_ADDRESS, default=0x29): cv.i2c_address,
            cv.Optional(CONF_RESOLUTION, default=8): cv.one_of(4, 8, int=True),
            cv.Optional(CONF_RANGING_HZ, default=10): cv.int_range(min=1, max=60),
            cv.Optional(CONF_MARGIN, default=200): cv.int_range(min=20, max=2000),
            cv.Optional(CONF_MIN_DISTANCE, default=40): cv.int_range(min=0, max=1000),
            cv.Optional(CONF_MAX_DISTANCE, default=1500): cv.int_range(min=100, max=4000),
            cv.Optional(CONF_MIN_ZONES, default=2): cv.int_range(min=1, max=64),
            cv.Optional(CONF_FRAMES_ON, default=2): cv.int_range(min=1, max=30),
            cv.Optional(CONF_FRAMES_OFF, default=5): cv.int_range(min=1, max=100),
            cv.Optional(CONF_PRESENCE): binary_sensor.binary_sensor_schema(
                device_class=DEVICE_CLASS_OCCUPANCY
            ),
            cv.Optional(CONF_DISTANCE): sensor.sensor_schema(
                unit_of_measurement="mm",
                accuracy_decimals=0,
                device_class=DEVICE_CLASS_DISTANCE,
                state_class=STATE_CLASS_MEASUREMENT,
                icon="mdi:ruler",
            ),
            cv.Optional(CONF_ZONES): sensor.sensor_schema(
                accuracy_decimals=0,
                state_class=STATE_CLASS_MEASUREMENT,
                icon="mdi:grid",
            ),
        }
    ).extend(cv.COMPONENT_SCHEMA),
    cv.only_with_arduino,
    _validate_hz,
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    cg.add(var.set_pins(config[CONF_SDA], config[CONF_SCL]))
    cg.add(var.set_frequency(config[CONF_FREQUENCY]))
    cg.add(var.set_address(config[CONF_ADDRESS]))
    cg.add(var.set_resolution(config[CONF_RESOLUTION]))
    cg.add(var.set_ranging_hz(config[CONF_RANGING_HZ]))
    cg.add(var.set_margin(config[CONF_MARGIN]))
    cg.add(var.set_min_distance(config[CONF_MIN_DISTANCE]))
    cg.add(var.set_max_distance(config[CONF_MAX_DISTANCE]))
    cg.add(var.set_min_zones(config[CONF_MIN_ZONES]))
    cg.add(var.set_frames_on(config[CONF_FRAMES_ON]))
    cg.add(var.set_frames_off(config[CONF_FRAMES_OFF]))
    if CONF_PRESENCE in config:
        b = await binary_sensor.new_binary_sensor(config[CONF_PRESENCE])
        cg.add(var.set_presence_sensor(b))
    if CONF_DISTANCE in config:
        s = await sensor.new_sensor(config[CONF_DISTANCE])
        cg.add(var.set_distance_sensor(s))
    if CONF_ZONES in config:
        s = await sensor.new_sensor(config[CONF_ZONES])
        cg.add(var.set_zones_sensor(s))
    cg.add_library("Wire", None)
    cg.add_library("sparkfun/SparkFun VL53L5CX Arduino Library", "^1.0.3")
