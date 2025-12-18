students = {
    'Davit': {'matem': 9, 'fizika': 8, 'qimia': 7},
    'Robert': {'matem': 7, 'fizika': 7, 'qimia': 8}
}
for name, subjects in students.items():
    avg = sum(subjects.values()) / len(subjects)
    print(name, "=", avg)

subjects_avg = {}
for name, subjects in students.items():
    for subject, grade in subjects.items():
        if subject not in subjects_avg:
            subjects_avg[subject] = []
        subjects_avg[subject].append(grade)
for subject, grades in subjects_avg.items():
    avg1 = sum(grades) / len(grades)
    print(subject, '=', avg1)


