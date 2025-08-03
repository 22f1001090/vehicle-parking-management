# 🚗 Vehicle Parking App - V1

A web-based multi-user parking management application for 4-wheeler parking lots, developed as part of the **Modern Application Development I** course.

This app allows an **Admin** to manage parking lots and monitor spot usage, and allows **Users** to register, log in, and reserve available parking spots.

---

## 🔧 Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: Jinja2 templating, HTML, CSS, Bootstrap
- **Database**: SQLite (created programmatically, no manual edits)
- **Templating**: Jinja2
- **Optional Tools**: Matplotlib, flask_login, JSON(API)

---

## 👥 Roles

### 👑 Admin (Superuser)

- Exists automatically when the database is created (no registration)
- Can create, update, and delete parking lots
- Can view and manage parking spot statuses
- Can view all registered users
- Can view summary charts

### 🙋 User

- Can register and log in
- Can book a parking spot in a selected parking lot
- Spot is auto-assigned (first available)
- Can release (vacate) the parking spot
- Can view booking history and summaries

---

## 🧱 Database Schema (Basic Structure)

### 🔹 User

- `id`: Primary key
- `username`, `password`, `email`, etc.

### 🔹 Admin

- Exists by default; no registration required

### 🔹 ParkingLot

- `id`: Primary key
- `prime_location_name`
- `price`: Per unit time
- `address`
- `pincode`
- `maximum_number_of_spots`

### 🔹 ParkingSpot

- `id`: Primary key
- `lot_id`: Foreign key (to ParkingLot)
- `status`: A (Available) / O (Occupied)

### 🔹 Reservation

- `id`: Primary key
- `spot_id`: Foreign key (to ParkingSpot)
- `user_id`: Foreign key (to User)
- `parking_timestamp`
- `leaving_timestamp`
- `parking_cost`: Calculated based on time and lot price

---

## 🖥️ Core Functionalities

### 🔐 Authentication

- Admin login (fixed credentials)
- User login/registration
- Role-based access control

### 📊 Admin Dashboard

- View all parking lots and their statuses
- Add/edit/delete parking lots
- Auto-create spots when lot is created
- View all users and reservation records
- Delete parking lot only if all spots are vacant
- View charts and summaries

### 🚙 User Dashboard

- Register and log in
- View available parking lots
- Auto-allocate available spot upon booking
- Vacate spot to release reservation
- Track session time and cost
- View past reservations and usage chart

---

## ➕ Recommended Features (Optional)

- Search for spots (by ID or lot)
- JSON-based API resources for lots/spots/users (Flask/Flask-RESTful)
- Chart.js-based visualizations
- HTML5 and JS form validations
- Flask extensions like `flask_login` for secure sessions
- Responsive Bootstrap UI

---

## 🚀 Getting Started

### 🔹 Clone the Repository

```bash
git clone https://github.com/your-username/vehicle-parking-app.git
cd vehicle-parking-app
