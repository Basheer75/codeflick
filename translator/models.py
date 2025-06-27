from django.db import models
from django.contrib.auth.models import User  # ✅ Correct import


class Level(models.TextChoices):
    BEGINNER = 'beginner', 'Beginner'
    INTERMEDIATE = 'intermediate', 'Intermediate'
    ADVANCED = 'advanced', 'Advanced'


class Question(models.Model):
    level = models.CharField(max_length=15, choices=Level.choices)
    title = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return f"{self.title} ({self.level})"


class SampleCode(models.Model):
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('cpp', 'C++'),
        ('java', 'Java'),
    ]
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES)
    code = models.TextField()

    def __str__(self):
        return f"{self.language} code for {self.question.title}"


class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)  # ✅ Will now work
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    source_lang = models.CharField(max_length=10)
    target_lang = models.CharField(max_length=10)
    submitted_code = models.TextField()
    is_correct = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)


class TestCase(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='test_cases')
    input_data = models.TextField()
    expected_output = models.TextField()

    def __str__(self):
        return f"TestCase for {self.question.title}"
