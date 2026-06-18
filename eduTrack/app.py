from flask import Flask, request, redirect, session, render_template_string
import statistics

app = Flask(__name__)
app.secret_key = "secret123"

students = []

def calculate(marks):
    total = sum(marks)
    percentage = total / len(marks)

    if percentage >= 90:
        grade = 'A'
    elif percentage >= 75:
        grade = 'B'
    elif percentage >= 50:
        grade = 'C'
    else:
        grade = 'Fail'

    return total, round(percentage,2), grade

LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Login</title>
<style>
body {font-family:Arial;background:#3f51b5;color:white;display:flex;justify-content:center;align-items:center;height:100vh;}
form {background:white;color:black;padding:30px;border-radius:10px;width:250px;}
input {display:block;margin:10px;padding:10px;width:100%;}
button {padding:10px;background:#3f51b5;color:white;border:none;width:100%;}
</style>
</head>
<body>
<form method="POST">
<h2>Admin Login</h2>
<input name="username" placeholder="Username" required>
<input name="password" type="password" placeholder="Password" required>
<button>Login</button>
</form>
</body>
</html>
"""

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>

:root {
--bg:#f4f6f9;
--text:#000;
--card:#fff;
--sidebar:#3f51b5;
}

body.dark {
--bg:#121212;
--text:#fff;
--card:#1e1e1e;
}

body {
margin:0;
font-family:Arial;
display:flex;
background:var(--bg);
color:var(--text);
}

.sidebar {
width:220px;
background:var(--sidebar);
color:white;
height:100vh;
padding:20px;
}

.sidebar a {
display:block;
color:white;
text-decoration:none;
margin:10px 0;
}

.main {
flex:1;
padding:20px;
}

.cards {
display:flex;
gap:15px;
flex-wrap:wrap;
}

.card {
background:var(--card);
padding:20px;
border-radius:10px;
flex:1;
min-width:200px;
}

input,button,select {
padding:10px;
margin:5px;
}

button {
background:#3f51b5;
color:white;
border:none;
cursor:pointer;
}

table {
width:100%;
margin-top:20px;
border-collapse:collapse;
background:var(--card);
}

th,td {
padding:10px;
border-bottom:1px solid #ccc;
}

canvas {
margin-top:20px;
background:var(--card);
padding:10px;
border-radius:10px;
}

/* Mobile */
@media(max-width:768px){
body {flex-direction:column;}
.sidebar {width:100%;height:auto;}
.cards {flex-direction:column;}
}

</style>
</head>

<body id="body">

<div class="sidebar">
<h2>SMS Admin</h2>
<a href="/">Dashboard</a>
<a href="/logout">Logout</a>
<button onclick="toggleDark()">🌙 Toggle Dark</button>
</div>

<div class="main">

<h1>Dashboard</h1>

<div class="cards">
<div class="card"><h3>Total</h3><h2>{{total}}</h2></div>
<div class="card"><h3>Average %</h3><h2>{{avg}}</h2></div>
<div class="card"><h3>Topper</h3><h2>{{topper}}</h2></div>
</div>

<h2>Add Student</h2>
<form method="POST">
<input name="name" placeholder="Name" required>
<input name="att" placeholder="Attendance %" required>
<input name="m1" placeholder="Sub1" required>
<input name="m2" placeholder="Sub2" required>
<input name="m3" placeholder="Sub3" required>
<input name="m4" placeholder="Sub4" required>
<input name="m5" placeholder="Sub5" required>
<button>Add</button>
</form>

<h2>Search & Filter</h2>
<form method="GET">
<input name="search" placeholder="Search by name">
<select name="grade">
<option value="">All Grades</option>
<option>A</option><option>B</option><option>C</option><option>Fail</option>
</select>
<button>Apply</button>
</form>

<h2>Records</h2>
<table>
<tr><th>Name</th><th>%</th><th>Grade</th><th>Attendance</th></tr>
{% for s in students %}
<tr>
<td>{{s.name}}</td>
<td>{{s.percentage}}</td>
<td>{{s.grade}}</td>
<td>{{s.att}}</td>
</tr>
{% endfor %}
</table>

<canvas id="chart1"></canvas>
<canvas id="chart2"></canvas>
<canvas id="chart3"></canvas>

</div>

<script>

// Dark Mode
function toggleDark(){
document.getElementById("body").classList.toggle("dark");
}

// Charts
new Chart(document.getElementById('chart1'), {
type:'bar',
data:{labels:{{names}},datasets:[{label:'%',data:{{percentages}}}]}
});

new Chart(document.getElementById('chart2'), {
type:'bar',
data:{labels:['S1','S2','S3','S4','S5'],datasets:[{label:'Avg',data:{{subject_avg}}}]}
});

new Chart(document.getElementById('chart3'), {
type:'scatter',
data:{datasets:[{label:'Attendance vs %',data:{{scatter}}}]}
});

</script>

</body>
</html>
"""

@app.route("/", methods=["GET","POST"])
def home():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        try:
            name = request.form["name"]
            att = int(request.form["att"])
            marks = [int(request.form[f"m{i}"]) for i in range(1,6)]

            total, percentage, grade = calculate(marks)

            students.append({
                "name": name,
                "marks": marks,
                "percentage": percentage,
                "grade": grade,
                "att": att
            })
        except:
            pass

        return redirect("/")

    search = request.args.get("search","").lower()
    grade_filter = request.args.get("grade","")

    filtered = []
    for s in students:
        if search in s["name"].lower() and (grade_filter=="" or s["grade"]==grade_filter):
            filtered.append(s)

    total = len(filtered)
    avg = round(statistics.mean([s["percentage"] for s in filtered]),2) if filtered else 0
    topper = max(filtered, key=lambda x:x["percentage"])["name"] if filtered else "None"

    names = [s["name"] for s in filtered]
    percentages = [s["percentage"] for s in filtered]

    subject_avg = []
    for i in range(5):
        vals = [s["marks"][i] for s in filtered]
        subject_avg.append(round(statistics.mean(vals),2) if vals else 0)

    scatter = [{"x":s["att"],"y":s["percentage"]} for s in filtered]

    return render_template_string(HTML,
        students=filtered,
        total=total,
        avg=avg,
        topper=topper,
        names=names,
        percentages=percentages,
        subject_avg=subject_avg,
        scatter=scatter
    )

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if request.form["username"]=="disha" and request.form["password"]=="disha":
            session["user"]="admin"
            return redirect("/")
    return LOGIN_HTML

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
