import math

def handle_oov(file):
    words = {}
    # topening the file and adding the start and stop tokens 
    with open(file, 'r') as file:
        for line in file:
            tokens = line.split()
            tokens.insert(0, "<START>")
            tokens.append("<STOP>")
            for token in tokens:
                # keeps track of word count
                words[token] = 1 + words.get(token, 0)

    words["<UNK>"] = 0
    less_three = []
    for w, c in words.items():
        # if word is found used less than 3 times 
        if c < 3:
            less_three.append(w)
            # <unk> count is added
            words["<UNK>"] += c
    for i in less_three:
        # deleting the less than 3 words
        del words[i]
    return words

def unigram_prob(words):
     # get the total minus start token
    length = sum(words.values()) - words["<START>"]
    u_p = {}
    for w, c in words.items():
        # get the probabilities of each word
        if w != "<START>":
            u_p[w] = c / length
    return u_p

def unigram_prob_add(words, a):
    # get the total minus start token
    length = sum(words.values()) - words["<START>"]
    u_p = {}
    for w, c in words.items():
        # get the probabilities of each word plus smoothing
        if w != "<START>":
            u_p[w] = (c + a) / (c + a * length)
    return u_p

def bigram(file):
    words= []
    bigram_count = {}
    for line in file:
        # get words from line
        tokens = line.split()
        # get indiviudal word
        for word in range(len(tokens) - 1):
            # have to group in a tuple since bigram
            words.append((tokens[word], tokens[word + 1]))
    for i in words:
        # get a count of the groupings
        bigram_count[i] = 1 + bigram_count.get(i, 0)
    return bigram_count

def trigram(file):
    words= []
    trigram_count = {}
    for line in file:
        # get words from line
        tokens = line.split()
        # get indiviudal word
        for word in range(len(tokens) - 2):
            # have to group in a tuple since trigram
            words.append((tokens[word], tokens[word + 1], tokens[word + 2]))
    for i in words:
        # get a count of the groupings
        trigram_count[i] = 1 + trigram_count.get(i, 0)
    return trigram_count

# perplexity calculation for bigram
def berp(file, bigram_count, unigram_count):
    length = 0
    words= []
    log_sum = 0
    for line in file:
        # get words from line
        tokens = line.split()
         # get indiviudal word
        length += len(tokens) - 1
        # keep track of length of the words minus start
        for word in range(len(tokens) - 1):
            words.append((tokens[word], tokens[word + 1]))
    for i in words:
        # have to make sure if i in bigram otherwise error
        if bigram_count.get(i, 0):
            # calculate the log sum
            log_sum += math.log(bigram_count[i]/unigram_count[i[0]])
    # return the perplexity value
    return math.exp(-log_sum/length)

# same thing as the regular perplexity calculation but smoothing 
def berp_add(file, bigram_count, unigram_count, a):
    length = 0
    words= []
    log_sum = 0
    for line in file:
        tokens = line.split()
        length += len(tokens) - 1
        for word in range(len(tokens) - 1):
            words.append((tokens[word], tokens[word + 1]))
    for i in words:
       # used try except in order to avoid 0 error
       try:
            # implemented the additive smoothing here with alpha a
            log_sum += math.log((bigram_count[i] + a)/(bigram_count[i] + a * unigram_count[i[0]]))
       except:
            continue
    # return perplexity value with addtive smoothing
    return math.exp(-log_sum/length)

# perplexity calculation for trigram 
def terp(file, bigram_count, trigram_count, unigram):
    length = 0
    words = []
    log_sum = 0
    for line in file:
        # get words from line
        tokens = line.split()
        # get indiviudal word
        length += len(tokens) - 1
        for word in range(len(tokens) - 2):
            # keep track of length of the words minus start
            words.append((tokens[word], tokens[word + 1], tokens[word + 2]))
    for i in words:
        # used try except in order to avoid 0 error
        try:
            # makes sure to get the correct count of start token or whatever
            if i[0] == "<START>":
                # log sum this stuff
                log_sum += math.log(trigram_count[i]/unigram["<START>"])
            else:
                log_sum += math.log(trigram_count[i]/bigram_count[i[0:2]])
        except:
            # else math.log 1 that 
            log_sum += math.log(1)
    return math.exp(-log_sum/length)

# same thing as the regular perplexity calculation but smoothing 
def terp_add(file, bigram_count, trigram_count, unigram, a):
    length = 0
    words = []
    log_sum = 0
    for line in file:
        tokens = line.split()
        length += len(tokens) - 1
        for word in range(len(tokens) - 2):
            words.append((tokens[word], tokens[word + 1], tokens[word + 2]))
    for i in words:
        try:
            # implemented the additive smoothing here with alpha a
            if i[0] == "<START>":
                log_sum += math.log((trigram_count[i] + a)/(trigram_count[i] + a * unigram["<START>"]))
            else:
                log_sum += math.log((trigram_count[i] + a)/(trigram_count[i] + a * bigram_count[i[0:2]]))
        except:
            log_sum += math.log(1)
    return math.exp(-log_sum/length)

def linear(file, trigram, bigram, unigram, l):
    words = []
    bi = 0
    ti = 0
    length = 0
    log_sum = 0
    total = (sum(unigram.values()) - unigram["<START>"])
    for line in file:
        tokens = line.split()
        length += len(tokens) - 2
        for word in range(len(tokens) - 2):
            words.append((tokens[word], tokens[word + 1], tokens[word + 2]))
    for i in words:
        try:
            bi = bigram[i[1:3]] / unigram[i[1:3][0]]
        except:
            bi = 0
        try:
            if i[0] == "<START>":
                ti = trigram[i]/unigram["<START>"]
            else:
                ti = trigram[i]/bigram[i[0:2]]
        except:
            ti = 1
        log_sum += math.log((l[0] * (unigram[i[2]]/total)) + (l[1] * bi) + (l[2] * ti))
    return math.exp(-log_sum/length)

# calculate perplexity for unigram
def perplexity(model, test_words):        
    log_sum = 0
    length_words = 0
    for line in test_words:
        for word in line.split():
            if word != "<START>":
                # log sum
                log_sum += math.log(model[word])
                # get total word count
                length_words +=1
    return math.exp(-log_sum/length_words)

# purpose of this function is to fit whatever file and model with the start and stop tokens which is crucial in my code
def get_words(file, model):
    words = []
    with open(file, 'r') as file:
        for line in file:
            tokens = line.split()
            for token in tokens:
                if token not in model:
                    # add unk
                    tokens[tokens.index(token)] = "<UNK>"
            # add start and stop
            tokens.insert(0, "<START>")
            tokens.append("<STOP>")
            # join the sentence and append to list
            words.append(" ".join(tokens))
    return words

if __name__ == "__main__":
    training_file = 'A2-Data/1b_benchmark.train.tokens'
    dev_file = 'A2-Data/1b_benchmark.dev.tokens'
    test_file = 'A2-Data/1b_benchmark.test.tokens'
    #t = "A2-Data/test"
    
    # all these print statements will give the values to what you are seeking, you can change/add as you seek
    unigram = handle_oov(training_file)
    print("Train Perplexity of Unigram:", perplexity(unigram_prob(unigram), get_words(training_file, unigram)))
    print("Dev Perplexity of Unigram:", perplexity(unigram_prob(unigram), get_words(dev_file, unigram)))
    print("Test Perplexity of Unigram:", perplexity(unigram_prob(unigram), get_words(test_file, unigram)))
    print("\n")
    print("Train Perplexity of Bigram:", berp(get_words(training_file, unigram), bigram(get_words(training_file, unigram)), unigram))
    print("Dev Perplexity of Bigram:", berp(get_words(dev_file, unigram), bigram(get_words(training_file, unigram)), unigram))
    print("Test Perplexity of Bigram:", berp(get_words(test_file, unigram), bigram(get_words(training_file, unigram)), unigram))
    print("\n")
    print("Train Perplexity of Trigram:", terp(get_words(training_file, unigram), bigram(get_words(training_file, unigram)), trigram(get_words(training_file, unigram)), unigram))
    print("Dev Perplexity of Trigram:", terp(get_words(dev_file, unigram), bigram(get_words(training_file, unigram)), trigram(get_words(training_file, unigram)), unigram))
    print("Test Perplexity of Trigram:", terp(get_words(test_file, unigram), bigram(get_words(training_file, unigram)), trigram(get_words(training_file, unigram)), unigram))
    print("\n")
    print("Train Perplexity of Unigram Add 1 Smoothing:", perplexity(unigram_prob_add(unigram, 0.7), get_words(training_file, unigram)))
    print("Dev Perplexity of Unigram Add 1 Smoothing:", perplexity(unigram_prob_add(unigram, 0.7), get_words(dev_file, unigram)))
    #print("Test Perplexity of Unigram Add 1 Smoothing:", perplexity(unigram_prob_add(unigram, 1), get_words(test_file, unigram)))
    print("\n")
    print("Train Perplexity of Bigram Add 1 Smoothing:", berp_add(get_words(training_file, unigram), bigram(get_words(training_file, unigram)), unigram, 0.7))
    print("Dev Perplexity of Bigram Add 1 Smoothing:", berp_add(get_words(dev_file, unigram), bigram(get_words(training_file, unigram)), unigram, 0.7))
    #print("Test Perplexity of Bigram Add 1 Smoothing:", berp_add(get_words(test_file, unigram), bigram(get_words(training_file, unigram)), unigram, 1))
    print("\n")
    print("Train Perplexity of Trigram Add 1 Smoothing:", terp_add(get_words(training_file, unigram), bigram(get_words(training_file, unigram)), trigram(get_words(training_file, unigram)), unigram, 0.7))
    print("Dev Perplexity of Trigram Add 1 Smoothing:", terp_add(get_words(dev_file, unigram), bigram(get_words(training_file, unigram)), trigram(get_words(training_file, unigram)), unigram, 0.7))
    #print("Test Perplexity of Trigram Add 1 Smoothing:", terp_add(get_words(test_file, unigram), bigram(get_words(training_file, unigram)), trigram(get_words(training_file, unigram)), unigram, 1))
    print("\n")
    print("Test Perplexity of Unigram Add 1 Smoothing:", perplexity(unigram_prob_add(unigram, 0.6), get_words(test_file, unigram)))
    print("Test Perplexity of Bigram Add 1 Smoothing:", berp_add(get_words(test_file, unigram), bigram(get_words(training_file, unigram)), unigram, 0.6))
    print("Test Perplexity of Trigram Add 1 Smoothing:", terp_add(get_words(test_file, unigram), bigram(get_words(training_file, unigram)), trigram(get_words(training_file, unigram)), unigram, 0.6))
    print("\n")
    print("Train Linear Smoothing Perplexity with Lambda Values (0.1, 0.3, 0.6):",(linear(get_words(training_file, unigram), trigram(get_words(training_file, unigram)), bigram(get_words(training_file, unigram)), unigram, [.1, .3, .6])))
    print("Dev Linear Smoothing Perplexity with Lambda Values (0.1, 0.3, 0.6):",(linear(get_words(dev_file, unigram), trigram(get_words(training_file, unigram)), bigram(get_words(training_file, unigram)), unigram, [.1, .3, .6])))
    print("\n")
    print("Train Linear Smoothing Perplexity with Lambda Values (0.1, 0.2, 0.4):",(linear(get_words(training_file, unigram), trigram(get_words(training_file, unigram)), bigram(get_words(training_file, unigram)), unigram, [.1, .2, .4])))
    print("Dev Linear Smoothing Perplexity with Lambda Values (0.1, 0.2, 0.4):",(linear(get_words(dev_file, unigram), trigram(get_words(training_file, unigram)), bigram(get_words(training_file, unigram)), unigram, [.1, .2, .4])))
    print("\n")
    print("Train Linear Smoothing Perplexity with Lambda Values (0.5, 0.8, 0.9):",(linear(get_words(training_file, unigram), trigram(get_words(training_file, unigram)), bigram(get_words(training_file, unigram)), unigram, [.5, .8, .9])))
    print("Dev Linear Smoothing Perplexity with Lambda Values (0.5, 0.8, 0.9):",(linear(get_words(dev_file, unigram), trigram(get_words(training_file, unigram)), bigram(get_words(training_file, unigram)), unigram, [.5, .8, .9])))
    print("Test Linear Smoothing Perplexity with Lambda Values (0.3, 0.4, 0.5):",(linear(get_words(test_file, unigram), trigram(get_words(training_file, unigram)), bigram(get_words(training_file, unigram)), unigram, [.3, .4, .5])))
    print("\n")
