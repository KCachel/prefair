from src import *
from comparedmethods import *
import numpy as np
import pandas as pd
from experiment_core import *
#Script for world happiness dataset

# Dataset Preparation
#1. We have to create a preference profile
econf = pd.read_excel('data\econ-freedom\efotw-2023-master-index-data-for-researchers-iso.xlsx')

#Need to remove the commas in country names for gurobi
econf.Countries = econf.Countries.apply(lambda x: x.replace(',', ''))
econf.Countries = econf.Countries.apply(lambda x: x.replace(' ', ''))
#Drop countries where region is singleton or alike
econf = econf[~econf['World Bank Region'].isin(['North America', 'South Asia'])]

rank_store = []
#reporting was every 5 years
for yr in range(1975, 2000, 5):
    filter= econf.loc[econf['Year'] == yr]
    rank = filter[['Countries', 'Economic Freedom Summary Index']].sort_values(by = ['Economic Freedom Summary Index'],
                                                                                     ignore_index = True, ascending=False)
    rank = rank[['Countries']]
    rank.rename(columns={'Countries': str(yr)}, inplace=True)
    rank_store.append(rank)
#reporting became annual
for yr in range(2017, 2021+1, 1):
    filter= econf.loc[econf['Year'] == yr]
    rank = filter[['Countries', 'Economic Freedom Summary Index']].sort_values(by = ['Economic Freedom Summary Index'],
                                                                                     ignore_index = True, ascending=False)
    rank = rank[['Countries']]
    rank.rename(columns={'Countries': str(yr)}, inplace=True)
    rank_store.append(rank)

#Final preference profile
econf_profile_df = pd.concat(rank_store,  axis = 1)
econf_profile_df = econf_profile_df.loc[0:39, :] #Top 40 candidates for each ranker

# Clean up the dataset
#For the features average the numeric indexes over the available years
econf = econf.drop(['Economic Freedom Summary Index'], axis=1)
econf = econf.groupby(['Countries', 'World Bank Region']).mean()
econf = econf.drop(['Year'], axis=1)
econf = econf.reset_index()
econf = econf.dropna(axis = 1)




profile_df = econf_profile_df
dataset_df = econf
candidates_col = 'Countries'
sa_col = 'World Bank Region'
fair_rep = 'EQUAL'
rank_fairness = 'EQUAL'
k_cnt = 20
#Profile item group dict
np_profile = profile_df.to_numpy()
unique_ = list(np.unique(np_profile))
print("There are ", len(unique_), " candidates in the preference profile.")
candidate_ids = list(np.unique(np_profile))
ranked_grps = [dataset_df.loc[dataset_df[candidates_col] == e][sa_col].item() for e in candidate_ids]
profile_item_group_dict = dict(zip(candidate_ids, ranked_grps))
dataset_name = 'Econ Freedom'
csv_name = 'results/econ-freedom/results_equal_rep.csv'
epira_bnd = .70 #highest observed exposure according to method

workflow(profile_df, dataset_df, candidates_col, sa_col, fair_rep, rank_fairness, k_cnt,
             profile_item_group_dict, candidate_ids, dataset_name, csv_name, epira_bnd)

fair_rep = 'PROPORTIONAL'
csv_name = 'results/econ-freedom/results_prop_rep.csv'
epira_bnd = .70 #highest observed exposure according to method
workflow(profile_df, dataset_df, candidates_col, sa_col, fair_rep, rank_fairness, k_cnt,
             profile_item_group_dict, candidate_ids, dataset_name, csv_name, epira_bnd)