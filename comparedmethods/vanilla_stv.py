import numpy as np
import pandas as pd


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
        # num_items = len(single_ranking) # use for borda count with different scores per ranking
        points_at_pos = list(range(num_items - 1, -1, -1))
        for item_pos in range(0, len(single_ranking)):
            item = single_ranking[item_pos]
            borda_scores[item] += points_at_pos[item_pos]

    return borda_scores


def single_transferable_vote(profile_df, profile_item_group_dict, seats):
    """
    Perform single transferable voting
    :param preference_df: Dataframe of preference profile
    :param profile_item_group_dict: Dictionary where candidates are keys and values are their groups
    :param seats: int number to elected
    :return: candidates_elected
    """
    num_rankings = len(profile_df.columns)
    considered_candidates = list(profile_item_group_dict.keys())
    tiebreak_scores = _preprocess_for_tiebreaks(profile_df, considered_candidates)
    num_candidates = len(considered_candidates)
    quota = np.floor(num_rankings / (seats + 1)) + 1  # droop quota
    vote_dict = {key: 0 for key in considered_candidates}  # initialize votes per candidate
    candidates_elected = []

    # Count first preferences
    first_prefs = profile_df.iloc[0].values
    candidates, counts = np.unique(first_prefs, return_counts=True)
    vote_dict = _tally_votes(vote_dict, candidates, counts)

    while len(candidates_elected) < seats:

        # Check if considered candidates need to be automatically elected
        if len(candidates_elected) + len(considered_candidates) == seats:
            candidates_elected = candidates_elected + considered_candidates

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
                candidates_elected.append(just_elect_cand)

                # Check if we are done (i.e. seats met)
                if len(candidates_elected) == seats:
                    print("Election Complete! The following candidates were chosen: ", candidates_elected)
                    return pd.DataFrame(candidates_elected)

                # Otherwise remove the candidate from the considered candidates
                considered_candidates.remove(just_elect_cand)

                # Track surplus
                if (just_elect_votenum - quota) != 0:
                    surplus_cands.append(just_elect_cand)
                    surplus_votes.append(just_elect_votenum)
                else:
                    # If no surplus remove the candidates from the vote_dict
                    del vote_dict[just_elect_cand]

            # Remove elected candidates from preference profile? Maybe don't need to do this

            # Transfer surplus if any, otherwise eliminate candidates & Remove elected candidates from votes dict
            if len(surplus_cands) > 0:
                # Transfer surplus
                vote_dict, considered_candidates, seats, profile_df, quota, candidates_elected = _transfer_surplus(
                    vote_dict, considered_candidates, seats, profile_df, quota,
                    candidates_elected, surplus_cands, surplus_votes)

        # Eliminate last place candidate
        else:
            vote_dict, considered_candidates = _elimination(vote_dict, considered_candidates, seats, profile_df,
                                                            quota, candidates_elected, tiebreak_scores)

    return pd.DataFrame(candidates_elected)

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
    # Transfer surplus
    for cand, votenum in zip(surplus_cands, surplus_votes):
        surplus = votenum - quota
        next_cands, pref_num = _next_preferences(considered_candidates, preference_df, cand)
        # Remove elected candidates from vote_dict
        del vote_dict[cand]
        # Distribute the surplus
        for next_cand, pref_weight in zip(next_cands, pref_num):
            #vote_dict[next_cand] = surplus / pref_weight
            vote_dict[next_cand] += surplus/np.sum(pref_num)*pref_weight

    return vote_dict, considered_candidates, seats, preference_df, quota, candidates_elected


def _next_preferences(considered_candidates, preference_df, cand):
    """
    Return the next preference after candidate cand
    :param considered_candidates: list of possible candidates to be elected
    :param preference_df: Dataframe of preference profile
    :param cand: candidate
    :return: Dictionary of candidates (keys) and values (votes)
    """
    next_cands = {}  # initialize num preferences per candidate
    num_rankings = len(preference_df.columns)
    for r in range(0, num_rankings):
        single_ranking = np.array(preference_df[preference_df.columns[r]])  # isolate ranking
        if (cand in single_ranking) == True:
            surplus_cand_indx = np.argwhere(single_ranking == cand).flatten()[0]
            next_indx = surplus_cand_indx + 1
            while (next_indx < len(single_ranking)):
                if single_ranking[next_indx] in considered_candidates:
                    # valid next preference so add it
                    if single_ranking[next_indx] in next_cands:
                        next_cands[single_ranking[next_indx]] += 1
                    else:
                        next_cands[single_ranking[next_indx]] = 1
                    break
                else:
                    next_indx += 1
    return list(next_cands.keys()), list(next_cands.values())


def _elimination(vote_dict, considered_candidates, seats, preference_df, quota, candidates_elected, tiebreak_scores):
    """
    Eliminate candidates
    :param vote_dict: Dictionary of candidates (keys) and their votes (values)
    :param considered_candidates: Candidates that can be elected
    :param seats: k count (length of consensus ranking)
    :param preference_df: Dataframe of preference profile
    :param quota: droop quota
    :param candidates_elected: list of candidates elected
    :param tiebreak_scores: Dictionary of canidates (keys) and tiebreak scores (values)
    :return: vote_dict, considered_candidates
    """
    # Eliminate
    possible_candidates = np.array(list(vote_dict.keys()))
    possible_votes = list(vote_dict.values())
    lowest_vote_cands = possible_candidates[list(possible_votes == np.min(possible_votes))]
    min_score = np.inf
    for c in lowest_vote_cands:
        if tiebreak_scores[c] < min_score:
            min_score = tiebreak_scores[c]
            eliminate_c = c

    # get votes that are transferred
    votes_transfereed_from_c = vote_dict[eliminate_c]
    # remove candidate from considered candidates
    considered_candidates.remove(eliminate_c)
    # Remove eliminated candidates from vote_dict
    del vote_dict[eliminate_c]
    if len(considered_candidates) + len(candidates_elected) == seats:
        # all remaining get elected
        return vote_dict, considered_candidates

    # if there are transferable votes get next preferences preferences
    if votes_transfereed_from_c > 0:
        next_cands, pref_num = _next_preferences(considered_candidates, preference_df, eliminate_c)

        # Distribute the surplus
        for next_cand, pref_weight in zip(next_cands, pref_num):
            #vote_dict[next_cand] = votes_transfereed_from_c / pref_weight
            vote_dict[next_cand] += votes_transfereed_from_c / np.sum(pref_num) * pref_weight

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

