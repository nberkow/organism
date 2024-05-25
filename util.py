import numpy as np
import math

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
    for i in range(iterations):
        bot.make_move()
    return(bot)

def get_net_diff(scores):
    return scores[-1] - scores[0]

def get_best_diff(scores):
    return max(scores) - scores[0]
    
def get_avg_diff(scores):
    return np.average(scores) - scores[0]

def rank_genomes_by_stat(round_stats, stat):

    """
    rank genomes for the given stat and return the sorted list

    round_stats - Nested dict. keys are raw genome sequences, vals are a dictionary of stats

    stat - the stat to use for ranking
    """

    ranked_genomes = []
    
    genome_by_stat_value = {}
    for g in round_stats:
        stat_val = round_stats[g][stat]
        if not stat_val in genome_by_stat_value:
            genome_by_stat_value[stat_val] = []
        genome_by_stat_value[stat_val].append(g)
    
    ordered_values = sorted(list(genome_by_stat_value.keys()), reverse=True)

    for stat_val in ordered_values:
        tied_genomes = genome_by_stat_value[stat_val]
        for genome in tied_genomes:
            ranked_genomes.append(genome)

    return(ranked_genomes)

def get_ranked_genomes_by_stat(round_stats, stats):

    """
    rank genomes by each stat. return a dictionary
        - keys: stats
        - vals: list of genomes sorted by stat value

    round_stats - Nested dict. keys are raw genome sequences, vals are a dictionary of stats

    stats - list of stats to use for ranking
    """

    ranked_genome_lists_by_stat = {}

    for stat in stats:
        ranked_genomes = rank_genomes_by_stat(round_stats, stat)
        ranked_genome_lists_by_stat[stat] = ranked_genomes

    return(ranked_genome_lists_by_stat)

def get_higest_scoring_genomes_across_stats(round_stats, stats, n):

    """
    get the higest scoring genomes across a list of stats. return a total of n genomes. 

    round_stats - Nested dict. keys are raw genome sequences, vals are a dictionary of stats

    stats - list of stats to use for ranking
    """

    ranked_genome_lists_by_stat = get_ranked_genomes_by_stat(round_stats, stats)

    min_list_len = math.inf
    for stat in ranked_genome_lists_by_stat:
        if len(ranked_genome_lists_by_stat[stat]) < min_list_len:
            min_list_len = len(ranked_genome_lists_by_stat[stat])

    selected_genomes = set()

    i = 0
    while i < min_list_len and len(selected_genomes) < n:
        j = 0
        while j < len(stats) and len(selected_genomes) < n:
            stat = stats[j]
            selected_genomes.add(ranked_genome_lists_by_stat[stat][i])
            j += 1
        i += 1

    return(list(selected_genomes))


def summarize_run(finished_bots, genomes_by_bot_name):

    raw_scores_by_genome = {}
    stats_by_genome = {}

    for bot in finished_bots:

        genome = genomes_by_bot_name[bot.name]
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