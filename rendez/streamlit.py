from turtle import distance
import streamlit as st
import pandas as pd
import numpy as np
import leafmap.foliumap as leafmap
import folium
from streamlit_folium import st_folium
import requests
from main import run
from dotenv import find_dotenv, load_dotenv
import os

load_dotenv(find_dotenv())

# initialize important lists
places = ["Restaurant", "Bar", "Night Club", "Movie Theater", "Gallery"]
key_to_id = {"Restaurant" : 'restaurant', "Bar": 'bar', "Night Club": 'night_club', "Movie Theater": 'movie_theater', "Gallery": 'art_gallery'}
cities = ['Washington DC', 'Chicago', 'New York City', 'Los Angeles', 'Atlanta']
city_features = {'Washington DC': {'lat': '38.902260', 'lng':'-77.035256', 'radius': '7500'}, 
                 'Chicago': {'lat': '41.852831', 'lng':'-87.630385', 'radius': '14000'}, 
                 'New York City': {'lat': '40.654447', 'lng':'-73.957754', 'radius':'20000'}, 
                 'Los Angeles': {'lat': '34.080467', 'lng':'-118.297799', 'radius':'20000'}, 
                 'Atlanta': {'lat': '33.764209', 'lng':'-84.430916', 'radius':'10000'}}

##dummy dataframe for testing
df = pd.DataFrame({
  'first column': [1, 2, 3, 4],
  'second column': [10, 20, 30, 40]
})

st.title(":beers: Welcome to Rendevous")
st.subheader("The Fastest Way to Plan a Night Out")
st.markdown('''How To Use;
1. :cityscape: Choose where you want to go 
2. :blue_heart: Choose what you care about
3. :world_map: View your route!''')


st.subheader('Your Night Out')


# m = leafmap.Map(center=[40, -100], zoom=3)
# lines = 'https://raw.githubusercontent.com/giswqs/leafmap/master/examples/data/cable_geo.geojson'
# m.add_geojson(lines, layer_name="Cable lines")
# m.to_streamlit(height=700)

# st.subheader("Link to [View on Google Maps]")
##Alternate Routes/Options

st.subheader('Need Some Help?')

chart_data = pd.DataFrame(
    np.random.randn(3, 3),
    columns=["a", "b", "c"])

st.bar_chart(chart_data)


#=================SIDEBAR=======================
st.sidebar.subheader("Select Your Route Options")

##Destination Types Select List and Logic

citiesdf = pd.DataFrame({
  'options': cities
})

def update_city():
    lat = city_features[st.session_state.city]['lat']
    lng = city_features[st.session_state.city]['lng']
    st.session_state.start = [float(lat),float(lng)]
    st.session_state.locations = [{'coords':[float(lat),float(lng)], 'pop_name':st.session_state.city, 'tip_name':st.session_state.city}]

destination_city = st.sidebar.selectbox(
    'Which city are you going to',
     citiesdf['options'], key = 'city', on_change=update_city)


destinations = pd.DataFrame({
  'options': places
})

destination_types1 = st.sidebar.selectbox(
    'Where do you want to go first?',
     destinations['options'], key = 'type1')

destination_types2 = st.sidebar.selectbox(
    'Where do you want to go second?',
     destinations['options'], key = 'type2')

destination_types3 = st.sidebar.selectbox(
    'Where do you want to go third?',
     destinations['options'], key = 'type3')
##Priorities Select List and Logic


####Priorities Logic;
# 1. Highly Reputable = Higher weight towards destinations with High Rating and 100+ Reviews
# 2. Great Location = Higher weight towards minimizing distance
# 3. Unbeatable Price = Higher weight towards pricing
# 4. Luxury Experience = Higher weight towards destinations that are expensive and High Rating
#note if Luxury Experience AND Unbeatable Price are selected they just cancel out and focus on High Rating

priorities = pd.DataFrame({
  'options': ["Highly Reputable", "Great Location", "Unbeatable Price", "Luxury Experience"]
})

##Initialize a value for priority_2 since its referenced in the variable priority_1 before assignment
priority_2 = "Great Location"


priority_1 = st.sidebar.selectbox(
    "What's most important for tonight?" ,
     priorities[priorities['options'] != priority_2], index = 0)

priority_2 = st.sidebar.selectbox(
    'What else matters to you?',
     priorities[priorities['options'] != priority_1], index = 1)



##MAP TESTING####

if 'locations' not in st.session_state:
    lat = city_features[st.session_state.city]['lat']
    lng = city_features[st.session_state.city]['lng']
    st.session_state.start = [float(lat),float(lng)]
    st.session_state.locations = [{'coords':[float(lat),float(lng)], 'pop_name':st.session_state.city, 'tip_name':st.session_state.city}]
    

def locate():
    placesapikey = os.getenv("API_KEY")
    
    types = [st.session_state.type1, st.session_state.type2, st.session_state.type3]
    
    lat = city_features[st.session_state.city]['lat']
    lng = city_features[st.session_state.city]['lng']
    radius = city_features[st.session_state.city]['radius']
    
    locations = []
    
    file_contents = []
    TYPES = ["Start"]
    
    for typest in types:
        typeid = key_to_id[typest]
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=" + lat + "%2C" + lng + "&radius=" + radius + "&type=" + typeid + "&key=" + placesapikey
    
        payload={}
        headers = {}
    
        response = requests.request("GET", url, headers=headers, data=payload)
    
        results = response.json()['results']
        file_contents.append(results)
        TYPES.append(typest)
        
    USER_NODE = [
        [
            {
                "geometry:location:lat": 38.919188013297024,
                "geometry:location:lng": -77.02494496019774,
                "name": 'Start'
            }
        ]
    ]  # the starting location

    biz_lists = USER_NODE + file_contents
    placesdf = run(biz_lists=biz_lists, type_list=TYPES, edge_objectives={}, node_objectives={})
    
    locations = [{'coords':[USER_NODE[0][0]['geometry:location:lat'], USER_NODE[0][0]['geometry:location:lng']], 'pop_name':USER_NODE[0][0]['name'], 'tip_name':USER_NODE[0][0]['name']}]
    
    for i in range(len(placesdf.index)-1):
        place = placesdf.iloc[i+1]

        locations.append({'coords':[place['geometry:location:lat'], place['geometry:location:lng']], 'pop_name':place['name'], 'tip_name':place['name']})
        
        
    st.session_state.locations = locations    
    st.session_state.start = locations[0]['coords']

submit = st.sidebar.button('Submit', on_click=locate)

m = folium.Map(location=st.session_state.start, zoom_start=14)

for location in st.session_state.locations:
  folium.Marker(
      location['coords'], 
      popup=location['pop_name'], 
      tooltip=location['tip_name']
  ).add_to(m)
  
st_data = st_folium(m, width = 725)

# call to render Folium map in Streamlit



###TO DO's
##Can we spot a city center?
##Can we fixed sequence
##input three types plot first 3 results on the map
