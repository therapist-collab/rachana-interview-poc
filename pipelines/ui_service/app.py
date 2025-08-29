from flask import Flask, render_template_string, redirect, url_for
import subprocess

app = Flask(__name__)

HTML = """
<!doctype html>
<title>Thera POC - Trigger UI</title>
<h2>Therapist App POC – Trigger Pipelines</h2>
<form method="post" action="/run-sentiment">
    <button type="submit">Run Sentiment Analysis</button>
</form>
<br>
<form method="post" action="/run-summary">
    <button type="submit">Run Summary Prediction</button>
</form>
<br>
<form method="post" action="/load-summaries">
    <button type="submit">Load Summaries to BigQuery</button>
</form>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/run-sentiment", methods=["POST"])
def run_sentiment():
    subprocess.run(["python", "app/analytics/analyze_sentiment.py"])
    return redirect(url_for("home"))

@app.route("/run-summary", methods=["POST"])
def run_summary():
    subprocess.run(["python", "app/analytics/predict_summary.py"])
    return redirect(url_for("home"))

@app.route("/load-summaries", methods=["POST"])
def load_summaries():
    subprocess.run(["python", "app/load/load_summaries.py"])
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
