from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Question, SampleCode, Level, Submission
import requests
  
# Signup View
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Signup failed. Please check your input.")
    else:
        form = UserCreationForm()

    return render(request, 'translator/auth.html', {
        'form': form,
        'activate_signup': True
    })



# Login View
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()

    return render(request, 'translator/auth.html', {
        'form': form,
        'activate_signup': False
    })





def hero_view(request):
    return render(request, 'translator/hero.html')

# Function to execute code via Piston API
def run_code(code, language, input_data=""):
    lang_map = {
        'python': 'python3',
        'cpp': 'cpp',
        'java': 'java'
    }

    payload = {
        "language": lang_map.get(language, 'python3'),
        "version": "*",
        "files": [{"name": "main", "content": code}],
        "stdin": input_data
    }

    response = requests.post("https://emkc.org/api/v2/piston/execute", json=payload)
    result = response.json()

    stdout = result.get('output') or result.get('run', {}).get('stdout', '')
    stderr = result.get('stderr') or result.get('run', {}).get('stderr', '')
    compile_error = result.get('compile', {}).get('stderr', '')

    if stderr or compile_error:
        return f"ERROR: {(stderr or compile_error).strip()}"

    return stdout.strip() if stdout else "ERROR: No output"


# Normalize function to compare expected vs actual output
def normalize_output(output):
    return output.strip().lower().replace('\r', '').replace('\n', '').replace(' ', '')


def home(request):
    levels = Level.choices
    return render(request, 'translator/home.html', {
        'levels': levels
    })



# AJAX view to load sample code dynamically
def load_question_code(request):
    question_id = request.GET.get('question_id')
    language = request.GET.get('language')

    try:
        sample = SampleCode.objects.get(question_id=question_id, language=language)
        return JsonResponse({'code': sample.code})
    except SampleCode.DoesNotExist:
        return JsonResponse({'code': ''})


# ✅ Show questions for selected level
def question_list(request, level):
    questions = Question.objects.filter(level=level)
    return render(request, 'translator/question_list.html', {
        'level': level,
        'questions': questions
    })


# ✅ Dedicated view for each question's translation page
def translate_view(request, question_id): 
    question = get_object_or_404(Question, id=question_id)
    levels = Level.choices
    result = None
    error_output = None
    failed_cases = []
    initial_code = ""
    actual_output = None 

    if request.method == 'POST':
        source_lang = request.POST.get('source_lang')
        target_lang = request.POST.get('target_lang')
        submitted_code = request.POST.get('submitted_code')

        # ✅ Check both source and target languages
        if not source_lang or not target_lang:
            error_output = "Both source and target languages are required."
        else:
            try:
                sample = SampleCode.objects.get(question=question, language=source_lang)
                initial_code = sample.code
            except SampleCode.DoesNotExist:
                initial_code = ""

            test_cases = question.test_cases.all()
            all_passed = True

            for case in test_cases:
                expected_output = run_code(initial_code, source_lang, case.input_data)
                actual_output = run_code(submitted_code, target_lang, case.input_data)

                if "ERROR:" in actual_output:
                    all_passed = False
                    error_output = actual_output
                    failed_cases.append((case.input_data, expected_output, actual_output))
                    break

                if normalize_output(expected_output) != normalize_output(actual_output):
                    all_passed = False
                    failed_cases.append((case.input_data, expected_output, actual_output))

            # ✅ Only save if both languages are valid
            if source_lang and target_lang:
                Submission.objects.create(
                    user=request.user,
                    question=question,
                    source_lang=source_lang,
                    target_lang=target_lang,
                    submitted_code=submitted_code,
                    is_correct=all_passed
                )

            result = "✅ All test cases passed!" if all_passed else f"❌ {len(failed_cases)} test case(s) failed."

    else:
        initial_code = ""
        if request.method == "POST" and source_lang:
            try:
                sample = SampleCode.objects.get(question=question, language=source_lang)
                initial_code = sample.code
            except SampleCode.DoesNotExist:
                initial_code = ""


    return render(request, 'translator/workspace.html', {
        'levels': levels,
        'questions': Question.objects.all(),
        'result': result,
        'error_output': error_output,
        'failed_cases': failed_cases,
        'initial_code': initial_code,
        'question': question,
        'level': question.level.lower(),
        'user_output': actual_output,
    })


@login_required
def history_view(request):
    submissions = Submission.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'translator/history.html', {'submissions': submissions})


# views.py


@login_required
def dashboard_view(request):
    return render(request, 'translator/dashboard.html', {
        'total_attempts': 10,
        'success_rate': 80,
        'most_solved_level': 'Beginner',
    })


@login_required
def profile_view(request):
    return render(request, 'translator/profile.html')
