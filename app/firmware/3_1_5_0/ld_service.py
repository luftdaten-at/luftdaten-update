from adafruit_ble import BLERadio
from adafruit_ble.services import Service
from adafruit_ble.uuid import VendorUUID
from adafruit_ble.characteristics import Characteristic, ComplexCharacteristic, Attribute
from adafruit_ble.characteristics.int import Uint8Characteristic
from adafruit_ble.characteristics.stream import StreamIn 

class LdService(Service):
    # Define a custom UUID for your service (use a UUID generator to get a unique one)
    uuid = VendorUUID("0931b4b5-2917-4a8d-9e72-23103c09ac29")

    # Define characteristics with their own UUIDs and properties

    # For reading AirStation Configuration
    air_station_configuration = Characteristic(
        uuid=VendorUUID("b47b0cdf-0ced-49a9-86a5-d78a03ea7674"),
        properties=Characteristic.READ,
        initial_value=bytes([0]),
        max_length=512,
    )

    # For reading sensor values
    sensor_values_characteristic = Characteristic(
        uuid=VendorUUID("4b439140-73cb-4776-b1f2-8f3711b3bb4f"),
        properties=Characteristic.READ,
        initial_value=bytes([0]),
        max_length=512,
    )

    # For reading details about this device
    device_info_characteristic = Characteristic(
        uuid=VendorUUID("8d473240-13cb-1776-b1f2-823711b3ffff"),
        properties=Characteristic.READ,
        initial_value=bytes([0]),
        max_length=512,
    )

    # For reading this device's status
    device_status_characteristic = Characteristic(
        uuid=VendorUUID("77db81d9-9773-49b4-aa17-16a2f93e95f2"),
        properties=Characteristic.READ,
        initial_value=bytes([0, 0, 0, 0]),
        max_length=512,
    )

    # For reading details about this device's installed sensors
    sensor_info_characteristic = Characteristic(
        uuid=VendorUUID("13fa8751-57af-4597-a0bb-b202f6111ae6"),
        properties=Characteristic.READ,
        initial_value=bytes([0]),
        max_length=512,
    )


    trigger_reading_characteristic_2 = Characteristic(
        uuid=VendorUUID("030ff8b1-1e45-4ae6-bf36-3bca4c38cdba"),
        properties=(Characteristic.WRITE | Characteristic.WRITE_NO_RESPONSE),
        initial_value=bytes(),
        max_length=512,
    )

    '''
    # For requesting that the device take a new sensor reading
    trigger_reading_characteristic_2 = StreamIn(
        uuid=VendorUUID("030ff8b1-1e45-4ae6-bf36-3bca4c38cdba"),   
    )
    trigger_reading_characteristic_2 = ComplexCharacteristic(
        uuid = VendorUUID("030ff8b1-1e45-4ae6-bf36-3bca4c38cdba"),
        properties = (Characteristic.WRITE | Characteristic.WRITE_NO_RESPONSE),
        read_perm=Attribute.NO_ACCESS,
        write_perm = Attribute.OPEN,
        max_length = 512
    )
    '''
