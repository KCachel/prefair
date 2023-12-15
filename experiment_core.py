#script for experimental_core
import comparedmethods as cr
import src as src
import FairRankTune as frt
import pandas as pd
import numpy as np

def workflow(profile_df, dataset_df, candidates_col, sa_col, fair_rep, rank_fairness, k_cnt,
             profile_item_group_dict, candidate_ids, dataset_name, csv_name,epira_bnd):


    #initialize data collectors
    method = []
    dataset = []
    kl_div_pool_cr = []
    kl_div_pool_profile = []
    fair_rep_values = []
    NDKL_values = []
    NDKL_ranked = []
    avg_sat_10 = []
    avg_sat_20 = []
    avg_sat_30 = []
    avg_sat_40 = []
    avg_sat_50 = []
    result = []
    pool_grp_cnts = []
    profile_grp_cnts = []
    cr_grp_cnts = []

    #necessary structures
    _, pool_group_cnt_dict, _, profile_group_cnt_dict = src.get_representation(profile_df, dataset_df,
                                                                               candidates_col, sa_col)
    pool_item_group_dict = src.get_item_group_dict(dataset_df, candidates_col, sa_col)

    #stv
    cr_stv = cr.single_transferable_vote(profile_df, profile_item_group_dict, k_cnt)
    assess_item_group_dict = src.get_item_group_dict_for_ranking(cr_stv, dataset_df, candidates_col, sa_col)
    assess_group_cnt_dict = src.rankingdf_to_proportions(cr_stv, pool_item_group_dict)
    method.append('STV')
    dataset.append(dataset_name)
    kl_div_pool_cr.append(src.KL_div_pool_assess_set(pool_group_cnt_dict, assess_group_cnt_dict, fair_rep))
    kl_div_pool_profile.append(src.KL_div_pool_assess_set(pool_group_cnt_dict, profile_group_cnt_dict, fair_rep))
    fair_rep_values.append(src.fair_representation(pool_group_cnt_dict, assess_group_cnt_dict, fair_rep))
    NDKL_values.append(src.NDKL(cr_stv, pool_item_group_dict, 'EQUAL'))
    NDKL_ranked.append(src.NDKL(cr_stv, assess_item_group_dict, 'EQUAL'))
    avg_sat_10.append(src.average_satisfaction_percentage(profile_df, .1, cr_stv, .1))
    avg_sat_20.append(src.average_satisfaction_percentage(profile_df, .1, cr_stv, .2))
    avg_sat_30.append(src.average_satisfaction_percentage(profile_df, .1, cr_stv, .3))
    avg_sat_40.append(src.average_satisfaction_percentage(profile_df, .1, cr_stv, .4))
    avg_sat_50.append(src.average_satisfaction_percentage(profile_df, .1, cr_stv, .5))
    result.append(cr_stv.iloc[:,0].values.tolist())
    pool_grp_cnts.append(pool_group_cnt_dict)
    profile_grp_cnts.append(profile_group_cnt_dict)
    cr_grp_cnts.append(assess_group_cnt_dict)

    # mc4
    cr_mc4 = cr.mc4(profile_df, k_cnt)
    assess_item_group_dict = src.get_item_group_dict_for_ranking(cr_mc4, dataset_df, candidates_col, sa_col)
    assess_group_cnt_dict = src.rankingdf_to_proportions(cr_mc4, pool_item_group_dict)
    method.append('MC4')
    dataset.append(dataset_name)
    kl_div_pool_cr.append(src.KL_div_pool_assess_set(pool_group_cnt_dict, assess_group_cnt_dict, fair_rep))
    kl_div_pool_profile.append(src.KL_div_pool_assess_set(pool_group_cnt_dict, profile_group_cnt_dict, fair_rep))
    fair_rep_values.append(src.fair_representation(pool_group_cnt_dict, assess_group_cnt_dict, fair_rep))
    NDKL_values.append(src.NDKL(cr_mc4, pool_item_group_dict, 'EQUAL'))
    NDKL_ranked.append(src.NDKL(cr_mc4, assess_item_group_dict, 'EQUAL'))
    avg_sat_10.append(src.average_satisfaction_percentage(profile_df, .1, cr_mc4, .1))
    avg_sat_20.append(src.average_satisfaction_percentage(profile_df, .1, cr_mc4, .2))
    avg_sat_30.append(src.average_satisfaction_percentage(profile_df, .1, cr_mc4, .3))
    avg_sat_40.append(src.average_satisfaction_percentage(profile_df, .1, cr_mc4, .4))
    avg_sat_50.append(src.average_satisfaction_percentage(profile_df, .1, cr_mc4, .5))
    result.append(cr_mc4.iloc[:, 0].values.tolist())
    pool_grp_cnts.append(pool_group_cnt_dict)
    profile_grp_cnts.append(profile_group_cnt_dict)
    cr_grp_cnts.append(assess_group_cnt_dict)

    #borda
    cr_borda = cr.BORDA(profile_df, candidate_ids, k_cnt)
    assess_item_group_dict = src.get_item_group_dict_for_ranking(cr_borda, dataset_df, candidates_col, sa_col)
    assess_group_cnt_dict = src.rankingdf_to_proportions(cr_borda, pool_item_group_dict)
    method.append('BORDA')
    dataset.append(dataset_name)
    kl_div_pool_cr.append(src.KL_div_pool_assess_set(pool_group_cnt_dict, assess_group_cnt_dict, fair_rep))
    kl_div_pool_profile.append(src.KL_div_pool_assess_set(pool_group_cnt_dict, profile_group_cnt_dict, fair_rep))
    fair_rep_values.append(src.fair_representation(pool_group_cnt_dict, assess_group_cnt_dict, fair_rep))
    NDKL_values.append(src.NDKL(cr_borda, pool_item_group_dict, 'EQUAL'))
    NDKL_ranked.append(src.NDKL(cr_borda, assess_item_group_dict, 'EQUAL'))
    avg_sat_10.append(src.average_satisfaction_percentage(profile_df, .1, cr_borda, .1))
    avg_sat_20.append(src.average_satisfaction_percentage(profile_df, .1, cr_borda, .2))
    avg_sat_30.append(src.average_satisfaction_percentage(profile_df, .1, cr_borda, .3))
    avg_sat_40.append(src.average_satisfaction_percentage(profile_df, .1, cr_borda, .4))
    avg_sat_50.append(src.average_satisfaction_percentage(profile_df, .1, cr_borda, .5))
    result.append(cr_borda.iloc[:,0].values.tolist())
    pool_grp_cnts.append(pool_group_cnt_dict)
    profile_grp_cnts.append(profile_group_cnt_dict)
    cr_grp_cnts.append(assess_group_cnt_dict)

    # EPIRA
    cr_epira = cr.EPIRA(profile_df, candidate_ids, profile_item_group_dict, k_cnt, epira_bnd)
    assess_item_group_dict = src.get_item_group_dict_for_ranking(cr_epira, dataset_df, candidates_col, sa_col)
    assess_group_cnt_dict = src.rankingdf_to_proportions(cr_epira, pool_item_group_dict)
    method.append('EPIRA')
    dataset.append(dataset_name)
    kl_div_pool_cr.append(src.KL_div_pool_assess_set(pool_group_cnt_dict, assess_group_cnt_dict, fair_rep))
    kl_div_pool_profile.append(src.KL_div_pool_assess_set(pool_group_cnt_dict, profile_group_cnt_dict, fair_rep))
    fair_rep_values.append(src.fair_representation(pool_group_cnt_dict, assess_group_cnt_dict, fair_rep))
    NDKL_values.append(src.NDKL(cr_epira, pool_item_group_dict, 'EQUAL'))
    NDKL_ranked.append(src.NDKL(cr_epira, assess_item_group_dict, 'EQUAL'))
    avg_sat_10.append(src.average_satisfaction_percentage(profile_df, .1, cr_epira, .1))
    avg_sat_20.append(src.average_satisfaction_percentage(profile_df, .1, cr_epira, .2))
    avg_sat_30.append(src.average_satisfaction_percentage(profile_df, .1, cr_epira, .3))
    avg_sat_40.append(src.average_satisfaction_percentage(profile_df, .1, cr_epira, .4))
    avg_sat_50.append(src.average_satisfaction_percentage(profile_df, .1, cr_epira, .5))
    result.append(cr_epira.iloc[:, 0].values.tolist())
    pool_grp_cnts.append(pool_group_cnt_dict)
    profile_grp_cnts.append(profile_group_cnt_dict)
    cr_grp_cnts.append(assess_group_cnt_dict)

    # PREFAIR IMPUTATION + EPIRA
    print("IEPIRA")
    item_group_dict, pool_group_cnt_dict, ranked_item_group_dict, profile_group_cnt_dict = src.getset.get_representation(
        profile_df, dataset_df, candidates_col, sa_col)
    features_df = dataset_df.drop(columns=[sa_col])  # Drop sensitive attribute
    completed_profile_df = src.imp._imputate_candidates(profile_df, features_df, candidates_col)
    candidates = np.asarray(list(item_group_dict.keys()))
    iepira_bnd = .9
    cr_iepira = cr.EPIRA(completed_profile_df, candidates, item_group_dict, k_cnt, iepira_bnd)
    assess_item_group_dict = src.get_item_group_dict_for_ranking(cr_iepira, dataset_df, candidates_col, sa_col)
    assess_group_cnt_dict = src.rankingdf_to_proportions(cr_iepira, pool_item_group_dict)
    method.append('PREFAIR(IMPUTE) + EPIRA')
    dataset.append(dataset_name)
    kl_div_pool_cr.append(src.KL_div_pool_assess_set(pool_group_cnt_dict, assess_group_cnt_dict, fair_rep))
    kl_div_pool_profile.append(src.KL_div_pool_assess_set(pool_group_cnt_dict, profile_group_cnt_dict, fair_rep))
    fair_rep_values.append(src.fair_representation(pool_group_cnt_dict, assess_group_cnt_dict, fair_rep))
    NDKL_values.append(src.NDKL(cr_iepira, pool_item_group_dict, 'EQUAL'))
    NDKL_ranked.append(src.NDKL(cr_iepira, assess_item_group_dict, 'EQUAL'))
    avg_sat_10.append(src.average_satisfaction_percentage(profile_df, .1, cr_iepira, .1))
    avg_sat_20.append(src.average_satisfaction_percentage(profile_df, .1, cr_iepira, .2))
    avg_sat_30.append(src.average_satisfaction_percentage(profile_df, .1, cr_iepira, .3))
    avg_sat_40.append(src.average_satisfaction_percentage(profile_df, .1, cr_iepira, .4))
    avg_sat_50.append(src.average_satisfaction_percentage(profile_df, .1, cr_iepira, .5))
    result.append(cr_iepira.iloc[:, 0].values.tolist())
    pool_grp_cnts.append(pool_group_cnt_dict)
    profile_grp_cnts.append(profile_group_cnt_dict)
    cr_grp_cnts.append(assess_group_cnt_dict)

    #RAPF
    kl_div_pool_cr_ = []
    kl_div_pool_profile_ = []
    fair_rep_values_ = []
    NDKL_values_ = []
    NDKL_ranked_ = []
    avg_sat_10_ = []
    avg_sat_20_ = []
    avg_sat_30_ = []
    avg_sat_40_ = []
    avg_sat_50_ = []
    full_sat_ = []
    top_1_indx_ = []
    sat_indx_cnt_top5_ = []
    sat_indx_cnt_top10_ = []
    for i in range(0,10):
        seed = i #for repro
        cr_rapf = cr.RAPF(profile_df, profile_item_group_dict, k_cnt, seed)
        assess_item_group_dict = src.get_item_group_dict_for_ranking(cr_rapf, dataset_df, candidates_col, sa_col)
        assess_group_cnt_dict = src.rankingdf_to_proportions(cr_rapf, pool_item_group_dict)
        kl_div_pool_cr_.append(src.KL_div_pool_assess_set(pool_group_cnt_dict, assess_group_cnt_dict, fair_rep))
        kl_div_pool_profile_.append(src.KL_div_pool_assess_set(pool_group_cnt_dict, profile_group_cnt_dict, fair_rep))
        fair_rep_values_.append(src.fair_representation(pool_group_cnt_dict, assess_group_cnt_dict, fair_rep))
        NDKL_values_.append(src.NDKL(cr_rapf, pool_item_group_dict, 'EQUAL'))
        NDKL_ranked_.append(src.NDKL(cr_rapf, assess_item_group_dict, 'EQUAL'))
        avg_sat_10_.append(src.average_satisfaction_percentage(profile_df, .1, cr_rapf, .1))
        avg_sat_20_.append(src.average_satisfaction_percentage(profile_df, .1, cr_rapf, .2))
        avg_sat_30_.append(src.average_satisfaction_percentage(profile_df, .1, cr_rapf, .3))
        avg_sat_40_.append(src.average_satisfaction_percentage(profile_df, .1, cr_rapf, .4))
        avg_sat_50_.append(src.average_satisfaction_percentage(profile_df, .1, cr_rapf, .5))
        full_sat_.append(src.full_sat_index(profile_df, .1, cr_rapf))
        top_1_indx_.append(src.full_sat_index(profile_df, 1 / k_cnt, cr_rapf))
        sat_indx_cnt_top5_.append(src.satisfaction_index_count(profile_df, 5, cr_rapf, 5, 1))
        sat_indx_cnt_top10_.append(src.satisfaction_index_count(profile_df, 10, cr_rapf, 10, 1))

    method.append('RAPF')
    dataset.append(dataset_name)
    kl_div_pool_cr.append(np.mean(kl_div_pool_cr_))
    kl_div_pool_profile.append(np.mean(kl_div_pool_profile_))
    fair_rep_values.append(np.mean(fair_rep_values_))
    NDKL_values.append(np.mean(NDKL_values_))
    NDKL_ranked.append(np.mean(NDKL_ranked_))
    avg_sat_10.append(np.mean(avg_sat_10_))
    avg_sat_20.append(np.mean(avg_sat_20_))
    avg_sat_30.append(np.mean(avg_sat_30_))
    avg_sat_40.append(np.mean(avg_sat_40_))
    avg_sat_50.append(np.mean(avg_sat_50_))
    result.append(cr_rapf.iloc[:,0].values.tolist())
    pool_grp_cnts.append(pool_group_cnt_dict)
    profile_grp_cnts.append(profile_group_cnt_dict)
    cr_grp_cnts.append(assess_group_cnt_dict)

    # PREFAIR IMPUTATION + RAPF
    kl_div_pool_cr_ = []
    kl_div_pool_profile_ = []
    fair_rep_values_ = []
    NDKL_values_ = []
    NDKL_ranked_ = []
    NDKL_ALLk_values_ = []
    NDKL_ALLk_ranked_ = []
    fairness_exposure_ = []
    avg_sat_10_ = []
    avg_sat_20_ = []
    avg_sat_30_ = []
    avg_sat_40_ = []
    avg_sat_50_ = []
    full_sat_ = []
    top_1_indx_ = []
    sat_indx_cnt_top5_ = []
    sat_indx_cnt_top10_ = []
    item_group_dict, pool_group_cnt_dict, ranked_item_group_dict, profile_group_cnt_dict = src.getset.get_representation(
        profile_df, dataset_df, candidates_col, sa_col)
    features_df = dataset_df.drop(columns=[sa_col])  # Drop sensative attribute
    completed_profile_df = src.imp._imputate_candidates(profile_df, features_df, candidates_col)
    for i in range(0, 10):
        seed = i  # for repro
        cr_irapf = cr.RAPF(completed_profile_df, item_group_dict, k_cnt, seed)
        assess_item_group_dict = src.get_item_group_dict_for_ranking(cr_irapf, dataset_df, candidates_col, sa_col)
        assess_group_cnt_dict = src.rankingdf_to_proportions(cr_irapf, pool_item_group_dict)
        kl_div_pool_cr_.append(src.KL_div_pool_assess_set(pool_group_cnt_dict, assess_group_cnt_dict, fair_rep))
        kl_div_pool_profile_.append(src.KL_div_pool_assess_set(pool_group_cnt_dict, profile_group_cnt_dict, fair_rep))
        fair_rep_values_.append(src.fair_representation(pool_group_cnt_dict, assess_group_cnt_dict, fair_rep))
        NDKL_values_.append(src.NDKL(cr_irapf, pool_item_group_dict, 'EQUAL'))
        NDKL_ranked_.append(src.NDKL(cr_irapf, assess_item_group_dict, 'EQUAL'))
        NDKL_ALLk_values_.append(src.NDKL_allpos(cr_irapf, pool_item_group_dict, 'EQUAL'))
        NDKL_ALLk_ranked_.append(src.NDKL_allpos(cr_irapf, assess_item_group_dict, 'EQUAL'))
        ex, _ = frt.EXP(cr_irapf, assess_item_group_dict, 'MinMaxRatio')
        fairness_exposure_.append(ex)
        avg_sat_10_.append(src.average_satisfaction_percentage(profile_df, .1, cr_irapf, .1))
        avg_sat_20_.append(src.average_satisfaction_percentage(profile_df, .1, cr_irapf, .2))
        avg_sat_30_.append(src.average_satisfaction_percentage(profile_df, .1, cr_irapf, .3))
        avg_sat_40_.append(src.average_satisfaction_percentage(profile_df, .1, cr_irapf, .4))
        avg_sat_50_.append(src.average_satisfaction_percentage(profile_df, .1, cr_irapf, .5))
        full_sat_.append(src.full_sat_index(profile_df, .1, cr_irapf))
        top_1_indx_.append(src.full_sat_index(profile_df, 1 / k_cnt, cr_irapf))
        sat_indx_cnt_top5_.append(src.satisfaction_index_count(profile_df, 5, cr_irapf, 5, 1))
        sat_indx_cnt_top10_.append(src.satisfaction_index_count(profile_df, 10, cr_irapf, 10, 1))

    method.append('PREFAIR(IMPUTE) + RAPF')
    dataset.append(dataset_name)
    kl_div_pool_cr.append(np.mean(kl_div_pool_cr_))
    kl_div_pool_profile.append(np.mean(kl_div_pool_profile_))
    fair_rep_values.append(np.mean(fair_rep_values_))
    NDKL_values.append(np.mean(NDKL_values_))
    NDKL_ranked.append(np.mean(NDKL_ranked_))
    avg_sat_10.append(np.mean(avg_sat_10_))
    avg_sat_20.append(np.mean(avg_sat_20_))
    avg_sat_30.append(np.mean(avg_sat_30_))
    avg_sat_40.append(np.mean(avg_sat_40_))
    avg_sat_50.append(np.mean(avg_sat_50_))
    result.append(cr_irapf.iloc[:, 0].values.tolist())
    pool_grp_cnts.append(pool_group_cnt_dict)
    profile_grp_cnts.append(profile_group_cnt_dict)
    cr_grp_cnts.append(assess_group_cnt_dict)

    #Balanced Committee
    cr_bce = cr.balanced_committee(profile_df, profile_item_group_dict, fair_rep, k_cnt)
    assess_item_group_dict = src.get_item_group_dict_for_ranking(cr_bce, dataset_df, candidates_col, sa_col)
    assess_group_cnt_dict = src.rankingdf_to_proportions(cr_bce, pool_item_group_dict)
    method.append('BALANCED-COMMITTEE-ELECTION')
    dataset.append(dataset_name)
    kl_div_pool_cr.append(src.KL_div_pool_assess_set(pool_group_cnt_dict, assess_group_cnt_dict, fair_rep))
    kl_div_pool_profile.append(src.KL_div_pool_assess_set(pool_group_cnt_dict, profile_group_cnt_dict, fair_rep))
    fair_rep_values.append(src.fair_representation(pool_group_cnt_dict, assess_group_cnt_dict, fair_rep))
    NDKL_values.append(src.NDKL(cr_bce, pool_item_group_dict, 'EQUAL'))
    NDKL_ranked.append(src.NDKL(cr_bce, assess_item_group_dict, 'EQUAL'))
    avg_sat_10.append(src.average_satisfaction_percentage(profile_df, .1, cr_bce, .1))
    avg_sat_20.append(src.average_satisfaction_percentage(profile_df, .1, cr_bce, .2))
    avg_sat_30.append(src.average_satisfaction_percentage(profile_df, .1, cr_bce, .3))
    avg_sat_40.append(src.average_satisfaction_percentage(profile_df, .1, cr_bce, .4))
    avg_sat_50.append(src.average_satisfaction_percentage(profile_df, .1, cr_bce, .5))
    result.append(cr_bce.iloc[:,0].values.tolist())
    pool_grp_cnts.append(pool_group_cnt_dict)
    profile_grp_cnts.append(profile_group_cnt_dict)
    cr_grp_cnts.append(assess_group_cnt_dict)


    # Prefair
    cr_prefair = src.preFAIR(profile_df, dataset_df, candidates_col, sa_col, fair_rep, k_cnt)
    assess_item_group_dict = src.get_item_group_dict_for_ranking(cr_prefair, dataset_df, candidates_col, sa_col)
    assess_group_cnt_dict = src.rankingdf_to_proportions(cr_prefair, pool_item_group_dict)
    method.append('PREFAIR')
    dataset.append(dataset_name)
    kl_div_pool_cr.append(src.KL_div_pool_assess_set(pool_group_cnt_dict, assess_group_cnt_dict, fair_rep))
    kl_div_pool_profile.append(src.KL_div_pool_assess_set(pool_group_cnt_dict, profile_group_cnt_dict, fair_rep))
    fair_rep_values.append(src.fair_representation(pool_group_cnt_dict, assess_group_cnt_dict, fair_rep))
    NDKL_values.append(src.NDKL(cr_prefair, pool_item_group_dict, 'EQUAL'))
    NDKL_ranked.append(src.NDKL(cr_prefair, assess_item_group_dict, 'EQUAL'))
    avg_sat_10.append(src.average_satisfaction_percentage(profile_df, .1, cr_prefair, .1))
    avg_sat_20.append(src.average_satisfaction_percentage(profile_df, .1, cr_prefair, .2))
    avg_sat_30.append(src.average_satisfaction_percentage(profile_df, .1, cr_prefair, .3))
    avg_sat_40.append(src.average_satisfaction_percentage(profile_df, .1, cr_prefair, .4))
    avg_sat_50.append(src.average_satisfaction_percentage(profile_df, .1, cr_prefair, .5))
    result.append(cr_prefair.iloc[:,0].values.tolist())
    pool_grp_cnts.append(pool_group_cnt_dict)
    profile_grp_cnts.append(profile_group_cnt_dict)
    cr_grp_cnts.append(assess_group_cnt_dict)



    # Save results
    dic = {'method': method,
           'dataset': dataset,
           'SFD': kl_div_pool_cr,
           'kl_div_pool_profile': kl_div_pool_profile,
           'fair_representation': fair_rep_values,
           'pNDKL': NDKL_values,
           'NDKL': NDKL_ranked,
           'avg_sat_10': avg_sat_10,
           'avg_sat_20': avg_sat_20,
           'avg_sat_30': avg_sat_30,
           'avg_sat_40': avg_sat_40,
           'avg_sat_50': avg_sat_50,
           'result': result,
           'pool_grp_cnts': pool_grp_cnts,
           'profile_grp_cnts': profile_grp_cnts,
           'consensusranking_grp_cnts': cr_grp_cnts
           }

    results = pd.DataFrame(dic)
    results.to_csv(csv_name, index=False)
