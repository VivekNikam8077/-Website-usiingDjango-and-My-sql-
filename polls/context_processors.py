from .models import User

def user_processor(request):
    """
    Context processor to ensure compatibility with both legacy and Django auth systems
    """
    # We don't need to add anything here because Django's auth context processor 
    # already adds 'user' and 'perms' to the context
    return {} 