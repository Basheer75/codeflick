from django.contrib import admin
from .models import Question, SampleCode, Submission, TestCase, Level

# Inline TestCase inside Question for easier input
class TestCaseInline(admin.TabularInline):
    model = TestCase
    extra = 1

# Custom Question Admin with TestCase inline
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'level']
    inlines = [TestCaseInline]

# Register all models
admin.site.register(Question, QuestionAdmin)
admin.site.register(SampleCode)
admin.site.register(Submission)
