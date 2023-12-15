from src.groupaware_stv import *
import src.imputation as imp
import src.getset_representation as getset



def preFAIR(profile_df, dataset_df, candidates_col, sa_col, fair_rep, k_cnt):
    """
    PreFAIR Fair Preference Aggregation
    :param profile_df: Dataframe of preference profile
    :param dataset_df: Dataframe of candidate dataset
    :param candidates_col: Column in dataset_df with candidate ids/names
    :param sa_col: Column in dataset_df with group information
    :param fair_rep: EQUAL or PROPORTIONAL
    :param k_cnt: length of consensus ranking
    :return: Dataframe consensus ranking
    """
    #Step 1: Calculate current representation

    item_group_dict, pool_group_cnt_dict, ranked_item_group_dict, profile_group_cnt_dict = getset.get_representation(
        profile_df, dataset_df, candidates_col, sa_col)

    # Step 2: Set fair representation
    group_constraints = getset.set_representation(pool_group_cnt_dict, profile_group_cnt_dict, fair_rep, k_cnt)

    #Step 3: Imputation
    diff = np.asarray(list(profile_group_cnt_dict.values())) - np.asarray(list(group_constraints.values()))
    if np.any(diff < 0):
        #Not enough candidates have to impute
        features_df = dataset_df.drop(columns=[sa_col]) #Drop sensative attribute
        completed_profile_df = imp._imputate_candidates(profile_df, features_df, candidates_col)
    else:
        completed_profile_df = profile_df


    #Step 4: Group-aware STV
    consensus = group_aware_single_transferable_vote(completed_profile_df, item_group_dict, group_constraints)
    return pd.DataFrame(consensus)