from src import *
from comparedmethods import *
import numpy as np
import pandas as pd
import FairRankTune as frt
import pycountry_convert as pc
from experiment_core import *
from config_abl import *
#Script for global sustainability competetive index

# Quick helper function to convert a country to its continent
def country_to_continent(country_name):
   #Manual outlies
    if country_name == 'Burma':
       return 'Asia'
    if country_name == 'Cote d\'Ivoire':
        return 'Africa'
    if country_name == 'Democratic Republic of Congo':
        return 'Africa'
    if country_name == 'Kyrgistan':
        return 'Asia'
    if country_name == 'Republic of Congo':
        return 'Africa'
    if country_name == 'St. Vincent and the Grenadines':
        return 'North America'
    if country_name == 'Timor-Leste':
        return 'Asia'
    if country_name == 'West Bank and Gaza':
        return 'Middle East'
    else:
        country_alpha2 = pc.country_name_to_country_alpha2(country_name)
        country_continent_code = pc.country_alpha2_to_continent_code(country_alpha2)
        country_continent_name = pc.convert_continent_code_to_continent_name(country_continent_code)
    return country_continent_name

# Dataset Preparation
#1. We have to create a preference profile
gsci_2017 = pd.read_excel('data\global-sustainability\GSCI_Scores_2017.xlsx')
gsci_2017['year']= 2017
gsci_2018 = pd.read_excel('data\global-sustainability\GSCI_Scores_2018.xlsx')
gsci_2018['year']= 2018
gsci_2019 = pd.read_excel('data\global-sustainability\GSCI_Scores_2019.xlsx')
gsci_2019['year']= 2019
gsci_2020 = pd.read_excel('data\global-sustainability\GSCI_Scores_2020.xlsx')
gsci_2020['year']= 2020
gsci_2021 = pd.read_excel('data\global-sustainability\GSCI_Scores_2021.xlsx')
gsci_2021['year']= 2021
gsci_2022 = pd.read_excel('data\global-sustainability\GSCI_Scores_2022.xlsx')
gsci_2022['year']= 2022

gsci = pd.concat([gsci_2017, gsci_2018, gsci_2019, gsci_2020, gsci_2021, gsci_2022])
#Drop countries with almost no data
gsci = gsci[~gsci['Country'].isin(['North Korea'])]

#Drop countries where region is singleton or alike
gsci = gsci[~gsci['Country'].isin(['West Bank and Gaza'])]

# Clean summary rows from datasets
gsci.drop(gsci[gsci['Country'] == 'Average'].index, inplace=True)
gsci.drop(gsci[gsci['Country'] == 'Max'].index, inplace=True)
gsci.drop(gsci[gsci['Country'] == 'Min'].index, inplace=True)
gsci.drop(gsci[gsci['Country'] == 'nan'].index, inplace=True)


rank_store = []
for yr in range(2017, 2022+1, 1):
    filter= gsci.loc[gsci['year'] == yr]
    rank = filter[['Country', 'Sustainable Competitiveness']].sort_values(by = ['Sustainable Competitiveness'],
                                                                                     ignore_index = True, ascending=False)
    rank = rank[['Country']]
    rank.rename(columns={'Country': str(yr)}, inplace=True)
    rank_store.append(rank)

#Final preference profile
gsci_profile_df = pd.concat(rank_store,  axis = 1)
gsci_profile_df = gsci_profile_df.loc[0:69, :] #Top 20 candidates for each ranker

# Clean up the dataset
#For the features average the numeric indexes over the available years
gsci = gsci.drop(['Sustainable Competitiveness'], axis=1)
gsci = gsci.groupby(['Country']).mean()
gsci = gsci.drop(['year'], axis=1)
gsci = gsci.reset_index()
gsci = gsci.dropna(axis = 1)




#Add the region sensitive attribute
countries_np = gsci['Country'].to_numpy()
continent_regions = [country_to_continent(c) for c in countries_np]
gsci['Regions'] = continent_regions

profile_df = gsci_profile_df
dataset_df = gsci
candidates_col = 'Country'
sa_col = 'Regions'
fair_rep = 'EQUAL'
rank_fairness = 'EQUAL'
k_cnt = 36
#Profile item group dict
np_profile = profile_df.to_numpy()
unique_ = list(np.unique(np_profile))
print("There are ", len(unique_), " candidates in the preference profile.")
candidate_ids = list(np.unique(np_profile))
ranked_grps = [dataset_df.loc[dataset_df[candidates_col] == e][sa_col].item() for e in candidate_ids]
profile_item_group_dict = dict(zip(candidate_ids, ranked_grps))
dataset_name = 'GSCI'
csv_name = 'results/global-sci/results_equal_rep.csv'
epira_bnd = .63 #highest observed exposure according to method

workflow(profile_df, dataset_df, candidates_col, sa_col, fair_rep, rank_fairness, k_cnt,
             profile_item_group_dict, candidate_ids, dataset_name, csv_name, epira_bnd)

fair_rep = 'PROPORTIONAL'
csv_name = 'results/global-sci/results_prop_rep.csv'
epira_bnd = .85 #highest observed exposure according to method
workflow(profile_df, dataset_df, candidates_col, sa_col, fair_rep, rank_fairness, k_cnt,
             profile_item_group_dict, candidate_ids, dataset_name, csv_name, epira_bnd)

prefair_akt, random_akt = config_study(profile_df, dataset_df, candidates_col, sa_col, pd.concat(rank_store,  axis = 1))
print("prefair average KT: ", prefair_akt)
print("random average KT: ", random_akt)