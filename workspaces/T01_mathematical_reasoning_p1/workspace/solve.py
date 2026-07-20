"""
T01_mathematical_reasoning - Linear Equations System
Solve: 2x + 3y - z = 8, -x + 4y + 2z = 5, 3x - y + 4z = 12
"""

import json


def det3(m):
    """3x3 determinant via Sarrus' rule."""
    return (
        m[0][0] * m[1][1] * m[2][2]
        + m[0][1] * m[1][2] * m[2][0]
        + m[0][2] * m[1][0] * m[2][1]
        - m[0][2] * m[1][1] * m[2][0]
        - m[0][1] * m[1][0] * m[2][2]
        - m[0][0] * m[1][2] * m[2][1]
    )


def replace_col(m, col, values):
    """Return a copy of matrix m with column `col` replaced by `values`."""
    res = [row[:] for row in m]
    for i in range(3):
        res[i][col] = values[i]
    return res


def solve_linear_system():
    """Solve the 3x3 system using Cramer's rule."""
    A = [[2, 3, -1], [-1, 4, 2], [3, -1, 4]]
    b = [8, 5, 12]

    D = det3(A)
    Dx = det3(replace_col(A, 0, b))
    Dy = det3(replace_col(A, 1, b))
    Dz = det3(replace_col(A, 2, b))

    x = Dx / D
    y = Dy / D
    z = Dz / D

    return {
        "determinants": {"D": D, "Dx": Dx, "Dy": Dy, "Dz": Dz},
        "solution": {"x": x, "y": y, "z": z},
    }


def verify(x, y, z):
    """Check the solution against the original equations."""
    eq1 = 2 * x + 3 * y - z
    eq2 = -x + 4 * y + 2 * z
    eq3 = 3 * x - y + 4 * z
    return {
        "eq1": {"expected": 8, "got": eq1, "pass": abs(eq1 - 8) < 1e-9},
        "eq2": {"expected": 5, "got": eq2, "pass": abs(eq2 - 5) < 1e-9},
        "eq3": {"expected": 12, "got": eq3, "pass": abs(eq3 - 12) < 1e-9},
    }


if __name__ == "__main__":
    result = solve_linear_system()
    s = result["solution"]
    v = verify(s["x"], s["y"], s["z"])

    print("=== LINEAR SYSTEM SOLUTION ===")
    print(f" 2x + 3y - z = 8")
    print(f"-x  + 4y + 2z = 5")
    print(f" 3x -  y + 4z = 12")
    print()
    dets = result["determinants"]
    print(f"D  = {dets['D']}")
    print(f"Dx = {dets['Dx']}")
    print(f"Dy = {dets['Dy']}")
    print(f"Dz = {dets['Dz']}")
    print()
    print(f"x = {s['x']}  ({s['x']:.6f})")
    print(f"y = {s['y']}  ({s['y']:.6f})")
    print(f"z = {s['z']}  ({s['z']:.6f})")
    print()
    print("VERIFICATION:")
    for k, vv in v.items():
        status = "✅ PASS" if vv["pass"] else "❌ FAIL"
        print(f"  {k}: got {vv['got']:.1f}, expected {vv['expected']}  {status}")
    print()
    all_pass = all(x["pass"] for x in v.values())
    print(f"All equations verified: {'YES' if all_pass else 'NO'}")
