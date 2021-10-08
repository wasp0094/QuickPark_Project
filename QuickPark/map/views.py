from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from .models import Search
from .forms import SearchForm
import folium
import geocoder
import math
import json
import os
#from sawo import createTemplate,getContext,verifyToken
from ip2geotools.databases.noncommercial import DbIpCity
from ipware import get_client_ip


import pandas as pd
import numpy as np

malls=pd.read_csv("map/malls.csv")
#malls.columns=['Name','available','total']
#print(malls.columns)
#print(malls.head())


data=[['Unity Mall , Delhi',28.5036, 77.0973 , 150 , 500]]
df=pd.DataFrame(data,columns=['name','lat','lng','available_slots','total_slots'])

#login_data=[['arjun','arjun_passwd'],['test','test_passwd']]
#login_df=pd.DataFrame(login_data,columns=['login','password'])

login_df=pd.read_csv("map/login.csv")



# Create your views here.

#def register(request):
    #if request.method=='POST':
        #form=CreateUserForm(request.POST)
        #if form.is_valid():
            #form.save()
            #return redirect('index')

#def login(request):
    #if request.method=='POST':
        #form=AuthenticationForm(data=request.POST)
        #if form.is_valid():
            #return redirect('index')
    #else:
        #form=AuthenticationForm()
    #return render(request,'home.html',{'form':form})        
                    

slots=[[28.6249,77.1109],[28.7383, 77.0822]]

def index(request):
    malls=pd.read_csv("map/malls.csv")
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/map')
    else:
        form = SearchForm()
    address = Search.objects.all().last()
    location = geocoder.osm(address)
    lat = location.lat
    lng = location.lng

    #print(math.floor(lat),math.floor(lng))
    
    country = location.country
    if lat == None or lng == None:
        address.delete()
        #return HttpResponse('You address input is invalid')
        return redirect('/map')

    # Create Map Object
    m = folium.Map(location=[29, 77], zoom_start=10)

    #folium.Marker([28.7383, 77.0822],tooltip="Click for more").add_to(m)

    folium.Marker([lat, lng], tooltip='Click for more',
                  popup=country).add_to(m)


    #for i in slots:
        #slot_lat,slot_long=i[0],i[1]
        #m = folium.Map(location=[19, -12], zoom_start=2)

        #folium.Marker([slot_lat, slot_long], tooltip='Click for more',
                  #popup=country,icon=folium.Icon(color='red')).add_to(m)

                     

    available_slots,total_slots="",""

    for index,row in df.iterrows():
        if math.floor(row['lat'])==math.floor(lat) and math.floor(row['lng'])==math.floor(lng):
            available_slots=row['available_slots']
            total_slots=row['total_slots']                  
    
    

    for index,row in malls.iterrows():
        location=geocoder.osm(row['Name'])
        lat,lng=location.lat,location.lng
        #print(row['available'])

        if lat==None or lng==None:
            #print(row['Name'])
            pass
        else:
            folium.Marker([lat,lng],tooltip=str(row['available']) + "/" + str(row['total_slots']),
            icon=folium.Icon(color='green'),popup=row['Name']).add_to(m) 

    user_country,user_city=location_user(request)
    #print("country:" ,user_country,"city: ",user_city)

    if user_city!=None and user_country!=None:
        location=geocoder.osm(user_city + "," + user_country)
        lat,lng=location.lat,location.lng   

        if lat==None or lng==None:
            pass
        else:
            folium.Circle(
            location=[lat,lng],
            popup=user_city,
            radius=20000,
            color='crimson',
            fill=True,
            fill_color='crimson'
            ).add_to(m)    

            


    # Get HTML Representation of Map Object
    m = m._repr_html_()
    context = {
        'm': m,
        'form': form,
        'available_slots':available_slots,
        'total_slots':total_slots
    }
    return render(request, 'index.html', context)

 

def login(request):
    #print(request.GET)
    login_df=pd.read_csv('map/login.csv')
    username=request.GET.get('user_name')
    password=request.GET.get('password')
    print("USERNAME: ",username,"PASSWORD: ",password)
    c=0

    for index,row in login_df.iterrows():
        if username!=None and password!=None:
            if row['username']==username and row['password']==password:
                #print("\nLOGGED IN\n")
                c=1
                break;
    if c==1:
        return redirect('index')
    else:
        return render(request,'signin.html')  

    return render(request,'signin.html')    
        

                    

                    
    #return render(request,'home.html')   


def location_user(request):
    ip,is_routable=get_client_ip(request)

    if ip is None:
        ip="0.0.0.0"

    try:
        response=DbIpCity.get(ip,api_key="free")
        country=response.country
        city=response.city
    except:
        country="India"
        city="Delhi" 

    if country=="ZZ" or city==None:
        country,city="India","Delhi"           
    
    return (country,city)

def about(request):
    return render(request,"quickpark.html")     

def register(request):
    login_df=pd.read_csv("map/login.csv")
    #print(request.GET)
    username=request.GET.get('user_name')
    email=request.GET.get('email')
    password1=request.GET.get('password1')
    password2=request.GET.get('password2')
    print("username",username)
    print("password",password1)
    print("password2",password2)
    #print("email",email)

    if username!=None and password1!=None and password2!=None:


        if (password1==password2) and (username not in login_df['username']):
            #login_df.append([username,password1])
            #login_df.loc[len(login_df.index)] = [ username,password1] 
            #login_df = pd.concat([login_df, [username,password1]], axis=0)
            data_frame={'username':username,'password':password1}
            login_df=login_df.append(data_frame,ignore_index = True)
            login_df.to_csv('map/login.csv')
            print(login_df.head())
            return redirect('signin.html')
        else:   
            return render(request,'signup.html')

    else:
        return render(request,'signup.html')


def book(request):
    confirmation=""
    context={"confirmation":confirmation} 
    name=request.GET.get('user_name')
    car_number=request.GET.get('carNum')
    place=request.GET.get('place')
    #print("place initial",place)
    #print(malls.head())

    places=["Ambience Mall , Vasant Kunj","City Centre , Dwarka , New Delhi","City Centre , Rohini, New Delhi",
    "D Mall , New Delhi","DLF Avenue , Saket","DLF Emporio , Vasant Kunj","Metro Walk , Rohini",
    "MGF City Square , Delhi","Pacific Mall , New Delhi","Unity One , Rohini , New Delhi"]
    
    if name!=None and car_number!=None and place!=None :
        #place=places[int(place)-1]
        #place=malls.iloc[int(place)-1,-3]
        #print(malls.iloc[int(place)-1,-3])
        #print(place)   

              

    #print("name: ",name)
    #print("car no. :",car_number)
    #print("place : ",place)
        c=0

        for index,row in malls.iterrows():
            if int(row['id'])== int(place):
                if row['available']>0:
                    c=1
                    
                    malls.loc[index,'available']=row['available']-1
                    malls.to_csv('map/malls.csv')
                    print("Slot confirmed")
                    break;

        if c==1:
            confirmation="Slot Confirmed"
            context={"confirmation":confirmation}
            return render(request,'book.html',context)
        else:
            confirmation="Slot not available"
            context={"confirmation":confirmation}
            return render(request,'book.html',context)
            #else:
                #print("place",place)
                #print(row['id'])
                #confirmation="Please Try Again"
                #print("Name didnt match")
                #context={"confirmation":confirmation}
                #return render(request,'book.html',context)

    return render(request,'book.html',context)                    


