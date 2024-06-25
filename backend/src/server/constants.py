verification_tags = {
    "Регулярные объекты": [
        ("Птицы", "bird"),
        ("Самолеты", "airplane"),
        ("Вертолеты", "helicopter"),
    ],
    "БПЛА": [
        ("Квадракоптеры", "quadcopter_uav"),
        ("БПЛА самолетного типа", "fixed-wing_uav"),
    ]
}

tag_translation = {
    "Птицы": "bird",
    "Самолеты": "airplane",
    "Вертолеты": "helicopter",
    "Квадракоптеры": "quadcopter_uav",
    "БПЛА самолетного типа": "fixed-wing_uav",
}

tag_translation_eng_rus = {
    "bird": "Птица",
    "plane": "Самолет",
    "airplane": "Самолет",
    "helicopter": "Вертолет",
    "uav": "Квадракоптер",
    "quadcopter_uav": "Квадракоптер",
    "fixed-wing_uav": "БПЛА самолетного типа",
    "fixed-wing-uav": "БПЛА самолетного типа",
}

label_map = {
    "quadcopter_uav" : 0,
    "airplane" : 1,
    "helicopter": 2,
    "bird" : 3,
    "fixed-wing_uav" : 4
}

confidence_thresholds = {
    0: 0.5,
    1: 0.3,  # может, 0.4
    2: 0.3,
    3: 0.3,
    4: 0.4,
}

colors = [
    "#4f3721",
    "#395470",
    "#d62a80",
    "#d60aaa",
    "#6add23",
    "#15912c",
    "#000000",
    "#5cc433",
    "#66c19e",
    "#2c6347",
    "#373d34",
    "#efc9dc",
    "#ea7269",
    "#332f04",
    "#27233f",
]
