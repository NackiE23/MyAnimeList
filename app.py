from flask import Flask, render_template, url_for, request, flash, session, redirect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'slk123jghl35468k90j1@$#%jl324@!!4)($kjvb'

menu = [
    {'name': 'first', 'url': 'first'},
    {'name': 'second', 'url': 'second'},
    {'name': 'third', 'url': 'third'},
]


@app.route("/index/")
@app.route("/")
def index():
    print(url_for("index"))
    return render_template('index.html', title="Врач", menu=menu)


@app.route("/about/")
def about():
    print(url_for("about"))
    return render_template("about.html", title="Про всіх", menu=menu)


@app.route("/first/", methods=["POST", "GET"])
def first():
    if request.method == "POST":
        if len(request.form['username']) > 2:
            flash('Message sended', category="success")
        else:
            flash('Error', category="error")

    return render_template("first.html", title="Send", menu=menu)


@app.route("/profile/<path:username>")  # int, float, path
def profile(username):
    return f"Username: {username}"


@app.route("/login/", methods=["POST", "GET"])
def first():
    if "userLogged" in session:
        return redirect(url_for('profile', username=session['userLogged']))
    elif request.method == "POST" and request.form['username'] == "selfedu" and request.form["psw"] == "123":
        session['userLogged'] = request.form['username']
        return redirect(url_for('profile', username=session['userLogged']))

    return render_template("login.html", title="Login", menu=menu)


@app.errorhandler(404)
def errorhandler404(error):
    return "Page isn`t exist! What are you doing here?", 404


# with app.test_request_context():
#     print(url_for("index"))
#     print(url_for("about"))
#     print(url_for("profile", username="asd"))


if __name__ == "__main__":
    app.run(debug=True)
