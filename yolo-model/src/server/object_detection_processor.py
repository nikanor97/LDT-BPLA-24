import os
import json
from concurrent.futures import ThreadPoolExecutor
from sahi import AutoDetectionModel
from sahi.predict import get_sliced_prediction, get_prediction
from sahi.utils.cv import read_image
import cv2
import numpy as np
from sklearn.metrics import precision_score, recall_score


class ObjectDetectionProcessor:
    def __init__(self, ckpt_path, input_dir, output_dir, device='cpu', confidence_thresholds=None, image_size=640):
        self.ckpt_path = ckpt_path
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        self.default_confidence_threshold = 0.25

        self.confidence_thresholds = confidence_thresholds if confidence_thresholds else {}

        self.detection_model = AutoDetectionModel.from_pretrained(
            model_type='yolov8',
            model_path=self.ckpt_path,
            confidence_threshold=self.default_confidence_threshold,
            image_size=image_size,
            device=device
        )

    def apply_custom_nms(self, boxes, scores, predictions, iou_threshold=0.8):
        indices = cv2.dnn.NMSBoxes(boxes, scores, score_threshold=self.default_confidence_threshold, nms_threshold=iou_threshold)
        if len(indices) == 0:
            return []
        indices = indices.flatten()
        best_predictions = [predictions[i] for i in indices]
        return best_predictions

    def get_intersecting_box(self, box1, box2):
        x1 = min(box1[0], box2[0])
        y1 = min(box1[1], box2[1])
        x2 = max(box1[2], box2[2])
        y2 = max(box1[3], box2[3])
        return x1, y1, x2, y2

    def has_intersection(self, box1, box2, threshold=0.3):
        intersection_area = self.calculate_intersection_area(box1, box2)
        box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
        box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])

        if box1_area == 0 or box2_area == 0:
            return False

        intersection_ratio = intersection_area / min(box1_area, box2_area)
        return intersection_ratio > threshold

    def calculate_intersection_area(self, box1, box2):
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])

        if x2 <= x1 or y2 <= y1:
            return 0
        return (x2 - x1) * (y2 - y1)

    def filter_predictions_by_confidence(self, predictions):
        filtered_predictions = []
        for pred in predictions:
            class_id = pred.category.id
            threshold = self.confidence_thresholds.get(class_id, self.default_confidence_threshold)
            if pred.score.value >= threshold:
                filtered_predictions.append(pred)
        return filtered_predictions

    def process_image(self, image_path, filename):
        image = read_image(image_path)
        height, width = image.shape[:2]
        margin = 100

        slice_height = min(1280, height) if width > 2300 or height > 1500 else 640
        slice_width = min(1280, width) if width > 2300 or height > 1500 else 640

        result = get_sliced_prediction(
            image=image_path,
            detection_model=self.detection_model,
            slice_height=slice_height,
            slice_width=slice_width,
            overlap_height_ratio=0.3,
            overlap_width_ratio=0.3,
            perform_standard_pred=True
        )

        predictions = result.object_prediction_list
        predictions = self.filter_predictions_by_confidence(predictions)

        boxes = [(int(pred.bbox.minx), int(pred.bbox.miny), int(pred.bbox.maxx), int(pred.bbox.maxy)) for pred in predictions]
        scores = [pred.score.value for pred in predictions]

        initial_image = cv2.imread(image_path).copy()
        for box, pred in zip(boxes, predictions):
            x1, y1, x2, y2 = box
            class_id = pred.category.id
            score = pred.score.value
            cv2.rectangle(initial_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(initial_image, f'{class_id} {score:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)

        base, ext = os.path.splitext(filename)
        # initial_output_image_path = os.path.join(self.output_dir, f'{base}_before_nms{ext}')
        # cv2.imwrite(initial_output_image_path, initial_image)

        new_predictions = []
        visited = set()

        for i in range(len(boxes)):
            if i in visited:
                continue
            current_box = boxes[i]
            has_merged = False
            for j in range(i + 1, len(boxes)):
                if j in visited:
                    continue
                if self.has_intersection(current_box, boxes[j]):
                    merged_box = self.get_intersecting_box(current_box, boxes[j])
                    x1, y1, x2, y2 = merged_box

                    x1 = max(x1 - margin, 0)
                    y1 = max(y1 - margin, 0)
                    x2 = min(x2 + margin, width - 1)
                    y2 = min(y2 + margin, height - 1)

                    crop_img = image[y1:y2, x1:x2]
                    crop_result = get_prediction(image=crop_img, detection_model=self.detection_model)
                    # crop_result.export_visuals(export_dir=self.output_dir, file_name=f'{base}_bet{i}{ext}', text_size=0.5, rect_th=1)
                    for pred in crop_result.object_prediction_list:
                        new_x1 = x1 + int(pred.bbox.minx)
                        new_y1 = y1 + int(pred.bbox.miny)
                        new_x2 = x1 + int(pred.bbox.maxx)
                        new_y2 = y1 + int(pred.bbox.maxy)
                        new_predictions.append((new_x1, new_y1, new_x2, new_y2, pred.category.id, pred.score.value))
                    visited.add(j)
                    has_merged = True
                    break
            if not has_merged:
                pred = predictions[i]
                new_predictions.append((current_box[0], current_box[1], current_box[2], current_box[3], pred.category.id, pred.score.value))

        final_boxes = [box[:4] for box in new_predictions]
        final_scores = [box[5] for box in new_predictions]
        final_predictions = self.apply_custom_nms(final_boxes, final_scores, new_predictions, iou_threshold=0.8)

        # final_image = cv2.imread(image_path).copy()
        # for box in final_predictions:
        #     x1, y1, x2, y2, class_id, score = box
        #     cv2.rectangle(final_image, (x1, y1), (x2, y2), (255, 0, 0), 2)
        #     cv2.putText(final_image, f'{class_id} {score:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)

        # final_output_image_path = os.path.join(self.output_dir, f'{base}_after_nms{ext}')
        # cv2.imwrite(final_output_image_path, final_image)

        self.save_yolo_format(final_predictions, width, height, base)

        return final_predictions

    def save_yolo_format(self, predictions, img_width, img_height, base_filename):
        yolo_output_path = os.path.join(self.output_dir, f'{base_filename}.txt')
        with open(yolo_output_path, 'w') as file:
            for pred in predictions:
                x1, y1, x2, y2, class_id, score = pred
                x_center = (x1 + x2) / 2.0 / img_width
                y_center = (y1 + y2) / 2.0 / img_height
                width = (x2 - x1) / img_width
                height = (y2 - y1) / img_height
                file.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

    def process_all_images(self):
        with ThreadPoolExecutor() as executor:
            futures = []
            for filename in os.listdir(self.input_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_path = os.path.join(self.input_dir, filename)
                    futures.append(executor.submit(self.process_image, image_path, filename))

