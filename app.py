from flask import Flask
from flask import render_template, request, redirect, url_for
from datetime import date

app = Flask(__name__)

categories = [
    {"icon": "🎸", "name": "Guitar", "description": "Practice your favorite songs and improve your skills!"},
    {"icon": "📚", "name": "SAT Prep", "description": "Boost your score with focused study sessions."},
    {"icon": "📚", "name": "SAT Prep", "description": "Boost your score with focused study sessions."},
    {"icon": "📚", "name": "SAT Prep", "description": "Boost your score with focused study sessions."},
    {"icon": "📚", "name": "SAT Prep", "description": "Boost your score with focused study sessions."},
    {"icon": "📚", "name": "SAT Prep", "description": "Boost your score with focused study sessions."},
    {"icon": "📚", "name": "SAT Prep", "description": "Boost your score with focused study sessions."},
]

#Home Page
@app.route("/", methods=["GET", "POST"])
def index():
    return render_template('index.html', categories=categories)

#Create Category Form
@app.route('/create-category', methods=['GET', 'POST'])
def create_category():
    if request.method == 'POST':
        name = request.form['name']
        icon = request.form['icon']
        color = request.form['color']
        # Save the new category...
        return redirect(url_for('index'))

    return render_template('create_category.html')

#Ind. Category Stats
@app.route('/category_stats/<int:category_id>')
def category_stats(category_id):
    category = categories[category_id - 1]
    return render_template('category_stats.html', category=category)

#Logger Form
@app.route('/log/<int:category_id>', methods=['GET', 'POST'])
def logger_form(category_id):
    category = categories[category_id - 1]    
    current_date = date.today().isoformat()

    if request.method == 'POST':
        return redirect(url_for('index'))

    return render_template('logger_form.html', category=category, current_date=current_date)

if __name__ == '__main__':
    app.run(debug=True)
