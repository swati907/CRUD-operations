from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Secret key for session management, flash messages, and CSRF protection
app.config['SECRET_KEY'] = 'a8f5f167f44f4964e6c998dee827110c'

# Database configuration (SQLite inside instance folder)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ---------------- MODEL ----------------
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    course = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Student {self.name}>'


# Create tables on first run
with app.app_context():
    db.create_all()


# ---------------- ROUTES ----------------

# READ - List all students + CREATE form on same page
@app.route('/')
def index():
    students = Student.query.order_by(Student.id).all()
    return render_template('index.html', students=students, edit_student=None)


# CREATE - Add new student
@app.route('/add', methods=['POST'])
def add_student():
    name = request.form.get('name')
    email = request.form.get('email')
    course = request.form.get('course')
    age = request.form.get('age')

    if not name or not email or not course or not age:
        flash('All fields are required!', 'error')
        return redirect(url_for('index'))

    existing = Student.query.filter_by(email=email).first()
    if existing:
        flash('A student with this email already exists!', 'error')
        return redirect(url_for('index'))

    new_student = Student(name=name, email=email, course=course, age=int(age))
    db.session.add(new_student)
    db.session.commit()
    flash('Student registered successfully!', 'success')
    return redirect(url_for('index'))


# UPDATE - Show edit form pre-filled
@app.route('/edit/<int:student_id>')
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)
    students = Student.query.order_by(Student.id).all()
    return render_template('index.html', students=students, edit_student=student)


# UPDATE - Process edit form submission
@app.route('/update/<int:student_id>', methods=['POST'])
def update_student(student_id):
    student = Student.query.get_or_404(student_id)

    student.name = request.form.get('name')
    student.email = request.form.get('email')
    student.course = request.form.get('course')
    student.age = int(request.form.get('age'))

    db.session.commit()
    flash('Student record updated successfully!', 'success')
    return redirect(url_for('index'))


# DELETE - Remove student
@app.route('/delete/<int:student_id>')
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash('Student record deleted successfully!', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
        
