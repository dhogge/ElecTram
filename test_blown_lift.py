#!/usr/bin/env python3
"""
Test script for blown lift aircraft implementation.
Demonstrates the effect of blown lift on aircraft performance.
"""

import sys
sys.path.insert(0, 'meow')

from aircraft import HybridElectricAircraft

def test_blown_lift():
    """Test blown lift implementation by comparing with and without blown lift"""

    print("="*80)
    print("BLOWN LIFT AIRCRAFT TEST")
    print("="*80)

    # Create aircraft
    aircraft = HybridElectricAircraft("DEP Test Aircraft")
    aircraft.set_powertrain('parallel', Hp_design=0.3)

    # Test 1: Get lift augmentation factor
    print("\n1. Testing lift augmentation factor calculation:")
    print(f"   DEP Enabled: {aircraft.dep_enabled}")
    print(f"   Max Augmentation Factor: {aircraft.dep_lift_aug_max}")
    print(f"   Blown Span Fraction: {aircraft.dep_blown_span_fraction}")

    aug_factor_on = aircraft.get_lift_augmentation_factor(blown_lift_active=True)
    aug_factor_off = aircraft.get_lift_augmentation_factor(blown_lift_active=False)

    print(f"\n   Augmentation factor (blown lift ON):  {aug_factor_on:.4f}")
    print(f"   Augmentation factor (blown lift OFF): {aug_factor_off:.4f}")
    print(f"   Lift increase with blown lift: {(aug_factor_on - 1.0) * 100:.1f}%")

    # Test 2: Create missions with different blown lift profiles
    print("\n2. Testing mission creation with blown lift profiles:")

    hybridization_profile = {
        'takeoff': 0.5,
        'climb': 0.3,
        'cruise': 0.2,
        'descent': 0.0,
        'loiter': 0.0,
        'landing': 0.3,
    }

    # Mission with blown lift on for takeoff/landing only (default)
    blown_lift_profile_default = None  # Uses defaults
    segments_default = aircraft.create_mission(hybridization_profile, blown_lift_profile_default)

    print("\n   Default blown lift profile:")
    for seg in segments_default:
        status = "ON" if seg.blown_lift_active else "OFF"
        print(f"   - {seg.name:10s}: blown_lift = {status}")

    # Mission with blown lift on for all segments
    blown_lift_profile_all_on = {
        'takeoff': True,
        'climb': True,
        'cruise': True,
        'descent': True,
        'loiter': True,
        'landing': True,
    }
    segments_all_on = aircraft.create_mission(hybridization_profile, blown_lift_profile_all_on)

    print("\n   All-on blown lift profile:")
    for seg in segments_all_on:
        status = "ON" if seg.blown_lift_active else "OFF"
        print(f"   - {seg.name:10s}: blown_lift = {status}")

    # Mission with blown lift off for all segments
    blown_lift_profile_all_off = {
        'takeoff': False,
        'climb': False,
        'cruise': False,
        'descent': False,
        'loiter': False,
        'landing': False,
    }
    segments_all_off = aircraft.create_mission(hybridization_profile, blown_lift_profile_all_off)

    print("\n   All-off blown lift profile:")
    for seg in segments_all_off:
        status = "ON" if seg.blown_lift_active else "OFF"
        print(f"   - {seg.name:10s}: blown_lift = {status}")

    # Test 3: Verify effective CLmax values
    print("\n3. Testing effective CLmax values:")
    print(f"\n   Base CLmax values:")
    print(f"   - CLmax_clean:   {aircraft.CLmax_clean:.2f}")
    print(f"   - CLmax_takeoff: {aircraft.CLmax_TO:.2f}")
    print(f"   - CLmax_landing: {aircraft.CLmax_land:.2f}")

    print(f"\n   With blown lift active (augmentation = {aug_factor_on:.4f}):")
    print(f"   - CLmax_clean:   {aircraft.CLmax_clean * aug_factor_on:.2f}")
    print(f"   - CLmax_takeoff: {aircraft.CLmax_TO * aug_factor_on:.2f}")
    print(f"   - CLmax_landing: {aircraft.CLmax_land * aug_factor_on:.2f}")

    # Calculate stall speed reduction
    V_stall_ratio = 1.0 / (aug_factor_on ** 0.5)
    print(f"\n   Stall speed reduction: {(1.0 - V_stall_ratio) * 100:.1f}%")
    print(f"   (V_stall with blown lift = {V_stall_ratio:.3f} × V_stall without)")

    print("\n" + "="*80)
    print("BLOWN LIFT TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_blown_lift()
