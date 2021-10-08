from django.http import HttpResponse
from django.shortcuts import render

def webpage(request):
	return render(request,"about.html")