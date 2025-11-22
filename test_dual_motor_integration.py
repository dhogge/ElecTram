#!/usr/bin/env python3
"""
Test script for dual motor DEP integration.

Compares:
1. Conventional aircraft (baseline)
2. Dual motor DEP (partial DEP with high-lift + cruise motors)
"""

import sys
sys.path.insert(0, 'meow')

from aircraft import HybridElectricAircraft

def test_dual_motor_dep():
    """Test the integrated dual motor DEP system"""

    print("="*80)
    print("DUAL MOTOR DEP INTEGRATION TEST")
    print("="*80)

    # ============================================================================
    # Test 1: Conventional Aircraft (Baseline)
    # ============================================================================
    print("\n" + "="*80)
    print("TEST 1: CONVENTIONAL AIRCRAFT (BASELINE)")
    print("="*80)

    ac_conv = HybridElectricAircraft("Conventional")
    ac_conv.set_powertrain('conventional', Hp_design=0.0)

    try:
        results_conv = ac_conv.size_aircraft(max_iterations=50, tolerance=0.01)
        conv_success = results_conv['converged']
        print(f"\n✓ Conventional aircraft converged successfully")
        print(f"  TOGW: {results_conv['TOGW_lb']:.0f} lb")
        print(f"  Wing: {results_conv['S_wing_ft2']:.1f} ft²")
        print(f"  Fuel: {results_conv['W_fuel_lb']:.0f} lb")
    except Exception as e:
        print(f"\n✗ Conventional aircraft FAILED: {e}")
        conv_success = False
        results_conv = None

    # ============================================================================
    # Test 2: Dual Motor DEP (Partial DEP)
    # ============================================================================
    print("\n" + "="*80)
    print("TEST 2: DUAL MOTOR DEP (PARTIAL DEP)")
    print("="*80)
    print("  12 high-lift motors (inboard) + 2 cruise motors (wingtip)")
    print("  High-lift active: takeoff, climb, landing")
    print("  Cruise motors active: all phases")

    ac_dual = HybridElectricAircraft("Dual-Motor-DEP")
    ac_dual.set_powertrain('dual_motor_dep', Hp_design=0.0)

    try:
        results_dual = ac_dual.size_aircraft(max_iterations=50, tolerance=0.01)
        dual_success = results_dual['converged']
        print(f"\n✓ Dual motor DEP converged successfully")
        print(f"  TOGW: {results_dual['TOGW_lb']:.0f} lb")
        print(f"  Wing: {results_dual['S_wing_ft2']:.1f} ft²")
        print(f"  Battery: {results_dual['W_battery_lb']:.0f} lb")
    except Exception as e:
        print(f"\n✗ Dual motor DEP FAILED: {e}")
        import traceback
        traceback.print_exc()
        dual_success = False
        results_dual = None

    # ============================================================================
    # Comparison
    # ============================================================================
    if conv_success and dual_success:
        print("\n" + "="*80)
        print("COMPARISON: Conventional vs Dual Motor DEP")
        print("="*80)

        print(f"\n{'Parameter':<30} {'Conventional':>15} {'Dual Motor':>15} {'Change':>15}")
        print("-"*80)

        togw_conv = results_conv['TOGW_lb']
        togw_dual = results_dual['TOGW_lb']
        print(f"{'TOGW (lb)':<30} {togw_conv:>15.0f} {togw_dual:>15.0f} {(togw_dual-togw_conv)/togw_conv*100:>14.1f}%")

        wing_conv = results_conv['S_wing_ft2']
        wing_dual = results_dual['S_wing_ft2']
        print(f"{'Wing Area (ft²)':<30} {wing_conv:>15.1f} {wing_dual:>15.1f} {(wing_dual-wing_conv)/wing_conv*100:>14.1f}%")

        fuel_conv = results_conv['W_fuel_lb']
        fuel_dual = results_dual['W_fuel_lb']
        print(f"{'Fuel (lb)':<30} {fuel_conv:>15.0f} {fuel_dual:>15.0f} {(fuel_dual-fuel_conv)/fuel_conv*100:>14.1f}%")

        batt_dual = results_dual['W_battery_lb']
        print(f"{'Battery (lb)':<30} {0:>15.0f} {batt_dual:>15.0f} {'N/A':>15}")

        pree_conv = results_conv['PREE']
        pree_dual = results_dual['PREE']
        print(f"{'PREE (N·m/Wh)':<30} {pree_conv:>15.3f} {pree_dual:>15.3f} {(pree_dual-pree_conv)/pree_conv*100:>14.1f}%")

        print("\n" + "="*80)
        print("KEY FINDINGS")
        print("="*80)
        print(f"  • Wing area reduction: {(wing_conv-wing_dual)/wing_conv*100:.1f}% (from blown lift)")
        print(f"  • TOGW change: {(togw_dual-togw_conv)/togw_conv*100:+.1f}%")
        print(f"  • Efficiency change: {(pree_dual-pree_conv)/pree_conv*100:+.1f}%")
        print(f"  • Battery weight: {batt_dual:.0f} lb ({batt_dual/togw_dual*100:.1f}% of TOGW)")

        if togw_dual < togw_conv * 1.5:
            print(f"\n  ✓ Dual motor DEP is VIABLE (TOGW reasonable)")
        else:
            print(f"\n  ⚠ Dual motor DEP is HEAVY (may need technology improvements)")

    elif conv_success:
        print(f"\n⚠ Dual motor DEP failed to converge, but conventional succeeded")
        print(f"  Conventional TOGW: {results_conv['TOGW_lb']:.0f} lb")

    elif dual_success:
        print(f"\n⚠ Conventional failed to converge, but dual motor DEP succeeded")
        print(f"  Dual motor TOGW: {results_dual['TOGW_lb']:.0f} lb")

    else:
        print(f"\n✗ Both configurations failed to converge")

    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_dual_motor_dep()
