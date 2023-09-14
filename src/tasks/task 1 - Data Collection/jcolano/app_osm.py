# %%
import osmnx as ox
import networkx as nx
import json
from geopy.geocoders import Nominatim
from geopy.point import Point

# %%
# Load the street network of Paris from OSM
graph = ox.graph_from_place('Paris, France', network_type='drive')


# %%
def get_driving_directions(start_lat, start_lng, end_lat, end_lng):
    # Create the origin and destination points
    origin = (start_lat, start_lng)
    destination = (end_lat, end_lng)

    # Retrieve the nearest network nodes for the origin and destination
    origin_node = ox.distance.nearest_nodes(graph, origin[1], origin[0])
    destination_node = ox.distance.nearest_nodes(graph, destination[1], destination[0])

   # Find the shortest path between the nodes
    route = nx.shortest_path(graph, origin_node, destination_node, weight='length')

    # Calculate the distance and estimated time
    distance = sum(ox.distance.great_circle_vec(graph.nodes[node]['y'], graph.nodes[node]['x'],
                                                graph.nodes[next_node]['y'], graph.nodes[next_node]['x'])
                   for node, next_node in zip(route[:-1], route[1:]))
    estimated_time = distance / 20  # Assuming average driving speed of 20 meters per second

    # Create the JSON response
    response = {
        'coordinates': [(graph.nodes[node]['y'], graph.nodes[node]['x']) for node in route],
        'distance': distance,
        'estimated_time': estimated_time
    }

    return response


# %%
def convert_node_ids_to_street_names(directions_json):
    # Convert node IDs to street names
    geolocator = Nominatim(user_agent='omdena-paris')
    instructions = []
    for lat, lon in directions_json['coordinates']:
        location = Point(lat, lon)
        address = geolocator.reverse(location, exactly_one=True)
        instructions.append(address.address)

    # Create the updated JSON response
    updated_directions_json = directions_json.copy()
    updated_directions_json['instructions'] = instructions
    del updated_directions_json['coordinates']

    return updated_directions_json

# %%
# Set custom user agent for Nominatim geolocator
geolocator = Nominatim(user_agent='omdena-paris')


# %%
# Example usage with two locations in Paris
start_lat = 48.8591
start_lng = 2.2945
end_lat = 48.8566
end_lng = 2.3522

# %%

directions = get_driving_directions(start_lat, start_lng, end_lat, end_lng)


# %%
# Convert node IDs to street names
updated_directions = convert_node_ids_to_street_names(directions)


# %%

# Print the updated JSON response with human-readable instructions
print(json.dumps(updated_directions, indent=4))

# %%



