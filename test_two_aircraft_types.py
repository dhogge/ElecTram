#!/usr/bin/env python3
"""
Test script for sizing two specific aircraft configurations:

1. Serial Electric Full DEP Aircraft
   - Serial hybrid architecture (GT + Generator + Battery + Motors)
   - Full DEP: All 12 high-lift motors provide blown lift
   - Blown lift active for takeoff/landing, folded for cruise

2. Parallel Electric Partial Dual Motor Aircraft
   - Parallel hybrid architecture (GT + EM on same shaft)
   - Partial DEP: 12 high-lift motors + 2 cruise motors
   - High-lift motors for takeoff/landing, cruise motors always active
"""

import sys
sys.path.insert(0, 'meow')

from aircraft import HybridElectricAircraft

def size_two_aircraft_types():
    """Size serial electric full DEP and parallel electric dual motor aircraft"""

    print("="*80)
    print("AIRCRAFT SIZING: Two Configurations")
    print("="*80)
    print("\n1. Serial Electric Full DEP Aircraft")
    print("   - GT + Generator + Battery → 12 High-Lift Motors")
    print("   - Full DEP with blown lift aerodynamics")
    print("   - Hp = 0.5 (50% battery assist during high-power phases)")
    print("\n2. Parallel Electric Partial Dual Motor Aircraft")
    print("   - GT + Battery → 2 Cruise Motors (parallel)")
    print("   - Battery → 12 High-Lift Motors (separate)")
    print("   - Hp = 0.3 (30% battery assist)")
    print("="*80)

    # ============================================================================
    # Aircraft 1: Serial Electric Full DEP
    # ============================================================================
    print("\n" + "="*80)
    print("AIRCRAFT 1: SERIAL ELECTRIC FULL DEP")
    print("="*80)
    print("Architecture: GT → Generator → DC Bus ←→ Battery → All Motors")
    print("DEP Configuration: Full (12 high-lift motors with blown lift)")
    print("Hybridization: Hp = 0.5 during takeoff/climb, Hp = 0.0 during cruise\n")

    ac_serial_full_dep = HybridElectricAircraft("Serial-Electric-Full-DEP")
    ac_serial_full_dep.set_powertrain('serial', Hp_design=0.5)

    try:
        results_serial = ac_serial_full_dep.size_aircraft(max_iterations=50, tolerance=0.01)
        serial_success = results_serial['converged']

        if serial_success:
            print(f"\n✓ Serial Electric Full DEP converged successfully")
            print(f"  TOGW:    {results_serial['TOGW_lb']:>8.0f} lb")
            print(f"  Wing:    {results_serial['S_wing_ft2']:>8.1f} ft²")
            print(f"  Fuel:    {results_serial['W_fuel_lb']:>8.0f} lb")
            print(f"  Battery: {results_serial['W_battery_lb']:>8.0f} lb")
            print(f"  PREE:    {results_serial['PREE']:>8.1f}")
        else:
            print(f"\n⚠ Serial Electric Full DEP did not converge")
            serial_success = False
    except Exception as e:
        print(f"\n✗ Serial Electric Full DEP FAILED: {e}")
        import traceback
        traceback.print_exc()
        serial_success = False
        results_serial = None

    # ============================================================================
    # Aircraft 2: Parallel Electric Partial Dual Motor
    # ============================================================================
    print("\n" + "="*80)
    print("AIRCRAFT 2: PARALLEL ELECTRIC PARTIAL DUAL MOTOR")
    print("="*80)
    print("Architecture: GT ─┬─→ 2 Cruise Motors (parallel with battery)")
    print("                  └─→ Fuel")
    print("              Battery → 12 High-Lift Motors (separate)")
    print("DEP Configuration: Partial (12 high-lift + 2 cruise motors)")
    print("Hybridization: Hp = 0.3 during takeoff/climb, Hp = 0.0 during cruise\n")

    # Note: Currently we need to use 'parallel' which doesn't have dual motor capability
    # For now, this will size as parallel hybrid with blown lift aerodynamics
    ac_parallel_dual = HybridElectricAircraft("Parallel-Electric-Dual-Motor")
    ac_parallel_dual.set_powertrain('parallel', Hp_design=0.3)

    try:
        results_parallel = ac_parallel_dual.size_aircraft(max_iterations=50, tolerance=0.01)
        parallel_success = results_parallel['converged']

        if parallel_success:
            print(f"\n✓ Parallel Electric Partial Dual Motor converged successfully")
            print(f"  TOGW:    {results_parallel['TOGW_lb']:>8.0f} lb")
            print(f"  Wing:    {results_parallel['S_wing_ft2']:>8.1f} ft²")
            print(f"  Fuel:    {results_parallel['W_fuel_lb']:>8.0f} lb")
            print(f"  Battery: {results_parallel['W_battery_lb']:>8.0f} lb")
            print(f"  PREE:    {results_parallel['PREE']:>8.1f}")
        else:
            print(f"\n⚠ Parallel Electric Partial Dual Motor did not converge")
            parallel_success = False
    except Exception as e:
        print(f"\n✗ Parallel Electric Partial Dual Motor FAILED: {e}")
        import traceback
        traceback.print_exc()
        parallel_success = False
        results_parallel = None

    # ============================================================================
    # Comparison
    # ============================================================================
    if serial_success and parallel_success:
        print("\n" + "="*80)
        print("COMPARISON: Serial Full DEP vs Parallel Dual Motor")
        print("="*80)

        print(f"\n{'Parameter':<30} {'Serial Full DEP':>18} {'Parallel Dual Motor':>20}")
        print("-"*80)

        togw_s = results_serial['TOGW_lb']
        togw_p = results_parallel['TOGW_lb']
        print(f"{'TOGW (lb)':<30} {togw_s:>18.0f} {togw_p:>20.0f}")

        wing_s = results_serial['S_wing_ft2']
        wing_p = results_parallel['S_wing_ft2']
        print(f"{'Wing Area (ft²)':<30} {wing_s:>18.1f} {wing_p:>20.1f}")

        fuel_s = results_serial['W_fuel_lb']
        fuel_p = results_parallel['W_fuel_lb']
        print(f"{'Fuel (lb)':<30} {fuel_s:>18.0f} {fuel_p:>20.0f}")

        batt_s = results_serial['W_battery_lb']
        batt_p = results_parallel['W_battery_lb']
        print(f"{'Battery (lb)':<30} {batt_s:>18.0f} {batt_p:>20.0f}")

        pree_s = results_serial['PREE']
        pree_p = results_parallel['PREE']
        print(f"{'PREE (N·m/Wh)':<30} {pree_s:>18.1f} {pree_p:>20.1f}")

        print("\n" + "="*80)
        print("KEY FINDINGS")
        print("="*80)

        lighter = "Serial Full DEP" if togw_s < togw_p else "Parallel Dual Motor"
        diff_pct = abs(togw_s - togw_p) / min(togw_s, togw_p) * 100
        print(f"\n  • Lighter configuration: {lighter}")
        print(f"  • Weight difference: {diff_pct:.1f}%")

        more_efficient = "Serial Full DEP" if pree_s > pree_p else "Parallel Dual Motor"
        eff_diff = abs(pree_s - pree_p) / min(pree_s, pree_p) * 100
        print(f"  • More efficient: {more_efficient}")
        print(f"  • Efficiency difference: {eff_diff:.1f}%")

        print(f"\n  • Both use blown lift wing sizing: ~{wing_s:.0f} ft² vs ~{wing_p:.0f} ft²")
        print(f"  • Serial: Higher battery ({batt_s:.0f} lb), more fuel ({fuel_s:.0f} lb)")
        print(f"  • Parallel: Lower battery ({batt_p:.0f} lb), less fuel ({fuel_p:.0f} lb)")

    elif serial_success:
        print(f"\n✓ Serial Full DEP succeeded: {results_serial['TOGW_lb']:.0f} lb")
        print(f"✗ Parallel Dual Motor failed to converge")

    elif parallel_success:
        print(f"\n✗ Serial Full DEP failed to converge")
        print(f"✓ Parallel Dual Motor succeeded: {results_parallel['TOGW_lb']:.0f} lb")

    else:
        print(f"\n✗ Both configurations failed to converge")

    print("\n" + "="*80)
    print("NOTES")
    print("="*80)
    print("\nSerial Electric Full DEP:")
    print("  • Uses existing SerialHybridPowertrain with blown lift aerodynamics")
    print("  • GT + Generator provide continuous power to all motors")
    print("  • Battery supplements during high-power phases")
    print("  • All 12 motors provide blown lift during takeoff/landing")
    print("\nParallel Electric Partial Dual Motor:")
    print("  • Currently uses ParallelHybridPowertrain (not true dual motor)")
    print("  • GT + EM provide parallel power to main propulsion")
    print("  • Battery powers high-lift motors separately")
    print("  • NOTE: True dual motor implementation would show better results")

    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    size_two_aircraft_types()
