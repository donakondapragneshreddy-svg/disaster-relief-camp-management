from flask import Flask, render_template_string, abort
import relief_app

app = Flask(__name__)

HOME_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Disaster Relief Management</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f1f5f9;
            margin: 0;
            color: #172033;
        }
        header {
            background: #123b5d;
            color: white;
            padding: 28px;
            text-align: center;
        }
        main {
            max-width: 900px;
            margin: 30px auto;
            padding: 16px;
        }
        .cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
        }
        .card {
            background: white;
            padding: 22px;
            border-radius: 12px;
            box-shadow: 0 2px 8px #0001;
        }
        a {
            color: #075985;
            font-weight: bold;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <header>
        <h1>Disaster Relief Resource & Camp Management</h1>
        <p>Monitor camps, aid, supplies and volunteers</p>
    </header>
    <main>
        <h2>Database Reports</h2>
        <div class="cards">
        {% for key, title in reports %}
            <div class="card">
                <h3>{{ title }}</h3>
                <a href="/report/{{ key }}">View report →</a>
            </div>
        {% endfor %}
        </div>
    </main>
</body>
</html>
"""

REPORT_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 25px; color: #172033; }
        pre { background: #f1f5f9; padding: 18px; border-radius: 8px;
              overflow-x: auto; white-space: pre-wrap; }
        a { color: #075985; }
    </style>
</head>
<body>
    <a href="/">← Back to dashboard</a>
    <h1>{{ title }}</h1>
    <pre>{{ content }}</pre>
</body>
</html>
"""


@app.route("/")
def home():
    reports = [
        (key, details[0])
        for key, details in relief_app.REPORTS.items()
    ]
    return render_template_string(HOME_PAGE, reports=reports)


@app.route("/report/<key>")
def show_report(key):
    if key not in relief_app.REPORTS:
        abort(404)

    con = relief_app.connect()
    try:
        content = relief_app.report(con, key)
    finally:
        con.close()

    return render_template_string(
        REPORT_PAGE,
        title=relief_app.REPORTS[key][0],
        content=content
    )
