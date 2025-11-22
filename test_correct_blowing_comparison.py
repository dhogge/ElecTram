#!/usr/bin/env python3
"""
Correct comparison: Serial Full DEP vs Parallel Partial Dual Motor

Serial Electric Full DEP:
- 12 rotors across ENTIRE wing span
- Blowing ratio = 1.0 (100% of wing is blown)
- Lift augmentation = 1.0 + (1.8-1.0) × 1.0 = 1.80 (80% increase!)

Parallel Electric Partial Dual Motor:
- Fewer rotors on PART of wing
- Blowing ratio = 0.5 (50% of wing is blown)
- Lift augmentation = 1.0 + (1.8-1.0) × 0.5 = 1.40 (40% increase)
"""

import sys
import json
import importlib
sys.path.insert(0, 'meow')

import aircraft
import config_loader

def set_blowing_config(blown_span_fraction, num_motors):
    """Update config with blowing parameters"""
    with open('meow/config.json', 'r') as f:
        config = json.load(f)

    config['dep_system']['blown_span_fraction'] = blown_span_fraction
    config['dep_system']['number_of_highlift_motors'] = num_motors
    config['dep_system']['use_for_wing_sizing'] = True if blown_span_fraction > 0 else False

    with open('meow/config.json', 'w') as f:
        json.dump(config, f, indent=2)

    # Reload modules
    importlib.reload(config_loader)
    importlib.reload(aircraft)


def test_correct_comparison():
    """Test with correct blowing ratios"""

    print("="*80)
    print("CORRECT COMPARISON: Full DEP vs Partial Dual Motor")
    print("="*80)
    print("\nSerial Electric FULL DEP:")
    print("  • 12 rotors across ENTIRE wing span")
    print("  • Blowing ratio = 1.0 (100% coverage)")
    print("  • Lift augmentation = 1.80x (80% increase)")
    print("\nParallel Electric PARTIAL Dual Motor:")
    print("  • 6 rotors on PART of wing")
    print("  • Blowing ratio = 0.5 (50% coverage)")
    print("  • Lift augmentation = 1.40x (40% increase)")
    print("="*80)

    # =========================================================================
    # Serial Full DEP with blowing ratio 1.0
    # =========================================================================
    print("\n" + "="*80)
    print("AIRCRAFT 1: SERIAL ELECTRIC FULL DEP (Blowing Ratio = 1.0)")
    print("="*80)

    set_blowing_config(blown_span_fraction=1.0, num_motors=12)

    ac_serial = aircraft.HybridElectricAircraft("Serial-Full-DEP-1.0")
    ac_serial.set_powertrain('serial', Hp_design=0.5)

    try:
        results_serial = ac_serial.size_aircraft(max_iterations=50, tolerance=0.01)
        serial_success = results_serial['converged']

        if serial_success:
            print(f"\n✓ Serial Full DEP (1.0 blowing) converged successfully")
            print(f"  TOGW:    {results_serial['TOGW_lb']:>8.0f} lb")
            print(f"  Wing:    {results_serial['S_wing_ft2']:>8.1f} ft²")
            print(f"  Fuel:    {results_serial['W_fuel_lb']:>8.0f} lb")
            print(f"  Battery: {results_serial['W_battery_lb']:>8.0f} lb")
            print(f"  PREE:    {results_serial['PREE']:>8.1f}")
        else:
            print("\n✗ Failed to converge")
            serial_success = False
    except Exception as e:
        print(f"\n✗ FAILED: {e}")
        serial_success = False
        results_serial = None

    # =========================================================================
    # Parallel Partial with blowing ratio 0.5
    # =========================================================================
    print("\n" + "="*80)
    print("AIRCRAFT 2: PARALLEL ELECTRIC PARTIAL DUAL MOTOR (Blowing Ratio = 0.5)")
    print("="*80)

    set_blowing_config(blown_span_fraction=0.5, num_motors=6)

    ac_parallel = aircraft.HybridElectricAircraft("Parallel-Partial-0.5")
    ac_parallel.set_powertrain('parallel', Hp_design=0.3)

    try:
        results_parallel = ac_parallel.size_aircraft(max_iterations=50, tolerance=0.01)
        parallel_success = results_parallel['converged']

        if parallel_success:
            print(f"\n✓ Parallel Partial (0.5 blowing) converged successfully")
            print(f"  TOGW:    {results_parallel['TOGW_lb']:>8.0f} lb")
            print(f"  Wing:    {results_parallel['S_wing_ft2']:>8.1f} ft²")
            print(f"  Fuel:    {results_parallel['W_fuel_lb']:>8.0f} lb")
            print(f"  Battery: {results_parallel['W_battery_lb']:>8.0f} lb")
            print(f"  PREE:    {results_parallel['PREE']:>8.1f}")
        else:
            print("\n✗ Failed to converge")
            parallel_success = False
    except Exception as e:
        print(f"\n✗ FAILED: {e}")
        parallel_success = False
        results_parallel = None

    # =========================================================================
    # Comparison
    # =========================================================================
    if serial_success and parallel_success:
        print("\n" + "="*80)
        print("FINAL COMPARISON")
        print("="*80)

        print(f"\n{'Parameter':<30} {'Serial Full DEP':>18} {'Parallel Partial':>18}")
        print("-"*80)
        print(f"{'Blowing Ratio':<30} {'1.0 (100%)':>18} {'0.5 (50%)':>18}")
        print(f"{'Lift Augmentation':<30} {'1.80x':>18} {'1.40x':>18}")
        print(f"{'Motors':<30} {12:>18d} {6:>18d}")
        print(f"{'TOGW (lb)':<30} {results_serial['TOGW_lb']:>18.0f} {results_parallel['TOGW_lb']:>18.0f}")
        print(f"{'Wing Area (ft²)':<30} {results_serial['S_wing_ft2']:>18.1f} {results_parallel['S_wing_ft2']:>18.1f}")
        print(f"{'Fuel (lb)':<30} {results_serial['W_fuel_lb']:>18.0f} {results_parallel['W_fuel_lb']:>18.0f}")
        print(f"{'Battery (lb)':<30} {results_serial['W_battery_lb']:>18.0f} {results_parallel['W_battery_lb']:>18.0f}")
        print(f"{'PREE':<30} {results_serial['PREE']:>18.1f} {results_parallel['PREE']:>18.1f}")

        togw_diff = results_parallel['TOGW_lb'] - results_serial['TOGW_lb']
        wing_diff = results_parallel['S_wing_ft2'] - results_serial['S_wing_ft2']
        pree_diff = ((results_parallel['PREE'] - results_serial['PREE']) / results_serial['PREE']) * 100

        print("\n" + "="*80)
        print("KEY FINDINGS")
        print("="*80)
        print(f"\n  • Serial gets 80% lift augmentation (1.80x) vs Parallel's 40% (1.40x)")
        print(f"  • Weight difference: {togw_diff:+.0f} lb ({togw_diff/results_serial['TOGW_lb']*100:+.1f}%)")
        print(f"  • Wing difference: {wing_diff:+.1f} ft² ({wing_diff/results_serial['S_wing_ft2']*100:+.1f}%)")
        print(f"  • Efficiency difference: {pree_diff:+.1f}%")

        if togw_diff < 0:
            print(f"\n  ✓ Parallel is {abs(togw_diff):.0f} lb lighter despite less blown lift")
            print(f"    (Simpler power conversion outweighs blown lift disadvantage)")
        else:
            print(f"\n  ✓ Serial is {abs(togw_diff):.0f} lb lighter due to superior blown lift")
            print(f"    (80% lift augmentation enables much smaller wing)")

        print("\n  This is the CORRECT comparison:")
        print("    - Serial FULL DEP uses entire wing for blown lift")
        print("    - Parallel PARTIAL has limited blown lift coverage")

    # Restore default config
    set_blowing_config(blown_span_fraction=0.65, num_motors=12)

    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    test_correct_comparison()
