from django.contrib import admin

# Register your models here.

from .models import QuizMulipleChoice, QuizTrueFalse, QuizCollection, QuizCollectionAnswer

admin.site.register(QuizMulipleChoice)
admin.site.register(QuizTrueFalse)
admin.site.register(QuizCollection)
admin.site.register(QuizCollectionAnswer)