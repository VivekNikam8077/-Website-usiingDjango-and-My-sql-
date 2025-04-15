from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Department, UserProfile, Poll, Choice

# डिपार्टमेंट फॉर्म
# विभाग बनवण्यासाठी आणि संपादित करण्यासाठी वापरला जातो
class DepartmentForm(forms.ModelForm):
    """Form for creating and editing departments."""
    
    class Meta:
        model = Department
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# वापरकर्ता प्रोफाइल फॉर्म 
# वापरकर्त्याच्या प्रोफाइलमध्ये विभाग नियुक्ती संपादित करण्यासाठी
class UserProfileForm(forms.ModelForm):
    """Form for editing user profiles, particularly department assignment."""
    
    class Meta:
        model = UserProfile
        fields = ['department']
        widgets = {
            'department': forms.Select(attrs={'class': 'form-select'}),
        }

# कस्टम वापरकर्ता निर्मिती फॉर्म
# नवीन वापरकर्ता तयार करताना विभाग असाईनमेंट समावेश करतो
class CustomUserCreationForm(UserCreationForm):
    """Extended user creation form that includes department assignment."""
    
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Assign the user to a department (optional)."
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # पासवर्ड फील्ड्सवर बूटस्ट्रॅप क्लासेस लागू करा
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
    
    def save(self, commit=True):
        user = super().save(commit=True)  # प्रोफाइल तयार करण्यासाठी प्रथम वापरकर्ता सेव्ह करा
        
        # विभाग मिळवा आणि वापरकर्त्याच्या प्रोफाइलला असाइन करा
        department = self.cleaned_data.get('department')
        if department:
            user.profile.department = department
            user.profile.save()
            
        return user

# पोल फॉर्म
# नवीन पोल तयार करण्यासाठी आणि संपादित करण्यासाठी
class PollForm(forms.ModelForm):
    """Form for creating and editing polls."""
    
    class Meta:
        model = Poll
        fields = ['question', 'department']
        widgets = {
            'question': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
        }

# चॉइस फॉर्म
# पोलमध्ये पर्याय जोडण्यासाठी आणि संपादित करण्यासाठी
class ChoiceForm(forms.ModelForm):
    """Form for creating and editing poll choices."""
    
    class Meta:
        model = Choice
        fields = ['choice_text']
        widgets = {
            'choice_text': forms.TextInput(attrs={'class': 'form-control'}),
        } 