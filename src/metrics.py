# Script for metrics
# References: Geyik, S. C., Ambler, S., & Kenthapadi, K. (2019, July).
# Fairness-aware ranking in search & recommendation systems with application to linkedin talent search.
# In Proceedings of the 25th acm sigkdd international conference on knowledge discovery & data mining (pp. 2221-2231).

import numpy as np
import pandas as pd

def full_sat_index(profile_df, profile_percentage, consensus_df):
    """
    What index does the consensus satisfy profile_percentage?
    :param profile_df: Dataframe of preference profile
    :param consensus_df: Dataframe of consensus ranking
    :param consensus_percentage: Depth of consensus ranking @ percentage
    :return: index as percentage
    """
    num_rankings = len(profile_df.columns)
    consensus = list(consensus_df[consensus_df.columns[0]])
    sats = []
    for r in range(0, num_rankings):
        indxs = []
        single_ranking = profile_df[profile_df.columns[r]]  # isolate ranking
        single_ranking = np.array(
            single_ranking[~pd.isnull(single_ranking)]
        )  # drop any NaNs
        top = list(single_ranking[0:round(profile_percentage * len(single_ranking))])
        for i in top:
            if i in consensus:
                indxs.append(consensus.index(i))
        if len(indxs) > 0:
            sats.append(np.max(indxs))
        else:
            return np.Inf
    return (np.max(sats)+1)/len(consensus)



def satisfaction_index_count(profile_df, profile_depth, consensus_df, consensus_depth, overlap):
    """
    Calculate percent of rankers satisfied (have overlap candidates @ both profile depth and consensus depth)
    :param profile_df: Dataframe of preference profile
    :param profile_depth: index of profile
    :param consensus_df: Dataframe of consensus ranking
    :param consensus_depth: index of consensus ranking
    :param overlap: How many items should be shared to be satisfied
    :return: Percent of rankers satisfied
    """
    consensus = list(consensus_df[consensus_df.columns[0]])
    consensus_top = consensus[0:consensus_depth]
    num_rankings = len(profile_df.columns)
    num_satisfied = 0
    for r in range(0, num_rankings):
        single_ranking = profile_df[profile_df.columns[r]]  # isolate ranking
        single_ranking = np.array(
            single_ranking[~pd.isnull(single_ranking)]
        )  # drop any NaNs
        top = list(single_ranking[0:profile_depth])
        top_length = len(top)
        intersection = set(top).intersection(set(consensus_top))
        if len(intersection) >= overlap:
            num_satisfied += 1
    satisfaction = num_satisfied/num_rankings
    return satisfaction


def average_satisfaction_percentage(profile_df, profile_percentage, consensus_df, consensus_percentage):
    """
    Average amongst rankers proportion of items shared between profile depth (as %) and consensus depth (as %)
    :param profile_df: Dataframe of preference profile
    :param profile_percentage: Depth of profile as percentage of profile
    :param consensus_df: Dataframe of consensus ranking
    :param consensus_percentage: Depth of consensus ranking as percentage of profile
    :return: satisfaction
    """
    consensus_depth = round(consensus_percentage*len(consensus_df[consensus_df.columns[0]]))
    consensus = list(consensus_df[consensus_df.columns[0]])
    consensus_top = consensus[0:consensus_depth]
    num_rankings = len(profile_df.columns)
    satisfied = []
    for r in range(0, num_rankings):
        single_ranking = profile_df[profile_df.columns[r]]  # isolate ranking
        single_ranking = np.array(
            single_ranking[~pd.isnull(single_ranking)]
        )  # drop any NaNs
        top = list(single_ranking[0:round(profile_percentage*len(single_ranking))])
        top_length = len(top)
        intersection = set(top).intersection(set(consensus_top))
        satisfied.append(len(intersection)/top_length)
    satisfaction = np.mean(satisfied)
    return satisfaction


def KL_div_pool_assess_set(pool_group_cnt_dict, assess_group_cnt_dict, fair_rep):
    """
    KL divergence between candidate pool and an assessed object
    :param pool_group_cnt_dict: Dictionary of groups (keys) and counts (values)
    :param assess_group_cnt_dict: From either a preference profile or a consensus ranking
    :param fair_rep: EQUAL or PROPORTIONAL
    :return: divergence value
    """
    if fair_rep == "EQUAL":
        desired_proportions = []
        consensus_proportions = []
        consenus_total = np.sum(list(assess_group_cnt_dict.values()))
        for grp, cnt in pool_group_cnt_dict.items():
            desired_proportions.append(1/len(list(pool_group_cnt_dict.keys())))
            if grp in assess_group_cnt_dict.keys():
                consensus_proportions.append(assess_group_cnt_dict[grp] / consenus_total)
            else:
                consensus_proportions.append(0)
    if fair_rep == "PROPORTIONAL":
        desired_proportions = []
        consensus_proportions = []
        pool_total = np.sum(list(pool_group_cnt_dict.values()))
        consenus_total = np.sum(list(assess_group_cnt_dict.values()))
        for grp, cnt in pool_group_cnt_dict.items():
            desired_proportions.append(cnt/pool_total)
            if grp in assess_group_cnt_dict.keys():
                consensus_proportions.append(assess_group_cnt_dict[grp] / consenus_total)
            else:
                consensus_proportions.append(0)
    kl = __kl_divergence(np.asarray(consensus_proportions), np.asarray(desired_proportions))
    return kl


def fair_representation(pool_group_cnt_dict, assess_group_cnt_dict, fair_rep):
    """
    Balance value
    :param pool_group_cnt_dict: Dictionary of groups (keys) and counts (values)
    :param assess_group_cnt_dict: From either a preference profile or a consensus ranking
    :param fair_rep: EQUAL or PROPORTIONAL
    :return: Value
    """
    if fair_rep == "EQUAL":
        if len(list(pool_group_cnt_dict.keys())) != len(list(assess_group_cnt_dict.keys())):
            val = 0 #one group is not selected into the assessed object
        else:
            assess_cnts = list(assess_group_cnt_dict.values()) #counts in object being measured
            total = np.sum(assess_cnts)
            proportions_of_assess_set = np.asarray(assess_cnts) / total
            val = np.min(proportions_of_assess_set) / np.max(proportions_of_assess_set)

    if fair_rep == "PROPORTIONAL":
        if len(list(pool_group_cnt_dict.keys())) != len(list(assess_group_cnt_dict.keys())):
            val = 0 #one group is not selected into the assessed object
        else:
            assess_cnts = list(assess_group_cnt_dict.values()) #counts in object being measured
            pool_cnts = list(pool_group_cnt_dict.values()) #counts in pool
            selection_rates = np.asarray(assess_cnts) / np.asarray(pool_cnts)
            val = np.min(selection_rates) / np.max(selection_rates)
    return val



def __kl_divergence(p, q):
    """
    Calculate KL-Divergence between P and Q, with epsilon to avoid divide by zero.
    :param p: Numpy array p distribution.
    :param q: Numpy array q distribution.
    :return: KL-Divergence score.
    """
    epsilon = 0.0000001  # Epsilon is used here to avoid P or Q is equal to 0. "
    p = p + epsilon
    q = q + epsilon

    return np.sum(p * np.log(p / q))


def NDKL(ranking_df, item_group_dict, fair_rep):
    """
    Calculate Normalized Discounted KL-Divergence Score (Geyik et al.) where chunks are num group increments.
    :param ranking_df: Pandas dataframe of ranking(s).
    :param item_group_dict: Dictionary of items (keys) and their group membership (values).
    :param fair_rep EQUAL or PROPORTIONAL
    :return: NDKL value.
    """
    if len(ranking_df.columns) > 1:
        raise AssertionError("NDKL can only be calculated on a single ranking.")

    single_ranking = ranking_df[ranking_df.columns[0]]  # isolate ranking
    single_ranking = np.array(
        single_ranking[~pd.isnull(single_ranking)]
    )  # drop any NaNs

    group_ids = [item_group_dict[c] for c in single_ranking]
    unique_grps = np.unique(list(item_group_dict.values()))
    group_ids = np.asarray( 
        [np.argwhere(unique_grps == grp_of_item)[0, 0] for grp_of_item in group_ids]
    )
    all_groups = np.asarray(list(item_group_dict.values()))
    all_group_ids = np.asarray(
        [np.argwhere(unique_grps == grp_of_item)[0, 0] for grp_of_item in all_groups]
    )
    num_groups = len(unique_grps)
    num_items = len(single_ranking)

    if fair_rep == 'PROPORTIONAL':
        #dr = __distributions(group_ids, num_groups)  # Distributions per group
        dr = __distributions(all_group_ids, num_groups)  # Distributions per group
    if fair_rep == 'EQUAL':
        dr = np.tile((1/(num_groups)), num_groups) #for more equal chunks
      # Array of Z scores

    chunks = list(range(num_groups, num_items + num_groups,num_groups))
    Z = __Z_Vector(len(chunks))
    vals = []
    for ind in range(0, len(list(range(num_groups, num_items+ num_groups,num_groups)))):
        end_prefix = chunks[ind]
        P = __distributions(group_ids[0 : end_prefix], num_groups)
        kl = __kl_divergence(P, dr)
        vals.append(Z[ind]*kl)
    result = (1 / np.sum(Z)) * np.sum(vals)
    return result


def NDKL_allpos(ranking_df, item_group_dict, fair_rep):
    """
    Calculate Normalized Discounted KL-Divergence Score (Geyik et al.).
    :param ranking_df: Pandas dataframe of ranking(s).
    :param item_group_dict: Dictionary of items (keys) and their group membership (values).
    :return: NDKL value.
    """
    if len(ranking_df.columns) > 1:
        raise AssertionError("NDKL can only be calculated on a single ranking.")

    single_ranking = ranking_df[ranking_df.columns[0]]  # isolate ranking
    single_ranking = np.array(
        single_ranking[~pd.isnull(single_ranking)]
    )  # drop any NaNs

    group_ids = [item_group_dict[c] for c in single_ranking]
    unique_grps = np.unique(list(item_group_dict.values()))
    group_ids = np.asarray(
        [np.argwhere(unique_grps == grp_of_item)[0, 0] for grp_of_item in group_ids]
    )
    all_groups = np.asarray(list(item_group_dict.values()))
    all_group_ids = np.asarray(
        [np.argwhere(unique_grps == grp_of_item)[0, 0] for grp_of_item in all_groups]
    )
    num_groups = len(unique_grps)
    num_items = len(single_ranking)

    if fair_rep == 'PROPORTIONAL':
        #dr = __distributions(group_ids, num_groups)  # Distributions per group
        dr = __distributions(all_group_ids, num_groups)  # Distributions per group
    if fair_rep == 'EQUAL':
        dr = np.tile((1/(num_groups)), num_groups) #for more equal chunks
    Z = __Z_Vector(num_items)  # Array of Z scores

    #Eq. 4 in Geyik et al.
    return (1 / np.sum(Z)) * np.sum(
        [
            Z[i]
            * __kl_divergence(__distributions(group_ids[0 : i + 1], num_groups), dr)
            for i in range(0, num_items)
        ]
    )


def __distributions(ranking, num_groups):
    """
    Calculate the proportion of each group
    :param ranking: Numpy array of group id represented in the ranking.
    :param num_groups: Int, number of distinct groups
    :return: Numpy array of each group's proportion.
    """
    return np.array(
        [((ranking == i).sum()) / len(ranking) for i in range(0, num_groups)]
    )


def __Z_Vector(k):
    """
    Calculate Z score
    :param k: Int, position of ranking.
    :return: Numpy array of Z values.
    """
    return 1 / np.log2(np.array(range(0, k)) + 2)