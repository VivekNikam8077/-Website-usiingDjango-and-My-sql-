# polls/admin_views.py
# या फाइलमध्ये पोल्स व्यवस्थापनासाठी अॅडमिन व्ह्यूज आहेत

from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from .models import Poll, Choice, Department

# पोल्स व्यवस्थापन पेज व्ह्यू
# सर्व पोल्सची यादी दाखवते आणि त्यांचे व्यवस्थापन करण्याची सुविधा देते
def admin_polls_list(request):
    # वापरकर्ता लॉगिन केला आहे आणि सुपरयुजर आहे का ते तपासणे
    if not request.session.get('is_superuser', False) and not (request.user and request.user.is_superuser):
        return redirect('polls:index')
    
    polls = Poll.get_all()
    context = {
        'polls': polls,
        'title': 'Manage Polls',
    }
    return render(request, 'polls/admin/list.html', context)

# नवीन पोल जोडण्यासाठी व्ह्यू
# पोलचे प्रश्न आणि पर्याय जोडण्याची सुविधा देते
def admin_add_poll(request):
    # वापरकर्ता लॉगिन केला आहे आणि सुपरयुजर आहे का ते तपासणे
    if not request.session.get('is_superuser', False) and not (request.user and request.user.is_superuser):
        return redirect('polls:index')
    
    if request.method == 'POST':
        question = request.POST.get('question', '')
        department_id = request.POST.get('department', None)
        
        if question:
            poll = Poll(question=question, created_by=request.user)
            
            # डिपार्टमेंट सेट करणे जर दिले असेल तर
            if department_id and department_id != 'none':
                try:
                    department = Department.objects.get(id=int(department_id))
                    poll.department = department
                except (Department.DoesNotExist, ValueError):
                    pass
            
            poll.save()
            
            # डायनॅमिक पर्याय जोडणे (जास्तीत जास्त 5)
            choice_count = 0
            for i in range(1, 6):  # 5 पर्यायांपर्यंत तपासणे
                choice_text = request.POST.get(f'choice{i}', '').strip()
                if choice_text:
                    poll.add_choice(choice_text)
                    choice_count += 1
            
            # किमान 2 पर्याय दिले आहेत का ते तपासणे
            if choice_count >= 2:
                messages.success(request, "Poll created successfully.")
                return redirect('polls:admin_polls_list')
            else:
                messages.error(request, "You must provide at least 2 choices for the poll.")
        else:
            messages.error(request, "Poll question cannot be empty.")
    
    # फॉर्मसाठी सर्व डिपार्टमेंट्स मिळवणे
    departments = Department.objects.all().order_by('name')
    
    context = {
        'title': 'Add Poll',
        'departments': departments,
    }
    return render(request, 'polls/admin/add.html', context)
    
# पोल डिटेल पेज व्ह्यू
# विशिष्ट पोलची सविस्तर माहिती दाखवते
def admin_poll_detail(request, poll_id):
    # वापरकर्ता लॉगिन केला आहे आणि सुपरयुजर आहे का ते तपासणे
    if not request.session.get('is_superuser', False) and not (request.user and request.user.is_superuser):
        return redirect('polls:index')
    
    poll = Poll.get_by_id(int(poll_id))
    if not poll:
        raise Http404("Poll does not exist")
        
    context = {
        'poll': poll,
        'title': f'Poll: {poll.question}',
    }
    return render(request, 'polls/admin/detail.html', context)

# पोल एडिट करण्यासाठी व्ह्यू
# पोलचा प्रश्न बदलण्याची सुविधा देते
def admin_edit_poll(request, poll_id):
    # वापरकर्ता लॉगिन केला आहे आणि सुपरयुजर आहे का ते तपासणे
    if not request.session.get('is_superuser', False) and not (request.user and request.user.is_superuser):
        return redirect('polls:index')
    
    poll = Poll.get_by_id(int(poll_id))
    if not poll:
        raise Http404("Poll does not exist")
    
    if request.method == 'POST':
        question = request.POST.get('question', '')
        if question:
            poll.question = question
            poll.save()
            messages.success(request, "Poll updated successfully.")
        else:
            messages.error(request, "Question field cannot be empty.")
        
        return redirect('polls:admin_poll_detail', poll_id=poll_id)
    
    return redirect('polls:admin_poll_detail', poll_id=poll_id)

# पोलमध्ये नवीन पर्याय जोडण्यासाठी व्ह्यू
# एका पोलमध्ये जास्तीत जास्त 5 पर्याय जोडता येतात
def admin_add_choice(request, poll_id):
    # वापरकर्ता लॉगिन केला आहे आणि सुपरयुजर आहे का ते तपासणे
    if not request.session.get('is_superuser', False) and not (request.user and request.user.is_superuser):
        return redirect('polls:index')
    
    poll = Poll.get_by_id(int(poll_id))
    if not poll:
        raise Http404("Poll does not exist")
    
    if request.method == 'POST':
        choice_text = request.POST.get('choice_text', '')
        if choice_text:
            # पोलमध्ये आधीच 5 पर्याय आहेत का ते तपासणे
            if poll.choices.all().count() >= 5:
                messages.error(request, "Maximum of 5 choices allowed per poll.")
            else:
                poll.add_choice(choice_text)
                messages.success(request, "Choice added successfully.")
        else:
            messages.error(request, "Choice text cannot be empty.")
    
    return redirect('polls:admin_poll_detail', poll_id=poll_id)

# पर्याय एडिट करण्यासाठी व्ह्यू
# पर्यायाचा मजकूर आणि वोट्स बदलण्याची सुविधा देते
def admin_edit_choice(request, poll_id, choice_id):
    # वापरकर्ता लॉगिन केला आहे आणि सुपरयुजर आहे का ते तपासणे
    if not request.session.get('is_superuser', False) and not (request.user and request.user.is_superuser):
        return redirect('polls:index')
    
    poll = Poll.get_by_id(int(poll_id))
    if not poll:
        raise Http404("Poll does not exist")
    
    try:
        choice = Choice.objects.get(pk=choice_id, poll=poll)
    except Choice.DoesNotExist:
        raise Http404("Choice does not exist")
    
    if request.method == 'POST':
        choice_text = request.POST.get('choice_text', '')
        votes = request.POST.get('votes', 0)
        
        if choice_text:
            choice.choice_text = choice_text
            try:
                choice.votes = int(votes)
            except (ValueError, TypeError):
                choice.votes = 0
            
            choice.save()
            messages.success(request, "Choice updated successfully.")
        else:
            messages.error(request, "Choice text cannot be empty.")
    
    return redirect('polls:admin_poll_detail', poll_id=poll_id)

# पर्याय डिलीट करण्यासाठी व्ह्यू
# एका पोलमध्ये किमान 2 पर्याय असणे आवश्यक आहे
def admin_delete_choice(request, poll_id, choice_id):
    # वापरकर्ता लॉगिन केला आहे आणि सुपरयुजर आहे का ते तपासणे
    if not request.session.get('is_superuser', False) and not (request.user and request.user.is_superuser):
        return redirect('polls:index')
    
    poll = Poll.get_by_id(int(poll_id))
    if not poll:
        raise Http404("Poll does not exist")
    
    try:
        choice = Choice.objects.get(pk=choice_id, poll=poll)
    except Choice.DoesNotExist:
        raise Http404("Choice does not exist")
    
    # डिलीट केल्यानंतर किमान 2 पर्याय राहतील का ते तपासणे
    if poll.choices.all().count() <= 2:
        messages.error(request, "A poll must have at least 2 choices. Add another choice before deleting this one.")
    else:
        if request.method == 'POST':
            choice.delete()
            messages.success(request, "Choice deleted successfully.")
    
    return redirect('polls:admin_poll_detail', poll_id=poll_id)

# पोल डिलीट करण्यासाठी व्ह्यू
# पोल आणि त्याचे सर्व पर्याय डिलीट करते
def admin_delete_poll(request, poll_id):
    # वापरकर्ता लॉगिन केला आहे आणि सुपरयुजर आहे का ते तपासणे
    if not request.session.get('is_superuser', False) and not (request.user and request.user.is_superuser):
        return redirect('polls:index')
    
    poll = Poll.get_by_id(int(poll_id))
    if not poll:
        raise Http404("Poll does not exist")
    
    if request.method == 'POST':
        poll.delete()
        messages.success(request, "Poll deleted successfully.")
        return redirect('polls:admin_polls_list')
    
    return redirect('polls:admin_poll_detail', poll_id=poll_id) 