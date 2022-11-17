from rendez.main import run
from test_preprocessor import load_json
import pandas as pd


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
                ["-price_level"],
                ["-rating", "price_level"],
            ],
        }
    )
    run(
        biz_lists=biz_lists,
        type_list=TYPES,
        p_df=priorities,
        priority_1="Highly Reputable",
        priority_2="Great Location",
    )


if __name__ == "__main__":
    test_main()
