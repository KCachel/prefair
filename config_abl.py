import pandas as pd
import numpy as np
import src as src
import random

from itertools import combinations
def config_study(profile_df, dataset_df, candidates_col, sa_col, full_profile_df):
    # Prefair
    features_df = dataset_df.drop(columns=[sa_col])  # Drop sensative attribute
    completed_profile_df = src.imp._imputate_candidates(profile_df, features_df, candidates_col)
    prefair_akt = avg_kt(completed_profile_df, full_profile_df)

    # Random
    # For every ranking:
    profile_dict = {}  # init empty dict
    num_unique_rankings = len(profile_df.columns)
    totals_random_akt = []
    for trail in range(0,10):
        for r in range(0, num_unique_rankings):
            single_ranking = pd.DataFrame(profile_df.iloc[:, r])  # isolate ranking
            candidates_ranked = list(single_ranking.to_numpy().flatten())
            unranked_set_df = dataset_df[~dataset_df[candidates_col].isin(candidates_ranked)]
            unranked_data = unranked_set_df.drop(columns=[candidates_col])
            candidates_unranked = list(unranked_set_df[candidates_col].to_numpy())
            #random shuffle
            #then append
            random.seed(123+trail)
            random.shuffle(candidates_unranked)
            completed_ranking = candidates_ranked + candidates_unranked
            profile_dict[list(profile_df.columns)[r]] = completed_ranking
        # Update profile
        random_profile_df = pd.DataFrame(profile_dict)
        random_akt = avg_kt(random_profile_df, full_profile_df)
        totals_random_akt.append(random_akt)
    print(totals_random_akt)
    return prefair_akt, np.mean(totals_random_akt)

def avg_kt(i_profile, known_profile):
    # For every ranking:
    num_unique_rankings = len(i_profile.columns)
    avg = []
    for r in range(0, num_unique_rankings):
        single_ranking = pd.DataFrame(i_profile.iloc[:, r])  # isolate ranking
        candidates_ranked = list(single_ranking.to_numpy().flatten())
        single_known_ranking = pd.DataFrame(known_profile.iloc[:, r])  # isolate ranking
        candidates_ranked_known = list(single_known_ranking.to_numpy().flatten())

        #drop candidates that are not known
        candidates_ranked = sorted(set(candidates_ranked) & set(candidates_ranked_known), key = candidates_ranked.index)
        candidates_ranked_known = [x for x in candidates_ranked_known if str(x) != 'nan']
        kt = ktd(candidates_ranked, candidates_ranked_known)
        avg.append(kt)
    return np.mean(avg)


def ktd(rank_a, rank_b):

    tau = 0
    n_candidates = len(rank_a)
    a = list(range(0, len(rank_a))) #make ints
    b = [rank_a.index(cand) for cand in rank_b]
    for i, j in combinations(range(n_candidates), 2):
        tau += (np.sign(a[i] - a[j]) ==
                -np.sign(b[i] - b[j]))
    return tau