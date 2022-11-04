import json

def load_json(file): #Loads Json file
	with open(file, errors='ignore') as jsonFile:
		jsonObject = json.load(jsonFile)
		jsonFile.close()
	return jsonObject


def create_business(business, number):#Maps business data to a dictionary 
	biz = {}
	biz['placeId'] = number
	biz['name'] = business['name']
	#biz['type'] = mapped to user input
	biz['rating'] = business['rating']
	biz['location'] = business['geometry']['location']
	return biz

def create_nodes(business, number):#Maps business data to a dictionary for node data
	node = {}
	#Define Node
	node['rating'] = business['rating']
	node['placeId'] = number
	#type defined from user input
	return node



def create_edge(previous_nodes, business, edges, number):#creates edges using the previous node values, and a business. It will add the edge to the current list of edges
	edge = {}
	for node in previous_nodes:
		edge['sourceId'] = node['placeId']
		edge['targetId'] = number
		edge['rating'] = 5 - float(business['rating'])
		edges.append(edge)
	return edges




if __name__ == "__main__":
    files = ['places_movie.json', 'places_bar.json', 'places_restaurants.json'] #test json files

    businesses = [{'placeId': 1, 'type': 'user_node', 'rating': False, 'distance': False, 'location': {'lat': 38, 'lng': -77}}] #format of business list-dict structure and User data
    nodes = [{'placeId': 1, 'type': 'user_node', 'rating': False}] #format for nodes list-dict structure and User data
    edges = [] # empty list to hold edges, passed in edges function and appended to
    previous_nodes = [{'placeId':1, 'type': 'user_node', 'rating': False}] #list to hold the nodes from the previous API call

    number = 2 #ID for nodes

    for file in files:
        jsonObject = load_json(f"test_data/{file}")
        prev_nodes = [] # empty list that will be populated with nodes from this loops run
        for business in jsonObject['results']: #loop through json results 
            if business['business_status'] != 'OPERATIONAL': #Check that the business is operating 
                continue
            businesses.append(create_business(business, number))#appends businesses created from json object to the businesses list in the paremeters
            nodes.append(create_nodes(business, number)) #appends nodes created from the json object to the nodes list in the paremeters
            prev_nodes.append(create_nodes(business, number)) #maps nodes from this json object to the nodes list in the parameters 
            create_edge(previous_nodes,business,edges, number)#appends edges from the
            number += 1
        previous_nodes = prev_nodes.copy() #overwrites the previous_nodes variable with the nodes from this loop run 



