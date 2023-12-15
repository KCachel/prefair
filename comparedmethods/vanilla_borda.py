import numpy as np
import pandas as pd

def BORDA(profile_df, candidate_ids, k_cnt):
    """
    BORDA preference aggregation.
    :param profile_df: Dataframe of preference profile
    :param considered_candidates:  Numpy array of canidates ids
    :param k_cnt: length of consensus ranking
    :return:Dataframe of consensus ranking
    """
    num_rankings = len(profile_df.columns)
    borda_scores = {key: 0 for key in candidate_ids}
    num_items = len(candidate_ids) # use for borda count with same scores per ranking
    for r in range(0, num_rankings):
        single_ranking = profile_df[profile_df.columns[r]]  # isolate ranking
        single_ranking = np.array(
            single_ranking[~pd.isnull(single_ranking)]
        )  # drop any NaNs
        points_at_pos = list(range(num_items - 1, -1, -1))
        for item_pos in range(0, len(single_ranking)):
            item = single_ranking[item_pos]
            borda_scores[item] +=points_at_pos[item_pos]

    ids = list(borda_scores.keys())
    new_scores = [borda_scores[cand] for cand in ids]
    scores, ordered_candidate_ids = zip(*sorted(zip(new_scores, ids), reverse=True))
    return pd.DataFrame(ordered_candidate_ids[0:k_cnt])