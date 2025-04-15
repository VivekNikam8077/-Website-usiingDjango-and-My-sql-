from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# विभाग मॉडेल
# विविध विभागांची माहिती ठेवते ज्यांना कर्मचारी/वापरकर्ते असाइन केले जाऊ शकतात
class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name


# वापरकर्ता प्रोफाइल मॉडेल
# प्रत्येक वापरकर्त्यासाठी अतिरिक्त माहिती ठेवते, जसे की त्यांचा विभाग
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


# वापरकर्ता तयार केल्यावर प्रोफाइल तयार करण्यासाठी सिग्नल हँडलर
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


# वापरकर्ता सेव्ह केल्यावर प्रोफाइल सेव्ह करण्यासाठी सिग्नल हँडलर
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not hasattr(instance, 'profile'):
        UserProfile.objects.create(user=instance)
    instance.profile.save()


# पोल मॉडेल 
# मतदान प्रश्न आणि संबंधित माहिती ठेवते
class Poll(models.Model):
    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='polls')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, 
                                 help_text="If set, only users from this department can vote")
    
    def __str__(self):
        return self.question
    
    # सर्व पोल्स मिळवण्यासाठी क्लास मेथड
    @classmethod
    def get_all(cls):
        return cls.objects.all()
    
    # आयडी द्वारे पोल मिळवण्यासाठी क्लास मेथड
    @classmethod
    def get_by_id(cls, poll_id):
        try:
            return cls.objects.get(id=poll_id)
        except cls.DoesNotExist:
            return None
    
    # पोलमध्ये नवीन पर्याय जोडण्यासाठी मेथड
    def add_choice(self, choice_text):
        choice = Choice.objects.create(poll=self, choice_text=choice_text)
        return choice
    
    # पोलवरील एकूण मतांची संख्या मिळवण्यासाठी मेथड
    def total_votes(self):
        return sum(choice.votes for choice in self.choices.all())
    
    # चॉइसेस प्रॉपर्टी - या पोलचे सर्व पर्याय मिळवण्यासाठी
    @property
    def choices(self):
        return self.choice_set
    
    # वापरकर्त्याने यापूर्वी मतदान केले आहे का ते तपासण्यासाठी मेथड
    def has_user_voted(self, user):
        if not user.is_authenticated:
            return False
        return Vote.objects.filter(poll=self, user=user).exists()

    # वापरकर्ता या पोलवर मतदान करू शकतो का ते तपासण्यासाठी मेथड
    def can_user_vote(self, user):
        if not user.is_authenticated:
            return False
        
        # जर पोलला विभाग प्रतिबंध नसेल, तर कोणताही प्रमाणीकृत वापरकर्ता मतदान करू शकतो
        if not self.department:
            return True
        
        # वापरकर्त्याकडे योग्य विभागासह प्रोफाइल आहे का ते तपासा
        try:
            return user.profile.department == self.department
        except:
            return False


# चॉइस मॉडेल
# पोल पर्याय आणि त्यांच्या मतांची संख्या ठेवते
class Choice(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    
    def __str__(self):
        return self.choice_text
    
    # पर्यायावर मतदान करण्यासाठी मेथड
    def vote(self):
        self.votes += 1
        self.save()
    
    # मतांची टक्केवारी मोजण्यासाठी प्रॉपर्टी
    @property
    def votes_percentage(self):
        total = self.poll.total_votes()
        if total > 0:
            return int((self.votes / total) * 100)
        return 0


# मतदान मॉडेल
# वापरकर्त्यांचे मतदान रेकॉर्ड सांभाळते
class Vote(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    # प्रति वापरकर्ता फक्त एकच मत निश्चित करण्यासाठी
    class Meta:
        unique_together = ['poll', 'user']
