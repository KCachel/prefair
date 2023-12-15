import iteround
import numpy as np

def get_representation(profile_df, dataset_df, candidates_col, sa_col):
    """
    Return data structures capturing the representation of groups in a preference profile.
    :param profile_df: Dataframe of preference profile
    :param dataset_df: Dataframe of candidate dataset
    :param candidates_col: Column in dataset_df with candidate ids/names
    :param sa_col: Column in dataset_df with group information
    :return: item_group_dict, pool_group_cnt_dict, ranked_item_group_dict, profile_group_cnt_dict
    """
    # SA data for all candidates (i.e., whole pool)
    unique_candidates = list(np.unique(dataset_df[candidates_col].values))
    sa = [dataset_df.loc[dataset_df[candidates_col] == c][sa_col].item() for c in unique_candidates]
    item_group_dict = dict(zip(unique_candidates, sa))
    groups, count_per_group, = np.unique(sa, return_counts=True)
    # Dictionary of groups and their counts
    pool_group_cnt_dict = dict(map(lambda i, j: (i, j), groups, count_per_group))

    # SA data for candidates in the profile
    unique_ranked_candidates = list(np.unique(profile_df))
    sa_ranked = [dataset_df.loc[dataset_df[candidates_col] == c][sa_col].item() for c in unique_ranked_candidates]
    groups_ranked, count_per_ranked_group = np.unique(sa_ranked, return_counts=True)
    ranked_item_group_dict = dict(zip(unique_ranked_candidates, sa_ranked))
    profile_group_cnt_dict = {}
    for group in list(pool_group_cnt_dict.keys()):
        if group in groups_ranked:  # group is in the profile
            profile_group_cnt_dict[group] = count_per_ranked_group[np.where(groups_ranked == group)[0][0]]
        else:  # group is not in the profile
            profile_group_cnt_dict[group] = 0

    return item_group_dict, pool_group_cnt_dict, ranked_item_group_dict, profile_group_cnt_dict

def set_representation(pool_group_cnt_dict, profile_group_cnt_dict, fair_rep, k):
    """
    Return dictionary (groups keys) and values are counts per group for desired fairness and k value.
    :param pool_group_cnt_dict: Dict - keys = groups and values = count in the pool
    :param profile_group_cnt_dict: Dict - keys = groups and values = count in the preference profile
    :param fair_rep: 'EQUAL' or 'PROPORTIONAL'
    :param k: int of consensus ranking length
    :return: dictionary of keys = groups and counts are values
    """
    curr_grp_cnts = list(profile_group_cnt_dict.values()) #current count per group
    total_grp_cnts = list(pool_group_cnt_dict.values()) #total count per group
    grp_n = len(list(profile_group_cnt_dict.values())) #num groups
    if fair_rep == "EQUAL":
        #make all k/number of groups
        per_grp = [k // grp_n + (1 if x < k % grp_n else 0) for x in range(grp_n)]
        if _check_grp_cnts(per_grp, total_grp_cnts) == True:
            #make all groups as big as smallest group
            print("The k value you selected cannot be achieve with equal representation, so each group will have as many members as the smallest group.")
            per_grp = [np.min(curr_grp_cnts[np.nonzero(curr_grp_cnts)])] * grp_n

    if fair_rep == "PROPORTIONAL":
        #Use the pool proportion
        prop = np.asarray(total_grp_cnts)/ np.sum(total_grp_cnts)
        per_grp = iteround.saferound(prop*k, 0)

    return dict(zip(list(profile_group_cnt_dict.keys()), per_grp))

def _check_grp_cnts(per_grp, total_grp_cnts):
    """
    Check if there is enough candidates per group
    :param per_grp: dictionary of set constraints (keys are groups)
    :param total_grp_cnts: dictionary of total group counts (keys are groups)
    :return: True or False
    """
    difs = [total_grp_cnts[i] - per_grp[i] for i in range(0, len(per_grp))]
    return np.all(np.asarray(difs) < 0)