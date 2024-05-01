import numpy as np

def get_clean_subtree(sequence, coords):

    """
    get the largest fully enclosed sublist
    """

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

def get_random_genomes(n, min_length=20, raw_length=1000, p = [.25, .25, .25, .25]):

    g = 0
    t = 0
    genomes = []

    while g < n and t < 10**9:
        raw_seq = make_random_sequence(raw_length)
        valid_tree = get_clean_subtree(raw_seq, [0, len(raw_seq)])
        if len(valid_tree) >= min_length:
            genomes.append(valid_tree)
            g+=1
        t+=1
    return(genomes)
