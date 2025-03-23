from flask import Flask
from flask import render_template, request, redirect

app = Flask(__name__)

class Log:
    def __init__(self, date, title, rate):
        self.date = date
        self.title = title
        self.rate = rate

    def __repr__(self):
        return f"Log(date={self.date}, title={self.title}, rate={self.rate})"

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template('index.html')

@app.route("/log", methods=['POST'])
def log():
    if request.method == 'POST':
        date = request.form['date']
        title = request.form['title']
        rate = request.form['rate']

        log_entry = Log(date, title, rate)

    return render_template('log.html', log=log_entry)

if __name__ == '__main__':
    app.run(debug=True)
