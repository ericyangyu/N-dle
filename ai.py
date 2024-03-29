import re
import string

import numpy as np


class AI:
    def __init__(self, vocab_file, num_letters=5, num_guesses=6):
        self.vocab_file = vocab_file
        self.num_letters = num_letters
        self.num_guesses = 6

        self.vocab, self.vocab_scores, self.letter_scores = self.get_vocab(self.vocab_file)
        self.best_words = sorted(list(self.vocab_scores.items()), key=lambda tup: tup[1])[::-1]

        self.domains = None
        self.possible_letters = None

        self.reset()

    def solve(self):
        num_guesses = 0
        while [len(e) for e in self.domains] != [1 for _ in range(self.num_letters)]:
            num_guesses += 1
            word = self.sample()

            # # Always start with these two words
            # if num_guesses == 1:
            #     word = 'soare'
            # elif num_guesses == 2:
            #     word = 'culti'

            print('-----------------------------------------------')
            print(f'Guess #{num_guesses}/{self.num_guesses}: {word}')
            print('-----------------------------------------------')
            self.arc_consistency(word)

        print(f'You did it! The word is {"".join([e[0] for e in self.domains])}')


    def arc_consistency(self, word):
        print(f'Performing arc consistency check on {word}...')
        print(f'Specify 0 for completely nonexistent letter at the specified index, 1 for existent letter but incorrect index, and 2 for correct letter at correct index.')
        results = []

        # Collect results
        for l in word:
            while True:
                result = input(f'{l}: ')
                if result not in ['0', '1', '2']:
                    print('Incorrect option. Try again.')
                    continue
                results.append(result)
                break

        self.possible_letters += [word[i] for i in range(len(word)) if results[i] == '1']

        for i in range(len(word)):
            if results[i] == '0':
                if word[i] in self.possible_letters:
                    if word[i] in self.domains[i]:
                        self.domains[i].remove(word[i])
                else:
                    for j in range(len(self.domains)):
                        if word[i] in self.domains[j] and len(self.domains[j]) > 1:
                            self.domains[j].remove(word[i])
            if results[i] == '1':
                if word[i] in self.domains[i]:
                    self.domains[i].remove(word[i])
            if results[i] == '2':
                self.domains[i] = [word[i]]


    def reset(self):
        self.domains = [list(string.ascii_lowercase) for _ in range(self.num_letters)]
        self.possible_letters = []

    def sample(self):
        """
        Samples a best word given the current domains
        :return:
        """
        # Compile a regex of possible words with the current domain
        regex_string = ''
        for domain in self.domains:
            regex_string += ''.join(['[', ''.join(domain), ']', '{1}'])
        pattern = re.compile(regex_string)

        # From the words with the highest scores, only return the best word that match the regex pattern
        for word, _ in self.best_words:
            if pattern.match(word) and False not in [e in word for e in self.possible_letters]:
                return word

    def get_vocab(self, vocab_file):
        vocab = []
        with open(vocab_file, 'r') as f:
            for l in f:
                vocab.append(l.strip())

        # Count letter frequencies at each index
        letter_freqs = [{letter: 0 for letter in string.ascii_lowercase} for _ in range(self.num_letters)]
        for word in vocab:
            for i, l in enumerate(word):
                letter_freqs[i][l] += 1

        # Assign a score to each letter at each index by the probability of it appearing
        letter_scores = [{letter: 0 for letter in string.ascii_lowercase} for _ in range(self.num_letters)]
        for i in range(len(letter_scores)):
            max_freq = np.max(list(letter_freqs[i].values()))
            for l in letter_scores[i].keys():
                letter_scores[i][l] = letter_freqs[i][l] / max_freq

        # Find a sorted list of words ranked by sum of letter scores
        vocab_scores = {}  # (score, word)
        for word in vocab:
            score = 0
            for i, l in enumerate(word):
                score += letter_scores[i][l]

            # # Optimization: If repeating letters, deduct a couple points
            # if len(set(word)) < len(word):
            #     score -= 0.25 * (len(word) - len(set(word)))

            vocab_scores[word] = score

        return vocab, vocab_scores, letter_scores
