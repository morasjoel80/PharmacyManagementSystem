from flask import Flask
from flask_mysqldb import MySQL
from flask_cors import CORS
import config

app = Flask(__name__)
CORS(app)

# MySQL Configuration
app.config["MYSQL_HOST"] = config.MYSQL_CONFIG["host"]
app.config["MYSQL_USER"] = config.MYSQL_CONFIG["user"]
app.config["MYSQL_PASSWORD"] = config.MYSQL_CONFIG["password"]
app.config["MYSQL_DB"] = config.MYSQL_CONFIG["database"]

mysql = MySQL(app)

@app.route("/")
def home():
    return "Pharmacy Management System API is running!"

if __name__ == "__main__":
    app.run(debug=True)