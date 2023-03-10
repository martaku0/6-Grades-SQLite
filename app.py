import hashlib
import json
import math
import sqlite3

from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_bs4 import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, RadioField
from wtforms.validators import DataRequired, Length

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)
app.config['SECRET_KEY'] = 'dfghjkoiuyt%^&*98765'
date = datetime.now()

class LoginForm(FlaskForm):
    userLogin = StringField("Nazwa użytkownika", validators=[DataRequired()])
    userPass = PasswordField("Hasło:", validators=[DataRequired(), Length(min=0, max=16)])
    submit = SubmitField("Zaloguj")

class AddSubject(FlaskForm):
    subject = StringField('Nazwa przedmiotu:', validators=[DataRequired()])
    submit = SubmitField("Dodaj")

class AddGrade(FlaskForm):
    subject = SelectField("Wybierz przedmiot:", choices=str)
    term = RadioField('Wybierz semestr:', choices=[('term1', 'Semestr 1'), ('term2', 'Semestr 2')])
    category = SelectField('Kategoria ocen:', choices=[('answer', 'Odpowiedź'), ('quiz', 'Kartkówka'), ('test', 'Sprawdzian')])
    grade = SelectField('Ocena:', choices=[
        (6, 'Celujący'),
        (5, 'Bardzo dobry'),
        (4, 'Dobry'),
        (3, 'Dostateczny'),
        (2, 'Dopuszczający'),
        (1, 'Niedostateczny')
    ])
    submit = SubmitField("Dodaj")


def countAverage(subjectValue, termValue):
    connection = sqlite3.connect('data/grades')
    cursor = connection.cursor()
    cursor.execute(
        f"SELECT * FROM gradesTab INNER JOIN subjects ON subjects.id = gradesTab.subject INNER JOIN categories ON categories.id = gradesTab.category")
    grades = cursor.fetchall()
    connection.close()
    sum = 0
    len = 0
    if subjectValue == "" and termValue == "":
        for grade in grades:
            if grade[9] == 'answer' or grade[9] == 'quiz' or grade[9] == 'test':
                sum += grade[4]
                len+=1
    else:
        for grade in grades:
            if grade[7] == subjectValue:
                if grade[2] == termValue:
                    if grade[9] == 'answer' or grade[9] == 'quiz' or grade[9] == 'test':
                        sum += grade[4]
                        len += 1

    if len == 0:
        len = 1

    srednia = round(sum / len, 2)
    if (srednia % 1 >= 0.6):
        ocena = math.ceil(srednia)
    else:
        ocena = math.floor(srednia)

    return [srednia, ocena]

def countYearAverage(subjectValue):
    connection = sqlite3.connect('data/grades')
    cursor = connection.cursor()
    cursor.execute(
        f"SELECT * FROM gradesTab INNER JOIN subjects ON subjects.id = gradesTab.subject INNER JOIN categories ON categories.id = gradesTab.category")
    grades = cursor.fetchall()
    connection.close()
    sum = 0
    len = 0
    if subjectValue == "":
        for grade in grades:
            if grade[9] == 'answer' or grade[9] == 'quiz' or grade[9] == 'test':
                sum += grade[4]
                len += 1
    else:
        for grade in grades:
            if grade[7] == subjectValue:
                if grade[9] == 'answer' or grade[9] == 'quiz' or grade[9] == 'test':
                    sum += grade[4]
                    len += 1

    if len == 0:
        len = 1

    return round(sum/len, 2)

def yearly(subjectValue):
    srednia = countYearAverage(subjectValue)
    if (srednia % 1 >= 0.6):
        ocena = math.ceil(srednia)
    else:
        ocena = math.floor(srednia)

    return ocena

def zagrozenia():
    zagrozenia = []
    connection = sqlite3.connect('data/grades')
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM subjects")
    subjects = cursor.fetchall()
    for subject in subjects:
        if countYearAverage(subject[1]) < 2:
            zagrozenia.append(subject[1])
    connection.close()

    if len(zagrozenia) == 0:
        zagrozenia.append("Brak zagrożeń")

    print(zagrozenia)

    return zagrozenia

def najwyzszaSrednia():
    srednie = dict()

    connection = sqlite3.connect('data/grades')
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM subjects")
    subjects = cursor.fetchall()
    for subject in subjects:
        srednie[subject[1]] = countYearAverage(subject[1])
    connection.close()

    srednie = sorted(srednie.items(), key=lambda x:x[1])

    dwieNaj = []
    dwieNaj.append(list(srednie)[-1][0])
    dwieNaj.append(list(srednie)[-1][1])
    dwieNaj.append(list(srednie)[-2][0])
    dwieNaj.append(list(srednie)[-2][1])

    return dwieNaj

@app.route('/')
def index():
    return render_template('index.html', title='Home', userLogin=session.get("userLogin"), date=date)

@app.route("/logIn", methods=["POST", "GET"])
def login():
    login = LoginForm()
    if login.validate_on_submit():
        userLogin = login.userLogin.data
        userPass = login.userPass.data.encode()
        userPass = hashlib.sha256(userPass).hexdigest()
        connection = sqlite3.connect('data/grades')
        cursor = connection.cursor()
        cursor.execute(f"SELECT userLogin, firstName FROM users WHERE userLogin='{userLogin}' AND userPass='{userPass}'")
        user = cursor.fetchone()
        connection.close()
        if user:
            session["userLogin"] = user[0]
            session["firstName"] = user[1]
            return redirect("dashboard")
        else:
            flash('Błędne dane logowania')
            return redirect('logIn')
    return render_template("logIn.html", title="logowanie", login=login, userLogin=session.get("userLogin"), date=date, firstName=session.get('firstName'))

@app.route("/dashboard")
def dashboard():
    connection = sqlite3.connect('data/grades')
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM subjects")
    subjects = cursor.fetchall()
    cursor.execute(f"SELECT * FROM gradesTab INNER JOIN subjects ON subjects.id = gradesTab.subject INNER JOIN categories ON categories.id = gradesTab.category")
    grades = cursor.fetchall()
    connection.close()
    return render_template("dashboard.html", date=date, userLogin=session.get("userLogin"), firstName=session.get("firstName"), subjects=subjects, grades=grades, countAverage=countAverage, countYearAverage=countYearAverage, zagrozenia=zagrozenia, najwyzszaSrednia=najwyzszaSrednia, yearly=yearly)


@app.route("/addSubject", methods=['POST', 'GET'])
def addSubject():
    addSubject = AddSubject()
    if addSubject.validate_on_submit():
        with open("data/grades.json", encoding='utf-8') as gradesFile:
            grades = json.load(gradesFile)
            subject = addSubject.subject.data
            grades[subject] = {
                'term1':{'answer': [], 'quiz': [], 'test': [], 'intern': 0},
                'term2':{'answer': [], 'quiz': [], 'test': [], 'intern': 0, 'yearly': 0}
            }
        with open("data/grades.json", 'w', encoding='utf-8') as gradesFile:
            json.dump(grades, gradesFile)
            gradesFile.close()
            flash("Dane zapisane poprawnie.")
            return redirect('addSubject')
    return render_template("add-subject.html", title="Dodaj przedmiot", userLogin=session.get("userLogin"), date=date, addSubject=addSubject)

@app.route("/addGrade", methods=["POST","GET"])
def addGrade():
    addGrade = AddGrade()
    with open('data/grades.json', encoding='utf-8') as gradesFile:
        grades = json.load(gradesFile)
        gradesFile.close()
        addGrade.subject.choices = [subject for subject in grades]
    if addGrade.validate_on_submit():
        with open("data/grades.json", encoding='utf-8') as gradesFile:
            grades = json.load(gradesFile)
            subject = addGrade.subject.data
            term = addGrade.term.data
            category = addGrade.category.data
            grade = addGrade.grade.data
        with open("data/grades.json", 'w', encoding='utf-8') as gradesFile:
            grades[subject][term][category].append(int(grade))
            json.dump(grades, gradesFile)
            gradesFile.close()
            flash("Dane zapisane poprawnie.")
            return redirect('addGrade')
    return render_template('add-grade.html', title="Dodaj ocenę", userLogin=session.get("userLogin"), date=date, addGrade=addGrade)

@app.route("/logOut")
def logout():
    session.pop("userLogin")
    session.pop("firstName")
    return redirect("logIn")

@app.errorhandler(404)
def pageNotFound(error):
    return render_template('404.html', title='Error 404'), 404

@app.errorhandler(500)
def internalServerError(error):
    return render_template('500.html', title='Error 500'), 500

if __name__ == '__main__':
    app.run(debug=True)