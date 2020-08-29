# -*- coding: utf-8 -*-
"""App Models.
"""

import datetime
import logging
import threading
import time

import requests
from azure.cognitiveservices.vision.customvision.training.models import \
    CustomVisionErrorException
from django.db import models
from django.db.models.signals import pre_save
from django.utils import timezone

from ..azure_settings.models import Setting
from .exceptions import CannotChangeDemoProjectError

logger = logging.getLogger(__name__)


class Project(models.Model):
    """Azure Custom Vision Project Model
    """

    setting = models.ForeignKey(Setting, on_delete=models.CASCADE, null=True)
    customvision_id = models.CharField(max_length=200,
                                       null=True,
                                       blank=True,
                                       default="")
    name = models.CharField(max_length=200, null=True, blank=True, default="")
    download_uri = models.CharField(max_length=1000,
                                    null=True,
                                    blank=True,
                                    default="")
    training_counter = models.IntegerField(default=0)
    is_demo = models.BooleanField(default=False)

    # e.g. relabel
    retraining_counter = models.IntegerField(default=0)
    maxImages = models.IntegerField(default=20)
    needRetraining = models.BooleanField(default=True)
    relabel_expired_time = models.DateTimeField(default=timezone.now)

    def __repr__(self):
        return self.name.__repr__()
    
    def __str__(self):
        return self.name.__str__()

    @staticmethod
    def pre_save(**kwargs):
        """pre_save.

        Args:
            kwargs:
        """
        instance = kwargs["instance"]
        if instance.is_demo and instance.id:
            raise CannotChangeDemoProjectError
        try:
            logger.info("Project pre_save start")
            logger.info("Project id given: %s", instance.id)
            logger.info("Project customvision_id given: %s",
                        instance.customvision_id)
            logger.info("Project name given: %s", instance.name)
            logger.info("Checking...")
            if not instance.setting:
                logger.info("Project instance is demo. Pass pre_save")
                return
            if not instance.setting or not instance.setting.is_trainer_valid:
                instance.customvision_id = ""
                logger.info("Invalid setting. Set customvision id to ''")
                return
            trainer = instance.setting.get_trainer_obj()
            if instance.customvision_id:
                # Endpoint and Training_key is valid, and trying to save with
                # customvision_id...
                project = trainer.get_project(instance.customvision_id)
                instance.name = project.name
                logger.info("Project Found. Set instance.name to %s",
                            instance.name)
                return

            # Setting is valid, no customvision_id
            instance.name = (instance.name or
                             "VisionOnEdge-" +
                             datetime.datetime.utcnow().isoformat())
        except:
            logger.exception("Project pre_save Exception")
            instance.customvision_id = ""
        finally:
            logger.info("Project id set: %s", instance.id)
            logger.info("Project customvision_id set: %s",
                        instance.customvision_id)
            logger.info("Project name set: %s", instance.name)
            logger.info("Project pre_save end")

    def dequeue_iterations(self, max_iterations: int = 2):
        """dequeue_iterations.

        Args:
            max_iterations (int): max_iterations
        """
        try:
            trainer = self.setting.revalidate_and_get_trainer_obj()
            if not trainer:
                return
            if not self.customvision_id:
                return
            iterations = trainer.get_iterations(self.customvision_id)
            if len(iterations) > max_iterations:
                # TODO delete train in Train Model
                trainer.delete_iteration(self.customvision_id,
                                         iterations[-1].as_dict()["id"])
        except CustomVisionErrorException as customvision_err:
            logger.error(customvision_err)
        except:
            logger.exception("dequeue_iteration error")
            raise

    def create_project(self):
        """Create a project on CustomVision
        """
        logger.info("Creating obj detection project")

        trainer = self.setting.get_trainer_obj()
        try:
            if not self.name:
                self.name = ("VisionOnEdge-" +
                             datetime.datetime.utcnow().isoformat())
            project = trainer.create_project(
                name=self.name,
                domain_id=self.setting.obj_detection_domain_id,
            )
            self.customvision_id = project.id
            self.name = project.name
            update_fields = ["customvision_id", "name"]
            self.save(update_fields=update_fields)
        except CustomVisionErrorException as customvision_err:
            logger.error("Project create_project error %s", customvision_err)
            raise customvision_err
        except:
            logger.exception("Project create_project: Unexpected Error")
            raise

    def delete_tag_by_name(self, tag_name):
        """delete tag on custom vision"""
        logger.info("deleting tag: %s", tag_name)
        if not self.setting.is_trainer_valid:
            return
        if not self.customvision_id:
            return
        trainer = self.setting.get_trainer_obj()
        tags = trainer.get_tags(project_id=self.customvision_id)
        for tag in tags:
            if tag.name.lower() == tag_name.lower():
                trainer.delete_tag(project_id=self.customvision_id,
                                   tag_id=tag.id)
                logger.info("tag deleted: %s", tag_name)
                return

    def delete_tag_by_id(self, tag_id):
        """delete tag on custom vision"""
        logger.info("deleting tag: %s", tag_id)
        if not self.setting.is_trainer_valid:
            return
        if not self.customvision_id:
            return
        trainer = self.setting.get_trainer_obj()
        trainer.delete_tag(project_id=self.customvision_id, tag_id=tag_id)
        return

    def train_project(self):
        """
        Submit training task to CustomVision.
        Return training task submit result (boolean)
        : Success: return True
        : Failed : return False
        """
        is_task_success = False
        update_fields = []
        try:
            trainer = self.setting.revalidate_and_get_trainer_obj()
            if not trainer:
                logger.error("Trainer is invalid. Not going to train...")

            # Submit training task to CustomVision
            logger.info("%s %s submit training task to CustomVision",
                        self.customvision_id, self.name)
            trainer.train_project(self.customvision_id)

            # If all above is success
            is_task_success = True
            return is_task_success
        except CustomVisionErrorException as customvision_err:
            logger.error("From Custom Vision: %s", customvision_err.message)
            raise
        except Exception:
            logger.exception("Unexpected error while Project.train_project")
            raise
        finally:
            self.save(update_fields=update_fields)

    def export_iterationv3_2(self, iteration_id):
        """
        CustomVisionTrainingClient SDK may have some issues exporting
        Use the REST API
        """
        # trainer.export_iteration(customvision_id,
        # iteration.id,
        # 'ONNX')
        setting_obj = self.setting
        url = (setting_obj.endpoint + "customvision/v3.2/training/projects/" +
               self.customvision_id + "/iterations/" + iteration_id +
               "/export?platform=ONNX")
        res = requests.post(url,
                            "{body}",
                            headers={"Training-key": setting_obj.training_key})
        return res


class Task(models.Model):
    """Task Model"""

    task_type = models.CharField(max_length=100)
    status = models.CharField(max_length=200)
    log = models.CharField(max_length=1000)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def start_exporting(self):
        """Start Exporting"""

        def _export_worker(self):
            """Export Model Worker"""
            project_obj = self.project
            trainer = project_obj.setting.revalidate_and_get_trainer_obj()
            customvision_id = project_obj.customvision_id
            while True:
                time.sleep(1)
                iterations = trainer.get_iterations(customvision_id)
                if len(iterations) == 0:
                    logger.error("failed: not yet trained")
                    self.status = "running"
                    self.log = "failed: not yet trained"
                    self.save()
                    return

                iteration = iterations[0]
                if not iteration.exportable or iteration.status != "Completed":
                    self.status = "running"
                    self.log = "Status : training model"
                    self.save()
                    continue

                exports = trainer.get_exports(customvision_id, iteration.id)
                if len(exports) == 0 or not exports[0].download_uri:
                    logger.info("Status: exporting model")
                    self.status = "running"
                    self.log = "Status : exporting model"
                    res = project_obj.export_iterationv3_2(iteration.id)
                    self.save()
                    logger.info(res.json())
                    continue

                logger.info(
                    "Successfully export model. download_uri: %s",
                    exports[0].download_uri,
                )
                self.status = "ok"
                self.log = "Status : work done"
                self.save()
                # Get the latest object
                project_obj = Project.objects.get(pk=project_obj.id)
                project_obj.download_uri = exports[0].download_uri
                project_obj.save()
                break
            return

        threading.Thread(target=_export_worker, args=(self,)).start()


pre_save.connect(Project.pre_save, Project, dispatch_uid="Project_pre")