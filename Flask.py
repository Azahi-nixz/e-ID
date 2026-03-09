from flask import Flask, render_template_string, request
import uuid
import json
import qrcode
import os

app = Flask(__name__)

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ---------------- USER FORM ----------------
@app.route("/", methods=["GET","POST"])
def home():

    if request.method == "POST":

        name = request.form["name"]
        gender = request.form["gender"]
        birthday = request.form["birthday"]
        job = request.form["job"]
        health = request.form["health"]

        eid = str(uuid.uuid4())


        user = {
            "eid": eid,
            "name": name,
            "gender": gender,
            "birthday": birthday,
            "job": job,
            "health": health
        }

        data = load_data()
        data.append(user)
        save_data(data)

        if not os.path.exists("static"):
            os.makedirs("static")

        qr_link = f"{request.url_root}id/{eid}"
        img = qrcode.make(qr_link)
        img.save(f"static/{eid}.png")

        return render_template_string(id_card_html, user=user)

    return render_template_string(form_html)

@app.route("/id/<eid>")
def show_id(eid):

    users = load_data()

    for user in users:
        if user["eid"] == eid:
            return render_template_string(id_card_html, user=user)

    return "ID not found"

# ---------------- ADMIN PANEL ----------------
@app.route("/admin")
def admin():

    users = load_data()

    query = request.args.get("q")

    if query:
        users = [
            u for u in users
            if query.lower() in u["name"].lower()
            or query.lower() in u["eid"]
        ]

    return render_template_string(admin_html, users=users)


# ---------------- FORM PAGE ----------------
form_html = """
<!DOCTYPE html>
<html>
<head>
<title>e-ID beta</title>

<style>

body{
font-family: Arial;
background:#f5f5f5;
display:flex;
justify-content:center;
align-items:center;
height:100vh;
}

.card{
background:white;
padding:30px;
width:320px;
border-radius:12px;
box-shadow:0 5px 15px rgba(0,0,0,0.2);
}

h1{
text-align:center;
margin-bottom:20px;
}

input,select{
width:100%;
padding:10px;
margin-bottom:10px;
border:1px solid #ddd;
border-radius:6px;
}

button{
width:100%;
padding:12px;
background:black;
color:white;
border:none;
border-radius:6px;
cursor:pointer;
}

button:hover{
background:#333;
}

</style>

</head>

<body>

<div class="card">

<h1>e-ID beta</h1>

<form method="POST">

<input name="name" placeholder="Full Name" required>

<select name="gender">
<option>Male</option>
<option>Female</option>
<option>Other</option>
</select>

<input type="date" name="birthday">

<input name="job" placeholder="Occupation">

<input name="health" placeholder="Health Status">

<button type="submit">Submit</button>

</form>

</div>

</body>
</html>
"""

# ---------------- ID CARD ----------------
id_card_html = """

<!DOCTYPE html>
<html>
<head>

<style>

body{
background:#eaeaea;
font-family:Arial;
display:flex;
justify-content:center;
align-items:center;
height:100vh;
}

.card{
width:360px;
background:white;
border-radius:12px;
box-shadow:0 10px 30px rgba(0,0,0,0.25);
padding:20px;
}

.header{
font-size:20px;
font-weight:bold;
border-bottom:2px solid black;
margin-bottom:15px;
padding-bottom:5px;
text-align:center;
}

.row{
margin:6px 0;
font-size:14px;
}

.qr{
text-align:center;
margin-top:15px;
}

.qr img{
width:140px;
}

.eid{
font-size:10px;
color:#777;
word-wrap:break-word;
}

</style>

</head>

<body>

<div class="card">

<div class="header">Adventurer e-ID</div>

<div class="row"><b>Name:</b> {{user.name}}</div>
<div class="row"><b>Gender:</b> {{user.gender}}</div>
<div class="row"><b>Birthday:</b> {{user.birthday}}</div>
<div class="row"><b>Occupation:</b> {{user.job}}</div>
<div class="row"><b>Health Status:</b> {{user.health}}</div>

<div class="qr">
<img src="/static/{{user.eid}}.png">
</div>

<div class="eid">{{user.eid}}</div>

</div>

</body>
</html>

"""

# ---------------- ADMIN PANEL ----------------
admin_html = """

<!DOCTYPE html>
<html>

<head>

<style>

body{
font-family:Arial;
background:#f4f4f4;
padding:40px;
}

h1{
text-align:center;
margin-bottom:20px;
}

.container{
max-width:900px;
margin:auto;
}

.search{
text-align:center;
margin-bottom:20px;
}

input{
padding:10px;
width:250px;
border:1px solid #ccc;
border-radius:6px;
}

button{
padding:10px 15px;
background:black;
color:white;
border:none;
border-radius:6px;
cursor:pointer;
}

.user{
background:white;
padding:15px;
margin-bottom:12px;
border-radius:8px;
box-shadow:0 3px 10px rgba(0,0,0,0.15);
}

a{
color:black;
text-decoration:none;
font-weight:bold;
}

</style>

</head>

<body>

<h1>Admin Dashboard</h1>

<div class="container">

<div class="search">
<form method="GET">
<input name="q" placeholder="Search name or ID">
<button type="submit">Search</button>
</form>
</div>

{% for user in users %}

<div class="user">

<b>Name:</b> {{user.name}} <br>
<b>Gender:</b> {{user.gender}} <br>
<b>Job:</b> {{user.job}} <br>
<b>Health:</b> {{user.health}} <br>

<a href="/id/{{user.eid}}">View ID</a>

</div>

{% endfor %}

</div>

</body>
</html>

"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)