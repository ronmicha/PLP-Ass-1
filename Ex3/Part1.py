import sys
import os
import numpy as np
import pandas as pd


def create_user_profiles(ratings_df, output_directory):
    ratings_df = ratings_df.sort_values("userId")
    ratings_df['movieId'] = ratings_df['movieId'].astype('int32')
    user_profiles_df = pd.DataFrame({
        "userId": ratings_df["userId"].unique(),
        "movieIds": ratings_df.groupby("userId")["movieId"].apply(list),
        "ratings": ratings_df.groupby("userId")["rating"].apply(list)
    })
    user_profiles_df.to_csv(output_directory + r"user profiles.csv", index=False, header=True,
                            columns=['userId', 'movieIds', 'ratings'])


def create_item_profile(ratings_df, output_directory):
    ratings_df = ratings_df.sort_values("movieId")
    ratings_df['userId'] = ratings_df['userId'].astype('int32')
    item_profiles_df = pd.DataFrame({
        "movieId": ratings_df["movieId"].unique(),
        "userIds": ratings_df.groupby("movieId")["userId"].apply(list),
        "ratings": ratings_df.groupby("movieId")["rating"].apply(list)
    })
    item_profiles_df.to_csv(output_directory + r"item profiles.csv", index=False, header=True,
                            columns=['movieId', 'userIds', 'ratings'])


if __name__ == '__main__':
    try:
        # assert len(sys.argv) == 5, "Wrong number of arguments provided. Please provide 4 arguments"
        # assert sys.argv[1] == "ExtractProfiles", "Wrong method provided. Method must be 'ExtractProfiles'"
        # assert os.path.basename(sys.argv[2]) == "ratings.csv", "Wrong input file provided. Input file must be named 'ratings.csv'"
        # assert os.path.isfile(sys.argv[2]), "Input file path is invalid or file doesn't exist"
        # assert os.path.isdir(sys.argv[3]), "User Profiles directory is invalid or doesn't exist"
        # assert os.path.isdir(sys.argv[4]), "Item Profiles directory is invalid or doesn't exist"
        #
        # ratings_path = sys.argv[2]
        # user_profiles_directory = sys.argv[3]
        # items_profiles_directory = sys.argv[4]

        ratings_path = r"./ratings.csv"
        user_profiles_directory = ""
        items_profiles_directory = ""

        rating_df = pd.read_csv(ratings_path)
        create_user_profiles(rating_df, user_profiles_directory)
        create_item_profile(rating_df, items_profiles_directory)
    except Exception as ex:
        print "ERROR!", ex.message
