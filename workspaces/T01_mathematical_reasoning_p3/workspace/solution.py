"""
T01: Linear Equations System — Numerical Solution

Solves:
  2x + 3y - z = 8
  -x + 4y + 2z = 5
  3x - y + 4z = 12
"""
from fractions import Fraction
import json


def solve_system():
    """
    Solve using Gaussian elimination with exact fractions.

    Returns:
        dict: x, y, z as both float approximations and exact Fractions
    """
    # Augmented matrix as Fractions for exact arithmetic
    # [ 2   3  -1 |  8 ]
    # [ -1  4   2 |  5 ]
    # [ 3  -1   4 | 12 ]

    # Row 1: divide by 2
    R1 = [Fraction(2, 1), Fraction(3, 1), Fraction(-1, 1), Fraction(8, 1)]
    R2 = [Fraction(-1, 1), Fraction(4, 1), Fraction(2, 1), Fraction(5, 1)]
    R3 = [Fraction(3, 1), Fraction(-1, 1), Fraction(4, 1), Fraction(12, 1)]

    # Normalize R1: R1 = R1 / 2
    for i in range(4):
        R1[i] = R1[i] / 2

    # Eliminate x from R2: R2 = R2 + R1
    for i in range(4):
        R2[i] = R2[i] + R1[i]

    # Eliminate x from R3: R3 = R3 - 3*R1
    for i in range(4):
        R3[i] = R3[i] - Fraction(3, 1) * R1[i]

    # Eliminate y from R3: R3 = R3 + R2
    for i in range(4):
        R3[i] = R3[i] + R2[i]

    # Back substitution
    z = R3[3] / R3[2]
    y = (R2[3] - R2[2] * z) / R2[1]
    x = (R1[3] - R1[2] * z - R1[1] * y) / R1[0]

    result = {
        "x": float(x),
        "x_exact": str(x),
        "y": float(y),
        "y_exact": str(y),
        "z": float(z),
        "z_exact": str(z),
    }
    return result, x, y, z


def verify(x, y, z):
    """Substitute back to verify the solution."""
    eq1 = 2 * x + 3 * y - z
    eq2 = -x + 4 * y + 2 * z
    eq3 = 3 * x - y + 4 * z
    return {
        "2x + 3y - z": float(eq1),
        "expected": 8,
        "check": eq1 == 8 or abs(float(eq1) - 8) < 1e-10,
        "-x + 4y + 2z": float(eq2),
        "expected": 5,
        "check2": eq2 == 5 or abs(float(eq2) - 5) < 1e-10,
        "3x - y + 4z": float(eq3),
        "expected": 12,
        "check3": eq3 == 12 or abs(float(eq3) - 12) < 1e-10,
    }


if __name__ == "__main__":
    result, x, y, z = solve_system()
    print("=== SOLUTION ===")
    print(f"x = {result['x_exact']} ≈ {result['x']:.10f}")
    print(f"y = {result['y_exact']} ≈ {result['y']:.10f}")
    print(f"z = {result['z_exact']} ≈ {result['z']:.10f}")

    v = verify(x, y, z)
    print("\n=== VERIFICATION ===")
    print(f"2x + 3y - z = {v['2x + 3y - z']}  (expected 8)  {'✓' if v['check'] else '✗'}")
    print(f"-x + 4y + 2z = {v['-x + 4y + 2z']}  (expected 5)  {'✓' if v['check2'] else '✗'}")
    print(f"3x - y + 4z  = {v['3x - y + 4z']}  (expected 12) {'✓' if v['check3'] else '✗'}")

    print("\n=== JSON OUTPUT ===")
    print(json.dumps(result, indent=2))
