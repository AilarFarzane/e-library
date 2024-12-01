from django.contrib import admin

from .models import Book, BorrowingRecord

class BooksAdmin(admin.ModelAdmin):
    model = Book
    list_display = ('id', 'title', 'author', 'publication_year', 'copies_available', 'category')

class BorrowingRecordsAdmin(admin.ModelAdmin):
    model = BorrowingRecord
    list_display = ('id', 'book', 'user', 'borrow_date', 'return_date', 'returned_date', 'book_status')
    readonly_fields = ('book_status',)


admin.site.register(Book, BooksAdmin)
admin.site.register(BorrowingRecord, BorrowingRecordsAdmin)
