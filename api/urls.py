from django.urls import path

from .views import (
    HealthCheckView,
    CoveringListView,
    CoveringDetailView,
    TransactionSummaryView, 
    TransactionSummaryUnsyncedView,
    TransactionDetailUnsyncedView,
    ReportingPnL
)

urlpatterns = [
    path(
        "health/",
        HealthCheckView.as_view(),
        name="health"
    ),

    path(
        "covering/",
        CoveringListView.as_view(),
        name="covering-list"
    ),

    
    path(
        "covering/summary/",
        TransactionSummaryView.as_view(),
        name="covering-summary"
    ),
    
    path(
        "covering/summary/unsynced",
        TransactionSummaryUnsyncedView.as_view(),
        name="covering-summary"
    ),
    
    path(
        "covering/summary/unsyncedDetail",
        TransactionDetailUnsyncedView.as_view(),
        name="covering-summary"
    ),
    
    path(
        "reporting/pnl/",
        ReportingPnL.as_view(),
        name="reporting-pnl"
    ),
]