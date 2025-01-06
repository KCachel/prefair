import os
os.environ["OMP_NUM_THREADS"] = '1' #For Kmeans on windows comment if not applicable
import pandas as pd
import sklearn.cluster
#To use a different distance function change the below
def _imputate_candidates(profile_df, dataset_df, candidates_col):
    """
    Impute candidates in a partial preference profile
    :param profile_df: Dataframe of preference profile
    :param dataset_df: Dataframe of candidate dataset
    :param candidates_col: Column in dataset_df with candidate ids/names
    :return: profile_df
    """
    profile_dict = {} #init empty dict
    #For every ranking:
    num_unique_rankings = len(profile_df.columns)

    profile_df = profile_df.dropna() #handle top-k where voters have different k
    for r in range(0, num_unique_rankings):
        single_ranking = pd.DataFrame(profile_df.iloc[:, r])  # isolate ranking
        candidates_ranked = list(single_ranking.to_numpy().flatten())
        unranked_set_df = dataset_df[~dataset_df[candidates_col].isin(candidates_ranked)]
        unranked_data = unranked_set_df.drop(columns=[candidates_col])
        # Determine the centroid
        fit_data = dataset_df.drop(columns=[candidates_col])
        kmeans = sklearn.cluster.KMeans(n_clusters=1, init='k-means++', random_state=0).fit(fit_data)
        centroid = kmeans.cluster_centers_
        # Determine similarity between centroid and other candidates
        #Need to deal with string candidate ids here
        sim = sklearn.metrics.pairwise.cosine_similarity(centroid, unranked_data.to_numpy(), dense_output=True)
        unranked_set_df = unranked_set_df.assign(Sim = sim.flatten().tolist())
        unranked_set_df = unranked_set_df[[candidates_col, 'Sim']]
        # Order candidates by similarity to this centroid
        unranked_set_df = unranked_set_df.sort_values(by=['Sim'], ascending=False)
        completed_ranking = candidates_ranked + unranked_set_df[candidates_col].values.tolist()
        profile_dict[list(profile_df.columns)[r]] = completed_ranking

    #Update profile
    profile_df = pd.DataFrame(profile_dict)
    return profile_df





