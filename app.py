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
        # Process entries for month/day grouping and available_months
        min_date = log_entries[0].date
        max_date = log_entries[-1].date

        current_month_year = ""
        for entry in log_entries:
            month_year_str = entry.date.strftime("%Y-%m")
            if month_year_str not in available_months:
                available_months.append(month_year_str)

            entries_by_month_day[month_year_str][entry.date.day].append({
                'id': entry.id,
                'date': entry.date.isoformat(),
                'duration': entry.duration,
                'notes': entry.notes
            }) # Storing as dicts for easier JSON serialization later

        available_months.sort()

        # Calculate Lifetime Statistics
        lifetime_stats['total_sessions'] = len(log_entries)

        total_duration_query = session.query(func.sum(LogEntry.duration)).filter(LogEntry.category_id == category_id).scalar()
        lifetime_stats['total_minutes'] = total_duration_query if total_duration_query else 0
        lifetime_stats['total_hours_spent'] = math.ceil(lifetime_stats['total_minutes'] / 60)

        longest_session_query = session.query(func.max(LogEntry.duration)).filter(LogEntry.category_id == category_id).scalar()
        lifetime_stats['longest_session_minutes'] = longest_session_query if longest_session_query else 0

        if min_date and max_date:
            # Calculate total weeks for avg_hours_per_week
            # If only one entry, consider it as one week of activity for averaging.
            if min_date == max_date:
                 # If all entries are on the same day, consider it as 1 day activity in 1 week.
                total_days_span = 1
            else:
                total_days_span = (max_date - min_date).days + 1

            # Consider a minimum of 1 week even if the span is less, to avoid overly large avg for short periods.
            total_weeks = max(1, math.ceil(total_days_span / 7))

            if lifetime_stats['total_minutes'] > 0 and total_weeks > 0:
                total_hours = lifetime_stats['total_minutes'] / 60
                lifetime_stats['avg_hours_per_week'] = round(total_hours / total_weeks, 1)
            else:
                lifetime_stats['avg_hours_per_week'] = 0

    is_empty_category = not log_entries

    if is_empty_category:
        current_dt = datetime.now()
        current_year_month_str = current_dt.strftime("%Y-%m")
        available_months = [current_year_month_str]

        # For an empty category, we still want to show the current month's grid.
        # The JS will render days from 1 to days_in_month.
        # We don't need to pre-populate entries_by_month_day for an empty category,
        # as the JS renderCalendar will correctly show default (grey) circles
        # if logEntriesData[yearMonth][dayNum] is undefined or empty.
        # What's important is that available_months has the current month.

        # Reset lifetime_stats for an empty category to all zeros
        lifetime_stats = {
            'total_sessions': 0,
            'total_minutes': 0,
            'longest_session_minutes': 0,
            'avg_hours_per_week': 0,
            'total_hours_spent': 0
        }

    session.close()

    return render_template('category_stats.html',
                           category=category,
                           log_entries_data=entries_by_month_day,
                           available_months=available_months,
                           lifetime_stats=lifetime_stats,
                           is_empty_category=is_empty_category) # Pass the flag

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
        return redirect(url_for('category_stats', category_id=category_id))

    current_date_iso = date.today().isoformat()
    session.close()
    return render_template('logger_form.html', category=category, current_date=current_date_iso)

@app.route('/edit_category/<int:category_id>', methods=['GET', 'POST'])
def edit_category(category_id):
    session = SessionLocal()
    category_to_edit = session.query(Category).filter(Category.id == category_id).first()

    if not category_to_edit:
        session.close()
        return "Category not found", 404

    if request.method == 'POST':
        category_to_edit.name = request.form['name']
        category_to_edit.icon = request.form['icon']
        category_to_edit.description = request.form['description']
        session.commit()
        session.close()
        return redirect(url_for('category_stats', category_id=category_to_edit.id))

    # For GET request
    session.close() # Close session if only rendering
    return render_template('edit_category.html', category=category_to_edit)

@app.route('/delete_category/<int:category_id>/confirm')
def delete_category_confirm(category_id):
    session = SessionLocal()
    category_to_delete = session.query(Category).filter(Category.id == category_id).first()

    if not category_to_delete:
        session.close()
        return "Category not found", 404

    # Assuming cascade delete is set up for LogEntry items associated with this category.
    # If not, LogEntry items would need to be deleted manually first.
    session.delete(category_to_delete)
    session.commit()
    session.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
