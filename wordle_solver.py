import numpy as np
from collections import defaultdict


class WordleSolver():
    def __init__(self, guesses, answers, first_guess=None) -> None:
        self.guesses = guesses
        self.answers = answers
        self.first_guess = first_guess

    def filt_word(self, word, ref, info):
        # print(word, ref)
        word_set = set(word)

        for w, r, i in zip(word, ref, info):
            if i == '+' and w != r:
                # print('+')
                return False
            if i == '-' and (w == r or r not in word_set):
                # print('-')
                return False
            if i == '0' and r in word_set:
                # print(w, r, '0')
                return False
        # print('pass')
        return True

    
    def filt_words(self, words, ref, info):
        return [word for word in words if self.filt_word(word, ref, info)]

    def info(self, guess, answer):
        # information learned from guess. +: right spot, -: wrong spot, ' ': none
        res = ''
        answer_set = set(answer)
        for g, a in zip(guess, answer):
            res += '+' if g == a else '-' if g in answer_set else '0'
        
        # todo need to count new ' ' letters as info?
        return res
    
    def info_dists(self, guesses, answers):
        guesses_info_dists = {} # dict of group sizes by info for each guess

        for guess in guesses:
            guess_info_dist = defaultdict(float)
            for answer in answers:
                guess_info_dist[self.info(guess, answer)] += 1 / len(answers)
            
            guesses_info_dists[guess] = guess_info_dist
            
        return guesses_info_dists

    def entropy(self, guess_info_dist):
        return -sum([np.log10(p) * p for p in guess_info_dist.values()])

    
    def guess(self, guesses, answers):
        # guess with highest entropy

        guesses_info_dists = self.info_dists(guesses, answers)
        words_E = {guess: self.entropy(info_dist) for guess, info_dist in guesses_info_dists.items()}

        best_guess, best_E = max(words_E.items(), key=lambda x: x[1])
        return words_E, best_guess, best_E


    def play(self, answer, show=True):
        cur_info = '     '

        cur_guesses, cur_answers = self.guesses, self.answers
        for i in range(6):
            if i == 0 and self.first_guess is not None:
                best_guess, best_E = self.first_guess, 'idk'
            else:
                words_E, best_guess, best_E = self.guess(cur_guesses, cur_answers)

                if i == 0:
                    self.first_guess = best_guess
            
                
            cur_info = self.info(best_guess, answer)

            if show:
                print('guessing {} with entropy {}, info {}'.format(best_guess, best_E, cur_info))

            if cur_info == '+++++':
                if show:
                    print('answer was {} in {} guesses'.format(best_guess, i+1))
                return True, i + 1

            cur_answers = self.filt_words(cur_answers, best_guess, cur_info)
            cur_guesses = self.filt_words(cur_guesses, best_guess, cur_info)
            
            if show:
                print('{} answers left, {} guesses left'.format(len(cur_answers), len(cur_guesses)))
            # print(list(sorted(words_E.items(), key=lambda x: -x[1]))[:20], cur_answers, cur_guesses[:12])
        if show:
            print('answer was {}'.format(answer))
        return False, np.NaN
