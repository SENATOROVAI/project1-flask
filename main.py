import math
import random

from flask import Flask, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import sessionmaker


# create the extension
db = SQLAlchemy()
# create the app
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
# initialize the app with the extension
db.init_app(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fio = db.Column(db.String(), nullable=False)
    age = db.Column(db.Integer(), nullable=False)
    weight = db.Column(db.Integer(), nullable=False)
    ku = db.Column(db.String(), nullable=False)
    trainer = mapped_column(ForeignKey("trainer.id"))
    gender = db.Column(db.String(), nullable=False)


class Trainer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fio = db.Column(db.String(), nullable=False)
    team = mapped_column(ForeignKey("team.id"))


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    min_age = db.Column(db.Integer, nullable=False)
    max_age = db.Column(db.Integer, nullable=False)
    min_weight = db.Column(db.Integer, nullable=False)
    max_weight = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String, nullable=False)


def dict_user_to_battle(d: dict):
    return f"{d['fio']} {d['age']} лет {d['weight']} кг"

def generate_test_data_in_db():
    min_age = 4
    max_age = 13
    min_weight = 20
    max_weight = 40
    male_names = ["Сергей", "Андрей", "Антон", "Михаил", "Дмитрий", "Матвей", "Артур", "Тимофей", "Кирилл", "Максим", "Петр"]
    male_surnames = ["Иванов", "Петров", "Сидоров"]
    female_names = ["Александра", "Анастасия", "Юлия", "Алиса", "Ирина", "Алла", "Яна", "Кристина", "Дарья", "Анна", "Тамара"]
    female_surnames = ["Иванова", "Петрова", "Сидорова"]
    genders = ["МУЖ", "ЖЕН"]
    clubs = ["Тигры", "Медведи", "Локомотив", "Динамо", "Спартак", "Школа №2", "Детский сад №17", "Омон"]
    kus = ["Желтый", "Красный", "Зеленый", "Синий", "Черный"]

    cat_ages = [[4, 5], [6, 7], [8, 9], [10, 11], [12, 13]]
    cat_weights = []
    cat_weights.append([0, min_weight])
    for w in range(min_weight, max_weight, 5):
        cat_weights.append([w, w+5])
    cat_weights.append([max_weight, 50])

    for g in genders:
        for age in cat_ages:
            for w in cat_weights:
                if w[0] == 0:
                    w_str = f"до {w[1]} кг"
                elif w[1] == 50:
                    w_str = f"свыше {w[0]} кг"
                else:
                    w_str = f"{w[0]}-{w[1]} кг"

                new_category = Category(
                    name=f"{g} {age[0]}-{age[1]} {w_str}",
                    min_age=age[0],
                    max_age=age[1],
                    min_weight=w[0],
                    max_weight=w[1],
                    gender=g
                )
                db.session.add(new_category)
                db.session.commit()

    for _ in range(15):
        club = random.choice(clubs)
        team = db.session.query(Team).filter(Team.name == club).first()
        if not team:
            team = Team(
                name=club
            )
            db.session.add(team)
            db.session.commit()

        new_trainer = Trainer(
            fio=f"{random.choice(male_names)} {random.choice(male_surnames)}",
            team=team.id
        )
        db.session.add(new_trainer)
        db.session.commit()

        for _ in range(random.randint(40, 80)):
            gender = random.choice(genders)
            if gender == "МУЖ":
                fio = f"{random.choice(male_names)} {random.choice(male_surnames)}"
            else:
                fio = f"{random.choice(female_names)} {random.choice(female_surnames)}"

            new_user = User(
                fio=fio,
                age=random.randint(min_age, max_age),
                weight=random.randint(min_weight, max_weight),
                ku=random.choice(kus),
                trainer=new_trainer.id,
                gender=gender
            )
            db.session.add(new_user)
            db.session.commit()


with app.app_context():
    db.drop_all()
    db.create_all()
    generate_test_data_in_db()
    Session = sessionmaker(bind=db.engine)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/documents')
def documents():
    return render_template('documents.html')


@app.route('/document/<path:path>')
def document(path):
    return send_from_directory('reports', path)


@app.route('/childs')
def childs():
    session = Session()

    result = session.query(User, Trainer, Team).filter(User.trainer == Trainer.id, Trainer.team == Team.id).all()
    data = []
    for r in result:
        child = r[0].__dict__
        trainer = r[1].__dict__
        team = r[2].__dict__
        data.append({"child": child, "trainer": trainer, "team": team})

    return render_template('childs.html', data=data)


@app.route('/trainers')
def trainers():
    session = Session()

    result = session.query(Trainer, Team).filter(Trainer.team == Team.id).all()
    data = []
    for r in result:
        trainer = r[0].__dict__
        team = r[1].__dict__
        data.append({"trainer": trainer, "team": team})

    return render_template('trainers.html', data=data)


@app.route('/teams')
def teams():
    session = Session()

    result = session.query(Team).all()
    data = []
    for r in result:
        team = r.__dict__
        data.append({"team": team})

    return render_template('teams.html', data=data)


@app.route('/categories')
def categories():
    session = Session()

    result = session.query(Category).all()
    data = []
    for r in result:
        category = r.__dict__
        data.append({"category": category})

    return render_template('categories.html', data=data)


@app.route('/team/<team_id>')
def user_by_team(team_id):
    session = Session()

    result = session.query(User, Trainer, Team).filter(User.trainer == Trainer.id, Trainer.team == Team.id, Team.id == team_id).all()
    data = []
    for r in result:
        child = r[0].__dict__
        trainer = r[1].__dict__
        team = r[2].__dict__
        data.append({"child": child, "trainer": trainer, "team": team})

    return render_template('childs.html', data=data, suffix=f" команды {team['name']}")


@app.route('/trainer/<trainer_id>')
def user_by_trainer(trainer_id):
    session = Session()

    result = session.query(User, Trainer, Team).filter(User.trainer == Trainer.id, Trainer.team == Team.id, Trainer.id == trainer_id).all()
    data = []
    for r in result:
        child = r[0].__dict__
        trainer = r[1].__dict__
        team = r[2].__dict__
        data.append({"child": child, "trainer": trainer, "team": team})

    return render_template('childs.html', data=data, suffix=f" тренера {trainer['fio']}")



@app.route('/battle-net/<cat_id>')
def battle_net(cat_id):
    session = Session()

    category = session.query(Category).filter(Category.id == cat_id).first()

    childs = session.query(User).filter(
        User.gender == category.gender,
        User.age >= category.min_age,
        User.age <= category.max_age,
        User.weight >= category.min_weight,
        User.weight < category.max_weight
    ).all()

    if len(childs) >= 8:
        childs = childs[0:8]
    else:
        return render_template('battle-net.html', cat_name="В категории слишком мало участников", data=[])


    height = len(childs) - 1
    width = 3


    matrix = [["" for _ in range(width)] for _ in range(height*2)]

    # FILL BATTLE NET
    childs = [dict_user_to_battle(child.__dict__) for child in childs]
    pairs = []

    for i in range(0, len(childs), 2):
        pairs.append([childs[i], childs[i+1]])

    matrix_data = []
    matrix_data.append(pairs)

    for _ in range(3):
        temp = []
        while len(childs) != 0:
            temp.append([childs.pop(0), childs.pop(0)])

        for pair in temp:
            rn = random.randint(0, 1)
            childs.append(pair[rn])
            pair[rn] += " (победа)"

        matrix_data.append(temp)


    matrix[0][0] = matrix_data[0][0][0]
    matrix[1][0] = matrix_data[0][0][1]

    matrix[4][0] = matrix_data[0][1][0]
    matrix[5][0] = matrix_data[0][1][1]

    matrix[8][0] = matrix_data[0][2][0]
    matrix[9][0] = matrix_data[0][2][1]

    matrix[12][0] = matrix_data[0][3][0]
    matrix[13][0] = matrix_data[0][3][1]


    matrix[2][1] = matrix_data[1][0][0]
    matrix[3][1] = matrix_data[1][0][1]

    matrix[10][1] = matrix_data[1][1][0]
    matrix[11][1] = matrix_data[1][1][1]


    matrix[6][2] = matrix_data[2][0][0]
    matrix[7][2] = matrix_data[2][0][1]


    # FILL BATTLE NET

    return render_template('battle-net.html', cat_name=category.name, data=matrix)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
