# DHT11/DHT22 asynchronos driver for MicroPython
# Aaron Kirschen

from dht import DHT11 as _DHT11
from dht import DHT22 as _DHT22
import uasyncio as asyncio # micropython-async v3 (https://github.com/peterhinch/micropython-async/blob/master/v3/)
import logging
log = logging.getLogger(__name__)


class DHT11(_DHT11):
    def __init__(self, pin, readDelay=2, callback=None):
        self.pin = pin
        self.readDelay = readDelay
        self.temperature = None
        self.humidity = None
        self.callback = callback
        if not callback: self.callback = self._on_measurement 
        super().__init__(pin)

    def __iter__(self):  # Await 1st reading
        while ( (self.temperature is None) or (self.humidity is None) ):
            yield

    # Basic built in callback, overridable by initializing with callback key
    async def _on_measurement(self, measurement):
        log.debug(measurement)

   # Measure temperature continuously
    async def _run(self, readDelay):
        while True:
            try:
                self.temperature = self.temperature()
                self.humidity = self.humidity()
                # Run the callback
                try: await self.callback(self.temperature)
                except: self.callback(self.temperature)
                await asyncio.sleep(readDelay)
            except Exception as e:
                log.error('Error while fetching from DHT sensor buffer:\n {}'.format(e))        

    # Measure from sensor continously
    async def _measure(self,readDelay=2):
        if not readDelay:
            readDelay = self.readDelay
        while True:
            try:
                self.measure()
                await asyncio.sleep(readDelay)
            except Exception as e:
                log.error('Error while measuring from DHT sensor:\n {}'.format(e))      

    def convertToF(self,tempC):
        try:    return 1.8*tempC + 32
        except: return [1.8*temp + 32 for temp in tempC]


class DHT22(_DHT22):
    def __init__(self, pin, readDelay=2, unit='F',callback=None):
        self.pin = pin
        self.readDelay = readDelay
        self.unit = unit        
        self.temperature = None
        self.humidity = None
        self.callback = callback
        if not callback: self.callback = self._on_measurement 
        super().__init__(pin)

    def __iter__(self):  # Await 1st reading
        while ( (self.temperature is None) or (self.humidity is None) ):
            yield

    # Basic built in callback, overridable by initializing with callback key
    async def _on_measurement(self, measurement):
        log.debug(measurement)

   # Measure temperature continuously
    async def _run(self, readDelay):
        while True:
            try:
                temperature = self.temperature()
                humidity = self.humidity()
                if (isinstance(temperature, float) and isinstance(humidity, float)) or (isinstance(temperature, int) and isinstance(humidity, int)):
                    self.temperature = temperature
                    self.humidity = humidity
                    # temp = (b'{0:3.1f},'.format(temp))
                    # hum =  (b'{0:3.1f},'.format(hum))
                    # Run the callback
                    try: await self.callback(self.temperature)
                    except: self.callback(self.temperature)
                else: log.error('Invalid temperature/humidity fetched from DHT sensor!')
                await asyncio.sleep(readDelay)
            except Exception as e:
                log.error('Error while fetching from DHT sensor buffer:\n {}'.format(e))        


    # Measure from sensor continously
    async def _measure(self,readDelay=2):
        if not readDelay:
            readDelay = self.readDelay
        while True:
            try:
                self.measure()
                await asyncio.sleep(readDelay)
            except Exception as e:
                log.error('Error while measuring from DHT sensor:\n {}'.format(e))        

    def convertToF(self,tempC):
        try:    return 1.8*tempC + 32
        except: return [1.8*temp + 32 for temp in tempC]
