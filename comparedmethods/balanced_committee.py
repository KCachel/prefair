"""
References: https://github.com/huanglx12/Balanced-Committee-Election/blob/master/balanced_committee_election.pdf

"""
import numpy as np
import gurobipy as gp
from gurobipy import GRB
import pandas as pd
import iteround


def get_borda_scores(preference_df, candidate_ids):
    """
    Calculate borda score per item.
    :param profile_df: Dataframe of preference profile
    :param considered_candidates:  Numpy array of canidates ids
    :return: Dictionary of borda scores where candidates are keys and scores are values
    """
    num_rankings = len(preference_df.columns)
    borda_scores = {key: 0 for key in candidate_ids}
    num_items = len(candidate_ids) # use for borda count with same scores per ranking
    for r in range(0, num_rankings):
        single_ranking = preference_df[preference_df.columns[r]]  # isolate ranking
        single_ranking = np.array(
            single_ranking[~pd.isnull(single_ranking)]
        )  # drop any NaNs
        # num_items = len(single_ranking) # use for borda count with different scores per ranking
        points_at_pos = list(range(num_items - 1, -1, -1))
        for item_pos in range(0, len(single_ranking)):
            item = single_ranking[item_pos]
            borda_scores[item] +=points_at_pos[item_pos]

    ids = list(borda_scores.keys())
    new_scores = [borda_scores[cand] for cand in ids]
    scores, ordered_candidate_ids = zip(*sorted(zip(new_scores, ids), reverse=True))
    return ordered_candidate_ids, scores


def get_bounds(profile_item_group_dict, fair_rep, k):
    """
    Get upper and lower bound limits.
    :param profile_item_group_dict: Dictionary of groups (keys) and counts (values)
    :param fair_rep: EQUAL or PROPORTIONAL
    :param k: length of consensus
    :return: dictionary of groups (keys) and counts (vals)
    """
    grp_ids, total_grp_cnts = np.unique(list(profile_item_group_dict.values()), return_counts = True)
    grp_n = len(grp_ids)  # num groups
    if fair_rep == "PROPORTIONAL":
        #Use the pool proportion
        prop = np.asarray(total_grp_cnts)/ np.sum(total_grp_cnts)
        per_grp = iteround.saferound(prop*k, 0)
    if fair_rep == "EQUAL":
        # make all k/number of groups
        per_grp = [k // grp_n + (1 if x < k % grp_n else 0) for x in range(grp_n)]
        if _check_grp_cnts(per_grp, total_grp_cnts) == False:
            # make all groups as big as smallest group
            print(
                "The k value you selected cannot be achieve with equal representation, so each group will have as many members as the smallest group.")
            per_grp = [np.min(total_grp_cnts[np.nonzero(total_grp_cnts)])] * grp_n
    return dict(zip(list(grp_ids), per_grp))


def _check_grp_cnts(per_grp, total_grp_cnts):
    difs = [per_grp[i] - total_grp_cnts[i] for i in range(0, len(per_grp))]
    return np.all(np.asarray(difs) < 0)


def balanced_committee(profile_df, profile_item_group_dict, fair_rep, k_cnt):
    """
    Balancde Committee multiwinner voting from Celis et al. IJCAI'17
    :param profile_df: Dataframe of preference profile
    :param candidate_ids: List of candidates
    :param profile_item_group_dict: Dictionary of candidates (keys) and groups (values)
    :param k_cnt: length of consensus
    :return: consensus
    """
    #BORDA
    candidates, borda_scores = get_borda_scores(profile_df, list(profile_item_group_dict.keys()))
    item_strings = [str(var) for var in candidates]
    group_strings = [str(profile_item_group_dict[var]) for var in candidates]
    item_grpid_combo_strings = list(zip(item_strings, group_strings))
    bound_dict = get_bounds(profile_item_group_dict, fair_rep, k_cnt)

    num_groups = len(list(bound_dict.keys()))

    # Declare and initialize model
    m = gp.Model('BalC')

    x = m.addVars(item_grpid_combo_strings, name="cand", vtype=gp.GRB.BINARY)

    #
    # k item constraint
    m.addConstr((x.sum('*','*') == k_cnt), name = 'committee_size')

    #constraints for bounds
    for grp_id, lb in bound_dict.items():
        m.addConstr((x.sum('*', str(grp_id)) >= lb), name ='group_bounds')
        m.write('balcomm.lp')

    weights = {}
    iter = 0
    for (i, g) in item_grpid_combo_strings:
        weights[(i,g)] = borda_scores[iter]
        iter += 1

    candidates, scores = gp.multidict(weights)
    # objective function
    print("setting objective function.....")
    m.setObjective(x.prod(scores), GRB.MAXIMIZE)

    # Save model for inspection
    #m.write('balcomm.lp')

    m.optimize()
    # Display optimal values of decision variables
    # print("Printing variables....")
    # for v in m.getVars():
    #     if v.x > 1e-6:
    #         print(v.varName, v.x)

    committee_vars = [var.varName for var in m.getVars() if var.x == 1 and var.varName.startswith('cand')]
    committee_items = [(var.split(',')[0]).split('[')[1] for var in committee_vars]
    committee_items = np.asarray([i for i in committee_items])
    return pd.DataFrame(committee_items)








