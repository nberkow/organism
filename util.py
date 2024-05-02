import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import random
from scipy.stats import multivariate_normal

def get_clean_subtree(sequence, coords=None):

    """
    get the largest fully enclosed sublist
    """

    if not coords:
        coords = [0, len(sequence)]

    if not coords[1] - coords[0] > 1 or coords[1] > len(sequence):
        return('[]')

    rough_subseq = '[' + sequence[coords[0]:coords[1]] + ']'              
    stack_heights = {}  # track running differences of opens and closes
    substr_ends   = {}  # track the index where each stack becomes empty

    # iterate over the sequences, updating each potential subsequence
    for i in range(len(rough_subseq)):

        # create a new potential start at position i when encountering an open bracket
        if rough_subseq[i] == '[':
            stack_heights[i] = 0

        # update existing stacks (whether or not one was just created)
        for h in stack_heights:
            to_remove = []

            # If the current character is an open bracket 
            if rough_subseq[i] == '[':  
                stack_heights[h] += 1

            # If the current character is an close bracket
            if rough_subseq[i] == ']':
                stack_heights[h] -= 1

                # close off a balanced substring
                if stack_heights[h] == 0:
                    to_remove.append(h)
                    substr_ends[h] = i + 1

        # clean up finished stacks
        for h in to_remove:
            stack_heights.pop(h, None)

    max_len = 0
    max_len_substr = ''
    for s in substr_ends:
        if max_len < substr_ends[s] - s:
            max_len = substr_ends[s] - s
            max_len_substr = rough_subseq[s:substr_ends[s]]
    return(max_len_substr)

def make_random_sequence(n, p = [.25, .25, .25, .25]):
    
    characters = ['[',']','0','1']
    s = "".join(np.random.choice(characters, p=p, size=n))
    return(s)

def get_random_raw_genomes(n, min_length=20, raw_length=1000, p = [.25, .25, .25, .25]):

    g = 0
    t = 0
    genomes = []

    while g < n and t < 10**9:
        raw_seq = make_random_sequence(raw_length)
        valid_tree = get_clean_subtree(raw_seq, [0, len(raw_seq)])
        if len(valid_tree) >= min_length:
            genomes.append(raw_seq)
            g+=1
        t+=1
    return(genomes)

def mutate(genome, n, mutation_params={}):

    if len(mutation_params) == 0:
        mutation_params = {
            "p_substitution" : 0,
            "p_copy_paste"   : 0,
            "p_tandem_dupe"  : 0,
            "p_del"          : 0,
            "p_avg_seg_len"  : 0,
        }

def summarize_run(organism_list):

    diffs = []
    maxima = []

    for g in organism_list:
        score_diff = np.average(g.pos_log['s']) - g.pos_log['s'][0]
        diffs.append(score_diff)

        maximum = max(g.pos_log['s']) - g.pos_log['s'][0]
        maxima.append(maximum)

    stats = {
        "mean_diff" : np.average(diffs),
        "mean_max" : np.average(maxima),
        "std_diff" : np.std(diffs),
        "std_max" : np.std(maxima),
    }

    return(stats)

def plot_run_summary(run_stats, name):

    fig = go.Figure()
    for r in run_stats:

        stats = run_stats[r]
        y_vals = [stats["mean_diff"], stats["mean_max"]]
        y_std  = [stats["std_diff"], stats["std_max"]]

        fig.add_trace(go.Bar(
            name=r,
            x=['Score Diff', 'Max Score Reached'], y=y_vals,
            error_y=dict(type='data', array=y_std)
        ))

    fig.update_layout(barmode='group')
    fig.write_image(f"figures/summary_{name}.png")

def define_gradient_and_weights(x_range, y_range, means=1):
        
        gradient = []
        weights = []

        for i in range(means):
            x_mean = random.random() * (x_range[1] - x_range[0]) + x_range[0]
            y_mean = random.random() * (y_range[1] - y_range[0]) + y_range[0]
            dist = multivariate_normal([x_mean, y_mean])
            gradient.append(dist)

        denom = 0.
        raw = []

        for i in range(means):
            r = random.random()
            raw.append(r)
            denom += r
        
        for r in raw:
            weights.append(r/denom)

        return(gradient, weights)

def sequence_to_tree(s):

    def parse_inner_list(s, index):
        result = []
        num = ''
        while index < len(s):
            char = s[index]
            if char.isdigit():
                num += char
            elif char == '[':
                sublist, index = parse_inner_list(s, index + 1)
                result.append(sublist)
            elif char == ']':
                if num:
                    result.append(int(num, 2))
                    num = ''
                return result, index
            elif char == ',':
                if num:
                    result.append(int(num, 2))
                    num = ''
            index += 1
        return result, index

    result, _ = parse_inner_list(s, 0)
    return result


