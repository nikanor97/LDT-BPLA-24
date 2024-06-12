# verification_tags = {
#     "Помещения": [
#         ("Жилая комната/кухня", "kitchen_or_living_room"),
#         ("Ванная комната", "bathroom"),
#         ("Коридор внутри квартиры", "corridor"),
#     ],
#     "Предметы": [
#         ("Наличие двери", "door"),
#         ("Дверной проем пустой", "empty_doorway"),
#         ("Наличие унитаза", "toilet"),
#         ("Наличия ванны", "bathtub"),
#         ("Наличие электрической розетки или выключателя", "switch"),
#         ("Наличие кухни", "kitchen"),
#         ("Унитаз", "toilet"),
#         ("Раковина", "sink"),
#         ("Мусор", "trash"),
#     ],
#     "Частичная отделка": [
#         ("Пол чистовая отделка (ламинат, плитка)", "clean_floor"),
#         ("Потолок чистовая отделка (натяжной потолок, грильято)", "clean_ceiling"),
#         ("Стена чистовая отделка (обои, покраска, плитка)", "clean_wall"),
#         ("Стена черновая отделка (штукатурка)", "dirty_wall"),
#         ("Стена без отделки", "undecorated_wall"),
#         ("Отделка окна (подоконник, откосы)", "decorated_window"),
#     ],
# }

verification_tags = {
    "Регулярные объекты": [
        ("Птицы", "bird"),
        ("Самолеты", "plane"),
        ("Вертолеты", "helicopter"),
    ],
    "БПЛА": [
        ("Квадракоптеры", "uav"),
        ("БПЛА самолетного типа", "fixed-wing-uav"),
    ]
}


tag_translation = {
    "Коридор внутри квартиры": "corridor",
    "Дверь": "door",
    "Дверной проем пустой": "emptydoorway",
    "Наличие электрической розетки или выключателя": "switch",
    "Кухня": "kitchen",
    "Унитаз": "toilet",
    "Раковина": "sink",
    "Мусор": "garbage",
    "Батарея": "radiator",
    "Ванна": "bath",
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
