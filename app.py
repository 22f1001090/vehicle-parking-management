from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///vehichledb.sqlite3"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "thisismysecretkeyiitm@1234"

db = SQLAlchemy(app)
app.app_context().push()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'




# ------------------------Models-------------------------------
class User(UserMixin, db.Model):
    __tablename__='user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique = True, nullable = False)
    passhash = db.Column(db.String(100), nullable = False)
    fullname = db.Column(db.String(50), nullable = False)
    address = db.Column(db.String(200), nullable = False)
    pincode = db.Column(db.Integer, nullable = False)
    is_admin = db.Column(db.Boolean, nullable = False, default = False)
 
    @property
    def password(self):
        raise AttributeError("password is not an readable attribute")
    
    @password.setter
    def password(self, password):
        self.passhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.passhash, password)


class Parking_Lot(db.Model):
    __tablename__='parking_lot'
    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(200), nullable = False)
    price = db.Column(db.Float, nullable = False)
    address = db.Column(db.String(200), nullable = False)
    pincode = db.Column(db.Integer, nullable = False)
    maximum_no_of_spots = db.Column(db.Integer, nullable = False)
    spots = db.relationship('Parking_Spot', backref = 'parkinglot',lazy = True, cascade="all, delete-orphan")


class Parking_Spot(db.Model):
    __tablename__='parking_spot'
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable = False)
    status = db.Column(db.String(1), default='A')

class Reservation(db.Model):
    __tablename__='reservation'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable = False)
    vehicle_no = db.Column(db.String(12), nullable = False)
    start_time = db.Column(db.DateTime, nullable = False)
    end_time = db.Column(db.DateTime)
    parking_cost = db.Column(db.Float)

with app.app_context():
    db.create_all()
    admin = User.query.filter_by(username = 'admin@123gmail.com').first()
    if not admin:
        admin = User(username='admin@123gmail.com', password = 'admin', fullname = 'admin', address = 'address', pincode = 000000, is_admin = True)
        db.session.add(admin)
        db.session.commit()




#-----------------------Routes---------------------------------

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))






#-----------------------Index Routes---------------------------------

@app.route('/')
def index():
    return render_template("index.html")


#-----------------------User Authentication Routes------------------------------

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user=="" or password=="":
            flash("please fill email and password")
            return redirect("/login")
        if not user:
            flash("User does not exist")
            return redirect('/login')
        if not user.check_password(password):
            flash("incorrect password")
            return redirect('/login')
        
        login_user(user)
        if user.is_admin:
            return redirect("/admin/dashboard")
        else:
            return redirect("/user/dashboard")


    return render_template("login.html")



@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == "POST":
        username=request.form["email"]
        password=request.form["password"]
        fullname=request.form["fullName"]
        address=request.form["address"]
        pincode=request.form["pincode"]

        if username=="" and password=="":
            flash("Please fill up username and password")
            return redirect("/register")
        if User.query.filter_by(username=username).first():
            flash("User with this username already exists. Please choose some other name")
            return redirect("/register")

        user = User(username = username, password = password, fullname = fullname, address = address, pincode = pincode)
        db.session.add(user)
        db.session.commit()
        flash("user successfully registered")
        return redirect('/login')
    return render_template("register.html")


#-----------------------Admin Dashboard Routes---------------------------------


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash("Unauthorized Access")
        return redirect('/login') 
    parking_lots = Parking_Lot.query.all() 
    return render_template("admin_dashboard.html", parking_lots = parking_lots, user = current_user)

#-----------------------Admin Parking Lot CRUD Operations Routes---------------------------------

@app.route('/admin/create', methods=["GET", 'POST'])
@login_required
def create_parking_lot():
    if not current_user.is_admin:
        flash("You are not allowed to create.")
        return redirect('login')
    
    if request.method == "POST":
        prime_location_name = request.form["location"]
        price = request.form["price"]
        address = request.form["address"]
        pincode = request.form["pincode"]
        maximum_no_of_spots = request.form["spots"] 

        
        lot = Parking_Lot(prime_location_name = prime_location_name, price = price, address = address, pincode = pincode, maximum_no_of_spots = maximum_no_of_spots)
        db.session.add(lot)
        db.session.commit()

        for i in range(int(maximum_no_of_spots)):
            spot = Parking_Spot(lot_id = lot.id, status = 'A')
            db.session.add(spot)
        db.session.commit()

        flash("New Parking Lot is added.")
        return redirect('/admin/dashboard')
    
    return render_template('create_parking_lot.html')
        


@app.route("/admin/parking_lot/<int:lot_id>/update", methods=["GET", "POST"])
@login_required
def update_parking_lot(lot_id):
    if not current_user.is_admin:
        flash("You are not allowed to update.")
        return redirect('login')
    
    lot = Parking_Lot.query.get(lot_id)

    if request.method == "POST":
        lot.prime_location_name = request.form["location"]
        lot.price = request.form["price"]
        lot.address = request.form["address"]
        lot.pincode = request.form["pincode"]
        lot.maximum_no_of_spots = request.form["spots"]

        db.session.commit()
        flash("Parking Lot updated successfully")
        return redirect('/admin/dashboard')
    return render_template('update_parking_lot.html', lot = lot)

@app.route("/admin/parking_lot/<int:lot_id>/delete")
@login_required
def delete_parking_lot(lot_id):
    if not current_user.is_admin:
        flash("You are not allowed to delete.")
        return redirect('login')
    
    lot = Parking_Lot.query.get(lot_id)

    for spot in lot.spots:
        if spot.status=='O':
            flash("You cannot delete parking lot")
            return redirect('/admin/dashboard')
    db.session.delete(lot)
    db.session.commit()
    return redirect('/admin/dashboard')



#-----------------------Admin Parking Spot Routes---------------------------------

@app.route("/admin/parking_lot/<int:spot_id>")
@login_required
def admin_parking_spot_status(spot_id):
    if not current_user.is_admin:
        flash("You are not allowed to see status.")
        return redirect('login')
    
    spot = Parking_Spot.query.get(spot_id)
    
    return render_template("admin_parking_spot_status.html", spot = spot )


@app.route("/admin/parking_spot/delete/<int:spot_id>")
@login_required
def delete_parking_spot(spot_id):
    if not current_user.is_admin:
        flash("You are not allowed to delete parking lot.")
        return redirect('login')
    
    spot=Parking_Spot.query.get(spot_id)
    if spot.status=='O':
        flash("You cannot delete occupated parking spot.")
        return redirect('/admin/dashboard')
    
    db.session.delete(spot)
    db.session.commit()
    flash("A Parking Spot successfully deleted.")
    return redirect('/admin/dashboard')


@app.route("/admin/occupied_spot_details/<int:spot_id>")
@login_required
def occupied_spot_details(spot_id):
    if not current_user.is_admin:
        flash("You are not allowed to see status.")
        return redirect('login')
    
    spot = Parking_Spot.query.get(spot_id)
    reserve = Reservation.query.filter_by(spot_id = spot_id).first()

    parking_duration = datetime.now() - reserve.start_time
    parking_duration_hour = parking_duration.total_seconds()//3600

    est_parking_cost = parking_duration_hour*(spot.parkinglot.price)
    
    return render_template("parking_spot_detail.html", reserve = reserve, est_parking_cost = est_parking_cost)

@app.route("/admin/users")
@login_required
def admin_users():
    if not current_user.is_admin:
        flash("You are not allowed to see users.")
        return redirect('login')
    
    users = User.query.all()
    return render_template("admin_users.html", users = users, user = current_user)


#-----------------------Admin Search Routes---------------------------------

@app.route("/admin/search", methods=["GET"])
@login_required
def admin_search():
    if not current_user.is_admin:
        flash("Unauthorized access.")
        return redirect('/login')
    
    search_by = request.args.get("search_by")
    search_term = request.args.get("search_term")
    results = []

    if search_by and search_term:
        if search_by == "user_id":
            results = Reservation.query.filter_by(user_id=search_term).all()
        elif search_by == "spot_id":
            spot = Parking_Spot.query.filter_by(id=search_term).first()
            if spot:
                lot = Parking_Lot.query.get(spot.lot_id)
                if lot:
                    results = [lot]
        elif search_by == "location":
            results = Parking_Lot.query.filter(
                Parking_Lot.prime_location_name.ilike(f"%{search_term}%")
            ).all()
        else:
            flash("Invalid search category selected.")

    return render_template("admin_search.html", results=results, search_by=search_by, search_term=search_term, user = current_user)



#-----------------------Admin Summary Routes---------------------------------
def plot_to_base64(fig):
    img = io.BytesIO()
    fig.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    return base64.b64encode(img.read()).decode('utf-8')

@app.route('/admin/summary')
@login_required
def admin_summary():
    if not current_user.is_admin:
        flash("Unauthorized access.")
        return redirect('/login')

    lots = Parking_Lot.query.all()

    lot_names = []
    revenues = []
    pincodes = []
    available_counts = []
    occupied_counts = []

    for lot in lots:
        total_revenue = 0
        available = 0
        occupied = 0

        for spot in lot.spots:
            if spot.status == 'A':
                available += 1
            elif spot.status == 'O':
                occupied += 1

            for reservation in Reservation.query.filter_by(spot_id=spot.id).all():
                if reservation.parking_cost:
                    total_revenue += reservation.parking_cost

        lot_names.append(lot.prime_location_name or "Unnamed")
        pincodes.append(lot.pincode)
        revenues.append(total_revenue)
        available_counts.append(available)
        occupied_counts.append(occupied)

    # --- PIE Chart: Revenue (only if revenue exists) ---
    revenue_chart = None
    if any(revenues):
        fig1, ax1 = plt.subplots()
        ax1.pie(
            revenues,
            labels=lot_names,
            autopct='%1.1f%%',
            startangle=90,
            wedgeprops=dict(width=0.4)
        )
        ax1.set_title('Revenue per Parking Lot')
        revenue_chart = plot_to_base64(fig1)
        plt.close(fig1)

    # --- BAR Chart: Always show availability ---
    fig2, ax2 = plt.subplots()
    x = range(len(lot_names))
    ax2.bar(x, available_counts, label='Available', color='skyblue')
    ax2.bar(x, occupied_counts, bottom=available_counts, label='Occupied', color='salmon')
    ax2.set_xticks(x)
    ax2.set_xticklabels(lot_names, rotation=45, ha='right')
    ax2.set_ylabel('No. of Spots')
    ax2.set_title('Spot Availability')
    ax2.legend()
    status_chart = plot_to_base64(fig2)
    plt.close(fig2)

    lot_data = zip(lot_names, pincodes, available_counts, occupied_counts, revenues)

    return render_template("admin_summary.html",
                           revenue_chart=revenue_chart,
                           status_chart=status_chart,
                           lot_data=lot_data,
                           user=current_user)




#-----------------------User Dashboard Routes---------------------------------



@app.route('/user/dashboard')
@login_required
def user_dashboard():
    if current_user.is_admin:
        flash("Unauthorized Access")
        return redirect('/login')

    search_query = request.args.get('search', '').strip()

    # Search logic for parking lots
    if search_query:
        if search_query.isdigit():
            parking_lots = Parking_Lot.query.filter_by(pincode=int(search_query)).all()
        else:
            parking_lots = Parking_Lot.query.filter(
                Parking_Lot.prime_location_name.ilike(f"%{search_query}%")
            ).all()
    else:
        parking_lots = Parking_Lot.query.all()

    reservations = Reservation.query.filter_by(user_id=current_user.id)\
        .order_by(Reservation.start_time.desc()).all()

    user_reservations = []
    for res in reservations:
        spot = Parking_Spot.query.get(res.spot_id)
        lot = Parking_Lot.query.get(spot.lot_id)
        user_reservations.append({
            "id": res.id,
            "vehicle_no": res.vehicle_no,
            "start_time": res.start_time,
            "end_time": res.end_time,
            "parking_cost": res.parking_cost,
            "location_name": lot.prime_location_name
        })

    return render_template(
        'user_dashboard.html',
        parking_lots=parking_lots,
        user=current_user,
        reservations=user_reservations
    )

#-----------------------User Parking Spot Booking Routes---------------------------------


@app.route("/user/book/parking_spot/<int:lot_id>", methods=["GET", "POST"])
@login_required
def book_parking_spot(lot_id):
    if current_user.is_admin:
        flash("Unauthorized Access")
        return redirect('/login')
    
    lot = Parking_Lot.query.get(lot_id)
    for spot in lot.spots:
        if spot.status=='A':
            available_spot=spot.id
            break
    
    if request.method == "POST":
        user_id = current_user.id
        spot_id = available_spot
        vehicle_no = request.form["vehicle"]
        start_time = datetime.now()
        
        reserve = Reservation(user_id = user_id, spot_id = spot_id, vehicle_no = vehicle_no, start_time = start_time)
        db.session.add(reserve)
        updated_spot = Parking_Spot.query.get(available_spot)
        updated_spot.status='O'
        db.session.commit()


    return render_template('book_parking_spot.html', lot=lot, user = current_user, available_spot = available_spot)



@app.route('/user/release/<int:reservation_id>', methods=["GET", "POST"])
@login_required
def release_parking_spot(reservation_id):
    if current_user.is_admin:
        flash("Unauthorized Access")
        return redirect('/login')
    
    reservation = Reservation.query.get(reservation_id)
    if not reservation or reservation.user_id != current_user.id:
        flash("Reservation not found or unauthorized access.")
        return redirect('/user/dashboard')

    spot = Parking_Spot.query.get(reservation.spot_id)
    spot.status = 'A'
    db.session.delete(reservation)
    db.session.commit()
    
    flash("Parking spot released successfully.")
    return redirect('/user/dashboard')
    
#-----------------------User Summary Routes---------------------------------

def plot_to_base64(fig):
    img = io.BytesIO()
    fig.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    return base64.b64encode(img.read()).decode('utf-8')


@app.route('/user/summary')
@login_required
def user_summary():
    if current_user.is_admin:
        flash("Unauthorized Access")
        return redirect('/login')

    reservations = Reservation.query.filter_by(user_id=current_user.id).all()

    # Count usage by location
    location_count = {}
    for res in reservations:
        spot = Parking_Spot.query.get(res.spot_id)
        lot = Parking_Lot.query.get(spot.lot_id)
        location = lot.prime_location_name
        location_count[location] = location_count.get(location, 0) + 1

    # Plot Bar Chart: Number of reservations per location
    fig, ax = plt.subplots()
    locations = list(location_count.keys())
    counts = list(location_count.values())
    ax.bar(locations, counts, color='skyblue')
    ax.set_ylabel('Reservations')
    ax.set_xlabel('Location')
    ax.set_title('User Parking Spot Usage Summary')
    ax.tick_params(axis='x', rotation=45)

    usage_chart = plot_to_base64(fig)
    plt.close(fig)

    return render_template("user_summary.html", chart=usage_chart, user = current_user)




#-----------------------User Logout Route---------------------------------  



@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully")
    return redirect('/login')



if __name__ == '__main__':
    app.debug = True
    app.run()

