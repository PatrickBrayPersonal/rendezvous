from rendez.main import run
from test_preprocessor import load_json


def test_main():
    FILES = [
        "places_movie.json",
        "places_bar.json",
        "places_restaurants.json",
    ]  # test json files
    TYPES = ["start", "movie", "bar", "restaurant"]
    USER_NODE = [
        [
            {
                "geometry:location:lat": 38.919188013297024,
                "geometry:location:lng": -77.02494496019774,
            }
        ]
    ]  # the starting location

    file_contents = [load_json(f"test_data/{file}")["results"] for file in FILES]
    biz_lists = USER_NODE + file_contents
    run(
        biz_lists=biz_lists,
        type_list=TYPES,
        edge_objectives={"distance": 1},
        node_objectives={"price_level": 2},
    )


if __name__ == "__main__":
    test_main()
