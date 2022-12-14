import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests
from main import run
from dotenv import find_dotenv, load_dotenv
import statistics as stat

load_dotenv(find_dotenv())

# initialize important lists
places = [
    "Restaurant",
    "Amusement Park",
    "Aquarium",
    "Art Gallery",
    "Bakery",
    "Bar",
    "Book Store",
    "Bowling Alley",
    "Cafe",
    "Casino",
    "Department Store",
    "Library",
    "Movie Theater",
    "Museum",
    "Night Club",
    "Park",
    "Shopping Mall",
    "Tourist Attraction",
    "Zoo",
]
key_to_id = {
    "Amusement Park": "amusement_park",
    "Aquarium": "aquarium",
    "Art Gallery": "art_gallery",
    "Bakery": "bakery",
    "Bar": "bar",
    "Book Store": "book_store",
    "Bowling Alley": "bowling_alley",
    "Cafe": "cafe",
    "Casino": "casino",
    "Department Store": "department_store",
    "Library": "library",
    "Movie Theater": "movie_theater",
    "Museum": "museum",
    "Night Club": "night_club",
    "Park": "park",
    "Restaurant": "restaurant",
    "Shopping Mall": "shopping_mall",
    "Tourist Attraction": "tourist_attraction",
    "Zoo": "zoo",
}

radius = (
    "20000"  # radius around which to pull down places, in kilometers. Make adjustable?
)

##dummy dataframe for testing
df = pd.DataFrame({"first column": [1, 2, 3, 4], "second column": [10, 20, 30, 40]})
st.title(":beers: Welcome to Rendevous")
st.subheader("The Fastest Way to Plan a Night Out")
st.markdown(
    """1. :cityscape: Choose where you want to go 
2. :blue_heart: Choose what you care about
3. :world_map: View your route!"""
)


st.subheader("Your Night Out")

if "locations" not in st.session_state:  # default to displaying Washington DC
    lat = "38.902260"
    lng = "-77.035256"
    st.session_state.start = [float(lat), float(lng)]
    st.session_state.locations = [
        {
            "coords": [float(lat), float(lng)],
            "pop_name": "Washington DC",
            "tip_name": "Washington DC",
            "tip_type": "City",
            "total_ratings": 0,
            "rating": 0,
            "price_level": 0.0,
        }
    ]

##calc metrics
st.session_state.metrics = {
    "avg_price": 0,
    "reputation": 0,
    "avg_number_reviews": 0,
    "distance": 0,
}

prices = []
reviews = []
ratings = []

for spot in st.session_state.locations:

    if spot["price_level"] >= 0:
        prices.append(spot["price_level"])
    if spot["total_ratings"] >= 0:
        reviews.append(spot["total_ratings"])
    if spot["rating"] >= 0:
        ratings.append(spot["rating"])

st.session_state.metrics = {
    "avg_price": stat.mean(prices),
    "reputation": stat.mean(ratings),
    "avg_number_reviews": stat.mean(reviews),
    "distance": 0,
}

# display metrics
m1, m2, m3, m4 = st.columns(4)

m1.markdown(":money_with_wings: **Price Level**")
m1.write(round(st.session_state.metrics["avg_price"], 2))
m2.markdown(":star: **Star Rating**")
m2.write(round(st.session_state.metrics["reputation"], 2))
m3.markdown(":mega: **Average # Of Reviews**")
m3.write(round(st.session_state.metrics["avg_number_reviews"], 2))
m4.markdown(":shoe: **Distance**")
m4.write(round(st.session_state.metrics["distance"], 2))


# =================SIDEBAR=======================
st.sidebar.subheader("Select Your Route Options")

##Destination Types Select List and Logic


starting_point = st.sidebar.text_input(
    "What address would you like to start from?", key="address"
)


def find_starting_address():  # find user supplied starting address and display it on map, also setting it up to be the first node in the optimizer

    placesapikey = st.secrets["API_KEY"]
    locations = []

    url = (
        "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input="
        + st.session_state.address.replace(" ", "%2C")
        + "&inputtype=textquery&fields=formatted_address%2Cname%2Crating%2Copening_hours%2Cgeometry&key="
        + placesapikey
    )

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code != 200:
        st.error(f"API Key Failed {response.status_code}")
    elif len(response.json()["candidates"]) == 0:
        st.error(f"No results found for {st.session_state.address}")
    else:
        result = response.json()["candidates"][0]

        locations.append(
            {
                "coords": [
                    result["geometry"]["location"]["lat"],
                    result["geometry"]["location"]["lng"],
                ],
                "pop_name": result["name"],
                "tip_name": result["name"],
                "tip_type": "start",
                "total_ratings": 0,
                "rating": 0,
                "price_level": 0.0,
            }
        )

        st.session_state.locations = locations
        st.session_state.start = locations[0]["coords"]


address = st.sidebar.button("Find Address", on_click=find_starting_address)

destinations = pd.DataFrame({"options": places})

destination_types1 = st.sidebar.selectbox(
    "Where do you want to go first?", destinations["options"], key="type1"
)

destination_types2 = st.sidebar.selectbox(
    "Where do you want to go second?", destinations["options"], key="type2"
)

destination_types3 = st.sidebar.selectbox(
    "Where do you want to go third?", destinations["options"], key="type3"
)
##Priorities Select List and Logic


####Priorities Logic;
# 1. Highly Reputable = Higher weight towards destinations with High Rating and 100+ Reviews
# 2. Great Location = Higher weight towards minimizing distance
# 3. Unbeatable Price = Higher weight towards pricing
# 4. Luxury Experience = Higher weight towards destinations that are expensive and High Rating
# note if Luxury Experience AND Unbeatable Price are selected they just cancel out and focus on High Rating
# * List of available node attributes * #
# ['geometry:location:lat', 'geometry:location:lng', 'type', 'type_order',
#        'business_status', 'geometry:viewport:northeast:lat',
#        'geometry:viewport:northeast:lng', 'geometry:viewport:southwest:lat',
#        'geometry:viewport:southwest:lng', 'icon', 'icon_background_color',
#        'icon_mask_base_uri', 'name', 'opening_hours:open_now', 'photos',
#        'place_id', 'plus_code:compound_code', 'plus_code:global_code',
#        'rating', 'reference', 'scope', 'types', 'user_ratings_total',
#        'vicinity', 'price_level', 'id']
priorities = pd.DataFrame(
    {
        "options": [
            "Highly Reputable",
            "Great Location",
            "Unbeatable Price",
            "Luxury Experience",
        ],
        "objective": [
            ["-rating", "-user_ratings_total"],
            ["distance"],
            ["price_level"],
            ["-rating", "-price_level"],
        ],
    }
)
##Initialize a value for priority_2 since its referenced in the variable priority_1 before assignment
priority_2 = "Great Location"
priority_1 = st.sidebar.selectbox(
    "What's most important for tonight?",
    priorities["options"],
    index=0,
)

priority_2 = st.sidebar.selectbox(
    "What else matters to you?",
    priorities["options"],
    index=1,
)

##MAP TESTING####


def plan_night_out():  # callback function of Submit button. Pulls down places from API and passes to optimizer and updates st.session_state.location with results
    placesapikey = st.secrets["API_KEY"]

    types = [st.session_state.type1, st.session_state.type2, st.session_state.type3]

    lat = str(st.session_state.locations[0]["coords"][0])
    lng = str(st.session_state.locations[0]["coords"][1])

    locations = [st.session_state.locations[0]]

    file_contents = []
    TYPES = ["Start"]

    for typest in types:
        typeid = key_to_id[typest]
        url = (
            "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="
            + lat
            + "%2C"
            + lng
            + "&radius="
            + radius
            + "&type="
            + typeid
            + "&key="
            + placesapikey
        )

        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)

        results = response.json()["results"]
        file_contents.append(results)
        TYPES.append(typest)

    USER_NODE = [
        [
            {
                "geometry:location:lat": st.session_state.locations[0]["coords"][0],
                "geometry:location:lng": st.session_state.locations[0]["coords"][1],
                "name": st.session_state.locations[0]["pop_name"],
            }
        ]
    ]  # the starting location in the format that the optimizer wants

    biz_lists = USER_NODE + file_contents
    placesdf, message, soln = run(
        biz_lists=biz_lists,
        type_list=TYPES,
        priority_1=priority_1,
        priority_2=priority_2,
        p_df=priorities,
    )
    for i in range(len(placesdf.index) - 1):
        place = placesdf.iloc[i + 1]

        locations.append(
            {
                "coords": [
                    place["geometry:location:lat"],
                    place["geometry:location:lng"],
                ],
                "pop_name": place["name"],
                "tip_name": place["name"],
                "tip_type": place["type"],
                "total_ratings": place["user_ratings_total"],
                "rating": place["rating"],
                "price_level": float(place["price_level"]),
            }
        )

    st.session_state.locations = locations
    st.session_state.start = locations[0]["coords"]


submit = st.sidebar.button("Submit", on_click=plan_night_out)

m = folium.Map(location=st.session_state.start, zoom_start=14)

for location in st.session_state.locations:
    folium.Marker(
        location["coords"],
        popup=location["pop_name"],
        tooltip=f"{location['tip_name']}, {location['tip_type']}",
    ).add_to(m)

st_data = st_folium(m, width=725)  # call to render Folium map in Streamlit

st.markdown(
    """
# How does it work?

Our optimizer searches the solution space of all paths from the user???s starting point(s) to each desired business in the order that the user selects.

## Data Structure - Directed Graph

To formulate the optimization problem, we converted our input data to a directed graph of feasible solution paths. The edges of the graph are selected to illustrate the path that the user must take on their night-out. We optimize over a combination of the attributes of the businesses while minimizing the total distance traveled.

|                 |                                        Nodes                                     |                                                       Edges                                                    |
|-----------------|:--------------------------------------------------------------------------------:|:--------------------------------------------------------------------------------------------------------------:|
|     Represent   |   All potential businesses in the user???s area and the user???s current location.   |   Potential paths the user would take on their night-out. Edges are only created in the user-specified order.  |
|     Attributes  |   Characteristics of the business from google places API (ratings, price, etc.)  |   Haversine distance between the connected nodes.                                                              |
"""
)
st.image("example_graph.jpeg")
st.markdown(
    """
Example directed graph with for visiting a theater, restaurant and bar in an area with two of each business type. An example solution to this graph is marked by the red edges. Stars represent the rating of each business, which our optimizer weighs against distance in order to find the best solution.

## Preprocessing

Many businesses fall into categories of multiple types. This causes the optimizer to typically recommend staying at the same business when going from one stop to the next. This is especially common for bars and restaurants. To meet the desires of our users we removed these edges from the solution graph in order to prevent the optimizer from recommending repeat locations.

## Constraints

The problem???s constraints shrink the solution space to allow for a contiguous and complete night-out.

### Continuity Constraint

Each selected edge must share both nodes with another edge or the starting/ending node.

### Starting Constraint

Starting node (user???s location) must have an outgoing edge connected.

### Ending Constraint

There must be one edge connecting to a node of final business type.

## Objective

The objective in the solver is designed to be flexible and adjusted by the user???s input for two priorities. The attributes of each business from the google places API are considered within the context of the user???s declared preferences. The ???most important??? selection from the fronted is weighted twice as heavily as the ???what else is important to you??? selection.

|       Selection        |         Optimizer Minimizes     |
|------------------------|:-------------------------------:|
|     Highly Reputable   |   -rating, -user_ratings_total  |
|     Great Location     |   distance                      |
|     Unbeatable Price   |   price_level                   |
|     Luxury Experience  |   -rating, -price_level         |

## Solver ??? CP-SAT

 Our optimizer was built using the [OR-Tools](https://developers.google.com/optimization) CP-SAT solver, an interface for a meta-heuristic optimizer on top of a satisfiability solver. The optimizer can minimize attributes for businesses and paths between businesses (nodes and edges) visited. We will fit all attributes to a standard normal distribution prior to optimization in order to prevent large variables from overwhelming the objective.

## Attribute Scaling

Input attributes (distance, price level, number of ratings) come on different scales. In order to prevent larger values from having an outsized effect on the objective, we fit all attributes to a standard normal distribution prior to optimization.

The CP-SAT optimizer only accepts integer values as input. After scaling, attributes are multiplied by 10,000 and cast to integers to maintain data granularity.
    """
)
