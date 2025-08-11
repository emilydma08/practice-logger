from flask import Flask, jsonify, session
from flask import render_template, request, redirect, url_for
from datetime import date, timedelta
from database import Category, SessionLocal, LogEntry, init_db
from sqlalchemy import func
from collections import defaultdict
import math
from datetime import datetime
from functools import wraps
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize the database
init_db()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')  # Change this to a random secret key

# User credentials
USERS = {
    "emily": "password123",
    "andrew": "andrewpass",
    "alex": "alexpass",
    "sherri": "sherripass"
}

# Custom Jinja filter to format 'YYYY-MM' to 'Month YYYY'
def format_month_year(value_str):
    if not value_str:
        return ""
    try:
        dt_object = datetime.strptime(value_str, "%Y-%m")
        return dt_object.strftime("%B %Y")
    except ValueError:
        return value_str # Return original if parsing fails

app.jinja_env.filters['formatmonthyear'] = format_month_year

# Login Page
@app.route("/")
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username").strip().lower()
        password = request.form.get("password")
        if username in USERS and USERS[username] == password:
            session['username'] = username
            return redirect(url_for("dashboard"))
        else:
            return render_template("index.html", error="Invalid username or password")
    return render_template("index.html")

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


#Dashboard Page
@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    username = session['username']
    db_session = SessionLocal()
    categories = db_session.query(Category).filter_by(username=username).all()
    db_session.close()
    return render_template('dashboard.html', categories=categories)



#Create Category Form
@app.route('/create-category', methods=['GET', 'POST'])
@login_required
def create_category():
    if request.method == 'POST':
        name = request.form['name']
        icon = request.form['icon']
        description = request.form['description']
        username = session['username']

        db_session = SessionLocal()
        new_cat = Category(name=name, description=description, icon=icon, username=username)
        db_session.add(new_cat)
        db_session.commit()
        db_session.close()
        return redirect(url_for('dashboard'))

    return render_template('create_category.html')


def calculate_streaks(log_dates):
    if not log_dates:
        return 0, 0

    unique_dates = sorted(list(set(log_dates)))

    if not unique_dates:
        return 0, 0

    streaks = []
    current_streak = 1
    for i in range(1, len(unique_dates)):
        if (unique_dates[i] - unique_dates[i-1]).days == 1:
            current_streak += 1
        else:
            streaks.append(current_streak)
            current_streak = 1
    streaks.append(current_streak)

    longest_streak = max(streaks) if streaks else 0

    today = date.today()
    last_log_date = unique_dates[-1]

    current_streak_value = 0
    # A streak is "current" if the last log was today or yesterday
    if (today - last_log_date).days <= 1:
        current_streak_value = streaks[-1]

    return current_streak_value, longest_streak


#Ind. Category Stats
@app.route('/category_stats/<int:category_id>')
@login_required
def category_stats(category_id):
    username = session['username']
    db_session = SessionLocal()
    category = db_session.query(Category).filter_by(id=category_id, username=username).first()

    if not category:
        db_session.close()
        return "Category not found", 404

    log_entries = db_session.query(LogEntry).filter_by(category_id=category_id, username=username).order_by(LogEntry.date).all()

    available_months = []
    entries_by_month_day = defaultdict(lambda: defaultdict(list))

    lifetime_stats = {
        'current_streak': 0,
        'longest_streak': 0,
        'avg_time_per_day': 0,
        'total_sessions': 0,
    }

    if log_entries:
        log_dates = [entry.date for entry in log_entries]
        current_streak, longest_streak = calculate_streaks(log_dates)
        lifetime_stats['current_streak'] = current_streak
        lifetime_stats['longest_streak'] = longest_streak

        total_duration = sum(entry.duration for entry in log_entries)
        first_log_date = min(log_dates)
        days_since_first_log = (date.today() - first_log_date).days + 1

        if days_since_first_log > 0:
            lifetime_stats['avg_time_per_day'] = round(total_duration / days_since_first_log, 1)

        lifetime_stats['total_sessions'] = len(log_entries)

        for entry in log_entries:
            month_year_str = entry.date.strftime("%Y-%m")
            if month_year_str not in available_months:
                available_months.append(month_year_str)

            entries_by_month_day[month_year_str][entry.date.day].append({
                'id': entry.id,
                'date': entry.date.isoformat(),
                'duration': entry.duration,
                'notes': entry.notes
            })

        available_months.sort()

    else:
        current_year_month_str = datetime.now().strftime("%Y-%m")
        available_months = [current_year_month_str]

    db_session.close()

    return render_template('category_stats.html',
                           category=category,
                           log_entries_data=entries_by_month_day,
                           available_months=available_months,
                           lifetime_stats=lifetime_stats,
                           is_empty_category=(not log_entries))


#Logger Form
@app.route('/log/<int:category_id>', methods=['GET', 'POST'])
@login_required
def logger_form(category_id):
    username = session['username']
    db_session = SessionLocal()
    category = db_session.query(Category).filter_by(id=category_id, username=username).first()

    if not category:
        db_session.close()
        return "Category not found", 404

    if request.method == 'POST':
        form_date_str = request.form['date']
        duration_str = request.form['duration']
        notes = request.form.get('notes')

        entry_date = date.fromisoformat(form_date_str)
        duration_int = int(duration_str)

        new_log_entry = LogEntry(
            category_id=category.id,
            date=entry_date,
            duration=duration_int,
            notes=notes,
            username=username
        )
        db_session.add(new_log_entry)
        db_session.commit()
        db_session.close()
        return redirect(url_for('category_stats', category_id=category_id))

    current_date_iso = date.today().isoformat()
    db_session.close()
    return render_template('logger_form.html', category=category, current_date=current_date_iso)


@app.route('/edit_log/<int:log_id>', methods=['GET', 'POST'])
@login_required
def edit_log(log_id):
    username = session['username']
    db_session = SessionLocal()
    log_to_edit = db_session.query(LogEntry).filter_by(id=log_id, username=username).first()

    if not log_to_edit:
        db_session.close()
        return "Log entry not found", 404

    if request.method == 'POST':
        form_date_str = request.form['date']
        duration_str = request.form['duration']
        notes = request.form.get('notes')

        log_to_edit.date = date.fromisoformat(form_date_str)
        log_to_edit.duration = int(duration_str)
        log_to_edit.notes = notes

        try:
            db_session.commit()
            db_session.close()
        except Exception as e:
            db_session.rollback()
            db_session.close()
            # In a real app, you'd log this error
            raise

        return redirect(url_for('category_stats', category_id=log_to_edit.category_id))

    # For GET request
    category_info = {
        'id': log_to_edit.category_id,
        'icon': log_to_edit.category.icon,
        'name': log_to_edit.category.name
    }
    db_session.close()
    return render_template('edit_log.html', log=log_to_edit, category=category_info)


@app.route('/delete_log/<int:log_id>', methods=['POST'])
@login_required
def delete_log(log_id):
    username = session['username']
    db_session = SessionLocal()
    log_to_delete = db_session.query(LogEntry).filter_by(id=log_id, username=username).first()

    if not log_to_delete:
        db_session.close()
        return "Log entry not found", 404

    category_id = log_to_delete.category_id
    db_session.delete(log_to_delete)
    db_session.commit()
    db_session.close()

    return redirect(url_for('category_stats', category_id=category_id))


@app.route('/edit_category/<int:category_id>', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    username = session['username']
    db_session = SessionLocal()
    category_to_edit = db_session.query(Category).filter_by(id=category_id, username=username).first()

    if not category_to_edit:
        db_session.close()
        return "Category not found", 404

    if request.method == 'POST':
        category_to_edit.name = request.form['name']
        category_to_edit.icon = request.form['icon']
        category_to_edit.description = request.form['description']
        try:
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            print(f"Error committing changes: {e}")
            raise
        finally:
            db_session.close()

        return redirect(url_for('category_stats', category_id=category_id))

    db_session.close()
    return render_template('edit_category.html', category=category_to_edit)


@app.route('/delete_category/<int:category_id>/confirm')
@login_required
def delete_category_confirm(category_id):
    username = session['username']
    db_session = SessionLocal()
    category_to_delete = db_session.query(Category).filter_by(id=category_id, username=username).first()

    if not category_to_delete:
        db_session.close()
        return "Category not found", 404

    db_session.delete(category_to_delete)
    db_session.commit()
    db_session.close()

    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True)
