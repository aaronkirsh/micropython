# DS18x20 temperature sensor driver child-class for MicroPython using uasyncio to achieve 'asynchronous' operation
#   Aaron Kirschen

from ds18x20 import DS18X20 as _DS18X20
import uasyncio as asyncio # micropython-async v3 (https://github.com/peterhinch/micropython-async/blob/master/v3/)
import logging
log = logging.getLogger(__name__)

class DS18X20(_DS18X20):
    def __init__(self, onewire, readDelay=2, unit='F', callback=None):
        super().__init__(onewire)
        self.readDelay = readDelay
        self.temperature = None
        self.string = None
        self.unit = unit
        self.roms = None
        self.callback = callback
        if not callback: self.callback = self._on_measurement 
        loop = asyncio.get_event_loop()
        loop.create_task(self.scan(readDelay))
        loop.create_task(self._run(readDelay))

    # Basic built in callback, overridable by initializing with callback key
    async def _on_measurement(self, measurement):
        log.debug(measurement)

    # Measure temperature continuously
    async def _run(self, read_delay):
        while True:
            try:
                # If we have a sensor to read
                if self.roms:
                    # Convert the temp
                    self.convert_temp()
                    await asyncio.sleep_ms(750)
                    # Get the temperature
                    self.temperature = [self.read_temp(rom) for rom in self.roms]
                    log.debug(' Read DS Probe temperature:\n {}'.format(self.temperature))
                    # Convert to F if desired
                    if self.unit == 'F':
                        self.temperature = self.convertToF(self.temperature)
                    # Generate the string
                    self.string = []
                    for i in range(len(self.roms)):
                        self.string.append(
                            " DS Probe {} Temperature: {} * {}".format(
                                self.roms[i], self.temperature[i], self.unit
                            )
                        )
                    log.debug(' string generated:\n {}'.format(self.string))
                    # Run the callback
                    try: await self.callback(self.temperature)
                    except: self.callback(self.temperature)
                # Wait between readings    
                await asyncio.sleep(read_delay)
            except Exception as e:
                log.error('Error while measuring DS18X20 temperature:\n {}'.format(e))

    def __iter__(self):  # Await 1st reading
        while self.temperature is None:
            yield

    # Scan for roms continuously
    async def scan(self,readDelay=None):
        if not readDelay:
            readDelay = self.readDelay
        while True:
            try:
                self.roms = super().scan()
                await asyncio.sleep(readDelay)
            except Exception as e:
                log.error('Error while scanning for roms:\n {}'.format(e))

    def convertToF(self,tempC):
        try:    return 1.8*tempC + 32
        except: return [1.8*temp + 32 for temp in tempC]
