from typing import Dict, List

import pandas as pd

DEFAULT_FRAME_DIFF_THRESHOLD = (
    10  # сколько фреймов должно пройти, чтобы считать, что объект исчез
)

tag_translation = {
    "Коридор внутри квартиры": "corridor",
    "Дверь": "door",
    "Дверной проем пустой": "doorway",
    "Окно": "window",
    "Наличие электрической розетки или выключателя": "switch",
    "Кухня": "kitchen",
    "Унитаз": "toilet",
    "Раковина": "sink",
    "Мусор": "garbage",
    "Батарея": "radiator",
    "Ванна": "bath",
}


def to_most_close_frames(ids, frames_num):
    most_close_ids = []
    last_id = 0
    for i in range(frames_num):
        next_id = min(last_id + 1, len(ids) - 1)
        last_diff = (ids[last_id] - i) ** 2
        next_diff = (ids[next_id] - i) ** 2
        if last_diff < next_diff:
            most_close_ids.append(ids[last_id])
        else:
            most_close_ids.append(ids[next_id])
            last_id = next_id

    return most_close_ids


def all_frames_data(classification, detection, frames_num):
    cls_ids_input = list(sorted([int(fid) for fid in classification.keys()]))
    cls_ids = to_most_close_frames(cls_ids_input, frames_num)

    detection_ids_input = list(sorted(detection.keys()))
    detection_ids = to_most_close_frames(detection_ids_input, frames_num)

    print(f"Упорядочили индексы фреймов {cls_ids} / {detection_ids}")

    all_data = list(
        zip(
            [classification[str(i)] for i in cls_ids],
            [detection[i] for i in detection_ids],
        )
    )

    return all_data


def classify_mop(frame_classification, frame_detection, mop_threshold=0.5):
    if (
        max(
            frame_classification["corridor"],
            frame_classification["public_place"],
            frame_classification["other"],
        )
        > mop_threshold
    ):
        return True
    else:
        return False


def classify_room_or_kitchen(frame_classification, frame_detection, threshold=0.5):
    if max(frame_classification["room"], frame_classification["kitchen"]) > threshold:
        return True
    else:
        return False


def classify_bathroom_or_toilet(frame_classification, frame_detection, threshold=0.5):
    if frame_classification["bathroom"] > threshold:
        return True
    else:
        return False


def classify_floor(frame_classification, frame_detection):
    data = {
        "finishing": frame_classification["finishing_floor"],
        "rough": frame_classification["rough_floor"],
        "no": frame_classification["no_floor"],
    }
    max_key = max(data, key=data.get)
    return max_key


def classify_ceiling(frame_classification, frame_detection):
    data = {
        "finishing": frame_classification["finishing_ceiling"],
        "rough": frame_classification["rough_ceiling"],
        "no": frame_classification["no_ceiling"],
    }
    max_key = max(data, key=data.get)
    return max_key


def classify_wall(frame_classification, frame_detection):
    data = {
        "finishing": frame_classification["finishing_wall"],
        "rough": frame_classification["rough_wall"],
        "no": frame_classification["no_wall"],
    }
    max_key = max(data, key=data.get)
    return max_key


def classify_garbage(frame_classification, frame_detection, frame_diff, th=0.6):
    label = tag_translation["Мусор"]
    garbage_probs = frame_detection.get(label, [0.0])
    # garbage_boxes = frame_detection.get(label + "_boxes", [ ] )
    garbage_prob = max(garbage_probs)
    if garbage_prob > th:
        is_new_garbage = frame_diff > DEFAULT_FRAME_DIFF_THRESHOLD
        return True, garbage_prob
    else:
        return False, 0.0


def classify_switch(frame_classification, frame_detection, frame_diff, th=0.5):
    label = tag_translation["Наличие электрической розетки или выключателя"]
    switch_probs = frame_detection.get(label, [0.0])
    switch_count = len([p for p in switch_probs if p > th])
    if switch_count > 0:
        is_new_switch = frame_diff > DEFAULT_FRAME_DIFF_THRESHOLD
        return True, is_new_switch, switch_count
    else:
        return False, False, 0


def default_classify_and_new(probs, frame_diff, th=0.5):
    is_new = frame_diff > DEFAULT_FRAME_DIFF_THRESHOLD
    score = max(probs)
    return score > th, is_new, score


def classify_door(frame_classification, frame_detection, frame_diff, th=0.35):
    label_no = tag_translation["Дверной проем пустой"]
    probs_no = frame_detection.get(label_no, [0.0])
    is_door_no, is_new_door_no, score_no = default_classify_and_new(
        probs_no, frame_diff, th=th / 2
    )

    label_yes = tag_translation["Наличие электрической розетки или выключателя"]
    probs_yes = frame_detection.get(label_yes, [0.0])
    is_door_yes, is_new_door_yes, score_yes = default_classify_and_new(
        probs_yes, frame_diff, th=th
    )
    door_count = len([p for p in probs_yes + probs_no if p > th / 2])

    if is_door_no or is_door_yes:
        cls_score = ((1 - score_no) + score_yes) / 2
        cls_score = max(cls_score, 0)
        cls_score = min(cls_score, 1)
        ready_doors = round(door_count * cls_score)

        return True, is_new_door_no or is_new_door_yes, ready_doors, door_count

    return False, False, False, 0


def classify_bathtub(frame_classification, frame_detection, frame_diff):
    label = tag_translation["Ванна"]
    probs = frame_detection.get(label, [0.0])
    return default_classify_and_new(probs, frame_diff, th=0.7)


def classify_toilet(frame_classification, frame_detection, frame_diff):
    label = tag_translation["Унитаз"]
    probs = frame_detection.get(label, [0.0])
    return default_classify_and_new(probs, frame_diff, th=0.7)


def classify_sink(frame_classification, frame_detection, frame_diff):
    label = tag_translation["Раковина"]
    probs = frame_detection.get(label, [0.0])
    return default_classify_and_new(probs, frame_diff, th=0.7)


def classify_battery(frame_classification, frame_detection, frame_diff):
    label = tag_translation["Батарея"]
    probs = frame_detection.get(label, [0.0])
    return default_classify_and_new(probs, frame_diff, th=0.3)


def classify_kitchen(frame_classification, frame_detection, frame_diff):
    label = tag_translation["Кухня"]
    probs = frame_detection.get(label, [0.0])
    return default_classify_and_new(probs, frame_diff, th=0.3)


def classify_window(frame_classification, frame_detection, frame_diff, th=0.7):
    label = tag_translation["Окно"]
    probs = frame_detection.get(label, [0.0])
    return default_classify_and_new(probs, frame_diff, th=th)


def post_process(classification: Dict, detection_input: List[Dict], frames_num: int):
    detection = {}
    for det_data in detection_input:
        labels = det_data["labels"]
        logits = det_data["logits"]
        boxes = det_data["boxes"]
        detection[det_data["frame_id"]] = {}

        for i in range(len(labels)):
            label = labels[i]
            prob = logits[i]
            box = boxes[i]
            if label not in detection[det_data["frame_id"]]:
                detection[det_data["frame_id"]][label] = []
                detection[det_data["frame_id"]][label + "_boxes"] = []
            detection[det_data["frame_id"]][label].append(prob)
            detection[det_data["frame_id"]][label + "_boxes"].append(box)

    all_data = all_frames_data(classification, detection, frames_num)

    print(f"all_data[:10]: {all_data[:10]}")

    frame_results = []

    default_last = -1 - DEFAULT_FRAME_DIFF_THRESHOLD
    last_door_frame_id = default_last
    last_switch_frame_id = default_last
    last_window_frame_id = default_last
    last_garbage_frame_id = default_last
    last_bathtub_frame_id = default_last
    last_toilet_frame_id = default_last
    last_sink_frame_id = default_last
    last_battery_frame_id = default_last
    last_kitchen_frame_id = default_last

    for i, (frame_cls, frame_det) in enumerate(all_data):
        result = {}
        result["classification"] = frame_cls
        result["detection"] = frame_det

        is_mop = classify_mop(frame_cls, frame_det)
        result["mop"] = is_mop

        # Это для всех разделяем потом по МОП
        floor = classify_floor(frame_cls, frame_det)
        result["floor"] = floor
        ceiling = classify_ceiling(frame_cls, frame_det)
        result["ceiling"] = ceiling
        wall = classify_wall(frame_cls, frame_det)
        result["wall"] = wall

        # для счетчиков
        is_door, is_new_door, door_cls, door_count = classify_door(
            frame_cls, frame_det, i - last_door_frame_id
        )
        if is_door:
            last_door_frame_id = i
            result["door"] = (is_new_door, door_cls, door_count)

        garbage, garbage_score = classify_garbage(
            frame_cls, frame_det, i - last_garbage_frame_id
        )
        if garbage:
            result["garbage"] = garbage_score

        is_switch, is_new_switch, switch_count = classify_switch(
            frame_cls, frame_det, i - last_switch_frame_id
        )
        if is_switch:
            last_switch_frame_id = i
            result["switch"] = (is_new_switch, switch_count)

        # ванные
        is_bathtub, is_new_bathtub, bath_score = classify_bathtub(
            frame_cls, frame_det, i - last_bathtub_frame_id
        )
        if is_bathtub:
            last_bathtub_frame_id = i
            result["bathtub"] = (is_new_bathtub, bath_score)

        is_toilet, is_new_toilet, toilet_score = classify_toilet(
            frame_cls, frame_det, i - last_toilet_frame_id
        )
        if is_toilet:
            last_toilet_frame_id = i
            result["toilet"] = (is_new_toilet, toilet_score)

        is_sink, is_new_sink, sink_score = classify_sink(
            frame_cls, frame_det, i - last_sink_frame_id
        )
        if is_sink:
            last_sink_frame_id = i
            result["sink"] = (is_new_sink, sink_score)

        # объекты из конкретных комнат
        # if not is_mop:
        #     is_room_or_kitchen = classify_room_or_kitchen(frame_cls, frame_det)
        #     if is_room_or_kitchen:
        #         result["room"] = is_room_or_kitchen
        is_window, is_new_window, window_score = classify_window(
            frame_cls, frame_det, i - last_window_frame_id
        )
        if is_window:
            last_window_frame_id = i
            result["window"] = (is_new_window, window_score)

        is_battery, is_new_battery, battery_score = classify_battery(
            frame_cls, frame_det, i - last_battery_frame_id
        )
        if is_battery:
            last_battery_frame_id = i
            result["battery"] = (is_new_battery, battery_score)

        is_kitchen, is_new_kitchen, score = classify_kitchen(
            frame_cls, frame_det, i - last_kitchen_frame_id
        )
        if is_kitchen:
            last_kitchen_frame_id = i
            result["kitchen"] = (is_new_kitchen, score)

        frame_results.append(result)

    # финальный агрегат
    score_map = {}
    mop_frames = [res for res in frame_results if res["mop"]]
    score_map["mop_percent"] = len(mop_frames) / len(frame_results)
    score_map["mop_count"] = len(mop_frames)
    for cl in ["wall", "floor", "ceiling"]:
        for status in ["finishing", "rough", "no"]:
            if len(mop_frames) > 0:
                prop = len([res[cl] for res in mop_frames if res[cl] == status]) / len(
                    mop_frames
                )
            else:
                prop = 0
            score_map[f"mop_{cl}_{status}_percent"] = prop

    non_mop_frames = [res for res in frame_results if not res["mop"]]
    for cl in ["wall", "floor", "ceiling"]:
        for status in ["finishing", "rough", "no"]:
            if len(non_mop_frames) > 0:
                prop = len(
                    [res[cl] for res in non_mop_frames if res[cl] == status]
                ) / len(non_mop_frames)
            else:
                prop = 0
            score_map[f"non_mop_{cl}_{status}_percent"] = prop

    all_doors = [res["door"] for res in frame_results if "door" in res]

    doors_stat = {}
    doors_id = -1
    for door in all_doors:
        if door[0]:
            doors_id += 1
            doors_stat[doors_id] = []
        doors_stat[doors_id].append((door[1], door[2]))

    doors_count = 0
    finished_doors_count = 0
    for door in doors_stat:
        doors_count_agg = round(sum([d[1] for d in doors_stat[door]]) / len(doors_stat[door]))
        doors_count += doors_count_agg

        finished_doors_count_agg = round(sum([d[0] for d in doors_stat[door]]) / len(doors_stat[door]))
        finished_doors_count += finished_doors_count_agg

    finished_doors_percent = finished_doors_count / doors_count if doors_count > 0 else 0
    score_map["doors_count"] = doors_count
    score_map["finished_doors_percent"] = finished_doors_percent
    score_map["finished_doors_count"] = finished_doors_count

    all_garbage = len([res for res in frame_results if "garbage" in res])
    found_garbage = all_garbage > 0
    score_map["garbage"] = found_garbage

    all_switches = [res["switch"] for res in frame_results if "switch" in res]
    switches_new_only = [switch for switch in all_switches if switch[0]]
    switch_count = sum(switch[1] for switch in switches_new_only)
    score_map["switch_count"] = switch_count

    all_windows = [res["window"] for res in frame_results if "window" in res]
    finishing_windows = [window for window in all_windows if window[1] == "finishing"]
    finished_windows_percent = (
        len(finishing_windows) / len(all_windows) if len(all_windows) > 0 else 0
    )
    score_map["finished_windows_percent"] = finished_windows_percent

    all_bateries = [res for res in frame_results if "battery" in res]
    batteries_percent = (
        len(all_bateries) / len(all_windows) if len(all_windows) > 0 else 1
    )
    # TODO: не учитывается новые окна / батареи
    score_map["batteries_percent"] = min(1., batteries_percent)

    all_kitchens = [res["kitchen"] for res in frame_results if "kitchen" in res]
    kitchen_count = len([res for res in all_kitchens if res[0]])
    # kitchen_count = 1
    score_map["kitchen_count"] = kitchen_count

    # TODO: считать как долю от разных ванных комнат
    all_bathtubs = [res for res in frame_results if "bathtub" in res]
    bathtubs_count = len([res for res in all_bathtubs if res["bathtub"][0]])
    bathtub_percent = 1 if len(all_bathtubs) > 1 else 0
    score_map["bathtub_percent"] = bathtub_percent

    all_toilets = [res for res in frame_results if "toilet" in res]
    toilets_count = len([res for res in all_toilets if res["toilet"][0]])
    toilet_percent = 1 if len(all_toilets) > 1 else 0
    score_map["toilet_percent"] = toilet_percent

    all_sinks = [res for res in frame_results if "sink" in res]
    sink_count = len([res for res in all_sinks if res["sink"][0]])
    sink_percent = sink_count if len(all_sinks) > 1 else 0

    score_map["sink_percent"] = sink_percent

    return score_map, frame_results


def get_score_map_df(scores: Dict[str, float]) -> pd.DataFrame:
    score_map_dict = {
        "Тип помещения": [
            "Все помещения кроме МОП",
            "Все помещения кроме МОП",
            "Все помещения кроме МОП",
            "Все помещения кроме МОП",
            "Все помещения кроме МОП",
            "Все помещения кроме МОП",
            "Все помещения кроме МОП",
            "Все помещения кроме МОП",
            "Все помещения кроме МОП",
            "Все помещения",
            "Все помещения",
            "Все помещения",
            "Жилая/Кухня",
            "Жилая/Кухня",
            "Жилая/Кухня",
            "Ванная",
            "Ванная",
            "Ванная",
            "МОП",
            "МОП",
            "МОП",
            "МОП",
            "МОП",
            "МОП",
            "МОП",
            "МОП",
            "МОП",
        ],
        "Поверхность": [
            "Пол",
            "Пол",
            "Пол",
            "Стена",
            "Стена",
            "Стена",
            "Потолок",
            "Потолок",
            "Потолок",
            "-",
            "-",
            "-",
            "-",
            "-",
            "-",
            "-",
            "-",
            "-",
            "Пол",
            "Пол",
            "Пол",
            "Стена",
            "Стена",
            "Стена",
            "Потолок",
            "Потолок",
            "Потолок",
        ],
        "Класс": [
            "Нет отделки",
            "Черновая",
            "Чистовая",
            "Нет отделки",
            "Черновая",
            "Чистовая",
            "Нет отделки",
            "Черновая",
            "Чистовая",
            "Двери",
            "Мусор",
            "Розетки и выключатели",
            "Отделка окна",
            "Установленная батарея",
            "Кухня",
            "Унитаз",
            "Ванна",
            "Раковина",
            "Нет отделки",
            "Черновая",
            "Чистовая",
            "Нет отделки",
            "Черновая",
            "Чистовая",
            "Нет отделки",
            "Черновая",
            "Чистовая",
        ],
        "Метрика": [
            "Доля помещений с этим состоянием",
            "Доля помещений с этим состоянием",
            "Доля помещений с этим состоянием",
            "Доля помещений с этим состоянием",
            "Доля помещений с этим состоянием",
            "Доля помещений с этим состоянием",
            "Доля помещений с этим состоянием",
            "Доля помещений с этим состоянием",
            "Доля помещений с этим состоянием",
            "Доля от дверных проемов",
            "Факт наличия",
            "Количество",
            "Доля от общего числа окон",
            "Доля от общего числа окон",
            "Количество",
            "Доля от ванных комнат",
            "Доля от ванных комнат",
            "Доля от ванных комнат",
            "Доля помещений с этим состоянием",
            "Доля помещений с этим состоянием",
            "Доля помещений с этим состоянием",
            "Доля помещений с этим состоянием",
            "Доля помещений с этим состоянием",
            "Доля помещений с этим состоянием",
            "Доля помещений с этим состоянием",
            "Доля помещений с этим состоянием",
            "Доля помещений с этим состоянием",
        ],
        "Готовность Модель": [
            scores["non_mop_floor_no_percent"],
            scores["non_mop_floor_rough_percent"],
            scores["non_mop_floor_finishing_percent"],
            scores["non_mop_wall_no_percent"],
            scores["non_mop_wall_rough_percent"],
            scores["non_mop_wall_finishing_percent"],
            scores["non_mop_ceiling_no_percent"],
            scores["non_mop_ceiling_rough_percent"],
            scores["non_mop_ceiling_finishing_percent"],
            scores["doors_count"],
            scores["garbage"],
            scores["switch_count"],
            scores["finished_windows_percent"],
            scores["batteries_percent"],
            scores["kitchen_count"],
            scores["toilet_percent"],
            scores["bathtub_percent"],
            scores["sink_percent"],
            scores["mop_floor_no_percent"],
            scores["mop_floor_rough_percent"],
            scores["mop_floor_finishing_percent"],
            scores["mop_wall_no_percent"],
            scores["mop_wall_rough_percent"],
            scores["mop_wall_finishing_percent"],
            scores["mop_ceiling_no_percent"],
            scores["mop_ceiling_rough_percent"],
            scores["mop_ceiling_finishing_percent"],
        ],
    }
    return pd.DataFrame(score_map_dict)


if __name__ == "__main__":
    import random

    default_cls = lambda: {
        "finishing_floor": random.random(),
        "finishing_ceiling": random.random(),
        "finishing_wall": random.random(),
        "finishing_window": random.random(),
        "rough_floor": random.random(),
        "rough_ceiling": random.random(),
        "rough_wall": random.random(),
        "rough_window": random.random(),
        "no_floor": random.random(),
        "no_ceiling": random.random(),
        "no_wall": random.random(),
        "no_window": random.random(),
        "room": 0.9792545437812805,
        "kitchen": 0.02042144536972046,
        "bathroom": 0.022412117570638657,
        "corridor": 0.015363739803433418,
        "public_place": 0.0077429567463696,
        "other": 0.006326529663056135,
    }

    ## приближенный сценарий с МОП в начале
    test_classification = {str(i): default_cls() for i in range(100)}

    for i in range(10):
        test_classification[str(i)]["corridor"] = 0.9

    for i in range(10, 20):
        test_classification[str(i)]["bathroom"] = 0.9

    for i in range(20, 30):
        test_classification[str(i)]["kitchen"] = 0.9

    default_data = lambda fid: {
        "frame_id": fid,
        "boxes": [
            [
                0.4743027687072754,
                0.5019789934158325,
                0.7934666275978088,
                0.8652052879333496,
            ]
        ],
        "logits": [0.8834880590438843],
        "labels": ["toilet"],
    }
    test_detection = [default_data(i * 2) for i in range(50)]

    for i in range(10, 15):
        test_detection[i]["labels"] = ["bath", "sink"]
        test_detection[i]["logits"] = [0.8834880590438843, 0.8834880590438843]
        test_detection[i]["boxes"] = [
            [
                0.4743027687072754,
                0.5019789934158325,
                0.7934666275978088,
                0.8652052879333496,
            ],
            [
                0.4743027687072754,
                0.5019789934158325,
                0.7934666275978088,
                0.8652052879333496,
            ],
        ]

    for i in range(20, 25):
        test_detection[i]["labels"] = ["switch", "switch", "window", "switch"]
        test_detection[i]["logits"] = [
            0.8834880590438843,
            0.8834880590438843,
            0.8834880590438843,
            0.8834880590438843,
        ]
        test_detection[i]["boxes"] = [
            [
                0.4743027687072754,
                0.5019789934158325,
                0.7934666275978088,
                0.8652052879333496,
            ]
            for i in range(4)
        ]

    for i in range(40, 45):
        test_detection[i]["labels"] = ["switch", "switch", "window", "switch"]
        test_detection[i]["logits"] = [
            0.8834880590438843,
            0.8834880590438843,
            0.8834880590438843,
            0.8834880590438843,
        ]
        test_detection[i]["boxes"] = [
            [
                0.4743027687072754,
                0.5019789934158325,
                0.7934666275978088,
                0.8652052879333496,
            ]
            for i in range(4)
        ]

    for i in range(30, 35):
        test_detection[i]["labels"] = ["nothing in the doorway"]

    for i in range(15, 20):
        test_detection[i]["labels"] = ["nothing in the doorway"]

    for i in range(45, 50):
        test_detection[i]["labels"] = ["door"]

    # score_map, frame_results = post_process(
    #     test_classification, test_detection, frames_num=100
    # )
    # print(score_map)
    # print(frame_results)
    from detections import *
    score_map, frame_results = post_process(
        test_classification, detection_no_1["frames"], frames_num=450
    )
#     ## Дверь	Мусор?	Розеток	Отделка окна	Батарея	Кухня	Унитаз	Ванна	Раковина
# 9	10	11	12	13	14	15	16	17
# 0.0	0.0	0.0	0.0	1.0	1.0	0.0	0.0	0.0
    assert score_map["finished_doors_percent"] == 0, score_map["finished_doors_percent"]
    assert score_map["garbage"] == False, score_map["garbage"]
    assert score_map["switch_count"] == 0, score_map["switch_count"]
    # assert score_map["finished_windows_percent"] == 0, score_map["finished_windows_percent"]
    assert score_map["batteries_percent"] == 1, score_map["batteries_percent"]
    assert score_map["kitchen_count"] == 1, score_map["kitchen_count"]
    # 'bathtub_percent': 0.0, 'toilet_percent': 0.0, 'sink_percent': 0.0}
    assert score_map["bathtub_percent"] == 0, score_map["bathtub_percent"]
    assert score_map["toilet_percent"] == 0, score_map["toilet_percent"]
    assert score_map["sink_percent"] == 0, score_map["sink_percent"]

    print(score_map)


    score_map, frame_results = post_process(
        test_classification, detections_rough_0["frames"], frames_num=590
    )

    assert score_map["finished_doors_percent"] == 0, score_map["finished_doors_percent"]
    assert score_map["garbage"] == False, score_map["garbage"]
    assert score_map["switch_count"] == 0, score_map["switch_count"]
    # assert score_map["finished_windows_percent"] == 0, score_map["finished_windows_percent"]
    assert score_map["batteries_percent"] == 1, score_map["batteries_percent"]
    assert score_map["kitchen_count"] == 1, score_map["kitchen_count"]
    # 'bathtub_percent': 0.0, 'toilet_percent': 0.0, 'sink_percent': 0.0}
    assert score_map["bathtub_percent"] == 0, score_map["bathtub_percent"]
    assert score_map["toilet_percent"] == 0, score_map["toilet_percent"]
    assert score_map["sink_percent"] == 0, score_map["sink_percent"]

    print(score_map)

    score_map, frame_results = post_process(
        test_classification, detections_rough_4["frames"], frames_num=2010
    )

    assert score_map["finished_doors_percent"] == 0.6666666666666666, score_map["finished_doors_percent"]
    assert score_map["garbage"] == False, score_map["garbage"]
    assert score_map["switch_count"] == 0, score_map["switch_count"]
    # assert score_map["finished_windows_percent"] == 0, score_map["finished_windows_percent"]
    assert score_map["batteries_percent"] == 1, score_map["batteries_percent"]
    assert score_map["kitchen_count"] == 1, score_map["kitchen_count"]
    # 'bathtub_percent': 0.0, 'toilet_percent': 0.0, 'sink_percent': 0.0}
    assert score_map["bathtub_percent"] == 0, score_map["bathtub_percent"]
    assert score_map["toilet_percent"] == 0, score_map["toilet_percent"]
    assert score_map["sink_percent"] == 0, score_map["sink_percent"]

    print(score_map)

    score_map, frame_results = post_process(
        test_classification, finishing["frames"], frames_num=220
    )

    assert score_map["finished_doors_percent"] == 1., score_map["finished_doors_percent"]
    assert score_map["garbage"] == False, score_map["garbage"]
    assert score_map["switch_count"] == 0, score_map["switch_count"]
    # assert score_map["finished_windows_percent"] == 0, score_map["finished_windows_percent"]
    assert score_map["batteries_percent"] == 1, score_map["batteries_percent"]
    assert score_map["kitchen_count"] == 1, score_map["kitchen_count"]
    # 'bathtub_percent': 0.0, 'toilet_percent': 0.0, 'sink_percent': 0.0}
    assert score_map["bathtub_percent"] == 1, score_map["bathtub_percent"]
    assert score_map["toilet_percent"] == 1, score_map["toilet_percent"]
    assert score_map["sink_percent"] == 1, score_map["sink_percent"]

    print(score_map)
