import numpy as np
from scipy.stats import multivariate_normal

def get_functional_genome(sequence, coords=None):

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

def run_bot(args):
    
    """
    move each organism according to the genome and position once per iteration
    """
    
    bot, iterations = args
    #print(f"simulating bot {bot.name}")
    for i in range(iterations):
        bot.make_move()
    return(bot)    

def summarize_run(finished_bots, genomes_by_bot_name):

    raw_scores_by_genome = {}
    stats_by_genome = {}

    for bot in finished_bots:

        genome = genomes_by_bot_name[bot.name]
        print(genome[0:10])

        if not genome in raw_scores_by_genome:
            raw_scores_by_genome[genome] = {
                "net_diffs"    : [],
                "maxima_diffs"   : [],
                "average_diffs" : []
            }

            score_diff = bot.pos_log['s'][-1] - bot.pos_log['s'][0]
            raw_scores_by_genome[genome]["net_diffs"].append(score_diff)

            score_diff = np.average(bot.pos_log['s']) - bot.pos_log['s'][0]
            raw_scores_by_genome[genome]["average_diffs"].append(score_diff)

            maximum = max(bot.pos_log['s']) - bot.pos_log['s'][0]
            raw_scores_by_genome[genome]["maxima_diffs"].append(maximum)


    for genome in raw_scores_by_genome:
        stats_by_genome[genome] = {
            "mean_net_diff" : np.average(
                raw_scores_by_genome[genome]["net_diffs"]),
            "mean_best_diff" : np.average(
                raw_scores_by_genome[genome]["maxima_diffs"]),
            "mean_avg_diff" : np.average(
                raw_scores_by_genome[genome]["average_diffs"]),
            "std_net_diff" : np.std(
                raw_scores_by_genome[genome]["net_diffs"]),
            "std_best_diff" : np.std(
                raw_scores_by_genome[genome]["maxima_diffs"]),
            "std_avg_diff" : np.average(
                raw_scores_by_genome[genome]["average_diffs"]),
        }

    return(stats_by_genome)

def select_surviving_simulations(bot_stats, top_percent=.1):

    selected_sims = {}
    top_n = int(top_percent * len(bot_stats))

    bots_by_best_score = {}
    bots_by_average_score = {}

    for sim_name in bot_stats:
        stats = bot_stats[sim_name]

        best_score = stats["mean_diff"]
        bots_by_best_score[best_score] = sim_name

        avg_score = stats["mean_max"]
        bots_by_average_score[avg_score] = sim_name

    selected_best = sorted(list(bots_by_best_score.keys()), reverse=True)[0:top_n]
    selected_avg  = sorted(list(bots_by_average_score.keys()), reverse=True)[0:top_n]

    for v in selected_best:
        sim_name = bots_by_best_score[v]
        selected_sims[sim_name] = bot_stats[sim_name]

    for v in selected_avg:
        sim_name = bots_by_average_score[v]
        selected_sims[sim_name] = bot_stats[sim_name]

    return(selected_sims)


def gradient_score(gradients, weights, x, y):

    """
    calculate a gradient score at specific x,y position

    inputs:
    - gradient - a list of distribution objects
    - weights - a list of weights summing to one
    """

    score = 0
    for i in range(len(gradients)):
        score += gradients[i].pdf([x,y]) * weights[i]
    return(score)