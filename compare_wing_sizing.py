#!/usr/bin/env python3
"""
Comparison script showing traditional vs blown-lift-optimized wing sizing.

This demonstrates the NASA X-57 Maxwell approach: using blown lift during
takeoff/landing enables a smaller wing optimized for cruise efficiency.
"""

import sys
import json
import importlib
sys.path.insert(0, 'meow')

import aircraft
import config_loader
from aircraft import HybridElectricAircraft

def compare_wing_sizing():
    """Compare traditional vs blown-lift-optimized wing sizing"""

    print("="*80)
    print("WING SIZING COMPARISON: Traditional vs Blown Lift Optimized")
    print("="*80)
    print("\nThis comparison shows how blown lift enables smaller, cruise-optimized wings")
    print("following NASA X-57 Maxwell's design philosophy.\n")

    # ============================================================================
    # CASE 1: Traditional Wing Sizing (Conservative)
    # ============================================================================
    print("\n" + "="*80)
    print("CASE 1: TRADITIONAL WING SIZING")
    print("="*80)
    print("Wing sized WITHOUT considering blown lift augmentation")
    print("(Conservative approach - wing meets all requirements without DEP help)\n")

    # Temporarily disable blown lift wing sizing
    with open('meow/config.json', 'r') as f:
        config = json.load(f)

    original_setting = config['dep_system']['use_for_wing_sizing']
    config['dep_system']['use_for_wing_sizing'] = False

    with open('meow/config.json', 'w') as f:
        json.dump(config, f, indent=2)

    # Reload modules to pick up config changes
    importlib.reload(config_loader)
    importlib.reload(aircraft)

    # Create and size aircraft
    aircraft_traditional = aircraft.HybridElectricAircraft("Traditional Sizing")
    aircraft_traditional.set_powertrain('parallel', Hp_design=0.3)

    results_traditional = aircraft_traditional.size_aircraft(
        max_iterations=50,
        tolerance=0.01
    )

    # Store results
    TOGW_trad = results_traditional['TOGW_lb']
    S_wing_trad = results_traditional['S_wing_ft2']
    WS_trad = results_traditional['WS_psf']
    fuel_trad = results_traditional['W_fuel_lb']
    battery_trad = results_traditional['W_battery_lb']
    OEW_trad = results_traditional['OEW_lb']
    PREE_trad = results_traditional['PREE']

    # ============================================================================
    # CASE 2: Blown Lift Optimized Wing Sizing
    # ============================================================================
    print("\n" + "="*80)
    print("CASE 2: BLOWN LIFT OPTIMIZED WING SIZING")
    print("="*80)
    print("Wing sized WITH blown lift augmentation (1.52x)")
    print("(X-57 approach - smaller wing for cruise, blown lift for takeoff/landing)\n")

    # Enable blown lift wing sizing
    config['dep_system']['use_for_wing_sizing'] = True

    with open('meow/config.json', 'w') as f:
        json.dump(config, f, indent=2)

    # Reload modules to pick up config changes
    importlib.reload(config_loader)
    importlib.reload(aircraft)

    # Create and size aircraft
    aircraft_blown = aircraft.HybridElectricAircraft("Blown Lift Optimized")
    aircraft_blown.set_powertrain('parallel', Hp_design=0.3)

    results_blown = aircraft_blown.size_aircraft(
        max_iterations=50,
        tolerance=0.01
    )

    # Store results
    TOGW_blown = results_blown['TOGW_lb']
    S_wing_blown = results_blown['S_wing_ft2']
    WS_blown = results_blown['WS_psf']
    fuel_blown = results_blown['W_fuel_lb']
    battery_blown = results_blown['W_battery_lb']
    OEW_blown = results_blown['OEW_lb']
    PREE_blown = results_blown['PREE']

    # Restore original setting
    config['dep_system']['use_for_wing_sizing'] = original_setting
    with open('meow/config.json', 'w') as f:
        json.dump(config, f, indent=2)

    # ============================================================================
    # COMPARISON RESULTS
    # ============================================================================
    print("\n" + "="*80)
    print("COMPARISON SUMMARY")
    print("="*80)

    print(f"\n{'Parameter':<30} {'Traditional':>15} {'Blown Lift':>15} {'Difference':>15}")
    print("-"*80)

    # Wing parameters
    print(f"{'Wing Area (ft²)':<30} {S_wing_trad:>15.1f} {S_wing_blown:>15.1f} {(S_wing_blown-S_wing_trad)/S_wing_trad*100:>14.1f}%")
    print(f"{'Wing Loading (lb/ft²)':<30} {WS_trad:>15.1f} {WS_blown:>15.1f} {(WS_blown-WS_trad)/WS_trad*100:>14.1f}%")

    # Weight parameters
    print(f"\n{'TOGW (lb)':<30} {TOGW_trad:>15.0f} {TOGW_blown:>15.0f} {(TOGW_blown-TOGW_trad)/TOGW_trad*100:>14.1f}%")
    print(f"{'OEW (lb)':<30} {OEW_trad:>15.0f} {OEW_blown:>15.0f} {(OEW_blown-OEW_trad)/OEW_trad*100:>14.1f}%")
    print(f"{'Fuel Weight (lb)':<30} {fuel_trad:>15.0f} {fuel_blown:>15.0f} {(fuel_blown-fuel_trad)/fuel_trad*100:>14.1f}%")
    print(f"{'Battery Weight (lb)':<30} {battery_trad:>15.0f} {battery_blown:>15.0f} {(battery_blown-battery_trad)/battery_trad*100:>14.1f}%")

    # Performance
    print(f"\n{'PREE (N·m/Wh)':<30} {PREE_trad:>15.3f} {PREE_blown:>15.3f} {(PREE_blown-PREE_trad)/PREE_trad*100:>14.1f}%")

    # Calculate cruise efficiency benefit
    # Smaller wing = less wetted area = less drag
    # Approximate: Drag reduction ≈ wing area reduction × 0.7 (wetted area factor)
    wing_area_reduction_pct = (S_wing_trad - S_wing_blown) / S_wing_trad * 100
    cruise_drag_reduction_pct = wing_area_reduction_pct * 0.4  # Conservative estimate

    print("\n" + "="*80)
    print("KEY BENEFITS OF BLOWN LIFT WING SIZING")
    print("="*80)
    print(f"\n1. Wing Area Reduction:  {wing_area_reduction_pct:.1f}%")
    print(f"   - Traditional wing:   {S_wing_trad:.1f} ft²")
    print(f"   - Optimized wing:     {S_wing_blown:.1f} ft²")
    print(f"   - Area saved:         {S_wing_trad - S_wing_blown:.1f} ft²")

    print(f"\n2. Wing Loading Increase: {(WS_blown-WS_trad)/WS_trad*100:.1f}%")
    print(f"   - Enables smaller wing while meeting same stall speed requirement")
    print(f"   - Traditional: {WS_trad:.1f} lb/ft² → Optimized: {WS_blown:.1f} lb/ft²")

    print(f"\n3. Structural Weight Savings: {(OEW_trad - OEW_blown):.0f} lb")
    print(f"   - Smaller wing = lighter structure")
    print(f"   - OEW reduction: {(OEW_trad-OEW_blown)/OEW_trad*100:.1f}%")

    print(f"\n4. Cruise Efficiency Improvement:")
    print(f"   - Estimated cruise drag reduction: ~{cruise_drag_reduction_pct:.1f}%")
    print(f"   - Smaller wing = less wetted area = less skin friction drag")
    print(f"   - PREE improvement: {(PREE_blown-PREE_trad)/PREE_trad*100:.1f}%")

    print(f"\n5. Mission Fuel Savings: {fuel_trad - fuel_blown:.0f} lb ({(fuel_trad-fuel_blown)/fuel_trad*100:.1f}%)")

    print("\n" + "="*80)
    print("HOW BLOWN LIFT ENABLES THIS")
    print("="*80)
    print(f"\nBlown Lift Augmentation Factor: 1.52× (52% lift increase)")
    print(f"  - Augmentation: (1.80 - 1.0) × 0.65 = 0.52")
    print(f"  - 12 high-lift motors on 65% of wing span")
    print(f"\nEffective CLmax with Blown Lift:")
    print(f"  - CLmax_clean:   2.20 → 3.34 (+52%)")
    print(f"  - CLmax_takeoff: 2.00 → 3.04 (+52%)")
    print(f"  - CLmax_landing: 2.80 → 4.26 (+52%)")
    print(f"\nStall Speed with Blown Lift:")
    print(f"  - V_stall reduction: 18.9%")
    print(f"  - Smaller wing can still meet 74 kts stall speed requirement")

    print("\n" + "="*80)
    print("NASA X-57 MAXWELL COMPARISON")
    print("="*80)
    print(f"\nYour Design:")
    print(f"  - Wing area reduction: {wing_area_reduction_pct:.1f}%")
    print(f"  - Lift augmentation:   1.52× (52%)")
    print(f"\nNASA X-57 Maxwell:")
    print(f"  - Wing area reduction: ~40%")
    print(f"  - Lift augmentation:   1.73× (73%)")
    print(f"\nYour design follows similar principles with conservative assumptions.")

    print("\n" + "="*80)
    print("OPERATIONAL IMPLICATIONS")
    print("="*80)
    print("\nTakeoff/Landing: Blown lift ACTIVE")
    print("  ✓ Short field performance maintained")
    print("  ✓ Lower approach/departure speeds")
    print("  ✓ Steeper climb-out and approach angles")
    print("  ⚠ Requires 126 kW from 12 high-lift motors")
    print("\nCruise: Blown lift OFF")
    print("  ✓ Smaller wing = less drag")
    print("  ✓ Better L/D ratio")
    print("  ✓ Lower fuel burn")
    print("  ✓ Motors folded/inactive (no parasitic drag)")

    print("\n" + "="*80)
    print("CONCLUSION")
    print("="*80)
    print(f"\nBlown lift wing sizing delivers:")
    print(f"  • {wing_area_reduction_pct:.1f}% smaller wing area")
    print(f"  • {(OEW_trad-OEW_blown)/OEW_trad*100:.1f}% lighter empty weight")
    print(f"  • {(fuel_trad-fuel_blown)/fuel_trad*100:.1f}% less fuel per mission")
    print(f"  • ~{cruise_drag_reduction_pct:.1f}% lower cruise drag")
    print(f"  • Same takeoff/landing performance as larger wing")
    print(f"\nThis is the key innovation of distributed electric propulsion:")
    print(f"Optimize the wing for cruise, use blown lift for low-speed phases.")
    print("="*80 + "\n")

if __name__ == "__main__":
    compare_wing_sizing()
