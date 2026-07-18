#!/usr/bin/env python3
"""Solve 3x3 linear system and verify solution."""

import json


def solve():
    """
    2x + 3y -  z =  8
    -x + 4y + 2z =  5
    3x -  y + 4z = 12
    """
    # Using Cramer's rule via numpy-free manual elimination
    # Matrix form: A * [x, y, z]^T = B
    A = [[2, 3, -1],
         [-1, 4, 2],
         [3, -1, 4]]
    B = [8, 5, 12]

    def det3(m):
        """Determinant of 3x3 matrix."""
        return (m[0][0] * (m[1][1]*m[2][2] - m[1][2]*m[2][1])
                - m[0][1] * (m[1][0]*m[2][2] - m[1][2]*m[2][0])
                + m[0][2] * (m[1][0]*m[2][1] - m[1][1]*m[2][0]))

    def replace_col(m, col, vec):
        """Replace column in matrix with vector."""
        r = [row[:] for row in m]
        for i in range(3):
            r[i][col] = vec[i]
        return r

    detA = det3(A)
    assert detA != 0, "Matrix is singular"

    x = det3(replace_col(A, 0, B)) / detA
    y = det3(replace_col(A, 1, B)) / detA
    z = det3(replace_col(A, 2, B)) / detA

    # Round to avoid floating point noise
    x, y, z = round(x, 12), round(y, 12), round(z, 12)

    # Verify all equations
    eq1 = 2*x + 3*y - z
    eq2 = -x + 4*y + 2*z
    eq3 = 3*x - y + 4*z

    result = {
        "x": x,
        "y": y,
        "z": z,
        "as_fractions": {
            "x": "19/7",
            "y": "9/7",
            "z": "9/7"
        },
        "verification": {
            "eq1_2x+3y-z": {"expected": 8, "got": eq1, "pass": abs(eq1 - 8) < 1e-10},
            "eq2_-x+4y+2z": {"expected": 5, "got": eq2, "pass": abs(eq2 - 5) < 1e-10},
            "eq3_3x-y+4z": {"expected": 12, "got": eq3, "pass": abs(eq3 - 12) < 1e-10}
        },
        "all_pass": all(
            abs(eq - expected) < 1e-10
            for eq, expected in [(eq1, 8), (eq2, 5), (eq3, 12)]
        )
    }
    return result


if __name__ == "__main__":
    result = solve()
    print(json.dumps(result, indent=2))

    if result["all_pass"]:
        print(f"\n✅ Solution: x={result['x']}, y={result['y']}, z={result['z']}")
        print(f"   Exact:   x={result['as_fractions']['x']}, y={result['as_fractions']['y']}, z={result['as_fractions']['z']}")
    else:
        print("\n❌ Verification FAILED")
        exit(1)
