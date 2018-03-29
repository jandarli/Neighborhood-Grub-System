from django.contrib.auth.models import User

chef_one = User.objects.get(username="chef_one")

def get_chef_one():
    return User.objects.get(username="chef_one")
