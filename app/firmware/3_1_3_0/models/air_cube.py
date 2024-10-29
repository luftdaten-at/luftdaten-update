from models.ld_product_model import LdProductModel
from led_controller import RepeatMode
from enums import Color, LdProduct, Dimension, Quality, BleCommands
import time

class AirCube(LdProductModel): 
    def __init__(self, ble_service, sensors, battery_monitor, status_led):
        super().__init__(ble_service, sensors, battery_monitor, status_led)
        self.polling_interval = 0.01
        self.model_id = LdProduct.AIR_CUBE
        self.ble_on = False
        self.number_of_leds = 5
        self.last_measurement = None
        
    def receive_command(self, command):
        if(len(command) == 0):
            return
        cmd = command[0]
        if cmd == BleCommands.READ_SENSOR_DATA or cmd == BleCommands.READ_SENSOR_DATA_AND_BATTERY_STATUS:
            self.update_ble_sensor_data()
            print("Sensor values updated")
            self.status_led.show_led({
                'repeat_mode': RepeatMode.TIMES,
                'repeat_times': 1,
                'elements': [
                    {'color': Color.BLUE, 'duration': 0.1},
                ],
            })
        if cmd == BleCommands.READ_SENSOR_DATA_AND_BATTERY_STATUS:
            self.update_ble_battery_status()
            print("Battery status updated")
    
    def receive_button_press(self):
        self.ble_on = not self.ble_on
        if self.ble_on:
            self.status_led.show_led({
                'repeat_mode': RepeatMode.PERMANENT,
                'color': Color.BLUE,
            })
        else:
            self.status_led.turn_off_led()
    
    def tick(self):
        # Measure every 5 seconds (allow this to be settable)
        if self.last_measurement is None or time.monotonic() - self.last_measurement > 5:
            # This reads sensors & updates BLE - we don't mind updating BLE even if it is off
            self.update_ble_sensor_data()
            self.last_measurement = time.monotonic()
            # Update LEDs
            sensor_values = {
                Dimension.TEMPERATURE: [],
                Dimension.CO2: [],
                Dimension.PM2_5: [],
                Dimension.TVOC: [],
                # TODO AQI should depend on more than just total VOC
            }
            # Add sensor data - note there may be no data for some dimensions
            # Add HIGH quality data
            for sensor in self.sensors:
                for dimension in sensor.measures_values:
                    if sensor.value_quality[dimension] == Quality.HIGH:
                        if dimension in sensor_values.keys():
                            if sensor.current_values[dimension] is not None:
                                sensor_values[dimension].append(sensor.current_values[dimension])
            # If no HIGH quality data, add LOW quality data
            for sensor in self.sensors:
                for dimension in sensor.measures_values:
                    if dimension in sensor_values.keys():
                        if len(sensor_values[dimension]) == 0:
                            if sensor.current_values[dimension] is not None:
                                sensor_values[dimension].append(sensor.current_values[dimension])            
            # Update LEDs
            if len(sensor_values[Dimension.TEMPERATURE]) > 0:
                self._updateLed(1, 
                                sum(sensor_values[Dimension.TEMPERATURE]) / len(sensor_values[Dimension.TEMPERATURE]), 
                                [18, 24], 
                                [Color.BLUE, Color.GREEN, Color.RED],
                                )
            if len(sensor_values[Dimension.PM2_5]) > 0:
                self._updateLed(2, 
                                sum(sensor_values[Dimension.PM2_5]) / len(sensor_values[Dimension.PM2_5]), 
                                [5, 15],
                                [Color.GREEN, Color.YELLOW, Color.RED],
                                )
            if len(sensor_values[Dimension.TVOC]) > 0:
                self._updateLed(3, 
                                sum(sensor_values[Dimension.TVOC]) / len(sensor_values[Dimension.TVOC]), 
                                [220, 1430],
                                [Color.GREEN, Color.YELLOW, Color.RED],
                                )
            if len(sensor_values[Dimension.CO2]) > 0:
                self._updateLed(4,
                                sum(sensor_values[Dimension.CO2]) / len(sensor_values[Dimension.CO2]), 
                                [800, 1000, 1400], 
                                [Color.GREEN, Color.YELLOW, Color.ORANGE, Color.RED],
                                )
            
    def _updateLed(self, led_id, value, color_cutoffs, colors):
        color = colors[0]
        for i in range(len(color_cutoffs)):
            if value > color_cutoffs[i]:
                color = colors[i + 1]
        self.status_led.show_led({
            'repeat_mode': RepeatMode.PERMANENT,
            'color': color,
        }, led_id)

    def connection_update(self, connected):
        return
        if connected:
            self.status_led.show_led({
                'repeat_mode': RepeatMode.TIMES,
                'repeat_times': 1,
                'elements': [
                    {'color': Color.GREEN, 'duration': 1},
                ],
            })
        else:
            self.status_led.show_led({
                'repeat_mode': RepeatMode.FOREVER,
                'elements': [
                    {'color': Color.CYAN, 'duration': 0.5},
                    {'color': Color.OFF, 'duration': 0.5},
                ],
            })