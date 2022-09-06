from flask import render_template, url_for, flash, redirect, request, jsonify
from website.models import Cafe, User
from website.forms import RegistrationForm, LoginForm, CafeForm
from website import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required


# API
@app.route("/get-cafe/<int:cafe_id>")
def get_cafe(cafe_id):
    cafe = Cafe.query.get(cafe_id)

    return jsonify(cafe=cafe.to_dict())


# API
@app.route("/search")
def get_cafe_at_location():
    query_location = request.args.get("loc")
    cafe = db.session.query(Cafe).filter_by(location=query_location).first()
    if cafe:
        return jsonify(cafe=cafe.to_dict())
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})


# API
@app.route("/all-cafes")
def get_all_cafes():
    cafes = db.session.query(Cafe).all()

    return jsonify(cafes=[cafe.to_dict() for cafe in cafes])


@app.route("/")
def home():
    cafes = Cafe.query.all()

    return render_template("home.html", cafes=cafes)


@app.route("/add-cafe", methods=["GET", "POST"])
@login_required
def add_cafe():
    form = CafeForm()

    if form.validate_on_submit():
        new_cafe = Cafe(
            name=request.form.get("name"),
            map_url=request.form.get("map_url"),
            img_url=request.form.get("img_url"),
            location=request.form.get("location"),
            has_sockets=bool(request.form.get("has_sockets")),
            has_toilet=bool(request.form.get("has_toilet")),
            has_wifi=bool(request.form.get("has_wifi")),
            can_take_calls=bool(request.form.get("can_take_calls")),
            seats=request.form.get("seats"),
            coffee_price=request.form.get("coffee_price"),
        )

        db.session.add(new_cafe)
        db.session.commit()

        flash("The cafe has been added!", 'success')
        return redirect(url_for("home"))

    return render_template("add-cafe.html", title="Add cafe", form=form)


@app.route("/delete/<int:cafe_id>")
@login_required
def delete_cafe(cafe_id):
    cafe = Cafe.query.get(cafe_id)

    if cafe:
        db.session.delete(cafe)
        db.session.commit()

        flash("The cafe has been deleted.", 'success')
        return redirect(url_for("home"))
    else:
        flash(f"Sorry a cafe with that id does not exist.", "danger")
        return redirect(url_for("home"))


@app.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data, method='pbkdf2:sha256', salt_length=8).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        flash("Your account has been created!", 'success')
        return redirect(url_for("login"))

    return render_template("sign-up.html", title="Sign Up", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")

            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash(f"Login unsuccessful, please check email and password", "danger")

    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():
    logout_user()

    return redirect(url_for("home"))
