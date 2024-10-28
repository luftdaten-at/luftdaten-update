class LdProductModel:
    def __init__(self, ble_service, sensors, battery_monitor, status_led):
        self.model_id = None
        """Product model."""
        
        self.polling_interval = 0.1
        """Main loop polling interval in seconds."""
        
        self.ble_on = False
        """Whether to advertise over BLE."""
        
        self.number_of_leds = 1
        """Number of LEDs on the device."""
        
        # State injection
        self.ble_service = ble_service
        self.sensors = sensors
        self.battery_monitor = battery_monitor
        self.status_led = status_led
        self.status = bytearray([0, 0, 0, 0])
        
    def receive_command(self, command):
        """Process a command received on the BLE command characteristic."""
        pass
    
    def receive_button_press(self):
        """Process a button press event."""
        pass
    
    def tick(self):
        """Main loop tick. Called at regular intervals. 
        We do not need to check for commands here, these are passed separately."""
        pass
    
    def connection_update(self, connected):
        """Callback when BLE connection status changes.
        Will be called with False at the start of main loop."""
        pass
    
    # The following methods do not need to be overridden by subclasses.
    def update_ble_sensor_data(self):
        """Read out sensors values and update BLE characteristic."""
        vals_array = bytearray()
        for sensor in self.sensors:
            try:
                sensor.read()
            except:
                print(f"Error reading sensor {sensor.model_id}, using previous values")
            vals_array.extend(sensor.get_current_values())
        self.ble_service.sensor_values_characteristic = vals_array
    
    def update_ble_battery_status(self):
        """Read battery status and update BLE characteristic."""
        if self.battery_monitor is not None:
            self.status[0] = 1 # Has battery status: Yes
            self.status[1] = round(self.battery_monitor.cell_soc()) # Battery percentage
            self.status[2] = round(self.battery_monitor.cell_voltage() * 10) # Battery voltage
        else:
            self.status[0] = 0 # Has battery status: No
            self.status[1] = 0
            self.status[2] = 0
        self.ble_service.device_status_characteristic = self.status

    def update_ble_error_status(self, error_code):
        """Update BLE characteristic with error status."""
        self.status[3] = error_code
        self.ble_service.device_status_characteristic = self.status
        print(f"Error status updated: {error_code}")