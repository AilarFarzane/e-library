from django.urls import path

from .views import (BookListView, BookDetailView,
                    BorrowingRecordListView, BorrowingRecordDetailView, AnalyticsReportView
                    , UpdatedRecordApprovalView)



urlpatterns = [
    path('books/', BookListView.as_view(), name='book_list'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book_detail'),
    path('records/', BorrowingRecordListView.as_view(), name='borrowing_record_list'),
    path('user-records/', BorrowingRecordDetailView.as_view(), name='borrowing_record_detail'),
    path('user-records/<int:pk>/', BorrowingRecordDetailView.as_view(), name='borrowing_record_detail'),
    path('records/approve/', UpdatedRecordApprovalView.as_view(), name='record_approval_list'),
    path('records/approve/<int:pk>/', UpdatedRecordApprovalView.as_view(), name='record_approval'),
    path('analytics/', AnalyticsReportView.as_view(), name='analytics_report'),
]
