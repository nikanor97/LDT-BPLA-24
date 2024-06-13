import json
import os
from datetime import datetime
from typing import Any, Awaitable, Callable, Optional

import aiohttp
from aio_pika.abc import AbstractIncomingMessage
from common.rabbitmq.consumer import Subscription
from loguru import logger

from common.rabbitmq.publisher import Publisher
from src.db.main_db_manager import MainDbManager

# from supply_common.db.messages import DuosReportValid

import settings
from src.db.projects.models import VideoStatusOption
from src.server.projects.models import (
    ContentMarkupCreate,
    FramesWithMarkupCreate,
    MarkupListCreate,
)
from src.server.projects.post_processing import post_process, get_score_map_df


class Server:
    def __init__(
        self,
        publisher: Publisher,  # For responses
        main_db_manager: Optional[MainDbManager] = None,
    ) -> None:
        self._main_db_manager = main_db_manager
        self._publisher = publisher
        # self._message_processors: dict[str, Callable[[dict[str, Any], dict[str, Any]], Awaitable[Any]]] = {
        self._message_processors: dict[
            str, Callable[[dict[str, Any]], Awaitable[Any]]
        ] = {
            "models_predictions": self._process_predictions,
            "data_for_models": self._make_predictions
            # "classification": self._process_classification_results,
            # "detection": self._process_detection_results,  # type: ignore
        }

    @property
    def subscriptions(self) -> list[Subscription]:
        return [
            # Subscription(
            #     # queue_name="callisto-integration" if not settings.LOCAL_RUN else "callisto-integration-local",
            #     queue_name="models",
            #     callback=self.process_incoming_message,
            #     routing_key=message_type,
            #     exchange_name="FromModels",
            # )
            # for message_type in list(self._message_processors.keys())
            Subscription(
                # queue_name="callisto-integration" if not settings.LOCAL_RUN else "callisto-integration-local",
                queue_name="models",
                callback=self.process_incoming_message,
                routing_key="models_predictions",
                exchange_name="FromModels",
            ),
            Subscription(
                # queue_name="callisto-integration" if not settings.LOCAL_RUN else "callisto-integration-local",
                queue_name="models",
                callback=self.process_incoming_message,
                routing_key="data_for_models",
                exchange_name="ToModels",
            ),
        ]

    async def process_incoming_message(self, message: AbstractIncomingMessage) -> None:
        local_logger = logger.bind(
            headers=message.headers,
            routing_key=message.routing_key,
            exchane=message.exchange,
        )
        try:
            if message.routing_key is None:
                raise ValueError("routing key somehow is empty")

            local_logger.info(f"Received message from callisto")

            body = message.body.decode("utf-8")
            # message_data = json.loads(body)["data"]
            # message_header = json.loads(body)["header"]
            data = json.loads(body)["data"]

            local_logger.info(
                f"Exchange: {message.exchange}, "
                f"Type: {message.routing_key}, "
                # f"File ID: {message_header['file_id']}"
            )

            if message.routing_key in self._message_processors:
                processor = self._message_processors[str(message.routing_key)]
                # await processor(message_data, message_header)
                await processor(data)

        except:
            local_logger.exception(
                "While proceeding callisto message an exception occurred"
            )

    async def _process_predictions(self, data: dict[str, Any]) -> None:
        pred_classification = data["pred_classification"]
        pred_detection = data["pred_detection"]
        project_id = data["project_id"]
        video_id = data["video_id"]
        scoremap_classification = data["scoremap_classification"]

        async with self._main_db_manager.projects.make_autobegin_session() as session:
            labels = await self._main_db_manager.projects.get_labels_by_project(
                session, project_id
            )
            video = await self._main_db_manager.projects.get_video(session, video_id)
        from pprint import pprint

        pprint(labels)

        labels_names = [l.name for l in labels]
        label_id_by_name = dict()
        for label in labels:
            label_id_by_name[label.name] = label.id

        # pred_classification = json.loads(pred_classification)

        def get_label_id_by_name(name: str):
            try:
                words = name.split(" ")
                if len(words) > 1:
                    name = words[0]
                return label_id_by_name[name]
            except KeyError as ke:
                print(ke)
                return label_id_by_name[list(label_id_by_name.keys())[0]]

        vmc = ContentMarkupCreate(
            video_id=video_id,
            frames=[
                FramesWithMarkupCreate(
                    frame_offset=frame["frame_id"],
                    markup_list=[
                        MarkupListCreate(
                            coord_top_left=(
                                int(box[0] * video.width),
                                int(box[1] * video.height),
                            ),
                            coord_bottom_right=(
                                int(box[2] * video.width),
                                int(box[3] * video.height),
                            ),
                            label_id=get_label_id_by_name(frame["labels"][idx]),
                            confidence=frame["logits"][idx],
                        )
                        for idx, box in enumerate(frame["boxes"])
                        if frame["labels"][idx] != "kitchen"
                    ],
                )
                for frame in pred_detection["frames"]
            ],
        )

        async with self._main_db_manager.projects.make_autobegin_session() as session:
            await self._main_db_manager.projects.create_frames_with_markups(
                session, vmc
            )
            await self._main_db_manager.projects.change_video_status(
                session, video_id, VideoStatusOption.extracted
            )

        score_map, frame_results = post_process(
            pred_classification,
            pred_detection["frames"],
            frames_num=len(pred_classification),
        )
        print(score_map)
        score_map_df = get_score_map_df(score_map)

        # Here we use scoremap values from Alexander (cls model) everywhere where pred != -1
        # In cases where pred == 1 we use detection results from Oleg
        model_preds = score_map_df["Готовность Модель"]
        for idx, (val_det, val_cls) in enumerate(
            zip(model_preds, scoremap_classification)
        ):
            if val_cls == -1:
                model_preds[idx] = val_det
            else:
                model_preds[idx] = val_cls
        score_map_df["Готовность Модель"] = model_preds

        os.makedirs(settings.MEDIA_DIR / "score_maps", exist_ok=True)
        filename = f"{datetime.now().timestamp()}_{video_id}.csv"
        score_map_df.to_csv(settings.MEDIA_DIR / "score_maps" / filename)

    async def _make_predictions(self, data: dict[str, Any]) -> None:
        video_name = data["video_name"]
        labels_names = data["labels_names"]
        project_id = data["project_id"]
        video_id = data["video_id"]

        async with aiohttp.ClientSession() as session:
            data = {
                # "url": "file:///media/video/PXL_20230528_131042238.TS_1a0d0f83-827e-4af6-a37a-1b997102eb07.mp4",
                "url": f"file:///media/video/{video_name}",
                "labels": labels_names,
                "frames_step": settings.CLIP_FRAME_STEP,
            }

            async with session.post(
                f"http://{settings.CLIP_HOST}:{settings.CLIP_PORT}/detect", json=data
            ) as resp:
                pred_detection = await resp.json()

        # print(pred_detection)

        # async with aiohttp.ClientSession() as session:
        #     async with session.get(
        #         f"http://{settings.CLASSIFIER_HOST}:{settings.CLASSIFIER_PORT}/predict?file_name=/media/video/{video_name}"
        #     ) as resp:
        #         pred_classification = await resp.text()

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://{settings.CLASSIFIER_HOST}:{settings.CLASSIFIER_PORT}/predict?file_name=/media/video/{video_name}"
            ) as resp:
                classification_resp = await resp.text()

        classification_resp = json.loads(classification_resp)
        pred_classification = classification_resp["data"]

        # TODO: Use it together inside the post_processing.py
        scoremap_values = classification_resp["scores"]  # list, 27 elements

        message = dict()
        message["data"] = {
            "pred_classification": pred_classification,
            "scoremap_classification": scoremap_values,
            "pred_detection": pred_detection,
            "project_id": project_id,
            "video_id": video_id,
        }
        rabbit_message = await self._publisher.publish(
            routing_key="models_predictions",
            exchange_name="FromModels",
            data=message,
            ensure=False,
        )
        print(rabbit_message)

    # async def _process_duos_reports(self, message_data: dict[str, Any], message_header: dict[str, Any]) -> None:
    #     async with self._main_db_manager.messages.make_autobegin_session() as session:
    #         for charge in message_data["charges_by_settlement_class_list"]:
    #             await self._main_db_manager.messages.add_duos_report(
    #                 session=session,
    #                 # TODO: move the message to Schema Registry
    #                 value=DuosReportValid(
    #                     gsp_group_id=message_data["attrs"]["gsp_group_id"],
    #                     profile_class=charge["profile_class_id"],
    #                     settlement_date=datetime.strptime(message_data["attrs"]["settlement_date"], "%Y%m%d"),
    #                     llf_class_id=int(charge["line_loss_factor_class_id"]),
    #                     time_pattern_regime=charge["time_pattern_regime"],
    #                     ssc_id=charge["standard_settlement_configuration_id"],
    #                     settlement_class_msid_charge=charge["settlement_class_msid_charge"],
    #                     settlement_class_unit_charge=charge["settlement_class_unit_charge"],
    #                     file_id=message_header["file_id"],
    #                 ),
    #             )
    #         logger.info("DUoS report was added")
    #
    # async def _process_g1(self, message_data: list[dict[str, Any]], message_header: dict[str, Any]) -> None:
    #     async with self._main_db_manager.customers.make_autobegin_session() as session:
    #         # TODO: add saving received messages to the DB
    #         for reading in message_data:
    #             if reading["g1a"]["activity"] == "GAIN":
    #                 mpan = reading["g1a"]["mpan"]
    #                 try:
    #                     db_meter = await self._main_db_manager.customers.read_meter(session, mpan=mpan)
    #                     if db_meter is not None:
    #                         await db_meter.update(session, {"switch_status": "live"})
    #                 except NoResultFound:
    #                     logger.warning(f"G0001 message received, but no {mpan=} found in meter DB.")
