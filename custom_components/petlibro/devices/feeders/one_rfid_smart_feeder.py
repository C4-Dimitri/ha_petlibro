from typing import cast
from logging import getLogger

from .granary_feeder import GranaryFeeder


# Configure the logger
_LOGGER = getLogger(__name__)

class OneRFIDSmartFeeder(GranaryFeeder):   
    async def refresh(self):
        await super().refresh()

        # Fetch data from API
        grain_status = await self.api.device_grain_status(self.serial)
        real_info = await self.api.device_real_info(self.serial)

        # Update internal data
        self.update_data({
            "grainStatus": grain_status,
            "realInfo": real_info
        })

    @property
    def today_eating_time(self) -> int:
        eating_time_str = self._data.get("grainStatus", {}).get("eatingTime", "0'0''")
        if not eating_time_str:
            return 0

        try:
            minutes, seconds = map(int, eating_time_str.replace("''", "").split("'"))
            total_seconds = minutes * 60 + seconds
        except ValueError:
            return 0

        return total_seconds
    
    @property
    def today_eating_times(self) -> int:
        quantity = self._data.get("grainStatus", {}).get("todayEatingTimes")
        if not quantity:
            return 0

        return quantity

    @property
    def battery_state(self) -> str:
        return cast(str, self._data.get("realInfo", {}).get("batteryState"))
    
    @property
    def door_state(self) -> bool:
        # Accessing the realInfo section from _data
        state = bool(self._data.get("realInfo", {}).get("barnDoorState"))
        return state

    @property
    def food_dispenser_state(self) -> bool:
        # Accessing the realInfo section from _data
        state = not bool(self._data.get("realInfo", {}).get("grainOutletState"))
        return state
    
    @property
    def door_blocked(self) -> bool:
        # Accessing the realInfo section from _data
        state = bool(self._data.get("realInfo", {}).get("barnDoorError"))
        return state

    @property
    def food_low(self) -> bool:
        # Accessing the realInfo section from _data
        state = not bool(self._data.get("realInfo", {}).get("surplusGrain"))
        return state
