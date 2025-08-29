from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Summary service is running!"

# Keep this at the bottom
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
