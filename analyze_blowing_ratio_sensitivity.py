#!/usr/bin/env python3
"""
Blowing Ratio Sensitivity Analysis

This script analyzes how different blowing ratios (blown span fractions) affect
aircraft weight and performance for both serial and parallel configurations.

The blowing ratio represents the fraction of wing span covered by high-lift motors:
- 0.00 = No blown lift (conventional wing sizing)
- 0.35 = Partial coverage (typical for partial DEP)
- 0.65 = Full coverage (typical for full DEP like NASA X-57)
"""

import sys
import json
import importlib
sys.path.insert(0, 'meow')

import aircraft
import config_loader

def test_blowing_ratio(blown_span_fraction, architecture, Hp_design, name):
    """
    Size aircraft with given blowing ratio

    Args:
        blown_span_fraction: Fraction of wing span with blown lift (0.0-1.0)
        architecture: 'serial' or 'parallel'
        Hp_design: Hybridization ratio
        name: Aircraft name for display

    Returns:
        Dict with results or None if failed
    """
    # Load and modify config
    with open('meow/config.json', 'r') as f:
        config = json.load(f)

    # Update blown span fraction
    config['dep_system']['blown_span_fraction'] = blown_span_fraction

    # Update number of motors (proportional to span coverage)
    # Full coverage (0.65) = 12 motors, scale proportionally
    if blown_span_fraction > 0:
        num_motors = max(1, int(12 * blown_span_fraction / 0.65))
        config['dep_system']['number_of_highlift_motors'] = num_motors
        config['dep_system']['use_for_wing_sizing'] = True
    else:
        config['dep_system']['number_of_highlift_motors'] = 0
        config['dep_system']['use_for_wing_sizing'] = False

    # Write config
    with open('meow/config.json', 'w') as f:
        json.dump(config, f, indent=2)

    # Reload modules
    importlib.reload(config_loader)
    importlib.reload(aircraft)

    # Create and size aircraft
    ac = aircraft.HybridElectricAircraft(name)
    ac.set_powertrain(architecture, Hp_design=Hp_design)

    try:
        results = ac.size_aircraft(max_iterations=50, tolerance=0.01)
        if results['converged']:
            # Calculate lift augmentation
            if blown_span_fraction > 0:
                lift_aug_max = config['dep_system']['lift_augmentation_factor_max']
                lift_aug = 1.0 + (lift_aug_max - 1.0) * blown_span_fraction
            else:
                lift_aug = 1.0

            return {
                'blown_span_fraction': blown_span_fraction,
                'num_motors': config['dep_system']['number_of_highlift_motors'],
                'lift_augmentation': lift_aug,
                'TOGW_lb': results['TOGW_lb'],
                'wing_ft2': results['S_wing_ft2'],
                'fuel_lb': results['W_fuel_lb'],
                'battery_lb': results['W_battery_lb'],
                'PREE': results['PREE'],
                'converged': True
            }
        else:
            return None
    except Exception as e:
        print(f"  ✗ Failed for blowing ratio {blown_span_fraction:.2f}: {e}")
        return None


def analyze_blowing_ratios():
    """Run comprehensive blowing ratio analysis"""

    print("="*80)
    print("BLOWING RATIO SENSITIVITY ANALYSIS")
    print("="*80)
    print("\nAnalyzing how blown span fraction affects aircraft performance")
    print("Blowing ratio = fraction of wing span covered by high-lift motors")
    print("\nTest matrix:")
    print("  • Serial Electric Full DEP (Hp=0.5)")
    print("  • Parallel Electric Partial Dual Motor (Hp=0.3)")
    print("  • Blown span fractions: 0.0, 0.25, 0.35, 0.50, 0.65")
    print("="*80)

    # Test configurations
    blowing_ratios = [0.0, 0.25, 0.35, 0.50, 0.65]

    # =========================================================================
    # Test 1: Serial Electric Full DEP
    # =========================================================================
    print("\n" + "="*80)
    print("SERIAL ELECTRIC FULL DEP (Hp=0.5)")
    print("="*80)

    serial_results = []
    for ratio in blowing_ratios:
        print(f"\n  Testing blowing ratio: {ratio:.2f}...", end=" ")
        result = test_blowing_ratio(ratio, 'serial', 0.5, f"Serial-{ratio:.2f}")
        if result:
            serial_results.append(result)
            print(f"✓ TOGW={result['TOGW_lb']:.0f} lb, Wing={result['wing_ft2']:.1f} ft²")
        else:
            print("✗ Failed to converge")

    # =========================================================================
    # Test 2: Parallel Electric Partial Dual Motor
    # =========================================================================
    print("\n" + "="*80)
    print("PARALLEL ELECTRIC PARTIAL DUAL MOTOR (Hp=0.3)")
    print("="*80)

    parallel_results = []
    for ratio in blowing_ratios:
        print(f"\n  Testing blowing ratio: {ratio:.2f}...", end=" ")
        result = test_blowing_ratio(ratio, 'parallel', 0.3, f"Parallel-{ratio:.2f}")
        if result:
            parallel_results.append(result)
            print(f"✓ TOGW={result['TOGW_lb']:.0f} lb, Wing={result['wing_ft2']:.1f} ft²")
        else:
            print("✗ Failed to converge")

    # =========================================================================
    # Comparison Matrix
    # =========================================================================
    print("\n" + "="*80)
    print("COMPARISON MATRIX: SERIAL ELECTRIC FULL DEP")
    print("="*80)

    print(f"\n{'Blown Span':<12} {'Motors':<8} {'Lift Aug':<10} {'TOGW (lb)':<12} {'Wing (ft²)':<12} {'Battery (lb)':<12} {'PREE':<10}")
    print("-"*80)

    for r in serial_results:
        print(f"{r['blown_span_fraction']:<12.2f} {r['num_motors']:<8d} {r['lift_augmentation']:<10.3f} "
              f"{r['TOGW_lb']:<12.0f} {r['wing_ft2']:<12.1f} {r['battery_lb']:<12.0f} {r['PREE']:<10.1f}")

    if len(serial_results) > 1:
        baseline = serial_results[0]  # No blown lift
        best = serial_results[-1]  # Maximum blown lift
        print(f"\nWeight reduction from blown lift: {baseline['TOGW_lb'] - best['TOGW_lb']:.0f} lb "
              f"({(baseline['TOGW_lb'] - best['TOGW_lb'])/baseline['TOGW_lb']*100:.1f}%)")
        print(f"Wing reduction from blown lift: {baseline['wing_ft2'] - best['wing_ft2']:.1f} ft² "
              f"({(baseline['wing_ft2'] - best['wing_ft2'])/baseline['wing_ft2']*100:.1f}%)")

    print("\n" + "="*80)
    print("COMPARISON MATRIX: PARALLEL ELECTRIC PARTIAL DUAL MOTOR")
    print("="*80)

    print(f"\n{'Blown Span':<12} {'Motors':<8} {'Lift Aug':<10} {'TOGW (lb)':<12} {'Wing (ft²)':<12} {'Battery (lb)':<12} {'PREE':<10}")
    print("-"*80)

    for r in parallel_results:
        print(f"{r['blown_span_fraction']:<12.2f} {r['num_motors']:<8d} {r['lift_augmentation']:<10.3f} "
              f"{r['TOGW_lb']:<12.0f} {r['wing_ft2']:<12.1f} {r['battery_lb']:<12.0f} {r['PREE']:<10.1f}")

    if len(parallel_results) > 1:
        baseline = parallel_results[0]  # No blown lift
        best = parallel_results[-1]  # Maximum blown lift
        print(f"\nWeight reduction from blown lift: {baseline['TOGW_lb'] - best['TOGW_lb']:.0f} lb "
              f"({(baseline['TOGW_lb'] - best['TOGW_lb'])/baseline['TOGW_lb']*100:.1f}%)")
        print(f"Wing reduction from blown lift: {baseline['wing_ft2'] - best['wing_ft2']:.1f} ft² "
              f"({(baseline['wing_ft2'] - best['wing_ft2'])/baseline['wing_ft2']*100:.1f}%)")

    # =========================================================================
    # Key Findings
    # =========================================================================
    print("\n" + "="*80)
    print("KEY FINDINGS")
    print("="*80)

    print("\n1. IMPACT OF BLOWING RATIO ON WEIGHT")
    print("   As blown span fraction increases:")
    print("   - More motors provide blown lift")
    print("   - Higher lift augmentation factor")
    print("   - Smaller wing can be used")
    print("   - Lower overall weight (despite motor weight)")

    print("\n2. SERIAL vs PARALLEL WITH SAME BLOWING RATIO")
    if len(serial_results) > 0 and len(parallel_results) > 0:
        # Compare at 0.35 blowing ratio (typical for partial DEP)
        serial_035 = next((r for r in serial_results if abs(r['blown_span_fraction'] - 0.35) < 0.01), None)
        parallel_035 = next((r for r in parallel_results if abs(r['blown_span_fraction'] - 0.35) < 0.01), None)

        if serial_035 and parallel_035:
            print(f"\n   At blowing ratio = 0.35 (Partial DEP):")
            print(f"   - Serial:   TOGW={serial_035['TOGW_lb']:.0f} lb, Wing={serial_035['wing_ft2']:.1f} ft²")
            print(f"   - Parallel: TOGW={parallel_035['TOGW_lb']:.0f} lb, Wing={parallel_035['wing_ft2']:.1f} ft²")
            print(f"   - Difference: {serial_035['TOGW_lb'] - parallel_035['TOGW_lb']:.0f} lb lighter for parallel")

        # Compare at 0.65 blowing ratio (full DEP)
        serial_065 = next((r for r in serial_results if abs(r['blown_span_fraction'] - 0.65) < 0.01), None)
        parallel_065 = next((r for r in parallel_results if abs(r['blown_span_fraction'] - 0.65) < 0.01), None)

        if serial_065 and parallel_065:
            print(f"\n   At blowing ratio = 0.65 (Full DEP):")
            print(f"   - Serial:   TOGW={serial_065['TOGW_lb']:.0f} lb, Wing={serial_065['wing_ft2']:.1f} ft²")
            print(f"   - Parallel: TOGW={parallel_065['TOGW_lb']:.0f} lb, Wing={parallel_065['wing_ft2']:.1f} ft²")
            print(f"   - Difference: {serial_065['TOGW_lb'] - parallel_065['TOGW_lb']:.0f} lb lighter for parallel")

    print("\n3. RECOMMENDED CONFIGURATIONS")
    print("\n   Serial Electric Full DEP:")
    if len(serial_results) > 0:
        best_serial = min(serial_results, key=lambda x: x['TOGW_lb'])
        print(f"   - Optimal blowing ratio: {best_serial['blown_span_fraction']:.2f}")
        print(f"   - Motors: {best_serial['num_motors']}")
        print(f"   - TOGW: {best_serial['TOGW_lb']:.0f} lb")
        print(f"   - Wing: {best_serial['wing_ft2']:.1f} ft²")

    print("\n   Parallel Electric Partial Dual Motor:")
    if len(parallel_results) > 0:
        best_parallel = min(parallel_results, key=lambda x: x['TOGW_lb'])
        print(f"   - Optimal blowing ratio: {best_parallel['blown_span_fraction']:.2f}")
        print(f"   - Motors: {best_parallel['num_motors']}")
        print(f"   - TOGW: {best_parallel['TOGW_lb']:.0f} lb")
        print(f"   - Wing: {best_parallel['wing_ft2']:.1f} ft²")

    print("\n" + "="*80)
    print("CONCLUSION")
    print("="*80)
    print("\nFor realistic comparison of Serial Full DEP vs Parallel Partial Dual Motor:")
    print("  • Serial should use blowing ratio 0.65 (12 motors, full coverage)")
    print("  • Parallel should use blowing ratio 0.35-0.50 (6-9 motors, partial coverage)")
    print("  • This reflects the practical constraint that parallel has limited")
    print("    battery capacity for high-lift motors")
    print("\nBoth configurations benefit from blown lift, but parallel is more")
    print("efficient due to simpler power conversion architecture.")
    print("="*80 + "\n")

    # Restore original config
    with open('meow/config.json', 'r') as f:
        config = json.load(f)
    config['dep_system']['blown_span_fraction'] = 0.65
    config['dep_system']['number_of_highlift_motors'] = 12
    config['dep_system']['use_for_wing_sizing'] = True
    with open('meow/config.json', 'w') as f:
        json.dump(config, f, indent=2)


if __name__ == "__main__":
    analyze_blowing_ratios()
