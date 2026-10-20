
from flask import Flask, render_template_string, request, redirect
from datetime import datetime
from collections import Counter

app = Flask(__name__)

# Demo data for the classroom dashboard
students = [
    {"id": 1, "name": "Student 1", "present": True,
     "engagement": 82, "minutes": 45},
    {"id": 2, "name": "Student 2", "present": True,
     "engagement": 68, "minutes": 40},
    {"id": 3, "name": "Student 3", "present": False,
     "engagement": 0, "minutes": 0},
    {"id": 4, "name": "Student 4", "present": True,
     "engagement": 91, "minutes": 45},
    {"id": 5, "name": "Student 5", "present": True,
     "engagement": 74, "minutes": 42},
]

attendance_log = []
session_history = []


def get_suggestions(average):
    if average >= 80:
        return [
            "Engagement is high in this demo session.",
            "Continue using interactive teaching methods.",
            "Include short knowledge checks to maintain participation."
        ]
    elif average >= 60:
        return [
            "Try adding a short quiz or group activity.",
            "Pause periodically to invite student questions.",
            "Use visual examples to reinforce key concepts."
        ]
    else:
        return [
            "Consider a short break and a change of activity.",
            "Break complex topics into smaller sections.",
            "Ask students for feedback about lesson pace."
        ]


HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Attendance & Engagement Agent</title>
<style>
* { box-sizing: border-box; }
body {
    margin: 0; font-family: Arial, sans-serif;
    background: #f3f6fb; color: #202b43;
}
header {
    background: #18264a; color: white;
    padding: 24px 6%;
}
header h1 { margin: 0 0 8px; font-size: 27px; }
header p { margin: 0; color: #d5def5; }
.container { max-width: 1150px; margin: 28px auto; padding: 0 20px; }
.grid {
    display: grid; grid-template-columns: repeat(3, 1fr);
    gap: 18px; margin-bottom: 24px;
}
.card {
    background: white; padding: 22px;
    border-radius: 14px; box-shadow: 0 3px 15px #18264a0c;
}
.metric { font-size: 30px; font-weight: bold; margin-top: 10px; }
.muted { color: #73809b; font-size: 14px; }
h2 { font-size: 19px; margin-top: 0; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 13px 8px; text-align: left; border-bottom: 1px solid #edf0f6; }
th { color: #73809b; font-size: 13px; }
.status { color: #18794e; font-weight: bold; }
.absent { color: #c0392b; font-weight: bold; }
.progress { background: #e9edf5; height: 9px; border-radius: 10px; overflow: hidden; }
.bar { height: 100%; background: #476de0; }
button {
    border: 0; border-radius: 8px; padding: 10px 14px;
    cursor: pointer; background: #476de0; color: white;
}
button:hover { background: #304fb3; }
.suggestion { background: #f3f6ff; padding: 12px; border-radius: 8px; margin: 9px 0; }
footer { text-align: center; padding: 25px; color: #73809b; font-size: 13px; }
@media(max-width: 700px) {
    .grid { grid-template-columns: 1fr; }
    table { font-size: 13px; }
}
</style>
</head>

<script>
const engagementCanvas = document.getElementById('engagementChart');

if (engagementCanvas && typeof Chart !== 'undefined') {
    new Chart(engagementCanvas, {
        type: 'bar',
        data: {
            labels: [
                {% for s in students if s.present %}
                    {{ s.name | tojson }},
                {% endfor %}
            ],
            datasets: [{
                label: 'Engagement (%)',
                data: [
                    {% for s in students if s.present %}
                        {{ s.engagement }},
                    {% endfor %}
                ],
                backgroundColor: '#476de0',
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}
</script>

<body>
<header>
    <h1>Classroom Intelligence</h1>
    <p>Multimodal Attendance & Engagement Agent</p>
</header>

<div class="container">
    <p class="muted">Session date: {{ today }}</p>

    <div class="grid">
        <div class="card">
            <div class="muted">Total Students</div>
            <div class="metric">{{ total }}</div>
        </div>
        <div class="card">
            <div class="muted">Present Students</div>
            <div class="metric">{{ present }}</div>
            <p class="muted">{{ attendance_rate }}% attendance rate</p>
        </div>
        <div class="card">
            <div class="muted">Average Engagement</div>
            <div class="metric">{{ average }}%</div>
            <p class="muted">Illustrative demo data</p>
        </div>
    </div>

    <div class="card" style="margin-bottom:24px">
        <h2>Student Attendance</h2>
        <p class="muted">
            Use the buttons to update demo attendance.
            These are sample students, not real video detections.
        </p>
        <table>
            <tr>
                <th>Student</th><th>Attendance</th>
                <th>Engagement</th><th>Session</th><th>Action</th>
            </tr>
            {% for s in students %}
            <tr>
                <td>{{ s.name }}</td>
                <td class="{{ 'status' if s.present else 'absent' }}">
                    {{ 'Present' if s.present else 'Absent' }}
                </td>
                <td>
                    {% if s.present %}
                    {{ s.engagement }}%
                    <div class="progress">
                        <div class="bar" style="width:{{ s.engagement }}%"></div>
                    </div>
                    {% else %}—{% endif %}
                </td>
                <td>{{ s.minutes }} min</td>
                <td>
                    <form method="post" action="/toggle/{{ s.id }}">
                        <button type="submit">
                            Mark {{ 'Absent' if s.present else 'Present' }}
                        </button>
                    </form>
                </td>
            </tr>
            {% endfor %}
        </table>
    </div>

    <div class="grid">
        <div class="card" style="grid-column: span 2">
            <h2>Engagement Analytics</h2>
            <p class="muted">Engagement scores for present demo students</p>
            <canvas id="engagementChart" height="120"></canvas>
            {% for s in students %}
            {% if s.present %}
            <p>{{ s.name }} — {{ s.engagement }}%</p>
            <div class="progress">
                <div class="bar" style="width:{{ s.engagement }}%"></div>
            </div>
            {% endif %}
            {% endfor %}
            <p class="muted">
                Scores are illustrative. They do not establish attention,
                understanding, or learning outcomes.
            </p>
        </div>
        <div class="card">
            <h2>Teaching Suggestions</h2>
            {% for suggestion in suggestions %}
            <div class="suggestion">{{ suggestion }}</div>
            {% endfor %}
        </div>
    </div>

    <div class="card">
        <h2>Session Summary</h2>
        <p>Attendance: {{ present }} out of {{ total }} students</p>
        <p>Average engagement score: {{ average }}%</p>
        <form method="post" action="/save">
            <button type="submit">Save Session Summary</button>
        </form>
        {% if saved %}
        <p class="status">Session summary saved successfully!</p>
        {% endif %}
        <p class="muted">
            Demo note: records reset when the app restarts.
            Use authorized data and consent for any real classroom deployment.
        </p>
    </div>
</div>

<script>
const engagementCanvas = document.getElementById('engagementChart');

if (engagementCanvas && typeof Chart !== 'undefined') {
    new Chart(engagementCanvas, {
        type: 'bar',
        data: {
            labels: [
                {% for s in students if s.present %}
                    {{ s.name | tojson }},
                {% endfor %}
            ],
            datasets: [{
                label: 'Engagement (%)',
                data: [
                    {% for s in students if s.present %}
                        {{ s.engagement }},
                    {% endfor %}
                ],
                backgroundColor: '#476de0',
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}
</script>

<footer>Classroom Intelligence | Academic Project Prototype</footer>

<script
src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</body>
</html>
"""


@app.route("/")
def dashboard():
    present_students = [s for s in students if s["present"]]
    total = len(students)
    present = len(present_students)
    attendance_rate = round(present / total * 100) if total else 0

    average = (
        round(sum(s["engagement"] for s in present_students) / present)
        if present else 0
    )

    saved = request.args.get("saved") == "1"

    return render_template_string(
        HTML,
        students=students,
        total=total,
        present=present,
        attendance_rate=attendance_rate,
        average=average,
        today=datetime.now().strftime("%d %B %Y"),
        suggestions=get_suggestions(average),
        saved=saved,
        session_history=session_history
    )


@app.route("/toggle/<int:student_id>", methods=["POST"])
def toggle_attendance(student_id):
    for student in students:
        if student["id"] == student_id:
            student["present"] = not student["present"]
            if not student["present"]:
                student["minutes"] = 0
            else:
                student["minutes"] = 45
            break

    return redirect("/")


@app.route("/save", methods=["POST"])
def save_session():
    present_students = [s for s in students if s["present"]]
    total = len(students)
    present = len(present_students)
    average = (
        round(sum(s["engagement"] for s in present_students) / present)
        if present else 0
    )

    session_history.append({
        "date": datetime.now().strftime("%d-%m-%Y %H:%M"),
        "present": present,
        "total": total,
        "average_engagement": average
    })

    return redirect("/?saved=1")


if __name__ == "__main__":
    app.run(debug=True)



    