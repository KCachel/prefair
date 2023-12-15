import numpy as np
import pycountry_convert as pc
from experiment_core import *
#Script for world happiness dataset

# Quick helper function to convert a country to its continent
def country_to_continent(country_name):
   #Manual outlies
    if country_name == 'Congo (Brazzaville)':
       return 'Africa'
    if country_name == 'Congo (Kinshasa)':
        return 'Africa'
    if country_name == 'Hong Kong S.A.R. of China':
        return 'Asia'
    if country_name == 'Kosovo':
        return 'Europe'
    if country_name == 'Somaliland region':
        return 'Africa'
    if country_name == 'State of Palestine':
        return 'Middle East'
    if country_name == 'Taiwan Province of China':
        return 'Asia'
    if country_name == 'Turkey':
        return 'Asia'
    else:
        country_alpha2 = pc.country_name_to_country_alpha2(country_name)
        country_continent_code = pc.country_alpha2_to_continent_code(country_alpha2)
        country_continent_name = pc.convert_continent_code_to_continent_name(country_continent_code)
    return country_continent_name


# Dataset Preparation
#1. We have to create a preference profile
happiness = pd.read_excel('data\world-happiness\DataForTable2.1WHR2023.xls')
happiness = happiness.dropna()


#Add the region sensitive attribute
countries_np = happiness['Country name'].to_numpy()
continent_regions = [country_to_continent(c) for c in countries_np]
happiness['Regions'] = continent_regions

#Drop countries where region is singleton or alike
happiness = happiness[~happiness['Regions'].isin(['Middle East', 'Oceania'])]


rank_store = []
for yr in range(2006, 2022+1, 1):
    filter= happiness.loc[happiness['year'] == yr]
    rank = filter[['Country name', 'Life Ladder']].sort_values(by = ['Life Ladder'],
                                                                                     ignore_index = True, ascending=False)
    rank = rank[['Country name']]
    rank.rename(columns={'Country name': str(yr)}, inplace=True)
    rank_store.append(rank)

#Final preference profile
happiness_profile_df = pd.concat(rank_store,  axis = 1)
happiness_profile_df = happiness_profile_df.loc[0:19, :] #Top 20 candidates for each ranker

np_profile = happiness_profile_df.to_numpy()
unique_ = list(np.unique(np_profile))
print("There are ", len(unique_), " candidates in the preference profile.")

# 2. Clean up the dataset
#For the features average the numeric indexes over the available years
happiness = happiness.drop(['Life Ladder'], axis=1)
happiness = happiness.groupby(['Country name', 'Regions']).mean()
happiness = happiness.drop(['year'], axis=1)
happiness = happiness.reset_index()


profile_df = happiness_profile_df
dataset_df = happiness
candidates_col = 'Country name'
sa_col = 'Regions'
fair_rep = 'EQUAL'
rank_fairness = 'EQUAL'
k_cnt = 20
#Profile item group dict
np_profile = profile_df.to_numpy()
candidate_ids = list(np.unique(np_profile))
ranked_grps = [dataset_df.loc[dataset_df[candidates_col] == e][sa_col].item() for e in candidate_ids]
profile_item_group_dict = dict(zip(candidate_ids, ranked_grps))
dataset_name = 'World Happiness'
csv_name = 'results/world-happiness/results_equal_rep.csv'
epira_bnd = .9

workflow(profile_df, dataset_df, candidates_col, sa_col, fair_rep, rank_fairness, k_cnt,
             profile_item_group_dict, candidate_ids, dataset_name, csv_name, epira_bnd)

fair_rep = 'PROPORTIONAL'
csv_name = 'results/world-happiness/results_prop_rep.csv'
epira_bnd = .9
workflow(profile_df, dataset_df, candidates_col, sa_col, fair_rep, rank_fairness, k_cnt,
             profile_item_group_dict, candidate_ids, dataset_name, csv_name, epira_bnd)


