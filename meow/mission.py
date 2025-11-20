from dataclasses import dataclass
from atmosphere import atmosisa
from typing import List, Dict, Tuple
import numpy as np

# need to add rest of mission functions from aircraft.py to here

@dataclass
class MissionSegment:
    """Mission segment definition"""
    name: str
    altitude_start_ft: float
    altitude_end_ft: float
    Hp: float = 0.0  # Hybridization ratio for this segment

    # Results 
    time_sec: float = 0.0
    fuel_lb: float = 0.0
    battery_Wh: float = 0.0
    distance_nm: float = 0.0


def create_mission(self, hybridization_profile: Dict[str, float]) -> List[MissionSegment]:
    """
    Create mission profile with segment-specific hybridization
    """
    segments = [
        MissionSegment('takeoff', 0, 35, hybridization_profile.get('takeoff', 0.0)),
        MissionSegment('climb', 35, self.cruise_alt_ft, hybridization_profile.get('climb', 0.0)),
        MissionSegment('cruise', self.cruise_alt_ft, self.cruise_alt_ft,
                        hybridization_profile.get('cruise', 0.0)),
        MissionSegment('descent', self.cruise_alt_ft, 450, hybridization_profile.get('descent', 0.0)),
        MissionSegment('loiter', 450, 450, hybridization_profile.get('loiter', 0.0)),
        MissionSegment('landing', 450, 0, hybridization_profile.get('landing', 0.0)),
    ]

    return segments

# ======================= Simulation helpers ======================= #
def simulate_cruise_segment(self, segment: MissionSegment, W_lb: float, S_ft2: float) -> Tuple:
    """Cruise segment simulation"""
    # Atmospheric conditions
    h_m = segment.altitude_start_ft * 0.3048
    _, _, rho_kg_m3, _ = atmosisa(h_m)
    rho_slug_ft3 = rho_kg_m3 / 515.379

    # Cruise speed
    V_fps = self.cruise_speed_kts * 1.688

    # L/D calculation
    CL = W_lb / (0.5 * rho_slug_ft3 * V_fps**2 * S_ft2)
    CD = self.CD0 + self.K1 * CL**2
    D_lb = 0.5 * rho_slug_ft3 * V_fps**2 * S_ft2 * CD

    # Power required
    P_shaft_HP = D_lb * V_fps / (550 * self.tech.prop_efficiency)
    P_shaft_kW = P_shaft_HP * 0.7457

    # Power split
    power_split = self.powertrain.get_power_split(P_shaft_kW, segment.Hp)

    # Cruise time
    distance_ft = self.range_nm * 6076.12
    time_sec = distance_ft / V_fps

    # Consumption
    fuel_lb = power_split['fuel_rate_kg_s'] * time_sec * 2.20462
    battery_Wh = (power_split['battery_power_W'] * time_sec) / 3600

    segment.distance_nm = self.range_nm

    return time_sec, fuel_lb, battery_Wh

def simulate_climb_segment(self, segment: MissionSegment, W_lb: float, S_ft2: float) -> Tuple:
    """Climb segment simulation"""
    # Average weight during climb (assume 2% fuel burn)
    W_avg = W_lb * 0.99

    # Climb at 1.3 * V_stall for best angle
    rho_sl = 0.002377  # slug/ft³ at sea level
    V_stall_fps = np.sqrt(2 * W_avg / (rho_sl * S_ft2 * self.CLmax_clean))
    V_climb_fps = 1.3 * V_stall_fps

    # Climb gradient (5%)
    gamma = 0.05
    ROC_fps = V_climb_fps * gamma

    # L/D in climb
    CL_climb = W_avg / (0.5 * rho_sl * V_climb_fps**2 * S_ft2)
    CD_climb = self.CD0 + self.K1 * CL_climb**2

    # Thrust required
    T_lb = W_avg * (1/(CL_climb/CD_climb) + gamma)
    P_shaft_HP = T_lb * V_climb_fps / (550 * self.tech.prop_efficiency)
    P_shaft_kW = P_shaft_HP * 0.7457

    # Power split
    power_split = self.powertrain.get_power_split(P_shaft_kW, segment.Hp)

    # Climb time
    alt_change_ft = segment.altitude_end_ft - segment.altitude_start_ft
    time_sec = alt_change_ft / ROC_fps if ROC_fps > 0 else 600

    # Consumption
    fuel_lb = power_split['fuel_rate_kg_s'] * time_sec * 2.20462
    battery_Wh = (power_split['battery_power_W'] * time_sec) / 3600

    return time_sec, fuel_lb, battery_Wh

def simulate_descent_segment(self, segment: MissionSegment, W_lb: float, S_ft2: float) -> Tuple:
    """Descent segment - minimal power"""
    time_sec = 480  # 8 minutes typical descent
    fuel_lb = 0.02 * W_lb  # 2% weight as fuel
    battery_Wh = 100  # Minimal battery use
    return time_sec, fuel_lb, battery_Wh

def simulate_simple_segment(self, segment: MissionSegment, W_lb: float, S_ft2: float) -> Tuple:
    """Simple simulation for other segments"""
    time_sec = 180  # 3 minutes
    fuel_lb = 0.01 * W_lb
    battery_Wh = 200
    return time_sec, fuel_lb, battery_Wh

# ======================= Public API ======================= #
def simulate_mission(self, segments: List[MissionSegment], TOGW_lb: float,
                        S_wing_ft2: float) -> Dict:
    """Time-stepping mission simulation (Method A approach)"""
    W_current_lb = TOGW_lb
    total_fuel_lb = 0.0
    total_battery_Wh = 0.0
    total_time_sec = 0.0

    for segment in segments:
        # Simulate based on segment type
        if segment.name == 'cruise':
            t, f, b = simulate_cruise_segment(self, segment, W_current_lb, S_wing_ft2)
        elif segment.name == 'climb':
            t, f, b = simulate_climb_segment(self, segment, W_current_lb, S_wing_ft2)
        elif segment.name == 'descent':
            t, f, b = simulate_descent_segment(self, segment, W_current_lb, S_wing_ft2)
        else:
            t, f, b = simulate_simple_segment(self, segment, W_current_lb, S_wing_ft2)

        # Update weight
        W_current_lb -= f

        # Store results
        segment.time_sec = t
        segment.fuel_lb = f
        segment.battery_Wh = b

        # Accumulate
        total_fuel_lb += f
        total_battery_Wh += b
        total_time_sec += t

    return {
        'total_fuel_lb': total_fuel_lb,
        'total_battery_Wh': total_battery_Wh,
        'total_time_sec': total_time_sec,
        'segments': segments
    }
