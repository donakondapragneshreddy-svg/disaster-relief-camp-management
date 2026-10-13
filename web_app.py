from flask import Flask, render_template_string

app = Flask(__name__)

PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>Disaster Relief Camp Management</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
* { box-sizing: border-box; }
body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #102d27;
    color: #f4fff8;
}
header {
    background: #b8f5d5;
    color: #163d31;
    padding: 22px;
}
h1 { margin: 0 0 8px; font-size: 25px; }
header p { margin: 0; font-size: 13px; }
nav {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    padding: 12px 20px;
    background: #b8f5d5;
}
nav button {
    border: 0;
    padding: 10px 15px;
    background: transparent;
    color: #245b49;
    cursor: pointer;
    border-radius: 6px;
}
nav button.active, nav button:hover {
    background: #164b3b;
    color: white;
}
main { padding: 22px; max-width: 1100px; margin: auto; }
.stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(145px, 1fr));
    gap: 12px;
}
.card {
    background: #205344;
    border: 1px solid #477e69;
    border-radius: 12px;
    padding: 17px;
    margin-bottom: 14px;
}
.number { font-size: 29px; font-weight: bold; }
.muted { color: #c4dfd3; font-size: 13px; }
.columns {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 14px;
    margin-top: 14px;
}
.bar {
    height: 8px;
    background: #416c5d;
    border-radius: 8px;
    margin: 8px 0 15px;
}
.bar span {
    display: block;
    height: 100%;
    background: #a8f0c9;
    border-radius: 8px;
}
.alert { color: #ffb6ae; margin: 16px 0; }
section { display: none; }
section.active { display: block; }
table { width: 100%; border-collapse: collapse; }
th, td {
    text-align: left;
    padding: 11px 8px;
    border-bottom: 1px solid #477e69;
}
input, select {
    padding: 10px;
    border-radius: 6px;
    border: 1px solid #8eb9a5;
    margin: 5px 0 12px;
    max-width: 100%;
}
.action {
    background: #b8f5d5;
    color: #163d31;
    border: 0;
    padding: 10px 15px;
    border-radius: 6px;
    cursor: pointer;
}
@media(max-width:500px) {
    main { padding: 14px; }
    h1 { font-size: 21px; }
    table { font-size: 13px; }
}
</style>
</head>
<body>
<header>
    <h1>Disaster Relief Camp Management System</h1>
    <p>Telangana Flood Response · Demo data for project presentation</p>
</header>

<nav>
    <button class="active" onclick="showTab('overview',this)">Overview</button>
    <button onclick="showTab('needs',this)">Needs</button>
    <button onclick="showTab('distribute',this)">Distribute</button>
    <button onclick="showTab('stock',this)">Stock</button>
    <button onclick="showTab('audit',this)">Audit log</button>
</nav>

<main>
<section id="overview" class="active">
    <div class="stats">
        <div class="card"><div class="number" id="campCount">3</div>Active camps</div>
        <div class="card"><div class="number" id="peopleCount">27</div>People registered</div>
        <div class="card"><div class="number" id="needCount">7</div>Open needs</div>
        <div class="card"><div class="number" id="filledCount">2</div>Needs fulfilled</div>
    </div>
    <div class="columns">
        <div class="card">
            <h3>Needs met by camp</h3>
            <p>Siddipet Relief Camp A · 9 sheltered of 300</p>
            <div class="bar"><span style="width:33%"></span></div>
            <p>Hanamkonda Camp B · 9 sheltered of 180</p>
            <div class="bar"><span style="width:15%"></span></div>
            <p>Gajwel Camp C · 9 sheltered of 220</p>
            <div class="bar"><span style="width:33%"></span></div>
        </div>
        <div class="card">
            <h3>Stock alerts</h3>
            <p class="alert">Tarpaulin tent: only 12 left</p>
            <p class="alert">First-aid kits: only 8 left</p>
            <p class="muted">Low-stock items need attention.</p>
        </div>
    </div>
    <div class="card">
        <h3>Try the demo</h3>
        Open Needs to review requests, Distribute to record sample aid,
        or Stock to check supplies. Demo changes are temporary.
    </div>
</section>

<section id="needs">
    <h2>Relief Needs</h2>
    <div class="card">
        <table>
        <tr><th>Family</th><th>Camp</th><th>Need</th><th>Status</th></tr>
        <tr><td>Ravi Kumar</td><td>Camp A</td><td>Rice</td><td>Open</td></tr>
        <tr><td>Sita Devi</td><td>Camp B</td><td>Blankets</td><td>Open</td></tr>
        <tr><td>Arun Kumar</td><td>Camp C</td><td>First aid</td><td>Fulfilled</td></tr>
        </table>
    </div>
</section>

<section id="distribute">
    <h2>Distribute Aid</h2>
    <div class="card">
        <form onsubmit="recordAid(event)">
            <label>Camp</label><br>
            <select id="camp">
                <option>Camp A</option>
                <option>Camp B</option>
                <option>Camp C</option>
            </select><br>
            <label>Relief item</label><br>
            <select id="item">
                <option>Rice packets</option>
                <option>Blankets</option>
                <option>First-aid kits</option>
                <option>Tarpaulin tents</option>
            </select><br>
            <label>Quantity</label><br>
            <input id="quantity" type="number" min="1" value="1" required><br>
            <button class="action" type="submit">Record demo distribution</button>
        </form>
        <p id="message"></p>
    </div>
</section>

<section id="stock">
    <h2>Available Stock</h2>
    <div class="card">
        <table>
        <tr><th>Item</th><th>Available</th><th>Status</th></tr>
        <tr><td>Rice packets</td><td id="rice">120</td><td>Available</td></tr>
        <tr><td>Blankets</td><td id="blankets">45</td><td>Available</td></tr>
        <tr><td>First-aid kits</td><td id="kits">8</td><td>Low stock</td></tr>
        <tr><td>Tarpaulin tents</td><td id="tents">12</td><td>Low stock</td></tr>
        </table>
    </div>
</section>

<section id="audit">
    <h2>Audit Log</h2>
    <div class="card">
        <p>System initialized with sample disaster-relief data.</p>
        <div id="auditEntries"></div>
    </div>
</section>
</main>

<script>
function showTab(id, button) {
    document.querySelectorAll('section').forEach(
        s => s.classList.remove('active')
    );
    document.getElementById(id).classList.add('active');
    document.querySelectorAll('nav button').forEach(
        b => b.classList.remove('active')
    );
    button.classList.add('active');
}

function recordAid(event) {
    event.preventDefault();

    const item = document.getElementById('item').value;
    const qty = Number(document.getElementById('quantity').value);
    const camp = document.getElementById('camp').value;

    const ids = {
        'Rice packets': 'rice',
        'Blankets': 'blankets',
        'First-aid kits': 'kits',
        'Tarpaulin tents': 'tents'
    };

    const cell = document.getElementById(ids[item]);
    const available = Number(cell.textContent);

    if (qty < 1 || qty > available) {
        document.getElementById('message').textContent =
            'Invalid quantity or insufficient stock.';
        return;
    }

    cell.textContent = available - qty;
    document.getElementById('message').textContent =
        'Demo recorded: ' + qty + ' ' + item + ' for ' + camp + '.';

    const entry = document.createElement('p');
    entry.textContent = qty + ' ' + item + ' → ' + camp;
    document.getElementById('auditEntries').prepend(entry);
    document.getElementById('filledCount').textContent =
        Number(document.getElementById('filledCount').textContent) + 1;
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(PAGE)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
