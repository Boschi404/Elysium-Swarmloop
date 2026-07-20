# E-Commerce API — API Documentation

**Version:** 1.0.0

_REST API for managing users, products, and orders with CRUD operations_

---

## Table of Contents

- [`POST /orders`](#postorders) — Create an order
- [`GET /products`](#getproducts) — List all products
- [`POST /products`](#postproducts) — Create a product
- [`GET /products/{product_id}`](#getproductsproduct_id) — Get product by ID
- [`PUT /products/{product_id}`](#putproductsproduct_id) — Update a product
- [`GET /users`](#getusers) — List all users
- [`POST /users`](#postusers) — Create a user
- [`GET /users/{user_id}`](#getusersuser_id) — Get user by ID
- [`PUT /users/{user_id}`](#putusersuser_id) — Update a user
- [`DELETE /users/{user_id}`](#deleteusersuser_id) — Delete a user

---

## Data Schemas

### OrderCreate

_Request model for creating an order._

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_id` | `integer` | ✅ Yes | ID of the user placing the order |
| `items` | `array[OrderItem-Input]` | ✅ Yes | Order items (at least 1) |
| `shipping_address` | `string` | ✅ Yes | Shipping address |

### OrderItem-Input

_An item within an order._

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `product_id` | `integer` | ✅ Yes | ID of the product being ordered |
| `quantity` | `integer` | ✅ Yes | Quantity (must be positive) |
| `unit_price` | `number | string` | ✅ Yes | Price per unit at time of order |

### OrderItem-Output

_An item within an order._

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `product_id` | `integer` | ✅ Yes | ID of the product being ordered |
| `quantity` | `integer` | ✅ Yes | Quantity (must be positive) |
| `unit_price` | `string` | ✅ Yes | Price per unit at time of order |

### OrderResponse

_Response model for an order._

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `integer` | ✅ Yes |  |
| `user_id` | `integer` | ✅ Yes |  |
| `items` | `array[OrderItem-Output]` | ✅ Yes |  |
| `total` | `string` | ✅ Yes |  |
| `status` | `string` | ✅ Yes |  |
| `shipping_address` | `string` | ✅ Yes |  |
| `created_at` | `string` | ✅ Yes |  |
| `updated_at` | `string` | ✅ Yes |  |

### ProductCreate

_Request model for creating a product._

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | `string` | ✅ Yes | Product name |
| `description` | `string` | ❌ No | Product description |
| `price` | `number | string` | ✅ Yes | Price in EUR (positive) |
| `stock` | `integer` | ❌ No | Available stock quantity (default: `0`) |

### ProductResponse

_Response model for a product._

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `integer` | ✅ Yes |  |
| `name` | `string` | ✅ Yes |  |
| `description` | `string` | ✅ Yes |  |
| `price` | `string` | ✅ Yes |  |
| `stock` | `integer` | ✅ Yes |  |
| `created_at` | `string` | ✅ Yes |  |
| `updated_at` | `string` | ✅ Yes |  |

### ProductUpdate

_Request model for updating a product. All fields optional._

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | `string` | ❌ No | Product name |
| `description` | `string` | ❌ No | Product description |
| `price` | `number | string` | ❌ No | Price in EUR |
| `stock` | `integer` | ❌ No | Available stock |

### UserCreate

_Request model for creating a user._

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | `string` | ✅ Yes | Full name, at least 3 characters |
| `email` | `string` | ✅ Yes | Valid email address |
| `age` | `integer` | ✅ Yes | Age (1–149) |

### UserResponse

_Response model for a user._

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `integer` | ✅ Yes |  |
| `name` | `string` | ✅ Yes |  |
| `email` | `string` | ✅ Yes |  |
| `age` | `integer` | ✅ Yes |  |
| `created_at` | `string` | ✅ Yes |  |
| `updated_at` | `string` | ✅ Yes |  |

### UserUpdate

_Request model for updating a user. All fields optional._

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | `string` | ❌ No | Full name |
| `email` | `string` | ❌ No | Valid email address |
| `age` | `integer` | ❌ No | Age (1–149) |

---

## Endpoints

### `POST /orders`

**Summary:** Create an order

**Description:** Place a new order with one or more items.

**Operation ID:** `create_order_orders_post`

#### Request Body

**Required:** True

**Content-Type:** `application/json`
**Schema:** [OrderCreate](#ordercreate)

| `user_id` | `integer` | ✅ Yes | ID of the user placing the order |
| `items` | `array[OrderItem-Input]` | ✅ Yes | Order items (at least 1) |
| `shipping_address` | `string` | ✅ Yes | Shipping address |
| Field | Type | Required | Description |
|-------|------|----------|-------------|


#### Responses

**`201`** — Successful Response
- Schema: [OrderResponse](#orderresponse)

**`422`** — Validation Error

#### Example

<details>
<summary>Show example request / response</summary>

**Request:**

```http
POST /orders
Host: api.example.com
Content-Type: application/json

{
  "user_id": 1,
  "items": [
    {
      "product_id": 1,
      "quantity": 2,
      "unit_price": "79.99"
    },
    {
      "product_id": 3,
      "quantity": 1,
      "unit_price": "29.99"
    }
  ],
  "shipping_address": "123 Main Street, Springfield, IL 62701"
}
```

**Response:**

`201`:
```json
{
  "id": 1,
  "user_id": 1,
  "items": [
    {
      "product_id": 1,
      "quantity": 2,
      "unit_price": "79.99"
    },
    {
      "product_id": 3,
      "quantity": 1,
      "unit_price": "29.99"
    }
  ],
  "total": "189.97",
  "status": "pending",
  "shipping_address": "123 Main Street, Springfield, IL 62701",
  "created_at": "2026-07-20T12:00:00Z",
  "updated_at": "2026-07-20T12:00:00Z"
}
```

</details>

---

### `GET /products`

**Summary:** List all products

**Description:** Retrieve the full product catalogue.

**Operation ID:** `list_products_products_get`

#### Responses

**`200`** — Successful Response
- Schema: array[[ProductResponse](#productresponse)]

#### Example

<details>
<summary>Show example request / response</summary>

**Request:**

```http
GET /products
Host: api.example.com
Accept: application/json
```

**Response:**

`200`:
```json
[
  {
    "id": 1,
    "name": "Wireless Bluetooth Headphones",
    "description": "High-quality over-ear headphones with noise cancellation",
    "price": "79.99",
    "stock": 150,
    "created_at": "2026-07-20T12:00:00Z",
    "updated_at": "2026-07-20T12:00:00Z"
  }
]
```

</details>

---

### `POST /products`

**Summary:** Create a product

**Description:** Add a new product to the catalogue.

**Operation ID:** `create_product_products_post`

#### Request Body

**Required:** True

**Content-Type:** `application/json`
**Schema:** [ProductCreate](#productcreate)

| `name` | `string` | ✅ Yes | Product name |
| `description` | `string` | ❌ No | Product description |
| `price` | `number | string` | ✅ Yes | Price in EUR (positive) |
| `stock` | `integer` | ❌ No | Available stock quantity |
| Field | Type | Required | Description |
|-------|------|----------|-------------|


#### Responses

**`201`** — Successful Response
- Schema: [ProductResponse](#productresponse)

**`422`** — Validation Error

#### Example

<details>
<summary>Show example request / response</summary>

**Request:**

```http
POST /products
Host: api.example.com
Content-Type: application/json

{
  "name": "Wireless Bluetooth Headphones",
  "description": "High-quality over-ear headphones with noise cancellation",
  "price": "79.99",
  "stock": 150
}
```

**Response:**

`201`:
```json
{
  "id": 1,
  "name": "Wireless Bluetooth Headphones",
  "description": "High-quality over-ear headphones with noise cancellation",
  "price": "79.99",
  "stock": 150,
  "created_at": "2026-07-20T12:00:00Z",
  "updated_at": "2026-07-20T12:00:00Z"
}
```

</details>

---

### `GET /products/{product_id}`

**Summary:** Get product by ID

**Description:** Retrieve a single product by its unique identifier.

**Operation ID:** `get_product_products__product_id__get`

#### Path Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `product_id` | `integer` | ✅ Yes |  |

#### Responses

**`200`** — Successful Response
- Schema: [ProductResponse](#productresponse)

**`422`** — Validation Error

#### Example

<details>
<summary>Show example request / response</summary>

**Request:**

```http
GET /products/1
Host: api.example.com
Accept: application/json
```

**Response:**

`200`:
```json
{
  "id": 1,
  "name": "Wireless Bluetooth Headphones",
  "description": "High-quality over-ear headphones with noise cancellation",
  "price": "79.99",
  "stock": 150,
  "created_at": "2026-07-20T12:00:00Z",
  "updated_at": "2026-07-20T12:00:00Z"
}
```

</details>

---

### `PUT /products/{product_id}`

**Summary:** Update a product

**Description:** Partially update a product's fields (name, description, price, stock).

**Operation ID:** `update_product_products__product_id__put`

#### Path Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `product_id` | `integer` | ✅ Yes |  |

#### Request Body

**Required:** True

**Content-Type:** `application/json`
**Schema:** [ProductUpdate](#productupdate)

| `name` | `string` | ❌ No | Product name |
| `description` | `string` | ❌ No | Product description |
| `price` | `number | string` | ❌ No | Price in EUR |
| `stock` | `integer` | ❌ No | Available stock |
| Field | Type | Required | Description |
|-------|------|----------|-------------|


#### Responses

**`200`** — Successful Response
- Schema: [ProductResponse](#productresponse)

**`422`** — Validation Error

#### Example

<details>
<summary>Show example request / response</summary>

**Request:**

```http
PUT /products/1
Host: api.example.com
Content-Type: application/json

{
  "price": "69.99",
  "stock": 200
}
```

**Response:**

`200`:
```json
{
  "id": 1,
  "name": "Wireless Bluetooth Headphones",
  "description": "High-quality over-ear headphones with noise cancellation",
  "price": "79.99",
  "stock": 150,
  "created_at": "2026-07-20T12:00:00Z",
  "updated_at": "2026-07-20T12:00:00Z"
}
```

</details>

---

### `GET /users`

**Summary:** List all users

**Description:** Retrieve every registered user.

**Operation ID:** `list_users_users_get`

#### Responses

**`200`** — Successful Response
- Schema: array[[UserResponse](#userresponse)]

#### Example

<details>
<summary>Show example request / response</summary>

**Request:**

```http
GET /users
Host: api.example.com
Accept: application/json
```

**Response:**

`200`:
```json
[
  {
    "id": 1,
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "age": 30,
    "created_at": "2026-07-20T12:00:00Z",
    "updated_at": "2026-07-20T12:00:00Z"
  }
]
```

</details>

---

### `POST /users`

**Summary:** Create a user

**Description:** Register a new user with name, email and age.

**Operation ID:** `create_user_users_post`

#### Request Body

**Required:** True

**Content-Type:** `application/json`
**Schema:** [UserCreate](#usercreate)

| `name` | `string` | ✅ Yes | Full name, at least 3 characters |
| `email` | `string` | ✅ Yes | Valid email address |
| `age` | `integer` | ✅ Yes | Age (1–149) |
| Field | Type | Required | Description |
|-------|------|----------|-------------|


#### Responses

**`201`** — Successful Response
- Schema: [UserResponse](#userresponse)

**`422`** — Validation Error

#### Example

<details>
<summary>Show example request / response</summary>

**Request:**

```http
POST /users
Host: api.example.com
Content-Type: application/json

{
  "name": "Alice Johnson",
  "email": "alice@example.com",
  "age": 30
}
```

**Response:**

`201`:
```json
{
  "id": 1,
  "name": "Alice Johnson",
  "email": "alice@example.com",
  "age": 30,
  "created_at": "2026-07-20T12:00:00Z",
  "updated_at": "2026-07-20T12:00:00Z"
}
```

</details>

---

### `GET /users/{user_id}`

**Summary:** Get user by ID

**Description:** Retrieve a single user by their unique identifier.

**Operation ID:** `get_user_users__user_id__get`

#### Path Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `user_id` | `integer` | ✅ Yes |  |

#### Responses

**`200`** — Successful Response
- Schema: [UserResponse](#userresponse)

**`422`** — Validation Error

#### Example

<details>
<summary>Show example request / response</summary>

**Request:**

```http
GET /users/1
Host: api.example.com
Accept: application/json
```

**Response:**

`200`:
```json
{
  "id": 1,
  "name": "Alice Johnson",
  "email": "alice@example.com",
  "age": 30,
  "created_at": "2026-07-20T12:00:00Z",
  "updated_at": "2026-07-20T12:00:00Z"
}
```

</details>

---

### `PUT /users/{user_id}`

**Summary:** Update a user

**Description:** Partially update a user's fields (name, email, age).

**Operation ID:** `update_user_users__user_id__put`

#### Path Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `user_id` | `integer` | ✅ Yes |  |

#### Request Body

**Required:** True

**Content-Type:** `application/json`
**Schema:** [UserUpdate](#userupdate)

| `name` | `string` | ❌ No | Full name |
| `email` | `string` | ❌ No | Valid email address |
| `age` | `integer` | ❌ No | Age (1–149) |
| Field | Type | Required | Description |
|-------|------|----------|-------------|


#### Responses

**`200`** — Successful Response
- Schema: [UserResponse](#userresponse)

**`422`** — Validation Error

#### Example

<details>
<summary>Show example request / response</summary>

**Request:**

```http
PUT /users/1
Host: api.example.com
Content-Type: application/json

{
  "name": "Alice J.",
  "age": 31
}
```

**Response:**

`200`:
```json
{
  "id": 1,
  "name": "Alice Johnson",
  "email": "alice@example.com",
  "age": 30,
  "created_at": "2026-07-20T12:00:00Z",
  "updated_at": "2026-07-20T12:00:00Z"
}
```

</details>

---

### `DELETE /users/{user_id}`

**Summary:** Delete a user

**Description:** Remove a user by their ID.

**Operation ID:** `delete_user_users__user_id__delete`

#### Path Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `user_id` | `integer` | ✅ Yes |  |

#### Responses

**`204`** — Successful Response

**`422`** — Validation Error

#### Example

<details>
<summary>Show example request / response</summary>

**Request:**

```http
DELETE /users/1
Host: api.example.com
```

**Response:**

`204`: *(no content)*

</details>

---


## Common Error Codes

| Status | Meaning | Typical Cause |
|--------|---------|---------------|
| `400` | Bad Request | Invalid or missing fields in request body |
| `404` | Not Found | Resource ID does not exist |
| `422` | Validation Error | Request body fails Pydantic validation |
| `500` | Internal Server Error | Unexpected server-side failure |

## Authentication

This API does not currently require authentication. All endpoints are publicly accessible.

## Server

Base URL: `http://localhost:8000`

