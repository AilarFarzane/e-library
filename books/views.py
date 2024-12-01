from urllib import request

from django.db.models import Count, Q
import jdatetime
from datetime import datetime
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import BookSerializer, BorrowingRecordSerializer
from .models import Book, BorrowingRecord



# defining permissions
from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        print(f"Authenticated: {request.user.is_authenticated}, Role: {getattr(request.user, 'role', None)}")
        return request.user.is_authenticated and request.user.role.lower() == 'admin'

class IsLibrarian(permissions.BasePermission):
    def has_permission(self, request, view):
        print(f"Authenticated: {request.user.is_authenticated}, Role: {getattr(request.user, 'role', None)}")
        return request.user.is_authenticated and request.user.role.lower() == 'librarian'

class IsMember(permissions.BasePermission):
    def has_permission(self, request, view):
        print(f"Authenticated: {request.user.is_authenticated}, Role: {getattr(request.user, 'role', None)}")
        return request.user.is_authenticated and request.user.role.lower() == 'member'


class BookListPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'


# this part is for listing all books (filtering is allowed as well) and posting a new book
class BookListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin | IsLibrarian]

    def get(self, request):
        category = request.query_params.get('category')
        author = request.query_params.get('author')
        publication_year = request.query_params.get('publication_year')

        books = Book.objects.all()

        if category:
            books = Book.objects.filter(category=category)
        if author:
            books = books.filter(author=author)
        if publication_year:
            books = books.filter(publication_year=publication_year)

        paginator = BookListPagination()
        paginated_books = paginator.paginate_queryset(books, request)
        serializer = BookSerializer(paginated_books, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin | IsLibrarian]


    def get(self,request, pk):
        book = get_object_or_404(Book, pk=pk)
        serializer = BookSerializer(book)
        return Response(serializer.data)

    def delete(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        serializer = BookSerializer(book, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#in this part, members can view the list of books and borrow them
class BorrowingRecordListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin | IsMember]


    def get(self, request):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BorrowingRecordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# in this part the user can view and send requests to update their records
class BorrowingRecordDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin | IsMember]

    def get(self, request):
        username = request.query_params.get('username')
        if not username:
            return Response(
                {"error": "Username is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        borrowing_records = BorrowingRecord.objects.filter(user__username=username)
        if not borrowing_records.exists():
            raise NotFound(detail="No borrowing records found for the provided username.")
        serializer = BorrowingRecordSerializer(borrowing_records, many=True)
        return Response(serializer.data)

    def patch(self, request, pk):
        username = request.query_params.get('username')
        if not username:
            return Response(
                {"error": "Username is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        borrowing_record = get_object_or_404(BorrowingRecord, pk=pk)
        borrowing_record.requested_changes = request.data
        borrowing_record.user_request_status = 'pending'

        return Response (
            {'message': "your request has been submitted for approval"}, status=status.HTTP_200_OK
        )


# in this part admin or librarian can approve or reject the changes that the user has made to their records
class UpdatedRecordApprovalView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin | IsLibrarian]

    def get(self, request):
        borrowing_record = BorrowingRecord.objects.filter(user_request_status='pending')
        if not borrowing_record.exists():
            raise NotFound(detail="No borrowing records found with pending status.")
        serializer = BorrowingRecordSerializer(borrowing_record, many=True)
        return Response(serializer.data)


    def patch(self, request, pk):
        borrowing_record = get_object_or_404(BorrowingRecord, pk=pk)

        action = request.data.get('action')
        if action == 'approve':
            for key, value in borrowing_record.requested_changes.items():
                setattr(borrowing_record, key, value)
            borrowing_record.user_request_status = 'approved'
            borrowing_record.requested_changes = None
            borrowing_record.save()

            return Response({'message': 'changes approved'}, status=status.HTTP_200_OK)

        elif action == 'reject':
            borrowing_record.status = 'rejected'
            borrowing_record.requested_changes = None
            borrowing_record.save()

            return Response({"message": "Changes rejected."}, status=HTTP_200_OK)

        return Response({"error": "Invalid action. choose approve / reject"}, status=HTTP_400_BAD_REQUEST)



# the analytics part
class AnalyticsReportView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]

    def get(self, request):
        most_borrowed_books = BorrowingRecord.objects.values('book__title') \
                                  .annotate(borrow_count=Count('book')) \
                                  .order_by('-borrow_count')[:5]

        active_users = BorrowingRecord.objects.values('user__username') \
                           .annotate(borrow_count=Count('user')) \
                           .order_by('-borrow_count')[:5]

        overdue_books_count = BorrowingRecord.objects.filter(
            Q(return_date__lt=jdatetime.date.today()) & Q(returned_date__isnull=True)
        ).count()

        report_data = {
            "most_borrowed_books": most_borrowed_books,
            "active_users": active_users,
            "overdue_books_count": overdue_books_count,
            "generated_at": jdatetime.date.today().strftime('%Y-%m-%d')
        }

        return Response(report_data)















