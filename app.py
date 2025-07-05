from flask import Flask
from flask import render_template, request, redirect, url_for
from datetime import date # date from datetime is used for date objects
from test_alch import Category, SessionLocal, LogEntry # Added LogEntry

app = Flask(__name__)

#Home Page
@app.route("/", methods=["GET", "POST"])
def index():
    session = SessionLocal()
    categories = session.query(Category).all()
    session.close()
    return render_template('index.html', categories=categories)

#Create Category Form
@app.route('/create-category', methods=['GET', 'POST'])
def create_category():
    if request.method == 'POST':
        name = request.form['name']
        icon = request.form['icon']
        description = request.form['description']

        session = SessionLocal()
        new_cat = Category(name=name, description=description, icon=icon)
        session.add(new_cat)
        session.commit()
        session.close()
        return redirect(url_for('index'))

    return render_template('create_category.html')

#Ind. Category Stats
@app.route('/category_stats/<int:category_id>')
def category_stats(category_id):
    session = SessionLocal()
    category = session.query(Category).filter(Category.id == category_id).first()
    # log_entries are accessed via category.log_entries due to the relationship
    # No specific query for log_entries needed here if relationship is set up correctly
    if category:
        # Access log_entries here to ensure they are loaded before closing session if needed by template
        log_entries = category.log_entries
        session.close()
        return render_template('category_stats.html', category=category, log_entries=log_entries)
    else:
        session.close()
        return "Category not found", 404

#Logger Form
@app.route('/log/<int:category_id>', methods=['GET', 'POST'])
def logger_form(category_id):
    session = SessionLocal()
    category = session.query(Category).filter(Category.id == category_id).first()

    if not category:
        session.close()
        return "Category not found", 404

    if request.method == 'POST':
        form_date_str = request.form['date']
        duration_str = request.form['duration']
        notes = request.form.get('notes') # .get to handle optional notes

        # Convert data
        entry_date = date.fromisoformat(form_date_str) # Use date.fromisoformat
        duration_int = int(duration_str)

        new_log_entry = LogEntry(
            category_id=category.id, # Use the actual category.id
            date=entry_date,
            duration=duration_int,
            notes=notes
        )
        session.add(new_log_entry)
        session.commit()
        session.close()
        return redirect(url_for('category_stats', category_id=category_id))

    # GET request
    current_date_iso = date.today().isoformat() # from datetime.date
    session.close() # Close session if only GET
    return render_template('logger_form.html', category=category, current_date=current_date_iso)

if __name__ == '__main__':
    app.run(debug=True)
