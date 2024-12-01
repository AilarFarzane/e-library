from rest_framework import serializers
from .models import Book, BorrowingRecord

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'publication_year', 'copies_available', 'category']



class BorrowingRecordSerializer(serializers.ModelSerializer):
    book_title = serializers.ReadOnlyField(source='book.title')
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = BorrowingRecord
        fields = ['id', 'book_title', 'user', 'borrow_date', 'return_date', 'returned_date', 'book_status', 'user_request_status']
        extra_kwargs = { 'book_title': {'read_only': True},
            'user': {'read_only': True},
            'borrow_date': {'read_only': True},
            'returned_date': {'read_only': True},
            'book_status': {'read_only': True},}
