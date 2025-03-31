# Ответ
'''Количество студентов: 120

Количество студентов по направлениям:
Анализ_данных - 21
Информационная_безопасность - 15
Искусственный_интеллект - 16
Компьютерные_науки - 28
Прикладная_информатика - 22
Прикладная_математика - 18

Количество студентов по формам направления:
Вечерняя - 38
Заочная - 37
Очная - 45

Максимальный средний балл по направлениям:
Анализ_данных - 4.81
Информационная_безопасность - 4.68
Искусственный_интеллект - 4.69
Компьютерные_науки - 4.55
Прикладная_информатика - 4.88
Прикладная_математика - 4.92

Минимальный средний балл по направлениям:
Анализ_данных - 2.15
Информационная_безопасность - 2.03
Искусственный_интеллект - 2.31
Компьютерные_науки - 2.0
Прикладная_информатика - 2.09
Прикладная_математика - 2.1

Средний средний балл по направлениям:
Анализ_данных - 3.6871428571428573
Информационная_безопасность - 3.4679999999999995
Искусственный_интеллект - 3.3075
Компьютерные_науки - 3.3514285714285714
Прикладная_информатика - 3.7095454545454545
Прикладная_математика - 4.003333333333334

Средний средний балл по уровню:
Аспирантура - 3.7676666666666665
Бакалавриат - 3.651212121212121
Магистратура - 3.5534615384615384
Специалитет - 3.3538709677419356

Средний средний балл по типу обучения:
Вечерняя - 3.529736842105263
Заочная - 3.5910810810810814
Очная - 3.6195555555555554

ТОП-5 студентов для повышенной стипендии:
Васильев Павел Владимирович - 4.87
Кузнецов Дмитрий Георгиевич - 4.86
Иванов Артем Маркович - 4.86
Никитин Владимир Сергеевич - 4.73
Васнецов Иван Павлович - 4.65

Количество однофамильцев в базе: 101

Полные тезки среди обучающихся: 8'''

import sqlite3

connection = sqlite3.connect("baza.db")
cursor = connection.cursor()

for s in open("lvl_education.txt"):
    lvl_education = s.strip().split()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS `lvl_education` (
        `id_lvl` integer primary key NOT NULL UNIQUE,
        `title` TEXT NOT NULL
        );
    ''')

    cursor.execute("INSERT INTO lvl_education VALUES (?, ?)", (lvl_education[0], lvl_education[1]))

for s2 in open("direction.txt"):
    direction = s2.strip().split()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS `direction` (
        `id_direction` integer primary key NOT NULL UNIQUE,
        `title` TEXT NOT NULL
        );
    ''')

    cursor.execute("INSERT INTO direction VALUES (?, ?)", (direction[0], direction[1]))

for s3 in open("types_of_training.txt"):
    types_of_training = s3.strip().split()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS `types_of_training` (
        `id_type_of_training` integer primary key NOT NULL UNIQUE,
        `title` TEXT NOT NULL
        );
    ''')

    cursor.execute("INSERT INTO types_of_training VALUES (?, ?)", (types_of_training[0], types_of_training[1]))

for s4 in open("students.txt"):
    students = s4.strip().split()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS `students` (
        `id_student` integer primary key NOT NULL UNIQUE,
        `id_lvl` INTEGER NOT NULL,
        `id_direction` INTEGER NOT NULL,
        `id_type_of_training` INTEGER NOT NULL,
        `surname` TEXT NOT NULL,
        `name` TEXT NOT NULL,
        `fathername` TEXT NOT NULL,
        `average_score` FLOAT NOT NULL,
    FOREIGN KEY(`id_lvl`) REFERENCES `lvl_education`(`id_lvl`),
    FOREIGN KEY(`id_direction`) REFERENCES `direction`(`id_direction`),
    FOREIGN KEY(`id_type_of_training`) REFERENCES `types_of_training`(`id_type_of_training`)
        );
    ''')

    cursor.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (students[0], students[1], students[2], students[3], students[4], students[5], students[6], students[7]))

connection.commit()

cursor.execute('''
    SELECT COUNT(*) FROM students;
''')
amount_student = cursor.fetchone()[0]

print(f"\nКоличество студентов: {amount_student}")

cursor.execute('''
    SELECT direction.title, COUNT(*) AS student_direction 
    FROM students
    JOIN direction ON students.id_direction = direction.id_direction
    GROUP BY direction.title;
''')
student_title_counts = cursor.fetchall()
print("\nКоличество студентов по направлениям:")
for student_title_dir in student_title_counts:
    print(f"{student_title_dir[0]} - {student_title_dir[1]}")

cursor.execute('''
    SELECT types_of_training.title, COUNT(*) AS student_type_of_training 
    FROM students
    JOIN types_of_training ON students.id_type_of_training = types_of_training.id_type_of_training
    GROUP BY types_of_training.title;
''')

student_type_counts = cursor.fetchall()
print("\nКоличество студентов по формам направления:")
for student_title_type in student_type_counts:
    print(f"{student_title_type[0]} - {student_title_type[1]}")

cursor.execute('''
    SELECT direction.title, MAX(average_score) AS max_avg_score 
    FROM students
    JOIN direction ON students.id_direction = direction.id_direction
    GROUP BY direction.title;
''')

max_average_score = cursor.fetchall()
print("\nМаксимальный средний балл по направлениям:")
for max_average in max_average_score:
    print(f"{max_average[0]} - {max_average[1]}")

cursor.execute('''
    SELECT direction.title, MIN(average_score) AS min_avg_score 
    FROM students
    JOIN direction ON students.id_direction = direction.id_direction
    GROUP BY direction.title;
''')

min_average_score = cursor.fetchall()
print("\nМинимальный средний балл по направлениям:")
for min_average in min_average_score:
    print(f"{min_average[0]} - {min_average[1]}")    

cursor.execute('''
    SELECT direction.title, AVG(average_score) AS avg_avg_score 
    FROM students
    JOIN direction ON students.id_direction = direction.id_direction
    GROUP BY direction.title;
''')

avg_average_score = cursor.fetchall()
print("\nСредний средний балл по направлениям:")
for avg_average in avg_average_score:
    print(f"{avg_average[0]} - {avg_average[1]}")  

cursor.execute('''
    SELECT lvl_education.title, AVG(average_score) AS avg_avg_score_lvl 
    FROM students
    JOIN lvl_education ON students.id_lvl = lvl_education.id_lvl
    GROUP BY lvl_education.title;
''')

avg_average_score_lvl = cursor.fetchall()
print("\nСредний средний балл по уровню:")
for avg_average_lvl in avg_average_score_lvl:
    print(f"{avg_average_lvl[0]} - {avg_average_lvl[1]}")  

cursor.execute('''
    SELECT types_of_training.title, AVG(average_score) AS avg_avg_score_types
    FROM students
    JOIN types_of_training ON students.id_type_of_training = types_of_training.id_type_of_training
    GROUP BY types_of_training.title;
''')

avg_average_score_type = cursor.fetchall()
print("\nСредний средний балл по типу обучения:")
for avg_average_type in avg_average_score_type:
    print(f"{avg_average_type[0]} - {avg_average_type[1]}")  

cursor.execute('''
    SELECT students.surname, students.name, students.fathername, students.average_score
    FROM students
    JOIN direction ON students.id_direction = direction.id_direction
    JOIN types_of_training ON students.id_type_of_training = types_of_training.id_type_of_training
    WHERE direction.title = 'Прикладная_информатика'
    AND types_of_training.title = 'Очная'
    ORDER BY students.average_score DESC
    LIMIT 5;
''')

top_students = cursor.fetchall()

print("\nТОП-5 студентов для повышенной стипендии:")
for student in top_students:
    print(f"{student[0]} {student[1]} {student[2]} - {student[3]:.2f}")

cursor.execute('''
    SELECT COUNT(*) AS count
    FROM students
    GROUP BY surname
    HAVING COUNT(*) > 1;
''')

same_surname_students = cursor.fetchall()

if same_surname_students:
    people = 0
    for surname in same_surname_students:
        people += surname[0]
    print(f"\nКоличество однофамильцев в базе: {people}")
else:
    print("\nОднофамильцев нет")

cursor.execute('''
    SELECT COUNT(*) AS count1
    FROM students
    GROUP BY surname, name, fathername
    HAVING COUNT(*) > 1;
''')

full_namesakes = cursor.fetchall()

if full_namesakes:
    full = 0
    for namesake in full_namesakes:
        full += namesake[0]
    print(f"\nПолные тезки среди обучающихся: {full}")
else:
    print("\nПолных тезок среди обучающихся нет.")

connection.close()