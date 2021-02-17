from django import forms


# A basic form that has a text input to input the username
class UserForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'username-textfield form-control',
                                                             'placeholder': '  Enter GitHub username'}),
                               max_length=20,
                               strip=True,
                               required=True,
                               label='')
