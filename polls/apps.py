from django.apps import AppConfig


# पोल्स अॅप कॉन्फिगरेशन
# या क्लासमध्ये अॅपचे बेसिक सेटिंग्स आहेत
class PollsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'polls'
