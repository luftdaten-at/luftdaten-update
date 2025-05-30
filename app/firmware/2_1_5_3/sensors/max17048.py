import adafruit_max1704x
from logger import logger

class MAX17048:
    """Driver for the MAX1704x Battery Monitor."""
    
    def __init__(self, i2c, address=0x36):
        """Initialize with an I2C bus and an optional I2C address."""
        self.i2c_device = adafruit_max1704x.MAX17048(i2c, address=address)

        logger.debug(
            "Found MAX1704x with chip version",
            hex(self.i2c_device.chip_version),
            "and id",
            hex(self.i2c_device.chip_id),
        )
            
    def cell_voltage(self):
        """Read and return the battery voltage in volts."""
        voltage = self.i2c_device.cell_voltage
        return voltage
    
    def cell_soc(self):
        """Read and return the state of charge (SOC) percentage."""
        soc = self.i2c_device.cell_percent
        return soc
    
    def quick_start(self):
        self.i2c_device.quick_start = True
        self.cell_voltage()
    
# Quick starting allows an instant 'auto-calibration' of the battery. However, its a bad idea
# to do this right when the battery is first plugged in or if there's a lot of load on the battery
# so uncomment only if you're sure you want to 'reset' the chips charge calculator.
# logger.debug("Quick starting")
# max17.quick_start = True