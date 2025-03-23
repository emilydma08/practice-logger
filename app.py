from flask import Flask
from flask import render_template, request, redirect

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template('index.html')

@app.route("/log", methods=['POST'])
def log():
    if request.method == 'POST':
        date = request.form['date']
        title = request.form['title']
        rating = request.form['rate']
    return render_template('log.html', log_date=date, title=title, rate=rating)

if __name__ == '__main__':
    app.run(debug=True)
