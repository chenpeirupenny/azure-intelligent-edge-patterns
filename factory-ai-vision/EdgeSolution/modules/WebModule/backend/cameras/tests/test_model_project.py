from rest_framework.test import APITransactionTestCase
from cameras.models import Project, Setting, Camera, Location, Part
from config import ENDPOINT, TRAINING_KEY
from unittest.mock import patch
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
import logging

project_prefix = "UnitTest"

logger = logging.getLogger(__name__)


class ModelProjectTestCase(APITransactionTestCase):
    def setUp(self):
        """Create serveral Location
        :DEFAULT_TRAINER: trainer create from configs
        :INVALID_TRAINER: an invalid trainer
        """
        valid_setting_obj = Setting.objects.create(name="valid_setting",
                                                   endpoint=ENDPOINT,
                                                   training_key=TRAINING_KEY,
                                                   is_trainer_valid=False)
        invalid_setting_obj = Setting.objects.create(name="invalid_setting",
                                                     endpoint=ENDPOINT,
                                                     training_key='',
                                                     is_trainer_valid=False)
        for i in range(3):
            demo_camera_obj = Camera.objects.create(name="demo_camera_{i}",
                                                    rtsp="0",
                                                    area="{i*2},{i*3}",
                                                    is_demo=True)
            camera_obj = Camera.objects.create(name="camera_{i}",
                                               rtsp="0",
                                               area="{i*2},{i*3}",
                                               is_demo=False)

            demo_location_obj = Location.objects.create(name=f"location_{i}",
                                                        description=f"description_{i}",
                                                        is_demo=True)
            location_obj = Location.objects.create(name=f"demo_location_{i}",
                                                   description=f"description_{i}",
                                                   is_demo=False)
            demo_part_obj = Part.objects.create(name=f"part_{i}",
                                                description=f"description_{i}",
                                                is_demo=True)
            part_obj = Part.objects.create(name=f"part_{i}",
                                           description=f"description_{i}",
                                           is_demo=False)
        self.exist_num = 3

    def test_setup_is_valid(self):
        self.assertEqual(Setting.objects.filter(
            training_key='').count(), 1)
        self.assertEqual(Setting.objects.filter(
            training_key=TRAINING_KEY).count(), 1)
        self.assertEqual(Camera.objects.filter(
            is_demo=True).count(), self.exist_num)
        self.assertEqual(Camera.objects.filter(
            is_demo=True).count(), self.exist_num)
        self.assertEqual(Location.objects.filter(
            is_demo=True).count(), self.exist_num)
        self.assertEqual(Location.objects.filter(
            is_demo=True).count(), self.exist_num)
        self.assertEqual(Part.objects.filter(
            is_demo=True).count(), self.exist_num)
        self.assertEqual(Part.objects.filter(
            is_demo=True).count(), self.exist_num)

    def test_create_1(self):
        """invalid setting -> customvision_id = ''
        """
        project_obj = Project.objects.create(
            setting=Setting.objects.filter(name='invalid_setting').first(),
            camera=Camera.objects.filter(name='demo_camera_1').first(),
            location=Location.objects.filter(name='demo_location_1').first(),
            customvision_project_id='super_valid_project_id',
            customvision_project_name=f'{project_prefix}-test_create_1',
            is_demo=False
        )
        self.assertFalse(project_obj.customvision_project_id ==
                         'super_valid_project_id')
        self.assertEqual(project_obj.customvision_project_id, '')

    def test_create_2(self):
        """valid setting will not create project on customvision
        will wait until train for the first time
        """
        trainer = CustomVisionTrainingClient(
            api_key=TRAINING_KEY, endpoint=ENDPOINT)
        project_count = len(trainer.get_projects())
        project_obj = Project.objects.create(
            setting=Setting.objects.filter(name='valid_setting').first(),
            camera=Camera.objects.filter(name='demo_camera_1').first(),
            location=Location.objects.filter(name='demo_location_1').first(),
            customvision_project_name=f'{project_prefix}-test_create_2',
            is_demo=False
        )

        project_count_after = len(trainer.get_projects())
        self.assertEqual(project_obj.customvision_project_id, '')
        self.assertEqual(project_count, project_count_after)

    def test_create_3(self):
        """valid setting with wrong customvision_project_id
        This state should not occur often...
        Set the customvision_project_id = ''
        Will not create project on customvision
        """
        project_obj = Project.objects.create(
            setting=Setting.objects.filter(
                name='valid_setting').first(),
            camera=Camera.objects.filter(
                name='demo_camera_1').first(),
            location=Location.objects.filter(
                name='demo_location_1').first(),
            customvision_project_id='5566thebest',
            customvision_project_name=f'{project_prefix}-test_create_3',
            is_demo=False)

        self.assertTrue(project_obj.customvision_project_id == '')

    def test_create_project(self):
        """create project with a valid setting.
        name should start with prefix so tear down will delete the project from custom vision
        """
        project_obj = Project.objects.create(
            setting=Setting.objects.filter(name='valid_setting').first(),
            camera=Camera.objects.filter(name='demo_camera_1').first(),
            location=Location.objects.filter(name='demo_location_1').first(),
            is_demo=False,
            customvision_project_id='56cannotdie',
            customvision_project_name=f'{project_prefix}-test_update_1'
        )
        # Project already created
        project_obj.save()
        self.assertTrue(project_obj.customvision_project_id == '')
        project_obj.create_project()
        self.assertFalse(project_obj.customvision_project_id == '')

    def test_update_1(self):
        """
        update with a invalid customvision_project_id.
        set customvision_project_id to ''
        """
        project_obj = Project.objects.create(
            setting=Setting.objects.filter(name='valid_setting').first(),
            camera=Camera.objects.filter(name='demo_camera_1').first(),
            location=Location.objects.filter(name='demo_location_1').first(),
            is_demo=False,
            customvision_project_name=f'{project_prefix}-test_update_1'
        )
        # Project already created
        project_obj.customvision_project_id = '56cannotdie'
        project_obj.save()
        self.assertTrue(project_obj.customvision_project_id == '')

    @classmethod
    def tearDownClass(self):
        logger.info("Deleting Projects on CustomVision")
        trainer = CustomVisionTrainingClient(
            api_key=TRAINING_KEY, endpoint=ENDPOINT)
        projects = trainer.get_projects()
        for project in projects:
            if project.name.find(project_prefix) == 0:
                trainer.delete_project(project_id=project.id)