import sys
import os
import numpy as np
import pandas as pd


# https://stackoverflow.com/questions/45835993/groupby-and-reduce-pandas-dataframes-with-numpy-arrays-as-entries
def create_user_profiles(ratings_df, output_csv_path):
    user_profiles_df = pd.DataFrame(columns=["userId", "movieId", "rating"])
    user_profiles_df["userId"] = ratings_df["userId"].unique()
    user_profiles_df["movieId"] = ratings_df.groupby("userId")["movieId"].apply(np.hstack)
    user_profiles_df["rating"] = ratings_df.groupby("userId")["rating"].apply(np.hstack)
    user_profiles_df.to_csv(output_csv_path + r"user profiles.csv", index=False)


def create_item_profile(ratings_df, output_csv_path):
    pass


if __name__ == '__main__':
    try:
        # assert len(sys.argv) == 5, "Wrong number of arguments provided. Please pass 4 arguments."
        # assert sys.argv[1] == "ExtractProfiles", "Wrong method provided. Method must be 'ExtractProfiles'"
        # assert os.path.basename(sys.argv[2]) == "ratings.csv", "Wrong input file provided. Input file must be 'ratings.csv'"
        # assert os.path.isfile(sys.argv[2]), "Input file path is invalid or doesn't exist"
        # assert os.path.isdir(sys.argv[3]), "User Profiles directory is invalid or doesn't exist"
        # assert os.path.isdir(sys.argv[4]), "Item Profiles directory is invalid or doesn't exist"

        ratings_path = r"./ratings.csv"
        user_profiles_csv_path = ""
        items_profiles_csv_path = ""

        ratings_df = pd.read_csv(ratings_path)
        create_user_profiles(ratings_df, user_profiles_csv_path)
        create_item_profile(ratings_df, items_profiles_csv_path)
    except Exception as ex:
        print "ERROR!", ex.message
