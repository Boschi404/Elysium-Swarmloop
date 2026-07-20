#!/usr/bin/env python3
"""Generate OpenAPI-style API documentation as Markdown."""
import json
import sys
from app.main import app

spec = app.openapi()
schemas = spec.get("components", {}).get("schemas", {})

# ═══════════════════════════════════════════════
#  Helper functions (defined BEFORE they are used)
# ═══════════════════════════════════════════════

def _val_from_type(fmeta):
    """Create a plausible example value from a schema field."""
    t = fmeta.get("type", "string")
    if t == "string":
        return "string"
    elif t == "integer":
        return 0
    elif t == "number":
        return 0.0
    elif t == "boolean":
        return False
    elif t == "array" and "items" in fmeta:
        item_ref = fmeta["items"].get("$ref", "")
        if item_ref:
            return [{"product_id": 1, "quantity": 1, "unit_price": "0.00"}]
        return []
    elif t == "object":
        return {}
    return None


def _make_example(sbody):
    """Generate a realistic example from a schema."""
    examples = {
        "UserResponse": {
            "id": 1,
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "age": 30,
            "created_at": "2026-07-20T12:00:00Z",
            "updated_at": "2026-07-20T12:00:00Z",
        },
        "UserCreate": {
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "age": 30,
        },
        "UserUpdate": {
            "name": "Alice J.",
            "age": 31,
        },
        "ProductResponse": {
            "id": 1,
            "name": "Wireless Bluetooth Headphones",
            "description": "High-quality over-ear headphones with noise cancellation",
            "price": "79.99",
            "stock": 150,
            "created_at": "2026-07-20T12:00:00Z",
            "updated_at": "2026-07-20T12:00:00Z",
        },
        "ProductCreate": {
            "name": "Wireless Bluetooth Headphones",
            "description": "High-quality over-ear headphones with noise cancellation",
            "price": "79.99",
            "stock": 150,
        },
        "ProductUpdate": {
            "price": "69.99",
            "stock": 200,
        },
        "OrderResponse": {
            "id": 1,
            "user_id": 1,
            "items": [
                {"product_id": 1, "quantity": 2, "unit_price": "79.99"},
                {"product_id": 3, "quantity": 1, "unit_price": "29.99"},
            ],
            "total": "189.97",
            "status": "pending",
            "shipping_address": "123 Main Street, Springfield, IL 62701",
            "created_at": "2026-07-20T12:00:00Z",
            "updated_at": "2026-07-20T12:00:00Z",
        },
        "OrderCreate": {
            "user_id": 1,
            "items": [
                {"product_id": 1, "quantity": 2, "unit_price": "79.99"},
                {"product_id": 3, "quantity": 1, "unit_price": "29.99"},
            ],
            "shipping_address": "123 Main Street, Springfield, IL 62701",
        },
        "OrderItem": {
            "product_id": 1,
            "quantity": 2,
            "unit_price": "79.99",
        },
    }
    name = sbody.get("title", "")
    if name in examples:
        return examples[name]
    result = {}
    for fname, fmeta in sbody.get("properties", {}).items():
        result[fname] = _val_from_type(fmeta)
    return result


def _build_example_body(op):
    """Build an example JSON body from the request body schema."""
    try:
        rb = op.get("requestBody", {})
        content = rb.get("content", {})
        for ctype, cmeta in content.items():
            cs = cmeta.get("schema", {})
            ref = cs.get("$ref", "")
            ref_name = ref.split("/")[-1] if ref else ""
            if ref_name and ref_name in schemas:
                return json.dumps(_make_example(schemas[ref_name]), indent=2, default=str)
    except Exception:
        pass
    return '{\n  "example": "value"\n}'


def _build_example_response(schema):
    """Build an example response JSON."""
    ref = schema.get("$ref", "")
    if ref:
        ref_name = ref.split("/")[-1]
        if ref_name in schemas:
            return _make_example(schemas[ref_name])
    if schema.get("type") == "array" and "items" in schema:
        item_ref = schema["items"].get("$ref", "")
        if item_ref:
            item_name = item_ref.split("/")[-1]
            if item_name in schemas:
                return [_make_example(schemas[item_name])]
    if "properties" in schema:
        return {k: _val_from_type(v) for k, v in schema["properties"].items()}
    return None


def _schema_table(ref_name):
    """Render an inline schema table for a referenced schema."""
    sbody = schemas.get(ref_name, {})
    lines = []
    lines.append("| Field | Type | Required | Description |")
    lines.append("|-------|------|----------|-------------|")
    props = sbody.get("properties", {})
    required_set = set(sbody.get("required", []))
    for fname, fmeta in props.items():
        ftype = fmeta.get("type", "string")
        if ftype == "array" and "items" in fmeta:
            iref = fmeta["items"].get("$ref", "")
            if iref:
                ftype = f"array[{iref.split('/')[-1]}]"
            else:
                ftype = f"array[{fmeta['items'].get('type', 'object')}]"
        if "$ref" in fmeta:
            ftype = fmeta["$ref"].split("/")[-1]
        if "anyOf" in fmeta:
            ts = [t.get("type", t.get("$ref", "").split("/")[-1]) for t in fmeta["anyOf"]]
            ftype = " | ".join(t for t in ts if t and t != "null")
        req = "✅ Yes" if fname in required_set else "❌ No"
        desc = fmeta.get("description", "")
        L(f"| `{fname}` | `{ftype}` | {req} | {desc} |")
    return "\n".join(lines)


# ═══════════════════════════════════════════════
#  Document builder
# ═══════════════════════════════════════════════

lines = []
def L(text=""):
    lines.append(text)

L("# E-Commerce API — API Documentation")
L()
L("**Version:** 1.0.0")
L()
L("_REST API for managing users, products, and orders with CRUD operations_")
L()
L("---")
L()

# ── Table of Contents ──────────────────────────
L("## Table of Contents")
L()
paths = spec["paths"]
for path, methods in sorted(paths.items()):
    for method in ["get", "post", "put", "delete"]:
        if method in methods:
            op = methods[method]
            anchor = f"{method}{path.replace('/','').replace('{','').replace('}','')}"
            L(f"- [`{method.upper()} {path}`](#{anchor}) — {op['summary']}")
L()
L("---")
L()

# ── Data Schemas ───────────────────────────────
if schemas:
    L("## Data Schemas")
    L()
    for sname, sbody in schemas.items():
        if sname in ("HTTPValidationError", "ValidationError"):
            continue
        L(f"### {sname}")
        L()
        desc = sbody.get("description", "")
        if desc:
            L(f"_{desc}_")
            L()
        L("| Field | Type | Required | Description |")
        L("|-------|------|----------|-------------|")
        props = sbody.get("properties", {})
        required_set = set(sbody.get("required", []))
        for fname, fmeta in props.items():
            ftype = fmeta.get("type", "string")
            if ftype == "array" and "items" in fmeta:
                iref = fmeta["items"].get("$ref", "")
                if iref:
                    ftype = f"array[{iref.split('/')[-1]}]"
                else:
                    ftype = f"array[{fmeta['items'].get('type', 'object')}]"
            if "$ref" in fmeta:
                ftype = fmeta["$ref"].split("/")[-1]
            if "anyOf" in fmeta:
                ts = [t.get("type", t.get("$ref", "").split("/")[-1]) for t in fmeta["anyOf"]]
                ftype = " | ".join(t for t in ts if t and t != "null")
            req = "✅ Yes" if fname in required_set else "❌ No"
            desc = fmeta.get("description", "")
            default = fmeta.get("default", "")
            if default != "" and default is not None:
                desc = f"{desc} (default: `{default}`)"
            L(f"| `{fname}` | `{ftype}` | {req} | {desc} |")
        L()
    L("---")
    L()

# ── Endpoints ──────────────────────────────────
L("## Endpoints")
L()

for path, methods in sorted(paths.items()):
    for method in ["get", "post", "put", "delete"]:
        if method not in methods:
            continue

        op = methods[method]
        anchor = f"{method}{path.replace('/','').replace('{','').replace('}','')}"

        L(f"### `{method.upper()} {path}`")
        L()
        L(f"**Summary:** {op['summary']}")
        L()
        L(f"**Description:** {op['description']}")
        L()
        L(f"**Operation ID:** `{op['operationId']}`")
        L()

        # Path parameters
        path_params = [p for p in op.get("parameters", []) if p.get("in") == "path"]
        query_params = [p for p in op.get("parameters", []) if p.get("in") == "query"]

        if path_params:
            L("#### Path Parameters")
            L()
            L("| Name | Type | Required | Description |")
            L("|------|------|----------|-------------|")
            for p in path_params:
                ps = p.get("schema", {})
                ptype = ps.get("type", "string")
                req = "✅ Yes" if p.get("required") else "❌ No"
                desc = p.get("description", ps.get("description", ""))
                L(f"| `{p['name']}` | `{ptype}` | {req} | {desc} |")
            L()

        if query_params:
            L("#### Query Parameters")
            L()
            L("| Name | Type | Required | Description |")
            L("|------|------|----------|-------------|")
            for p in query_params:
                ps = p.get("schema", {})
                ptype = ps.get("type", "string")
                req = "✅ Yes" if p.get("required") else "❌ No"
                desc = p.get("description", ps.get("description", ""))
                default = ""
                if "default" in ps:
                    default = f" (default: `{ps['default']}`)"
                L(f"| `{p['name']}` | `{ptype}` | {req} | {desc}{default} |")
            L()

        # Request body
        if "requestBody" in op:
            rb = op["requestBody"]
            L("#### Request Body")
            L()
            L(f"**Required:** {rb.get('required', False)}")
            L()
            content = rb.get("content", {})
            for ctype, cmeta in content.items():
                cs = cmeta.get("schema", {})
                ref = cs.get("$ref", "")
                ref_name = ref.split("/")[-1] if ref else ""
                L(f"**Content-Type:** `{ctype}`")
                if ref_name:
                    L(f"**Schema:** [{ref_name}](#{ref_name.lower()})")
                    L()
                    L(_schema_table(ref_name))
                    L()
            L()

        # Responses
        L("#### Responses")
        L()
        for status_code, resp in op["responses"].items():
            desc = resp.get("description", "")
            rcontent = resp.get("content", {})
            L(f"**`{status_code}`** — {desc}")
            if rcontent:
                for _, rmeta in rcontent.items():
                    rs = rmeta.get("schema", {})
                    ref = rs.get("$ref", "")
                    ref_name = ref.split("/")[-1] if ref else ""
                    if ref_name and ref_name not in ("HTTPValidationError", "ValidationError"):
                        L(f"- Schema: [{ref_name}](#{ref_name.lower()})")
                    elif rs.get("type") == "array" and "items" in rs:
                        item_ref = rs["items"].get("$ref", "")
                        item_name = item_ref.split("/")[-1] if item_ref else ""
                        if item_name:
                            L(f"- Schema: array[[{item_name}](#{item_name.lower()})]")
                    elif "properties" in rs:
                        L(f"- Schema: (inline)")
                        for fname, fmeta in rs.get("properties", {}).items():
                            ftype = fmeta.get("type", "string")
                            if "$ref" in fmeta:
                                ftype = fmeta["$ref"].split("/")[-1]
                            desc = fmeta.get("description", "")
                            L(f"  - `{fname}`: `{ftype}` — {desc}")
            L()

        # Example
        L("#### Example")
        L()
        L("<details>")
        L("<summary>Show example request / response</summary>")
        L()
        L("**Request:**")
        L()
        if method == "get":
            if path_params:
                ep = path.replace("{user_id}", "1").replace("{product_id}", "1")
                L(f"```http\nGET {ep}\nHost: api.example.com\nAccept: application/json\n```")
            else:
                L(f"```http\nGET {path}\nHost: api.example.com\nAccept: application/json\n```")
        elif method == "delete":
            ep = path.replace("{user_id}", "1").replace("{product_id}", "1")
            L(f"```http\nDELETE {ep}\nHost: api.example.com\n```")
        elif method == "post":
            L(f"```http\nPOST {path}\nHost: api.example.com\nContent-Type: application/json\n\n{_build_example_body(op)}\n```")
        elif method == "put":
            ep = path.replace("{user_id}", "1").replace("{product_id}", "1")
            L(f"```http\nPUT {ep}\nHost: api.example.com\nContent-Type: application/json\n\n{_build_example_body(op)}\n```")
        L()
        L("**Response:**")
        L()
        for status_code, resp in op["responses"].items():
            if status_code.startswith("2"):
                rcontent = resp.get("content", {})
                if rcontent:
                    for _, rmeta in rcontent.items():
                        rs = rmeta.get("schema", {})
                        example = _build_example_response(rs)
                        if example:
                            L(f"`{status_code}`:")
                            L(f"```json\n{json.dumps(example, indent=2, default=str)}\n```")
                else:
                    L(f"`{status_code}`: *(no content)*")
                break
        L()
        L("</details>")
        L()
        L("---")
        L()

# ── Error Codes ────────────────────────────────
L()
L("## Common Error Codes")
L()
L("| Status | Meaning | Typical Cause |")
L("|--------|---------|---------------|")
L("| `400` | Bad Request | Invalid or missing fields in request body |")
L("| `404` | Not Found | Resource ID does not exist |")
L("| `422` | Validation Error | Request body fails Pydantic validation |")
L("| `500` | Internal Server Error | Unexpected server-side failure |")
L()

# ── Authentication ─────────────────────────────
L("## Authentication")
L()
L("This API does not currently require authentication. All endpoints are publicly accessible.")
L()

# ── Server ─────────────────────────────────────
L("## Server")
L()
L("Base URL: `http://localhost:8000`")
L()

output = "\n".join(lines)
print(output)
