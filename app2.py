from flask import Flask, render_template, redirect, url_for, request, session

class DnDApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = "your_secret_key"  # Replace with a strong secret key
        self.accounts = {
            "player1": "password1",
            "player2": "password2",
            "player3": "password3",
            "player4": "password4",
        }
        self.characters = {
            "player1": {"name": "Thalion", "class": "Ranger", "abilities": {"STR": 12, "DEX": 16, "CON": 14, "INT": 10, "WIS": 14, "CHA": 8}},
            "player2": {"name": "Kaelen", "class": "Fighter", "abilities": {"STR": 18, "DEX": 14, "CON": 16, "INT": 10, "WIS": 12, "CHA": 10}},
            "player3": {"name": "Sylvara", "class": "Wizard", "abilities": {"STR": 8, "DEX": 14, "CON": 12, "INT": 18, "WIS": 12, "CHA": 14}},
            "player4": {"name": "Ragnar", "class": "Cleric", "abilities": {"STR": 14, "DEX": 10, "CON": 16, "INT": 12, "WIS": 18, "CHA": 12}},
        }
        self.setup_routes()

    def setup_routes(self):
        @self.app.route("/", methods=["GET", "POST"])
        def login():
            if request.method == "POST":
                username = request.form["username"]
                password = request.form["password"]
                if username in self.accounts and self.accounts[username] == password:
                    session["user"] = username
                    return redirect(url_for("character"))
                else:
                    return "Invalid username or password", 401
            return render_template("login.html")

        @self.app.route("/character")
        def character():
            if "user" not in session:
                return redirect(url_for("login"))
            user = session["user"]
            character = self.characters[user]
            return render_template("character.html", character=character)

        @self.app.route("/logout")
        def logout():
            session.pop("user", None)
            return redirect(url_for("login"))

    def run(self):
        self.app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    app_instance = DnDApp()
    app_instance.run()
