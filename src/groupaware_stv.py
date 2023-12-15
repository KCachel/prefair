import numpy as np
import pandas as pd
import itertools


def _preprocess_for_tiebreaks(preference_df, considered_candidates):
    """
    Get Borda scores for tie-breaking.
    :param preference_df: Dataframe of preference profile
    :param considered_candidates:  Numpy array of canidates ids
    :return: Dictionary of borda scores where candidates are keys and scores are values
    """
    num_rankings = len(preference_df.columns)
    borda_scores = {key: 0 for key in considered_candidates}
    num_items = len(considered_candidates)  # use for borda count with same scores per ranking
    for r in range(0, num_rankings):
        single_ranking = preference_df[preference_df.columns[r]]  # isolate ranking
        single_ranking = np.array(
            single_ranking[~pd.isnull(single_ranking)]
        )  # drop any NaNs
        # num_items = len(single_ranking) # use for borda coutn with different scores per ranking
        points_at_pos = list(range(num_items - 1, -1, -1))
        for item_pos in range(0, len(single_ranking)):
            item = single_ranking[item_pos]
            borda_scores[item] += points_at_pos[item_pos]

    return borda_scores

def group_aware_single_transferable_vote(preference_df, item_group_dict, group_constraints):
    """
    Perform fair consensus ranking from preference profile.
    :param preference_df: Dataframe of preference profile
    :param item_group_dict: Dictionary where candidates are keys and values are their groups
    :param group_constraints: Dictionary of groups = keys and values are count per group
    :return: candidates_elected
    """
    seats = np.sum(list(group_constraints.values()))
    num_rankings = len(preference_df.columns)
    considered_candidates = list(item_group_dict.keys())
    group_considered_candidates = _get_considered_by_group(item_group_dict)
    tiebreak_scores = _preprocess_for_tiebreaks(preference_df, considered_candidates)
    quota = np.floor(num_rankings/(seats + 1)) + 1 #droop quota
    vote_dict = {key: 0 for key in considered_candidates} #initialize votes per candidate
    candidates_elected = []

    #Count first preferences
    first_prefs = preference_df.iloc[0].values
    candidates, counts = np.unique(first_prefs, return_counts=True)
    vote_dict = _tally_votes(vote_dict, candidates, counts)


    while len(candidates_elected) < seats:

        # Check if considered candidates need to be automatically elected
        if len(candidates_elected) + len(considered_candidates) == seats:
            candidates_elected = candidates_elected + considered_candidates
            candidates_elected = _fairbuckets(candidates_elected, item_group_dict)
            print("Prefair STV Complete! The following candidates were chosen: ", candidates_elected)
            return candidates_elected

        # Check if a group is done being elected, if so transfer their votes
        elim_grps = []
        for grp, seats_left in group_constraints.items():
            # check if done because we need to automatically elect the remaining candidates
            if len(group_considered_candidates[grp]) == seats_left:
                #we need to automatically elect the remaining candidates
                just_elected_cands = group_considered_candidates[grp]
                just_elected_votes = [vote_dict[c] for c in just_elected_cands]

                # Sort candidates by number of votes
                just_elected_votes, just_elected_cands = zip(
                    *sorted(zip(just_elected_votes, just_elected_cands), reverse=True))
                # Add each elected candidate in order of votes
                for just_elect_votenum, just_elect_cand in zip(just_elected_votes, just_elected_cands):
                    # Elect candidate
                    grp_just_elect_cand = item_group_dict[just_elect_cand]
                    candidates_elected.append(just_elect_cand)
                    # Remove the candidate from the considered candidates
                    considered_candidates.remove(just_elect_cand)
                    group_constraints[grp_just_elect_cand] -= 1
                    group_considered_candidates[grp_just_elect_cand].remove(just_elect_cand)
                    del vote_dict[just_elect_cand]
                # Check if we are done (i.e. seats met)
                if len(candidates_elected) == seats:
                    candidates_elected = _fairbuckets(candidates_elected, item_group_dict)
                    print("Prefair STV Complete! The following candidates were chosen: ", candidates_elected)
                    return candidates_elected

                seats_left  = group_constraints[grp]


            if seats_left == 0:
                elim_grps.append(grp)

        if len(elim_grps) > 0: #we have groups to eliminate
            #Remove all eliminated groups at once from considered candidates
            for group_elim in elim_grps:
                # remove all group members from considered_candidates to help get next preferences
                for c in group_considered_candidates[group_elim]:
                    considered_candidates.remove(c)
            #Elimante each group and transfer their surplus
            for group_elim in elim_grps:
                vote_dict, considered_candidates, preference_df, group_considered_candidates = eliminate_group(vote_dict,
                                considered_candidates, preference_df, group_considered_candidates,
                                group_elim)
                del group_constraints[group_elim]

        # Elect if you can
        elif np.any(list(vote_dict.values()) >= quota):
            # Candidates are elected (at least one candidate has votes equal or greater than the quota
            cands = np.array(list(vote_dict.keys()))
            votes = np.array(list(vote_dict.values()))
            just_elected_cands = cands[votes >= quota]
            just_elected_votes = votes[votes >= quota]

            # Sort candidates by number of votes
            just_elected_votes, just_elected_cands = zip(
                *sorted(zip(just_elected_votes, just_elected_cands), reverse=True))
            # Add each elected candidate in order of votes
            surplus_cands = []
            surplus_votes = []
            for just_elect_votenum, just_elect_cand in zip(just_elected_votes, just_elected_cands):

                # Elect candidate
                grp_just_elect_cand = item_group_dict[just_elect_cand]
                if group_constraints[grp_just_elect_cand] > 0:
                    candidates_elected.append(just_elect_cand)
                else: #you can no longer elect candidates from this group
                    break


                # Check if we are done (i.e. seats met)
                if len(candidates_elected) == seats:
                    candidates_elected = _fairbuckets(candidates_elected, item_group_dict)
                    print("Prefair STV Complete! The following candidates were chosen: ", candidates_elected)
                    return candidates_elected

                # Otherwise remove the candidate from the considered candidates
                considered_candidates.remove(just_elect_cand)
                group_constraints[grp_just_elect_cand] -= 1
                group_considered_candidates[grp_just_elect_cand].remove(just_elect_cand)


                # Track surplus
                if (just_elect_votenum - quota) != 0:
                    surplus_cands.append(just_elect_cand)
                    surplus_votes.append(just_elect_votenum)
                else:
                    # If no surplus remove the candidates from the vote_dict
                    del vote_dict[just_elect_cand]


            # Transfer surplus if any, otherwise eliminate candidates & Remove elected candidates from votes dict
            if len(surplus_cands) > 0:
                # Transfer surplus
                vote_dict, considered_candidates, seats, preference_df, quota, candidates_elected = _transfer_surplus(
                    vote_dict, considered_candidates, seats, preference_df, quota,
                    candidates_elected, surplus_cands, surplus_votes)

        #Eliminate last place candidate
        else:
            vote_dict, considered_candidates = _elimination(vote_dict, considered_candidates, seats, preference_df,
                                                            candidates_elected, tiebreak_scores, item_group_dict,
                                                            group_constraints, group_considered_candidates)

    candidates_elected = _fairbuckets(candidates_elected, item_group_dict)
    return candidates_elected


def eliminate_group(vote_dict, considered_candidates, preference_df, group_considered_candidates, group_elim):
    """
    When you can no longer elected candidates from this group transfer their votes.
    :param vote_dict: Dictionary of candidates (keys) and their votes (values)
    :param considered_candidates: Candidates that can be elected
    :param preference_df: Dataframe of preference profile
    :param group_considered_candidates: Dictionary of groups (keys) and their candidates that can be elected (values)
    :param group_elim: Group to eliminate
    :return: vote_dict, considered_candidates, preference_df, group_considered_candidates
    """
    #for every group member get votes that can be transferred
    for eliminated_c in group_considered_candidates[group_elim]:
        votes_trans_from_c = vote_dict[eliminated_c]

        # Remove eliminated candidates from vote_dict
        del vote_dict[eliminated_c]

        # if there are transferable votes get next preferences
        if votes_trans_from_c > 0:
            next_cands, pref_num = _next_preferences(considered_candidates, preference_df, eliminated_c)

            # Distribute the surplus
            for next_cand, pref_weight in zip(next_cands, pref_num):
                vote_dict[next_cand] = votes_trans_from_c / pref_weight
    del group_considered_candidates[group_elim]
    return vote_dict, considered_candidates, preference_df, group_considered_candidates


def _transfer_surplus(vote_dict, considered_candidates, seats, preference_df, quota,
                      candidates_elected, surplus_cands, surplus_votes):
    """
    Transfer surplus votes
    :param vote_dict: Dictionary of candidates (keys) and their votes (values)
    :param considered_candidates: Candidates that can be elected
    :param seats: k count (length of consensus ranking)
    :param preference_df: Dataframe of preference profile
    :param quota: droop quota
    :param candidates_elected: list of candidates elected
    :param surplus_cands: list of candidates with surplus
    :param surplus_votes: list of surplus votes corresponding to surplus_cands
    :return: vote_dict, considered_candidates, seats, preference_df, quota, candidates_elected
    """

    #Transfer surplus
    for cand, votenum in zip(surplus_cands, surplus_votes):
        surplus = votenum - quota
        next_cands, pref_num = _next_preferences(considered_candidates, preference_df, cand)
        # Remove elected candidates from vote_dict
        del vote_dict[cand]
        #Distribute the surplus
        for next_cand, pref_weight in zip(next_cands, pref_num):
            vote_dict[next_cand] = surplus/pref_weight


    return vote_dict, considered_candidates, seats, preference_df, quota, candidates_elected

def _next_preferences(considered_candidates, preference_df, cand):
    """
    Return the next preference after candidate cand
    :param considered_candidates: list of possible candidates to be elected
    :param preference_df: Dataframe of preference profile
    :param cand: candidate
    :return: Dictionary of candidates (keys) and values (votes)
    """
    next_cands = { } #initialize num preferences per candidate
    num_rankings = len(preference_df.columns)
    for r in range(0, num_rankings):
        single_ranking = np.array(preference_df[preference_df.columns[r]])  # isolate ranking
        if cand in single_ranking:
            surplus_cand_indx = np.argwhere(single_ranking == cand).flatten()[0]
            next_indx = surplus_cand_indx + 1
            while(next_indx < len(single_ranking)):
                if single_ranking[next_indx] in considered_candidates:
                    #valid next preference so add it
                    if single_ranking[next_indx] in next_cands:
                        next_cands[single_ranking[next_indx]] += 1
                    else:
                        next_cands[single_ranking[next_indx]] = 1
                    break
                else:
                    next_indx += 1
    return list(next_cands.keys()), list(next_cands.values())


def _elimination(vote_dict, considered_candidates, seats, preference_df, candidates_elected, tiebreak_scores,
                 item_group_dict, group_constraints, group_considered_candidates):
    """
    Eliminate candidates
    :param vote_dict: Dictionary of candidates (keys) and their votes (values)
    :param considered_candidates: Candidates that can be elected
    :param seats: k count (length of consensus ranking)
    :param preference_df: Dataframe of preference profile
    :param quota: droop quota
    :param candidates_elected: list of candidates elected
    :param tiebreak_scores: Dictionary of canidates (keys) and tiebreak scores (values)
    :param item_group_dict: Dictionary where candidates are keys and values are their groups
    :param group_constraints: Dictionary of groups = keys and values are count per group
    :param group_considered_candidates: Dictionary of groups (keys) and their candidates that can be elected (values)
    :return: vote_dict, considered_candidates
    """
    # Eliminate
    possible_candidates = np.array(list(vote_dict.keys()))
    possible_votes = list(vote_dict.values())
    lowest_vote_cands = possible_candidates[list(possible_votes == np.min(possible_votes))]
    min_score = np.Inf
    eliminate_c = None
    for c in lowest_vote_cands:
        group_c = item_group_dict[c]
        potential_seats = group_constraints[group_c]
        num_remaining_group = len(group_considered_candidates[group_c])
        if tiebreak_scores[c] < min_score and (num_remaining_group - 1) >= potential_seats:
            min_score = tiebreak_scores[c]
            eliminate_c = c
            eliminate_c_group = group_c

    if eliminate_c is None: #Cannot eliminate someone
        return vote_dict, considered_candidates
    #get votes that are transferred
    votes_transfereed_from_c = vote_dict[eliminate_c]
    #remove candidate from considered candidates
    considered_candidates.remove(eliminate_c)
    # Remove eliminated candidates from vote_dict
    del vote_dict[eliminate_c]
    # Remove eliminated candidate from group considered candidates
    group_considered_candidates[eliminate_c_group].remove(eliminate_c)
    if len(considered_candidates) + len(candidates_elected) == seats:
        #all remaining get elected
        return vote_dict, considered_candidates

    #if there are transferable votes get next preferences preferences
    if votes_transfereed_from_c > 0:
        next_cands, pref_num = _next_preferences(considered_candidates, preference_df, eliminate_c)

        # Distribute the surplus
        for next_cand, pref_weight in zip(next_cands, pref_num):
            vote_dict[next_cand] = votes_transfereed_from_c / pref_weight

    return vote_dict, considered_candidates


def _tally_votes(vote_dict, candidates, counts):
    """
    Calculate votes in vote dict
    :param vote_dict: Dictionary of candidates (keys) and their votes (values)
    :param candidates: list of candidates
    :param counts: counts
    :return: updated vote_dict
    """
    for cand, vote_num in zip(candidates, counts):
        vote_dict[cand] += vote_num
    return vote_dict


def _get_considered_by_group(item_group_dict):
    """
    Create dictionary of groups (keys) and their candidates that can be elected (values)
    :param item_group_dict: Dictionary where candidates are keys and values are their groups
    :return: group_considered_candidates
    """
    group_considered_candidates = {}
    for cand, group in item_group_dict.items():
        if group in group_considered_candidates: # group is already in dictionary
            group_considered_candidates[group] = group_considered_candidates[group] + [cand]
        else:
            group_considered_candidates[group] = [cand]
    return group_considered_candidates

def _fairbuckets(candidates_elected, item_group_dict):
    """
    Ensure output satisfies rank fairness by arranging the candidates into buckets.
    :param candidates_elected: list of candidates
    :param item_group_dict: Dictionary where candidates are keys and values are their groups
    :return: list of candidates
    """
    group_ids = [item_group_dict[c] for c in candidates_elected]
    groups = pd.unique(group_ids) #preserve order
    grp_cnt = [group_ids.count(grp) for grp in groups]
    candidate_group_dict = dict(zip(candidates_elected, group_ids))
    assignments = []
    bucket_num = int(np.ceil(len(group_ids) / len(groups)))
    for grp_indx in range(0, len(groups)):
        cnt = grp_cnt[grp_indx]
        assignment = [cnt // bucket_num + (1 if x < cnt % bucket_num else 0) for x in range(bucket_num)]
        if assignment[0] > 1:
            # reverse it so that 1 is first
            assignment = assignment[::-1]
        assignments.append(assignment)
    buckets = [list(x) for x in zip(*assignments)]
    named_buckets = []
    for bucket in buckets:
        named_bucket = []
        for i in range(0, len(groups)):
            count = bucket[i]
            grp = groups[i]
            named_bucket.append([grp]*count)
        named_buckets.append(list(itertools.chain(*named_bucket)))
    flat_buckets = list(itertools.chain(*named_buckets))
    for cand in candidates_elected:
        curr_grp = candidate_group_dict[cand]
        update_indx = flat_buckets.index(curr_grp)
        flat_buckets[update_indx] = cand
    return flat_buckets


