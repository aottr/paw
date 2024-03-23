from django.shortcuts import render
from .forms import FblAuthForm

def fbl_authentication_start(request):
    if request.method == "POST":
        form = FblAuthForm(request.POST)
        if form.is_valid():
            
            # set hidden fields with dob and badge number
            return render(request, "fbl_auth_get_code.html")
        else:
            return render(request, "fbl_auth_start.html", {"form": form})
    else:
        form = FblAuthForm()

    return render(request, "auth_start.html", {"form": form})

def fbl_authentication_get_code(request):
    return render(request, "fbl_auth_get_code.html")