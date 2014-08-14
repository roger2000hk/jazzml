""" Generate the n-grams with NLTK. 
    Question: should I bind notes to rhythm? """

from collections import defaultdict
import sys

from nltk import bigrams, trigrams, FreqDist
from nltk.collocations import *

# My imports
sys.path.append('./code/extract/')
sys.path.append('./code/ngram')

def genNGrams(dataList, n=3):
    """ Given a unigram list of notes or chords, generate n-grams 
        (of order(s) n, default n=3) as a list of items and return those. """

    if n == 1: # unigram
        return(dataList)
    elif n == 2:
        return(list(bigrams(dataList)))  
    elif n == 3:
        return(list(trigrams(dataList)))

def genSimpleFreqProbs(ngrams_original):
    """ Given the generated n-grams, return simple probabilities. Simple 
        version: Prob = (# of term occurrences) / (total # of term occurrences). 

        Note you can use this for unigrams, bigrams, etc. """
    # ngrams = [tuple(i) for i in ngrams_original]
    # ngramFD = FreqDist(ngrams) # frequencies for n-grams
    ngramsFD = genSimpleFreqs(ngrams_original)
    numNgrams = len(ngrams_original)
    for k, v in ngramFD.items():
        ngramFD[k] = (ngramFD[k] / float(numNgrams))
    return ngramFD

def genSimpleFreqs(ngrams_original):
    """ Helper method to just generate the frequencies of each n-gram. """
    ngrams = [tuple(i) for i in ngrams_original]
    return FreqDist(ngrams)

def bindNotesLens(ngrams, ngramlens):
    """ Given the generated n-gram notes and the generated n-gram lengths, return
        a list of tuples ((note i, len i), (note i+1, len(i+1))). """
    if isinstance(ngrams[0], list) is True or isinstance(ngrams[0], tuple) is True:
        return [tuple([(i, j) for i, j in zip(notes, lens)]) for notes, lens in zip(ngrams, ngramlens)]
    return [tuple([notes, lens]) for notes, lens in zip(ngrams, ngramlens)]

def reverseTuple(tup):
    """ Given a tuple ((a, b, c)), moves last item out and to front: ((c, (a, b))). """
    if type(tup) is int:
        tup = (tup,)
    if len(tup) == 1:
        return tup
    elif len(tup) == 2:
        return tup[::-1]
    else:
        return tuple((tup[-1], tup[:-1]))

def unreverseTuple(tup):
    """ Given reversed conditional tuple (c, (a, b)), converts back to ((a, b, c)). """
    if len(tup) == 1:
        return tup
    elif len(tup) == 2 and isinstance(tup[1], tuple) is False:
        return tup[::-1]
    elif len(tup) == 2 and isinstance(tup[0], tuple) is True and isinstance(tup[1], tuple) is True:
        return tup[::-1]
    else:
        result = [i for i in tup[1]]
        result.append(tup[0])
        return tuple(result)

def ngramProbs(notes, notelens, n=2):
    """ Use the n-gram model to return a dictionary of n-grams (n=2:bigram)
        and their n-gram probabilities. 

        Remember: P(w_a, w_b) = f(w_b, w_a) / f(w_b) """
    ### Goal: create dictionary where key = (n-gram, length(s) ), value = probability. ###

    # All the bigram terms f((w1, L1), (w2, L2)), the numerator
    terms_n = bindNotesLens(genNGrams(notes, n), genNGrams(notelens, n))
    fdict_n = genSimpleFreqs(terms_n) # f((w1 L1), (w2 L2))

    # All the (n-1)gram terms f(w1, L1), the denominator
    terms_nless = bindNotesLens(genNGrams(notes, n-1), genNGrams(notelens, n-1))
    fdict_nless = genSimpleFreqs(terms_nless) # f((w1 L1))

    # All the conditional bigram terms ((w_i+1 L-i+1, w_i L_i)) # move last item to front
    terms_ncond = map(reverseTuple, terms_n)

    # Build the conditional probability dictionary.
    condProbs = defaultdict()
    for term in terms_ncond:
        queryNumerator = unreverseTuple(term) 
        queryDenominator = queryNumerator[::-1]
        if len(queryDenominator) == 1:
            queryDenominator = queryDenominator[0]
        condProbs[term] = fdict_n[queryNumerator] / fdict_nless[queryDenominator]

    return condProbs


    # Build the conditional probability dictionary.
    # condProbs = defaultdict()
    # for ngramTuple in terms_ncond.items():
    #     next = ngramTuple[0]
    #     given = ngramTuple[1]
        # flatten into tuple

        # condProbs[ngramTuple]

    # terms_nless = 1
    # return terms_n, terms_nless, fdict_n, fdict_nless, terms_ncond