import sqlite3
from pathlib import Path

from flask import Flask, abort, redirect, render_template, render_template_string, request, url_for


app = Flask(__name__, template_folder=".")
DATABASE = Path(__file__).with_name("attendance.db")


def initialize_database():
		with sqlite3.connect(DATABASE) as connection:
				connection.execute(
						"""
						CREATE TABLE IF NOT EXISTS attendance (
								id INTEGER PRIMARY KEY AUTOINCREMENT,
								name TEXT NOT NULL,
								registration_number TEXT NOT NULL,
								submitted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
						)
						"""
				)


initialize_database()


@app.get("/")
def attendance_form():
		return render_template("index.html")


@app.post("/submit")
def submit_attendance():
		name = request.form.get("name", "").strip()
		registration_number = request.form.get("RegNo", "").strip()
		if not name or not registration_number:
				abort(400, description="Name and registration number are required.")

		with sqlite3.connect(DATABASE) as connection:
				connection.execute(
						"INSERT INTO attendance (name, registration_number) VALUES (?, ?)",
						(name, registration_number),
				)

		return redirect(url_for("attendance_records"))


@app.get("/records")
def attendance_records():
		with sqlite3.connect(DATABASE) as connection:
				connection.row_factory = sqlite3.Row
				records = connection.execute(
						"SELECT name, registration_number, submitted_at "
						"FROM attendance ORDER BY id DESC"
				).fetchall()

		return render_template_string(
				"""<!doctype html>
<html lang="en">
	<head>
		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<title>Attendance records</title>
		<style>
			body { margin: 0; padding: 32px 16px; background: #eef4ff; color: #1d2433; font-family: Arial, sans-serif; }
			main { max-width: 900px; margin: 0 auto; }
			h1 { color: #2f6fed; }
			.tabs { display: flex; gap: 4px; margin-bottom: 20px; padding: 4px; border: 1px solid #dfe7f5; border-radius: 10px; background: white; }
			.tabs a { flex: 1; padding: 10px 12px; border-radius: 7px; color: #68768c; font-size: 0.95rem; font-weight: 700; text-align: center; text-decoration: none; }
			.tabs a[aria-current="page"] { background: #2f6fed; color: white; }
			.table-wrap { overflow-x: auto; background: white; border: 1px solid #dfe7f5; border-radius: 8px; }
			table { width: 100%; border-collapse: collapse; text-align: left; }
			th, td { padding: 12px 16px; border-bottom: 1px solid #dfe7f5; }
			th { background: #f9fbff; }
			tbody tr:last-child td { border-bottom: 0; }
		</style>
	</head>
	<body>
		<main>
			<h1>Attendance records</h1>
			<nav class="tabs" aria-label="Attendance pages">
				<a href="{{ url_for('attendance_form') }}">New attendance</a>
				<a href="{{ url_for('attendance_records') }}" aria-current="page">View attendance</a>
			</nav>
			{% if records %}
			<div class="table-wrap">
				<table>
					<thead><tr><th>Name</th><th>Registration number</th><th>Submitted at (UTC)</th></tr></thead>
					<tbody>
						{% for record in records %}
						<tr>
							<td>{{ record.name }}</td>
							<td>{{ record.registration_number }}</td>
							<td>{{ record.submitted_at }}</td>
						</tr>
						{% endfor %}
					</tbody>
				</table>
			</div>
			{% else %}
			<p>No attendance submissions yet.</p>
			{% endif %}
		</main>
	</body>
</html>""",
				records=records,
		)


if __name__ == "__main__":
		app.run(host="127.0.0.1", port=5000)
