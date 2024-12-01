import jdatetime
from django_jalali.db import models as jmodels

from django.db import models
from django.contrib.auth import get_user_model

from django.core.validators import RegexValidator


User = get_user_model()

isbn_validator = RegexValidator(
    regex=r'^(?=(?:[^0-9]*[0-9]){10}(?:(?:[^0-9]*[0-9]){3})?$)[\d-]+$',
    message='Enter a valid ISBN number.'
)


class Book(models.Model):

    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    ISBN = models.CharField(max_length=100, validators=[isbn_validator])
    publication_year = models.IntegerField()
    copies_available = models.IntegerField()
    category = models.CharField(max_length=100)


    def __str__(self):
        return self.title

class BorrowingRecord(models.Model):

    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    borrow_date = jmodels.jDateField(null=False, blank=False)
    return_date = jmodels.jDateField(null=False, blank=False)
    returned_date = jmodels.jDateField(null=True, blank=True)

    REQUEST_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    user_request_status = models.CharField(max_length=100, choices=REQUEST_CHOICES, default='approved')
    requested_changes = models.JSONField(null=True, blank=True)



    @property
    def book_status(self):
        if self.returned_date == self.return_date:
            return 'returned'
        if jdatetime.date.today() > self.return_date:
            return 'overdue'
        if self.returned_date is not None and self.returned_date < self.return_date:
            return 'returned'
        else:
            return 'borrowed'


    def save(self, *args, **kwargs):
        if self.pk:
            previous_instance = self.__class__.objects.get(pk=self.pk)
            previous_status = previous_instance.book_status
        else:
            previous_status = None

        print('Saving:', self.book.copies_available)
        print('Previous status:', previous_status)
        print('New status:', self.book_status)


        if previous_status != 'borrowed' and self.book_status == 'borrowed':
            if self.book.copies_available > 0:
                self.book.copies_available -= 1

        if self.book_status == 'returned' and previous_status != 'returned':
            self.book.copies_available += 1

        self.book.save()
        print('Updated copies available:', self.book.copies_available)
        super().save(*args, **kwargs)







