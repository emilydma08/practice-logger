from flask import Flask, jsonify # Added jsonify for potential future use, though not in current plan step for app.py
from flask import render_template, request, redirect, url_for
from datetime import date, timedelta
from test_alch import Category, SessionLocal, LogEntry
from sqlalchemy import func # For database functions like sum, max, etc.
from collections import defaultdict
import math # For rounding hours
from datetime import datetime # For parsing month string

app = Flask(__name__)

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
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username").strip().lower()
    if not username.isalnum():
        return "Invalid username", 400
    return redirect(url_for("user_dashboard", username=username))


#Dashboard Page
@app.route("/<username>/", methods=["GET"])
def user_dashboard(username):
    session = SessionLocal(username)  
    categories = session.query(Category).all()
    session.close()
    return render_template('dashboard.html', categories=categories, username=username)



#Create Category Form
@app.route('/<username>/create-category', methods=['GET', 'POST'])
def create_category(username):
    if request.method == 'POST':
        name = request.form['name']
        icon = request.form['icon']
        description = request.form['description']

        session = SessionLocal(username)  # 🔧
        new_cat = Category(name=name, description=description, icon=icon)
        session.add(new_cat)
        session.commit()
        session.close()
        return redirect(url_for('user_dashboard', username=username))  # 🔧

    return render_template('create_category.html', username=username)


#Ind. Category Stats
@app.route('/<username>/category_stats/<int:category_id>')
def category_stats(username, category_id):
    session = SessionLocal(username)  # 🔧
    category = session.query(Category).filter(Category.id == category_id).first()

    if not category:
        session.close()
        return "Category not found", 404

    log_entries = session.query(LogEntry).filter(LogEntry.category_id == category_id).order_by(LogEntry.date).all()

    available_months = []
    entries_by_month_day = defaultdict(lambda: defaultdict(list))

    lifetime_stats = {
        'total_sessions': 0,
        'total_minutes': 0,
        'longest_session_minutes': 0,
        'avg_hours_per_week': 0,
        'total_hours_spent': 0
    }

    if log_entries:
        min_date = log_entries[0].date
        max_date = log_entries[-1].date

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
        lifetime_stats['total_sessions'] = len(log_entries)

        total_duration = session.query(func.sum(LogEntry.duration)).filter(LogEntry.category_id == category_id).scalar()
        lifetime_stats['total_minutes'] = total_duration if total_duration else 0
        lifetime_stats['total_hours_spent'] = math.ceil(lifetime_stats['total_minutes'] / 60)

        longest_session = session.query(func.max(LogEntry.duration)).filter(LogEntry.category_id == category_id).scalar()
        lifetime_stats['longest_session_minutes'] = longest_session if longest_session else 0

        total_days_span = max(1, (max_date - min_date).days + 1)
        total_weeks = max(1, math.ceil(total_days_span / 7))

        if lifetime_stats['total_minutes'] > 0:
            total_hours = lifetime_stats['total_minutes'] / 60
            lifetime_stats['avg_hours_per_week'] = round(total_hours / total_weeks, 1)

    else:
        current_year_month_str = datetime.now().strftime("%Y-%m")
        available_months = [current_year_month_str]

    session.close()

    return render_template('category_stats.html',
                           category=category,
                           log_entries_data=entries_by_month_day,
                           available_months=available_months,
                           lifetime_stats=lifetime_stats,
                           is_empty_category=(not log_entries),
                           username=username)  # 🔧


#Logger Form
@app.route('/<username>/log/<int:category_id>', methods=['GET', 'POST'])
def logger_form(username, category_id):
    session = SessionLocal(username)  # 🔧
    category = session.query(Category).filter(Category.id == category_id).first()

    if not category:
        session.close()
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
            notes=notes
        )
        session.add(new_log_entry)
        session.commit()
        session.close()
        return redirect(url_for('category_stats', username=username, category_id=category_id))  # 🔧

    current_date_iso = date.today().isoformat()
    session.close()
    return render_template('logger_form.html', category=category, current_date=current_date_iso, username=username)

@app.route('/<username>/edit_category/<int:category_id>', methods=['GET', 'POST'])
def edit_category(username, category_id):
    session = SessionLocal(username)  # 🔧
    category_to_edit = session.query(Category).filter(Category.id == category_id).first()

    if not category_to_edit:
        session.close()
        return "Category not found", 404

    if request.method == 'POST':
        category_to_edit.name = request.form['name']
        category_to_edit.icon = request.form['icon']
        category_to_edit.description = request.form['description']
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error committing changes: {e}")
            raise
        finally:
            session.close()

        return redirect(url_for('category_stats', username=username, category_id=category_id))  # 🔧

    session.close()
    return render_template('edit_category.html', category=category_to_edit, username=username)


@app.route('/<username>/delete_category/<int:category_id>/confirm')
def delete_category_confirm(username, category_id):
    session = SessionLocal(username)  # 🔧
    category_to_delete = session.query(Category).filter(Category.id == category_id).first()

    if not category_to_delete:
        session.close()
        return "Category not found", 404

    session.delete(category_to_delete)
    session.commit()
    session.close()

    return redirect(url_for('user_dashboard', username=username))  # 🔧


if __name__ == '__main__':
    app.run(debug=True)
