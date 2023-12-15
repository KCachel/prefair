import numpy as np
import pandas as pd
from experiment_core import *


# Dataset Preparation
#1. We have to create a preference profile
ibmhr = pd.read_csv('data/hr-analytics/IBMHRAnalytics.csv')
ibmhr = ibmhr.select_dtypes(['number'])
ibmhr = ibmhr.dropna()

#Add the Age sensitive attribute
bins = [18, 20, 30, 40, 50, 60]
labels = ['10s','20s','30s','40s','50+']
ibmhr['BinnedAge'] = pd.cut(ibmhr['Age'], bins=bins, labels=labels)
ibmhr = ibmhr.dropna(subset = ['BinnedAge'])
ibmhr['EmployeeNumber'] = ibmhr['EmployeeNumber'].apply(str)


# Rank by years at the company
yearsatcompany_emprank = ibmhr[['EmployeeNumber', 'YearsAtCompany']].sort_values(by = ['YearsAtCompany'],
                                                                                 ignore_index = True, ascending=False)
yearsatcompany_emprank = yearsatcompany_emprank[['EmployeeNumber']]
yearsatcompany_emprank.rename(columns={'EmployeeNumber': 'RankByYearsAtCompany'}, inplace=True)

# Rank by years in current role
yearscurrentrole_emprank = ibmhr[['EmployeeNumber', 'YearsInCurrentRole']].sort_values(by = ['YearsInCurrentRole'],
                                                                                 ignore_index = True, ascending=False)
yearscurrentrole_emprank = yearscurrentrole_emprank[['EmployeeNumber']]
yearscurrentrole_emprank.rename(columns={'EmployeeNumber': 'RankByYearsInCurrentRole'}, inplace=True)

# Rank by years since last promotion
yearslastpromo_emprank = ibmhr[['EmployeeNumber', 'YearsSinceLastPromotion']].sort_values(by = ['YearsSinceLastPromotion'],
                                                                                 ignore_index = True, ascending=False)
yearslastpromo_emprank = yearslastpromo_emprank[['EmployeeNumber']]
yearslastpromo_emprank.rename(columns={'EmployeeNumber': 'RankByYearsSinceLastPromotion'}, inplace=True)

# Rank by years with current manager
yearscurrman_emprank = ibmhr[['EmployeeNumber', 'YearsWithCurrManager']].sort_values(by = ['YearsWithCurrManager'],
                                                                                 ignore_index = True, ascending=False)
yearscurrman_emprank = yearscurrman_emprank[['EmployeeNumber']]
yearscurrman_emprank.rename(columns={'EmployeeNumber': 'RankByYearsWithCurrManager'}, inplace=True)

#Final preference profile
ibm_hr_profile_df = pd.concat([yearsatcompany_emprank, yearscurrentrole_emprank, yearslastpromo_emprank, yearscurrman_emprank],  axis = 1)
ibm_hr_profile_df = ibm_hr_profile_df.loc[0:499, :] #Top 500 candidates for each ranker



np_profile = ibm_hr_profile_df.to_numpy()
unique_employees = list(np.unique(np_profile))
print("There are ", len(unique_employees), " candidates in the preference profile.")


# Gender
# np_profile = ibm_hr_profile_df.to_numpy()
# unique_employees = list(np.unique(np_profile))
# employee_gender = [ibmhr.loc[ibmhr['EmployeeNumber'] == emp]['Gender'].item() for emp in unique_employees]
# profile_item_group_dict = dict(zip(unique_employees, employee_gender))



profile_df = ibm_hr_profile_df
dataset_df = ibmhr
candidates_col = 'EmployeeNumber'
sa_col = 'BinnedAge'
fair_rep = 'EQUAL'
rank_fairness = 'EQUAL'
k_cnt = 100
#Profile item group dict
np_profile = profile_df.to_numpy()
candidate_ids = list(np.unique(np_profile))
ranked_grps = [dataset_df.loc[dataset_df[candidates_col] == e][sa_col].item() for e in candidate_ids]
profile_item_group_dict = dict(zip(candidate_ids, ranked_grps))
dataset_name = 'IBMHR'
csv_name = 'results/ibmhr/results_equal_rep.csv'
epira_bnd = .9 #seems to be limit in this data

workflow(profile_df, dataset_df, candidates_col, sa_col, fair_rep, rank_fairness, k_cnt,
             profile_item_group_dict, candidate_ids, dataset_name, csv_name, epira_bnd)

fair_rep = 'PROPORTIONAL'
csv_name = 'results/ibmhr/results_prop_rep.csv'

epira_bnd = .9 #seems to be limit in this data
workflow(profile_df, dataset_df, candidates_col, sa_col, fair_rep, rank_fairness, k_cnt,
             profile_item_group_dict, candidate_ids, dataset_name, csv_name, epira_bnd)
