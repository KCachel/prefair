# Script for helper functions
import numpy as np
import pandas as pd
def get_item_group_dict_for_ranking(ranking_df, dataset_df, candidates_col, sa_col):
    """
    Create item group dict.
    :param ranking_df: Dataframe of candidates
    :param dataset_df: Dataframe of candidate pool
    :param candidates_col: Column in dataset_df with candidate ids/names
    :param sa_col: Column in dataset_df with group information
    :return: item_group_dict
    """
    unique_candidates = list(np.unique(ranking_df.values))
    sa = [dataset_df.loc[dataset_df[candidates_col] == c][sa_col].item() for c in unique_candidates]
    item_group_dict = dict(zip(unique_candidates, sa))
    return item_group_dict

def get_item_group_dict(dataset_df, candidates_col, sa_col):
    """
    Create item group dict.
    :param dataset_df: Dataframe of candidate pool
    :param candidates_col: Column in dataset_df with candidate ids/names
    :param sa_col: Column in dataset_df with group information
    :return: item_group_dict
    """
    unique_candidates = list(np.unique(dataset_df[candidates_col].values))
    sa = [dataset_df.loc[dataset_df[candidates_col] == c][sa_col].item() for c in unique_candidates]
    item_group_dict = dict(zip(unique_candidates, sa))
    return item_group_dict

def rankingdf_to_proportions(ranking_df, item_group_dict):
    """
    Calculate each group's proportion of a dataframe of ranking(s) i.e. the preference profile or consensus ranking.
    :param ranking_df:Dataframe of candiates
    :param item_group_dict: Dictionary where candidates are keys and values are their groups
    :return: group_cnt_dict
    """
    num_rankings = len(ranking_df.columns)
    candidates = []
    for r in range(0, num_rankings):
        single_ranking = ranking_df[ranking_df.columns[r]]  # isolate ranking
        single_ranking = np.array(
            single_ranking[~pd.isnull(single_ranking)]
        )  # drop any NaNs
        candidates = candidates + single_ranking.tolist()
    unique_candidates = np.unique(candidates)
    groups_of_df = [item_group_dict[c] for c in unique_candidates]
    grps, grp_count = np.unique(groups_of_df, return_counts=True)
    group_cnt_dict = dict(zip(grps.tolist(), grp_count.tolist()))
    return group_cnt_dict

