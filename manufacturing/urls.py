from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from .views import WorkOrderViewSet,ProductionLineitemViewSet,ProductionLineitemPieViewSet,WorkOrderitemViewSet, Manufacture_CostViewSet, ProductionLineViewSet, WorkstationViewSet,WorkstationItemViewSet, QualityTestViewSet, ManufacturingRecordViewSet

router = routers.DefaultRouter()
router.register('workorders', WorkOrderViewSet)
router.register('workordersitem', WorkOrderitemViewSet)
router.register('cost', Manufacture_CostViewSet)
router.register('productionlines', ProductionLineViewSet)
router.register('productionlinesitem', ProductionLineitemViewSet)
router.register('productionlinesitemPie', ProductionLineitemPieViewSet)
router.register('workstations', WorkstationViewSet)
router.register('workstationsitem', WorkstationItemViewSet)
router.register('qualitytests', QualityTestViewSet)
router.register('manufacturingrecords', ManufacturingRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),
]


# from django.urls import path
# from .views import (
#     WorkOrderListCreateAPIView, WorkOrderDetailAPIView,
#     RawMaterialListCreateAPIView, RawMaterialDetailAPIView,
#     ProductionLineListCreateAPIView, ProductionLineDetailAPIView,
#     WorkstationListCreateAPIView, WorkstationDetailAPIView,
#     QualityTestListCreateAPIView, QualityTestDetailAPIView,
#     ManufacturingRecordListCreateAPIView, ManufacturingRecordDetailAPIView,
# )

# urlpatterns = [
#     path('workorders/', WorkOrderListCreateAPIView.as_view(), name='workorder-list-create'),
#     path('workorders/<int:pk>/', WorkOrderDetailAPIView.as_view(), name='workorder-detail'),
#     path('rawmaterials/', RawMaterialListCreateAPIView.as_view(), name='rawmaterial-list-create'),
#     path('rawmaterials/<int:pk>/', RawMaterialDetailAPIView.as_view(), name='rawmaterial-detail'),
#     path('productionlines/', ProductionLineListCreateAPIView.as_view(), name='productionline-list-create'),
#     path('productionlines/<int:pk>/', ProductionLineDetailAPIView.as_view(), name='productionline-detail'),
#     path('workstations/', WorkstationListCreateAPIView.as_view(), name='workstation-list-create'),
#     path('workstations/<uuid:pk>/', WorkstationDetailAPIView.as_view(), name='workstation-detail'),
#     path('qualitytests/', QualityTestListCreateAPIView.as_view(), name='qualitytest-list-create'),
#     path('qualitytests/<int:pk>/', QualityTestDetailAPIView.as_view(), name='qualitytest-detail'),
#     path('manufacturingrecords/', ManufacturingRecordListCreateAPIView.as_view(), name='manufacturingrecord-list-create'),
#     path('manufacturingrecords/<int:pk>/', ManufacturingRecordDetailAPIView.as_view(), name='manufacturingrecord-detail'),
# ]
