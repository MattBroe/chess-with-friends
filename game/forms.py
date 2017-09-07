from django.contrib.auth.forms import UserCreationForm

class UserCreateForm(UserCreationForm):
    
    def __init__(self, *args, **kwargs):
        super(UserCreateForm, self).__init__(*args, **kwargs)
        self.fields['password1'].help_text = "Your password can't be too similar to your other personal information. Your password must contain at least 8 characters.Your password can't be a commonly used password. Your password can't be entirely numeric."