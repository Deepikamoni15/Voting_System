from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = "voting_system_secret"

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'voting_system'

mysql = MySQL(app)

@app.route('/')
def home():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name FROM candidates")
    candidates = cur.fetchall()
    cur.close()

    # Convert tuples to dictionaries
    candidates = [{'id': row[0], 'name': row[1]} for row in candidates]
    return render_template('index.html', candidates=candidates)

@app.route('/vote', methods=['POST'])
def vote():
    if 'voted' in session:
        return jsonify({'status': 'error', 'message': 'You have already voted!'})

    candidate_id = request.json.get('candidate_id')
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM candidates WHERE id = %s", (candidate_id,))
    candidate = cur.fetchone()

    if candidate:
        cur.execute("INSERT INTO votes (candidate_id) VALUES (%s)", (candidate_id,))
        mysql.connection.commit()
        cur.close()
        session['voted'] = True
        return jsonify({'status': 'success', 'message': 'Vote successfully recorded!'})

    cur.close()
    return jsonify({'status': 'error', 'message': 'Invalid candidate!'})

@app.route('/results')
def results():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT c.name, COUNT(v.id) AS vote_count
        FROM candidates c
        LEFT JOIN votes v ON c.id = v.candidate_id
        GROUP BY c.id
    """)
    results = cur.fetchall()
    cur.close()

    # Convert tuples to dictionaries
    results = [{'name': row[0], 'vote_count': row[1]} for row in results]
    return render_template('results.html', results=results)

@app.route('/manage', methods=['GET', 'POST'])
def manage():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        action = request.form['action']
        name = request.form['name']
        if action == "add" and name:
            cur.execute("INSERT INTO candidates (name) VALUES (%s)", (name,))
        elif action == "delete" and name:
            cur.execute("DELETE FROM candidates WHERE name = %s", (name,))
        mysql.connection.commit()
    cur.execute("SELECT id, name FROM candidates")
    candidates = cur.fetchall()
    cur.close()

    # Convert tuples to dictionaries
    candidates = [{'id': row[0], 'name': row[1]} for row in candidates]
    return render_template('manage.html', candidates=candidates)

if __name__ == '__main__':
    app.run(debug=True)
