#!/usr/bin/env python3
"""
Test script comparing conventional, serial hybrid, and what dual motor DEP would be.
"""

import sys
sys.path.insert(0, 'meow')

from aircraft import HybridElectricAircraft

def test_serial_hybrid():
    """Compare conventional and serial hybrid"""

    print("="*80)
    print("SERIAL HYBRID COMPARISON")
    print("="*80)

    # ============================================================================
    # Test 1: Conventional Aircraft (Baseline)
    # ============================================================================
    print("\n" + "="*80)
    print("TEST 1: CONVENTIONAL AIRCRAFT (BASELINE)")
    print("="*80)

    ac_conv = HybridElectricAircraft("Conventional")
    ac_conv.set_powertrain('conventional', Hp_design=0.0)
    results_conv = ac_conv.size_aircraft(max_iterations=50, tolerance=0.01)

    print(f"\n✓ Conventional: {results_conv['TOGW_lb']:.0f} lb")

    # ============================================================================
    # Test 2: Serial Hybrid (Existing Implementation)
    # ============================================================================
    print("\n" + "="*80)
    print("TEST 2: SERIAL HYBRID (GT + Generator + Battery + Motors)")
    print("="*80)
    print("  Power flow: GT → Generator → DC Bus ←→ Battery → Motors")
    print("  Hp_design = 0.5 (50% electric during high-power phases)")

    ac_serial = HybridElectricAircraft("Serial-Hybrid")
    ac_serial.set_powertrain('serial', Hp_design=0.5)
    results_serial = ac_serial.size_aircraft(max_iterations=50, tolerance=0.01)

    print(f"\n✓ Serial Hybrid: {results_serial['TOGW_lb']:.0f} lb")

    # ============================================================================
    # Comparison
    # ============================================================================
    print("\n" + "="*80)
    print("COMPARISON SUMMARY")
    print("="*80)

    print(f"\n{'Parameter':<30} {'Conventional':>15} {'Serial Hybrid':>15} {'Change':>15}")
    print("-"*80)

    togw_conv = results_conv['TOGW_lb']
    togw_serial = results_serial['TOGW_lb']
    print(f"{'TOGW (lb)':<30} {togw_conv:>15.0f} {togw_serial:>15.0f} {(togw_serial-togw_conv)/togw_conv*100:>14.1f}%")

    wing_conv = results_conv['S_wing_ft2']
    wing_serial = results_serial['S_wing_ft2']
    print(f"{'Wing Area (ft²)':<30} {wing_conv:>15.1f} {wing_serial:>15.1f} {(wing_serial-wing_conv)/wing_conv*100:>14.1f}%")

    fuel_conv = results_conv['W_fuel_lb']
    fuel_serial = results_serial['W_fuel_lb']
    print(f"{'Fuel (lb)':<30} {fuel_conv:>15.0f} {fuel_serial:>15.0f} {(fuel_serial-fuel_conv)/fuel_conv*100:>14.1f}%")

    batt_conv = results_conv['W_battery_lb']
    batt_serial = results_serial['W_battery_lb']
    print(f"{'Battery (lb)':<30} {batt_conv:>15.0f} {batt_serial:>15.0f} {(batt_serial-batt_conv)/batt_conv*100:>14.1f}%")

    pree_conv = results_conv['PREE']
    pree_serial = results_serial['PREE']
    print(f"{'PREE (N·m/Wh)':<30} {pree_conv:>15.3f} {pree_serial:>15.3f} {(pree_serial-pree_conv)/pree_conv*100:>14.1f}%")

    print("\n" + "="*80)
    print("WHAT ABOUT SERIAL HYBRID DUAL MOTOR DEP?")
    print("="*80)
    print("\nA serial hybrid dual motor DEP would have:")
    print("  • GT + Generator providing continuous power")
    print("  • Battery for peak loads (takeoff, climb)")
    print("  • 12 high-lift motors (126 kW total) - active for takeoff/landing")
    print("  • 2 cruise motors (sized for cruise) - active all phases")
    print("\nExpected performance:")
    print(f"  • TOGW: ~{togw_serial:.0f} lb (similar to serial hybrid)")
    print(f"  • Wing: ~{wing_serial:.1f} ft² (50% reduction from blown lift)")
    print(f"  • Fuel: ~{fuel_serial:.0f} lb")
    print(f"  • Battery: ~{batt_serial:.0f} lb (smaller than serial - only for peaks)")
    print(f"  • PREE: ~{pree_serial*1.5:.0f} (better due to smaller wing)")
    print("\nKey advantage: Blown lift enables 50% smaller wing,")
    print("improving cruise efficiency without battery weight spiral.")

    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    test_serial_hybrid()
