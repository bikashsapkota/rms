# Phase 1 Development Use Cases

Based on the `README.md` and `DEVELOPMENT_PHASES.md` files, here are the detailed use cases for Phase 1 of the Restaurant Management System, organized by user role.

---

### 🏢 **Use Cases for Organization Admin**

The Organization Admin is responsible for managing the entire organization, which can contain multiple restaurants.

| Use Case | API Endpoints |
| :--- | :--- |
| **As an Org Admin, I can create a new restaurant** within my organization so that I can expand my business. | `POST /restaurants` |
| **As an Org Admin, I can list all restaurants** in my organization to get an overview of all my locations. | `GET /restaurants` |
| **As an Org Admin, I can create user accounts** (e.g., Restaurant Managers, Staff) for my organization so that I can delegate responsibilities. | `POST /users` |
| **As an Org Admin, I can view all users** within my organization to manage staff across all locations. | `GET /users` |
| **As an Org Admin, I can update user profiles and roles** within my organization to manage staff changes. | `PUT /users/{id}` |

---

### 🍽️ **Use Cases for Restaurant Manager**

The Restaurant Manager is responsible for the day-to-day operations of a single restaurant.

| Use Case | API Endpoints |
| :--- | :--- |
| **As a Restaurant Manager, I can update the settings and details** of my restaurant (e.g., name, address, phone) to keep information current. | `PUT /restaurants/{id}` |
| **As a Restaurant Manager, I can create new menu categories** (e.g., "Appetizers", "Main Courses") to structure my restaurant's menu. | `POST /menu/categories` |
| **As a Restaurant Manager, I can view all menu categories** for my restaurant to see how the menu is organized. | `GET /menu/categories` |
| **As a Restaurant Manager, I can view the details of a specific menu category** to check its contents. | `GET /menu/categories/{id}` |
| **As a Restaurant Manager, I can update a menu category** to change its name or description. | `PUT /menu/categories/{id}` |
| **As a Restaurant Manager, I can delete a menu category** if it's no longer needed. | `DELETE /menu/categories/{id}` |
| **As a Restaurant Manager, I can create a new menu item** within a category, including its name, description, and price. | `POST /menu/items` |
| **As a Restaurant Manager, I can view all menu items**, with options to filter them (e.g., by category), to manage the menu. | `GET /menu/items` |
| **As a Restaurant Manager, I can view the details of a specific menu item** to check its properties. | `GET /menu/items/{id}` |
| **As a Restaurant Manager, I can update a menu item's** details, such as its price or description. | `PUT /menu/items/{id}` |
| **As a Restaurant Manager, I can delete a menu item** if it is no longer offered. | `DELETE /menu/items/{id}` |
| **As a Restaurant Manager, I can log in to the system** to access my management dashboard. | `POST /auth/login` |
| **As a Restaurant Manager, I can view my own user profile** to see my account details. | `GET /auth/me` |
| **As a Restaurant Manager, I can log out of the system** to securely end my session. | `POST /auth/logout` |

---

### 🧑‍🍳 **Use Cases for Staff**

Staff members have limited permissions focused on viewing information relevant to their roles.

| Use Case | API Endpoints |
| :--- | :--- |
| **As a Staff member, I can log in to the system** to access restaurant information. | `POST /auth/login` |
| **As a Staff member, I can view the restaurant's menu categories and items** so I can answer customer questions. | `GET /menu/categories`<br>`GET /menu/items` |
| **As a Staff member, I can view my own user profile** to check my account details. | `GET /auth/me` |
| **As a Staff member, I can log out of the system** to securely end my session. | `POST /auth/logout` |

---

### 👤 **Use Cases for Customer**

Customers are unauthenticated users who can view the public-facing menu.

| Use Case | API Endpoints |
| :--- | :--- |
| **As a Customer, I can view the public menu** for a restaurant to decide what I want to order. | `GET /menu/public` |
