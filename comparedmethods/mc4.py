import pandas as pd
import numpy as np
#References: https://github.com/kalyaniuniversity/MC4/blob/master/mc4/algorithm.py
np.set_printoptions(formatter={'float': lambda x: "{0:0.6f}".format(x)})


def get_dataframe(file):
    """
    Returns a dataframe object of a csv file
    :param file: path of the csv file
    :return: Dataframe
    """

    return pd.read_csv(file)


def get_voter_item_count(df):
    """
    :param df: Profile
    :return: voters int: count of voters providing preferences, items int: count of items being ranked (each ranked by >= 1 voter)
        item_key ndarray: array of unique items
    """

    voters = len(df.columns)
    unique_items = pd.unique(df.values.ravel('K')) #this includes nan if we have a partial list
    item_key = unique_items[~pd.isnull(unique_items)] #drop any nans
    items = len(item_key)
    int_vals = list(range(items))
    item_key_dict = dict(zip(item_key, int_vals))
    return voters, items, item_key_dict




def fill_transition_matrix_mc4(df, items, item_key_dict):
    """
    Return partial transition matrix from the dataframe containing different ranks using mC4
    :param df: Dataframe of reference profile
    :param items: list of candidates
    :param item_key_dict: Dictionary of candidates (keys) and groups (values)
    :return: Transition matrix
    """
    matrix = np.zeros((items,items))
    df_np = df.to_numpy()
    items = list(item_key_dict.keys())
    for a in items:
        for b in items:
            if a != b:
                ab_loc = np.bitwise_or(df_np == a, df_np == b) #locations of a and b
                rank_both = np.count_nonzero(ab_loc, axis = 0) == 2 #voters who rank both a and b
                pref_both = df_np[:,rank_both] #pref lists with both a and b
                ab_compared_in = np.count_nonzero(rank_both)
                a_over_b_count = 0
                for i in range(ab_compared_in):
                    a_over_b_count += np.count_nonzero(np.where(pref_both[:,i] == a)[0] < np.where(pref_both[:,i] == b)[0]) #count row index of a is < (higher) row index of b
                if ab_compared_in > 0 and a_over_b_count / ab_compared_in  >= 0.5: #strict majority prefer a to b by voter ranking a and b
                    matrix[item_key_dict[b],item_key_dict[a]] = 1
                else:
                    matrix[item_key_dict[b], item_key_dict[a]] = 0
    return matrix


def get_normalized_transition_matrix(partial_mat, items):
    """
    Norm transition matrix
    :param partial_mat: Partial transition matrix
    :param items: number of candidated
    :return: normalized transition matrix
    """

    matrix = partial_mat/items
    #matrix = partial_mat / (np.sum(partial_mat, axis=1) + 1)[:, None]

    for a in range(items):
        matrix[a,a] = 1 - np.sum(matrix[a,:])


    return matrix

def fix_diagnols(partial_mat, items):
    """
    Update diagnols to 1 - row sum
    :param partial_mat: partial transition matrix
    :param items: number of items
    :return: transition matrix
    """


    matrix = partial_mat

    for a in range(items):
        matrix[a,a] = 1 - np.sum(matrix[a,:])


    return matrix

def ergodic_transition(norm_matrix, alpha, items):
    """
    Return ergodic transition matrix from normalized transition matrix
    :param norm_matrix: normalized transition matrix
    :param alpha: number of items
    :param items:  small, positive ergotic number
    :return:
    """

    return (norm_matrix * (1 - alpha)) + (alpha / items)

def get_initial_distribution_matrix(items):
    """
    Initial distribution
    :param items: number of items
    :return: initial distribution matrix
    """
    return np.repeat((1 / items), items)


def solve_stationary_distribution_matrix(state_matrix, transition_matrix, precision, iterations):
    """
    Returns stationary distribution matrix
    :param state_matrix: initial distribution matrix
    :param transition_matrix: final transition matrix or ergodic transition matrix
    :param precision: acceptable error margin for convergence, default is 1e-07
    :param iterations: number of iterations to reach stationary distribution
    :return: stationary distribution matrix
    """
    counter = 1

    while counter <= iterations:

        current_state_matrix = state_matrix

        new_state_matrix = state_matrix.dot(transition_matrix)

        error = new_state_matrix - current_state_matrix

        if (np.abs(error) < precision).all():
            break

        state_matrix = new_state_matrix

        counter += 1

    return state_matrix

def extract_ranks(matrix, item_key):
    """
    Get ranking from matrix
    :param matrix: final matrix
    :param item_key: Dictionary of candidates (keys)
    :return: Consensus ranking
    """
    state_matrix = np.copy(matrix)
    ranking = []
    item_names = list(item_key.keys())
    item_indexers = list(item_key.values())
    for i in range(len(item_key)):
        max_indx = np.argmax(state_matrix)
        ranking.append(item_names[item_indexers.index(max_indx)])
        state_matrix[max_indx] = -np.inf

    return np.asarray(ranking)


def mc4(profile_df, k_cnt):
    """
    Preference Aggregation by Dwork et al. MC4 Algorithm
    :param profile_df: Dataframe of preference profile
    :param k_cnt: length of consensus
    :return: consensus ranking
    """
    alpha = 1 / 7
    precision = 0.0000001,
    iterations = 500
    voters, items, item_key = get_voter_item_count(profile_df)
    partial_transition_matrix = fill_transition_matrix_mc4(profile_df, items, item_key)
    normalized_transition_matrix = fix_diagnols(partial_transition_matrix, items)
    ergodic_transition_matrix = ergodic_transition(normalized_transition_matrix, alpha, items)
    initial_distribution_matrix = get_initial_distribution_matrix(items)

    stationary_distribution_matrix = solve_stationary_distribution_matrix(initial_distribution_matrix,
                                                                          ergodic_transition_matrix, precision,
                                                                          iterations)
    result_ranking = extract_ranks(stationary_distribution_matrix, item_key)
    return pd.DataFrame(result_ranking[0:k_cnt])

