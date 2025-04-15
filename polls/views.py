from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from .models import Poll, Choice, Vote, Department, UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.urls import reverse
from .forms import DepartmentForm, UserProfileForm, CustomUserCreationForm, PollForm, ChoiceForm

import random


# डिफॉल्ट पोल्स तयार करण्यासाठी फंक्शन
# पोल अॅप्लिकेशनमध्ये काही डीफॉल्ट डेटा सेट करण्यासाठी वापरले जाते
def init_default_polls():
    try:
        if Poll.objects.count() == 0:
            poll1 = Poll.objects.create(question="What's your favorite programming language?")
            poll1.add_choice("Python")
            poll1.add_choice("JavaScript")
            poll1.add_choice("Java")
            poll1.add_choice("C++")

            poll2 = Poll.objects.create(question="What's your favorite framework?")
            poll2.add_choice("Django")
            poll2.add_choice("React")
            poll2.add_choice("Angular")
            poll2.add_choice("Vue.js")
    except:
        pass


# होम पेज व्ह्यू
# सर्व उपलब्ध पोल्स दिसतात आणि विभागानुसार फिल्टर केले जातात
def index(request):
    # सर्व पोल्सची यादी मिळवा
    base_query = Poll.get_all()
    
    # फीचर्ड पोल्स - शेवटचे 3 पोल्स
    featured_polls = base_query.order_by('-pub_date')[:3]
    
    # लोकप्रिय पोल्स - सर्वाधिक मतांसह 3 पोल्स
    popular_polls = sorted(
        list(base_query), 
        key=lambda x: x.total_votes(), 
        reverse=True
    )[:3]
    
    # वापरकर्ता लॉगिन असल्यास विभागानुसार मुख्य पोल्स फिल्टर करा
    if request.user.is_authenticated:
        # विभाग प्रतिबंध नसलेले पोल्स प्लस या वापरकर्त्याच्या विभागासाठी पोल्स मिळवा
        user_department = None
        if hasattr(request.user, 'profile') and hasattr(request.user.profile, 'department'):
            user_department = request.user.profile.department
        
        if user_department:
            # विभाग प्रतिबंध नसलेले किंवा वापरकर्त्याच्या विभागाशी जुळणारे पोल्स मिळवा
            polls = base_query.filter(department__isnull=True) | base_query.filter(department=user_department)
            polls = polls.distinct().order_by('-pub_date')
        else:
            # वापरकर्त्याला विभाग नाही, फक्त अप्रतिबंधित पोल्स दाखवा
            polls = base_query.filter(department__isnull=True).order_by('-pub_date')
            
        # स्टाफ आणि सुपरयुजर्स सर्व पोल्स पाहू शकतात
        if request.user.is_staff or request.user.is_superuser:
            polls = base_query.order_by('-pub_date')
    else:
        # अनप्रमाणित वापरकर्त्यांसाठी, फक्त अप्रतिबंधित पोल्स दाखवा
        polls = base_query.filter(department__isnull=True).order_by('-pub_date')
    
    # प्रदर्शनासाठी सर्व विभाग मिळवा
    departments = Department.objects.all().order_by('name')
    
    # संदर्भ डेटा
    context = {
        'polls': polls,
        'featured_polls': featured_polls,
        'popular_polls': popular_polls,
        'departments': departments,
    }
    
    return render(request, 'polls/index.html', context)

# पोल तपशील व्ह्यू
# विशिष्ट पोलचे तपशील दाखवते आणि मतदानाची सुविधा देते
def detail(request, poll_id):
    try:
        poll = Poll.get_by_id(poll_id)
        if poll is None:
            raise Http404("Poll does not exist")
            
        if hasattr(poll, 'choices'):
            choice_count = poll.choices.count()
            print(f"Poll has {choice_count} choices")
        
        # वापरकर्त्याने आधीच मतदान केले आहे का ते तपासा
        has_voted = poll.has_user_voted(request.user) if request.user.is_authenticated else False
        
        # वापरकर्ता विभागानुसार मतदान करू शकतो का ते तपासा
        can_vote = poll.can_user_vote(request.user)
        
        return render(request, 'polls/detail.html', {
            'poll': poll, 
            'has_voted': has_voted,
            'can_vote': can_vote
        })
    except Exception as e:
        print(f"Error in detail view: {str(e)}")  # डीबगिंगसाठी
        raise Http404(f"Error loading poll: {str(e)}")

# मतदान व्ह्यू
# वापरकर्त्यांना पोलमध्ये मतदान करण्याची सुविधा देते
def vote(request, poll_id):
    try:
        poll = Poll.get_by_id(poll_id)
        if poll is None:
            raise Http404("Poll does not exist")
        
        # वापरकर्ता प्रमाणित आहे का ते तपासा
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to vote.")
            return redirect('login')
        
        # वापरकर्ता विभागानुसार मतदान करू शकतो का ते तपासा
        if not poll.can_user_vote(request.user):
            messages.error(request, "You don't have permission to vote on this poll.")
            return redirect('polls:detail', poll_id=poll.id)
        
        if request.method == 'POST':
            try:
                # वापरकर्त्याने आधीच मतदान केले आहे का ते तपासा
                if poll.has_user_voted(request.user):
                    messages.warning(request, "You have already voted on this poll.")
                    return redirect('polls:poll_results', poll_id=poll.id)
                
                # निवडी अस्तित्वात आहेत आणि प्रवेशयोग्य आहेत याची खात्री करा
                if not hasattr(poll, 'choices') or poll.choices.count() == 0:
                    return render(request, 'polls/detail.html', {
                        'poll': poll,
                        'error_message': "This poll has no choices to vote on.",
                    })
                
                choice_index = int(request.POST.get('choice', ''))
                choices = list(poll.choices.all())
                
                if choice_index < 0 or choice_index >= len(choices):
                    return render(request, 'polls/detail.html', {
                        'poll': poll,
                        'error_message': "You didn't select a valid choice.",
                    })
                
                selected_choice = choices[choice_index]
                selected_choice.vote()
                
                # मत नोंदवा
                Vote.objects.create(
                    poll=poll,
                    user=request.user,
                    choice=selected_choice
                )
                
                messages.success(request, "Your vote has been recorded successfully!")
                return redirect('polls:poll_results', poll_id=poll.id)
            except (ValueError, IndexError, TypeError, AttributeError) as e:
                return render(request, 'polls/detail.html', {
                    'poll': poll,
                    'error_message': f"Invalid choice selection: {str(e)}",
                })
        
        # POST नसल्यास, तपशील पृष्ठावर पुनर्निर्देशित करा
        return redirect('polls:detail', poll_id=poll.id)
            
    except Exception as e:
        print(f"Error in vote view: {str(e)}")  # डीबगिंगसाठी
        raise Http404(f"Error processing vote: {str(e)}")

# निकाल व्ह्यू 
# विशिष्ट पोलसाठी मतदान निकाल दाखवते
def results(request, poll_id):
    try:
        poll = Poll.get_by_id(poll_id)
        if poll is None:
            raise Http404("Poll does not exist")
            
        if hasattr(poll, 'choices'):
            choice_count = poll.choices.count()
            print(f"Poll has {choice_count} choices")
        
        return render(request, 'polls/results.html', {'poll': poll})
    except Exception as e:
        print(f"Error in results view: {str(e)}")  # डीबगिंगसाठी
        raise Http404(f"Error loading results: {str(e)}")

# नवीन पोल तयार करण्यासाठी व्ह्यू
# फक्त स्टाफ वापरकर्त्यांसाठी उपलब्ध
def create(request):
    """नवीन पोल तयार करण्यासाठी व्ह्यू फंक्शन. फक्त स्टाफ वापरकर्त्यांसाठी उपलब्ध."""
    if not request.user.is_authenticated:
        return redirect('login')
        
    # वापरकर्ता स्टाफ आहे का ते तपासा
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to create polls.")
        return redirect('polls:index')
        
    if request.method == 'POST':
        question = request.POST.get('question', '')
        choices = [request.POST.get(f'choice{i}', '') for i in range(1, 5)]
        department_id = request.POST.get('department', '')
        
        if not question:
            return render(request, 'polls/create.html', {
                'error_message': 'Question is required.',
                'departments': Department.objects.all().order_by('name')
            })
            
        valid_choices = [c for c in choices if c.strip()]
        if not valid_choices:
            return render(request, 'polls/create.html', {
                'error_message': 'At least one choice is required.',
                'departments': Department.objects.all().order_by('name')
            })
        
        try:
            # पोल तयार करा
            poll = Poll.objects.create(question=question, created_by=request.user)
            
            # विभाग सेट करा जर दिला असेल तर
            if department_id and department_id != '':
                try:
                    department = Department.objects.get(id=int(department_id))
                    poll.department = department
                    poll.save()
                except (Department.DoesNotExist, ValueError):
                    pass
            
            # सर्व वैध निवडी जोडा
            for choice_text in valid_choices:
                if choice_text.strip():
                    poll.add_choice(choice_text)
                    
            # कोणत्याही निवडी तयार केल्या गेल्या का ते तपासा
            if poll.choices.count() == 0:
                # जर कोणतीही निवड तयार केली नाही, तर पोल हटवा आणि त्रुटी दाखवा
                poll.delete()
                return render(request, 'polls/create.html', {
                    'error_message': 'Failed to create choices. Please try again.',
                    'departments': Department.objects.all().order_by('name')
                })
                
            return redirect('polls:detail', poll_id=poll.id)
        except Exception as e:
            print(f"Error creating poll: {str(e)}")
            return render(request, 'polls/create.html', {
                'error_message': f'Error creating poll: {str(e)}',
                'departments': Department.objects.all().order_by('name')
            })
    
    # फॉर्मसाठी सर्व विभाग मिळवा
    context = {
        'departments': Department.objects.all().order_by('name')
    }
    return render(request, 'polls/create.html', context)

# अबाउट पेज व्ह्यू
# वेबसाइटची माहिती दाखवते
def about(request):
    return render(request, 'polls/about.html')

# कॉन्टॅक्ट पेज व्ह्यू
# वापरकर्त्यांना संपर्क करण्यासाठी फॉर्म दाखवते
def contact(request):
    if request.method == 'POST':
        # वास्तविक अॅपमध्ये, फॉर्म डेटा इथे प्रोसेस केला जाईल
        return render(request, 'polls/contact_success.html')
    return render(request, 'polls/contact.html')

# पोल डिलीट करण्यासाठी व्ह्यू
# फक्त सुपरयुजर्ससाठी उपलब्ध
def delete_poll(request, poll_id):
    # वापरकर्ता सुपरयुजर आहे का ते तपासणे
    if not request.user.is_superuser:
        return redirect('polls:index')
    
    try:
        poll = Poll.get_by_id(poll_id)
        if poll is None:
            raise Http404("Poll does not exist")
        
        # डिलीट करण्याची पुष्टी
        if request.method == 'POST':
            # सर्व चॉईसेस डिलीट करणे
            poll.choices.all().delete()
            # पोल डिलीट करणे
            poll.delete()
            return redirect('polls:index')
        
        # पुष्टीकरण पेज दाखवणे
        return render(request, 'polls/delete_confirm.html', {'poll': poll})
    except Exception as e:
        print(f"Error in delete_poll view: {str(e)}")
        raise Http404(f"Error deleting poll: {str(e)}")

# सर्व पोल्सचे निकाल दाखवण्यासाठी व्ह्यू
def all_results(request):
    try:
        polls = Poll.get_all()
        return render(request, 'polls/all_results.html', {'polls': polls})
    except Exception as e:
        print(f"Error in all_results view: {str(e)}")
        return render(request, 'polls/all_results.html', {'polls': []})

# विशिष्ट पोलचे निकाल दाखवण्यासाठी व्ह्यू
def poll_results(request, poll_id):
    try:
        poll = Poll.get_by_id(poll_id)
        if poll is None:
            raise Http404("Poll does not exist")
        
        if hasattr(poll, 'choices'):
            choice_count = poll.choices.count()
            print(f"Poll has {choice_count} choices")
        
        return render(request, 'polls/results.html', {'poll': poll})
    except Exception as e:
        print(f"Error in poll_results view: {str(e)}")
        raise Http404(f"Error loading results: {str(e)}")

# वापरकर्ते व्यवस्थापन व्ह्यू
# फक्त स्टाफ वापरकर्त्यांसाठी उपलब्ध
@login_required
@user_passes_test(lambda u: u.is_staff)
def manage_users(request):
    # सर्व वापरकर्ते मिळवणे
    users_list = User.objects.all().order_by('-date_joined')
    
    # पेजिनेशन - प्रति पेज 10 वापरकर्ते
    paginator = Paginator(users_list, 10)
    page = request.GET.get('page')
    users = paginator.get_page(page)
    
    context = {
        'users': users,
    }
    
    return render(request, 'polls/manage_users.html', context)

# वापरकर्ता डिलीट करण्यासाठी व्ह्यू
# फक्त स्टाफ वापरकर्त्यांसाठी उपलब्ध
@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_user(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        # स्टाफ वापरकर्त्यांना स्वतःला किंवा सुपरयुजर्सना डिलीट करू देऊ नये
        if user != request.user and not user.is_superuser:
            username = user.username
            user.delete()
            messages.success(request, f'User "{username}" has been deleted successfully.')
        else:
            messages.error(request, "You cannot delete this user.")
    
    return redirect('polls:manage_users')

# माझे वोट्स व्ह्यू
# वापरकर्त्याने दिलेले वोट्स दाखवते
@login_required
def my_votes(request):
    # हे एक प्लेसहोल्डर आहे - वास्तविक सिस्टममध्ये वापरकर्त्याचे वोट्स ट्रॅक केले जातील
    polls = Poll.get_all().order_by('-pub_date')
    
    context = {
        'polls': polls,
        'title': 'My Votes',
        'message': 'Here are all the polls you have participated in.'
    }
    
    return render(request, 'polls/my_votes.html', context)

# डिपार्टमेंट फॉर्म क्लास
# डिपार्टमेंट तयार करण्यासाठी आणि अपडेट करण्यासाठी वापरली जाते
class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']

# यूजर प्रोफाइल फॉर्म क्लास
# वापरकर्त्याचे प्रोफाइल अपडेट करण्यासाठी वापरली जाते
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['department']

# कस्टम यूजर क्रिएशन फॉर्म क्लास
# नवीन वापरकर्ता तयार करण्यासाठी वापरली जाते
class CustomUserCreationForm(UserCreationForm):
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'department']
    
    def save(self, commit=True):
        user = super().save(commit=True)
        if self.cleaned_data.get('department'):
            user.profile.department = self.cleaned_data['department']
            user.profile.save()
        return user

# डिपार्टमेंट व्यवस्थापन व्ह्यू
# फक्त स्टाफ वापरकर्त्यांसाठी उपलब्ध
@login_required
@user_passes_test(lambda u: u.is_staff)
def manage_departments(request):
    # डीफॉल्ट डिपार्टमेंट्स तयार करणे
    create_default_departments()
    
    departments = Department.objects.all().order_by('name')
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Department created successfully.")
            return redirect('polls:manage_departments')
    else:
        form = DepartmentForm()
    
    context = {
        'departments': departments,
        'form': form,
    }
    
    return render(request, 'polls/manage_departments.html', context)

# डीफॉल्ट डिपार्टमेंट्स तयार करण्यासाठी फंक्शन
# जर डिपार्टमेंट्स अस्तित्वात नसतील तर त्यांना तयार करते
def create_default_departments():
    default_departments = [
        {
            'name': 'Computer Science',
            'description': 'Department focused on computing technologies, programming, and computer engineering.'
        },
        {
            'name': 'Law',
            'description': 'Department focused on legal studies, regulations, and judiciary matters.'
        },
        {
            'name': 'Marketing',
            'description': 'Department focused on business promotion, advertising strategies, and market research.'
        }
    ]
    
    for dept_data in default_departments:
        Department.objects.get_or_create(
            name=dept_data['name'],
            defaults={'description': dept_data['description']}
        )

# डिपार्टमेंट डिलीट करण्यासाठी व्ह्यू
# फक्त स्टाफ वापरकर्त्यांसाठी उपलब्ध
@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_department(request, dept_id):
    if request.method == 'POST':
        dept = get_object_or_404(Department, id=dept_id)
        dept.delete()
        messages.success(request, f'Department "{dept.name}" has been deleted successfully.')
    
    return redirect('polls:manage_departments')

# नवीन वापरकर्ता जोडण्यासाठी व्ह्यू
# फक्त स्टाफ वापरकर्त्यांसाठी उपलब्ध
@login_required
@user_passes_test(lambda u: u.is_staff)
def add_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User created successfully.")
            return redirect('polls:manage_users')
    else:
        form = CustomUserCreationForm()
    
    context = {
        'form': form,
        'title': 'Add User',
    }
    
    return render(request, 'polls/add_user.html', context)

# वापरकर्त्याचे डिपार्टमेंट बदलण्यासाठी व्ह्यू
# फक्त स्टाफ वापरकर्त्यांसाठी उपलब्ध
@login_required
@user_passes_test(lambda u: u.is_staff)
def edit_user_department(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, f'Department assignment for user "{user.username}" updated successfully.')
            return redirect('polls:manage_users')
    else:
        form = UserProfileForm(instance=user.profile)
    
    context = {
        'user_obj': user,
        'form': form,
        'title': 'Edit User Department',
    }
    
    return render(request, 'polls/edit_user_department.html', context)

# कस्टम ऑथेंटिकेशन बॅकएंड क्लास
# वापरकर्त्याला लॉगिन करण्यापूर्वी त्याचे डिपार्टमेंट तपासते
class DepartmentRequiredBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(request, username=username, password=password, **kwargs)
        if user is None:
            return None
            
        # सुपरयुजर्स आणि स्टाफला नेहमी परवानगी द्या
        if user.is_superuser or user.is_staff:
            return user
            
        # सामान्य वापरकर्त्यांसाठी, त्यांचे डिपार्टमेंट तपासा
        try:
            # वापरकर्त्याला प्रोफाइल नसेल तर लॉगिन नाकारा
            if not hasattr(user, 'profile'):
                return None
                
            # सामान्य वापरकर्त्यांना डिपार्टमेंट असणे आवश्यक आहे
            if user.profile.department is None:
                return None
            
            return user
        except:
            return None

# कस्टम लॉगिन व्ह्यू
# वापरकर्त्याला लॉगिन करण्यासाठी आणि त्यांना योग्य मेसेज दाखवण्यासाठी
def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            
            # पुढील URL किंवा डीफॉल्ट इंडेक्स मिळवा
            next_url = request.POST.get('next', '')
            if next_url and next_url != 'None':
                return redirect(next_url)
            else:
                return redirect('polls:index')
        else:
            # या युजरनेमचा वापरकर्ता अस्तित्वात आहे का ते तपासा
            try:
                existing_user = User.objects.get(username=username)
                # वापरकर्ता अस्तित्वात असेल पण ऑथेंटिकेशन फेल झाले असेल तर
                if existing_user and not (existing_user.is_staff or existing_user.is_superuser):
                    messages.error(request, "Your account is not authorized. Please contact an administrator.")
                else:
                    messages.error(request, "Invalid username or password.")
            except User.DoesNotExist:
                messages.error(request, "Invalid username or password.")
                
    return render(request, 'polls/login.html')
