from django.db import models
from django.contrib.auth.models import User
# Create your models here.
# Model for the multiple choice questions
class QuizMulipleChoice(models.Model):
    owner = models.ForeignKey('auth.User', related_name='multi', on_delete=models.CASCADE)
    question = models.TextField()
    option1 = models.TextField()
    option2 = models.TextField()
    option3 = models.TextField()
    option4 = models.TextField()
    answer = models.IntegerField()
    def __str__(self):
        return self.question

# Model for the true/false questions
class QuizTrueFalse(models.Model):
    owner = models.ForeignKey('auth.User', related_name='truefalse', on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.BooleanField()
    def __str__(self):
        return self.question
    
# Model for the collection of questions
class QuizCollection(models.Model):
    title = models.CharField(max_length=255)
    owner = models.ForeignKey('auth.User', related_name='collection', on_delete=models.CASCADE)
    trueFalseQuestions = models.ManyToManyField(QuizTrueFalse, related_name='collections')
    multiQuestions = models.ManyToManyField(QuizMulipleChoice, related_name='collections')

    shared_with = models.ManyToManyField('auth.User', related_name='shared_collections', blank=True)  # Users who can view but not edit
    answered = models.ManyToManyField('auth.User', related_name='answered_collections', blank=True)  # Users who have answered the quiz

    def __str__(self):
        return self.title
    

class QuizCollectionAnswer(models.Model):
    collectionID = models.ForeignKey('QuizCollection', on_delete=models.CASCADE)
    multiQuizID = models.ManyToManyField('QuizMulipleChoice', related_name="multi_answers", blank=True)
    trueFalseQuizID = models.ManyToManyField('QuizTrueFalse', related_name="tf_answers", blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_answers")
    shared_with = models.ManyToManyField(User, related_name="shared_answers", blank=True)
    answers = models.JSONField(default=dict)  # Store answers in JSON format
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.owner.username}'s answers for {self.collectionID.title}"

