# -*- coding: utf-8 -*-
"""API router
"""

from django.conf.urls import url
from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import DefaultRouter

from voe_training.azure_app_insight.api import views as app_insight_views
from voe_training.voe_settings.api import views as voe_setting_views
from voe_training.voe_projects.api import views as voe_project_views
from voe_training.voe_training_status.api import \
    views as voe_training_status_views
from voe_training.notifications.api import views as notifications_views
from voe_training.voe_parts.api import views as voe_part_views
from voe_training.voe_images.api import views as voe_image_views
# from voe_training.feedback.api import views as feedback_views
# from voe_training.image_predictions.api import \
    # views as image_prediction_views
# from voe_training.locations.api import views as location_views

# from voe_training.relabeling.api import views as relabel_views
# from voe_training.streams.api import views as stream_views
# from voe_training.video_feed.api import views as videofeed_views

router = DefaultRouter()
router.trailing_slash = '/?'
app_name = "api"

router.register('settings', voe_setting_views.SettingViewSet)
router.register('projects', voe_project_views.ProjectViewSet)
router.register('training_status',
                voe_training_status_views.TrainingStatusViewSet)
router.register('notifications', notifications_views.NotificationViewSet)
router.register('parts', voe_part_views.PartViewSet)
router.register('images', voe_image_views.ImageViewSet)
# router.register('cameras', views.CameraViewSet)
# router.register('parts', azure_part_views.PartViewSet)
# router.register('locations', location_views.LocationViewSet)
# router.register('image_predictions',
                # image_prediction_views.ImagePredictionViewSet)


# router.register('tasks', azure_training_views.TaskViewSet)

# router.register('feedback', feedback_views.FeedbackViewSet)

# router.register('images', image_views.ImageViewSet)

urlpatterns = router.urls

SchemaView = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns += [
    url(r'^swagger(?P<format>\.json|\.yaml)$',
        SchemaView.without_ui(cache_timeout=0),
        name='schema-json'),
    url(r'^swagger',
        SchemaView.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'),
    url(r'^swagger/$',
        SchemaView.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'),
    url(r'^redoc',
        SchemaView.with_ui('redoc', cache_timeout=0),
        name='schema-redoc'),
    url(r'^redoc/$',
        SchemaView.with_ui('redoc', cache_timeout=0),
        name='schema-redoc'),
]

# urlpatterns += [
    # url('streams/connect', stream_views.connect_stream),
    # path('streams/<int:stream_id>/disconnect', stream_views.disconnect_stream),
    # path('streams/<int:stream_id>/video_feed', stream_views.video_feed),
    # path('streams/<int:stream_id>/capture', stream_views.capture),
    # path('streams/<int:stream_id>/keep_alive', stream_views.keep_alive),
    # path('inference/video_feed', videofeed_views.video_feed),
    # path('inference/video_feed/keep_alive', videofeed_views.keep_alive),
    # path('projects/<int:project_id>/train', azure_training_views.train),
    # path('projects/<int:project_id>/export', azure_training_views.export),
    # path('projects/<int:project_id>/train_performance',
         # azure_training_views.train_performance),
    # path('projects/<int:project_id>/inference_video_feed',
         # stream_views.inference_video_feed),
    # path('projects/<int:project_id>/pull_cv_project',
         # azure_training_views.pull_cv_project),
    # path('projects/<int:project_id>/update_prob_threshold',
         # azure_training_views.update_prob_threshold),
    # path('projects/<int:project_id>/reset_project',
         # azure_training_views.reset_project),
    # path('projects/<int:project_id>/reset_camera',
         # azure_training_views.project_reset_camera),
    # path('projects/null/export', azure_training_views.export_null),
    # path('relabel', relabel_views.upload_relabel_image),
    # path('relabel/update', relabel_views.relabel_update),
    # path('appinsight/key', app_insight_views.instrumentation_key),
    # path('camera_utils/verify_rtsp', camera_util_views.verify_rtsp),
# ]
