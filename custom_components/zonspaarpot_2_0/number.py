"""Number platform for Zonspaarpot 2.0."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.const import UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import ZonspaarpotRuntimeData
from .const import DOMAIN
from .entity import ZonspaarpotEntity


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up load target number."""
    runtime_data: ZonspaarpotRuntimeData = entry.runtime_data
    async_add_entities([ZonspaarpotSetLoadNumber(runtime_data)])


class ZonspaarpotSetLoadNumber(ZonspaarpotEntity, NumberEntity):
    """Number entity for /api/v2/setload."""

    _attr_name = "Setload (watt)"
    _attr_native_min_value = 0
    _attr_native_max_value = 2300
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_mode = "box"
    _attr_translation_key = "setload"

    def __init__(self, runtime_data: ZonspaarpotRuntimeData) -> None:
        super().__init__(runtime_data)
        self._attr_unique_id = f"{DOMAIN}_{self._host}_setload"

    @property
    def native_value(self) -> float | None:
        """Return configured maximum load."""
        value = self.coordinator.data.config.get("load", {}).get("maxwatt")
        if value is None:
            return None
        return float(value)

    async def async_set_native_value(self, value: float) -> None:
        """Persist new maximum load configuration."""
        config_load = self.coordinator.data.config.get("load", {})
        wait_after_update = int(config_load.get("waitafterupdate", 1))
        awake = int(config_load.get("awake", 30))
        sleep = int(config_load.get("sleep", 0))

        await self._runtime_data.api.async_save_load_config(
            watt=int(round(value)),
            wait_after_update=wait_after_update,
            awake=awake,
            sleep=sleep,
        )
        await self.coordinator.async_request_refresh()
