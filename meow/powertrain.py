from dataclasses import dataclass
from typing import Dict, Optional

# NOTE: config_loader is not imported here; TechnologySpec is created via from_config in main file.

@dataclass
class TechnologySpec:
    """
    Component technology specifications.
    Values are provided via a config-like object with .get(section, key, subkey).
    """
    GT_specific_power_kW_kg: float = None
    GT_efficiency: float = None
    GT_BSFC_kg_kWh: float = None
    EM_specific_power_kW_kg: float = None
    EM_efficiency: float = None
    GEN_specific_power_kW_kg: float = None
    GEN_efficiency: float = None
    battery_specific_energy_Wh_kg: float = None
    battery_specific_power_kW_kg: float = None
    battery_SOC_margin: float = None
    battery_DOD: float = None
    prop_efficiency: float = None

    @classmethod
    def from_config(cls, cfg):
        return cls(
            GT_specific_power_kW_kg=cfg.get('hybrid_system', 'gas_turbine', 'specific_power_kW_kg'),
            GT_efficiency=cfg.get('hybrid_system', 'gas_turbine', 'efficiency'),
            GT_BSFC_kg_kWh=cfg.get('hybrid_system', 'gas_turbine', 'BSFC_kg_kWh'),
            EM_specific_power_kW_kg=cfg.get('hybrid_system', 'electric_motor', 'specific_power_kW_kg'),
            EM_efficiency=cfg.get('hybrid_system', 'electric_motor', 'efficiency'),
            GEN_specific_power_kW_kg=cfg.get('hybrid_system', 'generator', 'specific_power_kW_kg'),
            GEN_efficiency=cfg.get('hybrid_system', 'generator', 'efficiency'),
            battery_specific_energy_Wh_kg=cfg.get('hybrid_system', 'battery', 'specific_energy_Wh_kg'),
            battery_specific_power_kW_kg=cfg.get('hybrid_system', 'battery', 'specific_power_kW_kg'),
            battery_SOC_margin=cfg.get('hybrid_system', 'battery', 'SOC_margin_percent') / 100,
            battery_DOD=cfg.get('hybrid_system', 'battery', 'depth_of_discharge_percent') / 100,
            prop_efficiency=cfg.get('propulsion', 'propeller_efficiency'),
        )

class PowertrainBase:
    """Base class for all powertrain architectures"""
    def __init__(self, name: str, tech: TechnologySpec):
        self.name = name
        self.tech = tech
        # Component masses (lb)
        self.m_GT_lb = 0.0
        self.m_EM_lb = 0.0
        self.m_GEN_lb = 0.0
        self.m_battery_lb = 0.0
        self.m_fuel_lb = 0.0
        # Component powers (kW)
        self.P_GT_kW = 0.0
        self.P_EM_kW = 0.0
        self.P_GEN_kW = 0.0

    def size_components(self, P_shaft_kW: float, Hp: float):
        raise NotImplementedError

    def get_power_split(self, P_required_kW: float, Hp: float) -> Dict:
        raise NotImplementedError

    def get_total_propulsion_weight(self) -> float:
        """Total propulsion system weight (excluding fuel/battery)."""
        return self.m_GT_lb + self.m_EM_lb + self.m_GEN_lb

class ConventionalPowertrain(PowertrainBase):
    """Conventional fuel-only powertrain"""
    def __init__(self, tech: TechnologySpec):
        super().__init__("Conventional", tech)

    def size_components(self, P_shaft_kW: float, Hp: float = 0.0):
        self.P_GT_kW = P_shaft_kW
        self.m_GT_lb = (P_shaft_kW / self.tech.GT_specific_power_kW_kg) * 2.20462
        self.m_EM_lb = 0.0
        self.m_GEN_lb = 0.0

    def get_power_split(self, P_required_kW: float, Hp: float = 0.0) -> Dict:
        fuel_rate_kg_s = (P_required_kW * self.tech.GT_BSFC_kg_kWh) / 3600
        return {
            'P_GT_kW': P_required_kW,
            'P_EM_kW': 0.0,
            'fuel_rate_kg_s': fuel_rate_kg_s,
            'battery_power_W': 0.0,
        }

class ParallelHybridPowertrain(PowertrainBase):
    """
    Parallel Hybrid Architecture: GT and EM both connect to propeller shaft.
    Hp = P_EM / (P_EM + P_GT)
    """
    def __init__(self, tech: TechnologySpec):
        super().__init__("Parallel Hybrid", tech)

    def size_components(self, P_shaft_kW: float, Hp: float):
        self.P_EM_kW = P_shaft_kW * Hp
        self.P_GT_kW = P_shaft_kW * (1 - Hp)
        self.m_EM_lb = (self.P_EM_kW / self.tech.EM_specific_power_kW_kg) * 2.20462
        self.m_GT_lb = (self.P_GT_kW / self.tech.GT_specific_power_kW_kg) * 2.20462
        self.m_GEN_lb = 0.0

    def get_power_split(self, P_required_kW: float, Hp: float) -> Dict:
        P_GT_kW = P_required_kW * (1 - Hp)
        P_EM_kW = P_required_kW * Hp
        fuel_rate_kg_s = (P_GT_kW * self.tech.GT_BSFC_kg_kWh) / 3600
        battery_power_W = (P_EM_kW * 1000) / self.tech.EM_efficiency
        return {
            'P_GT_kW': P_GT_kW,
            'P_EM_kW': P_EM_kW,
            'fuel_rate_kg_s': fuel_rate_kg_s,
            'battery_power_W': battery_power_W,
        }

class SerialHybridPowertrain(PowertrainBase):
    """
    Serial Hybrid: GT drives generator, EM drives propeller.
    Battery supplements generator power. Hp = P_batt / (P_batt + P_gen)
    """
    def __init__(self, tech: TechnologySpec):
        super().__init__("Serial Hybrid", tech)

    def size_components(self, P_shaft_kW: float, Hp: float):
        self.P_EM_kW = P_shaft_kW
        P_electric_kW = P_shaft_kW / self.tech.EM_efficiency
        self.P_GEN_kW = P_electric_kW * (1 - Hp)
        self.P_GT_kW = self.P_GEN_kW / self.tech.GEN_efficiency
        self.m_EM_lb = (self.P_EM_kW / self.tech.EM_specific_power_kW_kg) * 2.20462
        self.m_GEN_lb = (self.P_GEN_kW / self.tech.GEN_specific_power_kW_kg) * 2.20462
        self.m_GT_lb = (self.P_GT_kW / self.tech.GT_specific_power_kW_kg) * 2.20462

    def get_power_split(self, P_required_kW: float, Hp: float) -> Dict:
        P_EM_kW = P_required_kW
        P_electric_kW = P_EM_kW / self.tech.EM_efficiency
        P_battery_kW = P_electric_kW * Hp
        P_generator_kW = P_electric_kW * (1 - Hp)
        P_GT_kW = P_generator_kW / self.tech.GEN_efficiency
        fuel_rate_kg_s = (P_GT_kW * self.tech.GT_BSFC_kg_kWh) / 3600
        battery_power_W = P_battery_kW * 1000
        return {
            'P_GT_kW': P_GT_kW,
            'P_EM_kW': P_EM_kW,
            'fuel_rate_kg_s': fuel_rate_kg_s,
            'battery_power_W': battery_power_W,
        }

class FullyElectricPowertrain(PowertrainBase):
    """Fully electric - battery only."""
    def __init__(self, tech: TechnologySpec):
        super().__init__("Fully Electric", tech)

    def size_components(self, P_shaft_kW: float, Hp: float = 1.0):
        self.P_EM_kW = P_shaft_kW
        self.m_EM_lb = (P_shaft_kW / self.tech.EM_specific_power_kW_kg) * 2.20462
        self.m_GT_lb = 0.0
        self.m_GEN_lb = 0.0

    def get_power_split(self, P_required_kW: float, Hp: float = 1.0) -> Dict:
        battery_power_W = (P_required_kW * 1000) / self.tech.EM_efficiency
        return {
            'P_GT_kW': 0.0,
            'P_EM_kW': P_required_kW,
            'fuel_rate_kg_s': 0.0,
            'battery_power_W': battery_power_W,
        }
