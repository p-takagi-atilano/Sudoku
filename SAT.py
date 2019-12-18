# Paolo Takagi-Atilano, October 26, 2017

import random


class SAT:
    def __init__(self, cnf_filename):
        self.clauses = set()     # set of propositional logic clauses (strings)
        self.assignment = []     # variable assignments
        self.var_to_index = {}   # dictionary mapping clause variables (string) to assignment indices (int)
        self.index_to_var = {}   # dictionary mapping assignment indices (int) to clause variables (string)
        self.threshold = 0.7     # probability of scoring rather than choosing random assignment/candidate
        self.max_flips = 100000  # max_flips for walksat
        self.walksat_clauses = set()  # set of clauses (in string format) that are unsatisfied clauses
        self.resets = 10         # number of resets for reset_walksat before giving up

        self.setup(cnf_filename)    # sets everything up, using provided filename

    # sets everything up, from given filename
    def setup(self, cnf_filename):
        f = open(cnf_filename, "r")

        # assignment index
        loc = 0
        for line in f:
            # add string to clauses
            self.clauses.add(str(line))
            # make list of vars in clause, without the '-' signs
            line_list = (line.replace('-', '')).split()

            # iterate through all variables in list of vars in clause
            for var in line_list:
                temp = str(var)     # make sure it is in string format
                # add to dictionaries and increment index
                if temp not in self.var_to_index.keys():
                    self.var_to_index[temp] = loc
                    self.index_to_var[loc] = temp
                    loc += 1

        # initialize assignment list to proper length, where every element is None
        for i in range(len(self.var_to_index.keys())):
            self.assignment.append(None)

        f.close()

    # gsat search algorithm
    def gsat(self):
        # setup
        self.random_assignment()
        iterations = 0
        temp = self.satisfied_clauses(False)

        # while solution not found
        while not temp == len(self.clauses):
            iterations += 1

            # decided not to score the assignment list
            if random.random() > self.threshold:
                i = random.randint(0, len(self.assignment) - 1)
                self.assignment[i] = not self.assignment[i]
            # score the assignment list
            else:
                i = random.choice(list(self.score_assignment()))
                self.assignment[i] = not self.assignment[i]

            # print out syntax and test to see if assignment is satisfied for next iteration
            print("iterations:", iterations, "satisfied clauses:", temp, "/", len(self.clauses))
            temp = self.satisfied_clauses(False)

        # solution found, print out final syntax and return True
        print("iterations:", iterations, "satisfied clauses:", temp, "/", len(self.clauses))
        print("\nGSAT solved after", iterations, "iterations")
        return True

    # returns set of assignment variables with highest # of satisfied clauses after being flipped, for gsat
    def score_assignment(self):
        # setup
        highest_score = -1
        highest_vars = set()

        # iterate through assignment variables
        for i in range(len(self.assignment)):
            # flip the variable, get score, and then unflip
            self.assignment[i] = not self.assignment[i]
            score = self.satisfied_clauses(False)
            self.assignment[i] = not self.assignment[i]

            # if score is > than current highest score, reset the set of vars
            if score > highest_score:
                highest_vars = set()
                highest_score = score
            # if score is >= than current highest score, add it to the set of vars
            if score >= highest_score:
                highest_vars.add(i)

        return highest_vars

    # walksat search algorithm
    def walksat(self):
        # setup
        self.random_assignment()
        temp = self.satisfied_clauses(True)

        # iterate until max flips value is reached
        for i in range(self.max_flips):
            iterations = i + 1

            # check to see if solution is found
            if temp == len(self.clauses):
                print("iterations:", iterations, "satisfied clauses:", temp, "/", len(self.clauses))
                print("\nWALKSAT solved after", iterations, "iterations")
                return True

            # decided not to score the candidate list
            if random.random() > self.threshold:
                i = random.choice(random.choice(list(self.walksat_candidates)).replace('-', '').split())
                self.assignment[self.var_to_index[i]] = not self.assignment[self.var_to_index[i]]
            # decided to score the candidate list
            else:
                i = random.choice(list(self.score_candidates()))
                self.assignment[self.var_to_index[i]] = not self.assignment[self.var_to_index[i]]

            # print out syntax and test to see if assignment is satisfied for next iteration
            # also find new set of candidates
            print("iterations:", iterations, "satisfied clauses:", temp, "/", len(self.clauses))
            temp = self.satisfied_clauses(True)

        print("WALKSAT max flips reached")
        return False

    # reset walksat serch algorithm
    def reset_walksat(self):
        for i in range(self.resets):
            if self.walksat():
                return True
            print(i, "resets")

        return False

    # aging walksat search algorithm
    def aging_walksat(self):
        # setup
        self.random_assignment()
        temp = self.satisfied_clauses(True)

        # iterate until max flips value is reached
        for i in range(self.max_flips):
            iterations = i + 1

            # check to see if solution is found
            if temp == len(self.clauses):
                print("iterations:", iterations, "satisfied clauses:", temp, "/", len(self.clauses))
                print("\nAging WALKSAT solved after", iterations, "iterations")
                return True

            # decided not to score the candidate list
            if random.random() > temp / len(self.clauses):
                i = random.choice(random.choice(list(self.walksat_candidates)).replace('-', '').split())
                self.assignment[self.var_to_index[i]] = not self.assignment[self.var_to_index[i]]
            # decided to score the candidate list
            else:
                i = random.choice(list(self.score_candidates()))
                self.assignment[self.var_to_index[i]] = not self.assignment[self.var_to_index[i]]

            # print out syntax and test to see if assignment is satisfied for next iteration
            # also find new set of candidates
            print("iterations:", iterations, "satisfied clauses:", temp, "/", len(self.clauses))
            temp = self.satisfied_clauses(True)

        print("Aging WALKSAT max flips reached")
        return False

    # returns set of walksat candidates with highest # of clauses satisfied after being flipped, for walksat
    def score_candidates(self):
        # setup
        highest_score = -1
        highest_candidates = set()

        # choose a random unsatisfied clause
        rand_clause = random.choice(list(self.walksat_candidates)).replace('-', '').split()

        # iterate through walksat candidates
        for candidate in rand_clause:
            # flip the score, then get the score, then unflip
            self.assignment[self.var_to_index[candidate]] = not self.assignment[self.var_to_index[candidate]]
            score = self.satisfied_clauses(False)
            self.assignment[self.var_to_index[candidate]] = not self.assignment[self.var_to_index[candidate]]

            # if score is > than current highest score, reset the set of vars
            if score > highest_score:
                highest_candidates = set()
                highest_score = score
            # if score is >= than current highest score, add it to the set of vars
            if score >= highest_score:
                highest_candidates.add(candidate)

        return highest_candidates

    # returns the number of satisfied clauses of the current assignment
    def satisfied_clauses(self, candidate):
        # reset walksat candidates
        self.walksat_candidates = set()
        satisfied = 0

        # iterate through clauses
        for clause in self.clauses:
            # iterate through vars in clauses
            temp = clause.split()
            already_satisfied = False
            for var_assign in range(len(temp)):
                # variable in clause is false when it is supposed to be -> clause is satisfied:
                if str(temp[var_assign])[0] == '-' and not self.assignment[self.var_to_index[temp[var_assign][1:]]] \
                        and not already_satisfied:
                    satisfied += 1
                    already_satisfied = True
                # variable in clause is true when it is supposed to be -> clause is satisfied:
                elif str(temp[var_assign])[0] != '-' and self.assignment[self.var_to_index[temp[var_assign]]] \
                        and not already_satisfied:
                    satisfied += 1
                    already_satisfied = True

            # if clause is not satisfied, add all variables to candidate set (and if told to do so):
            if candidate and not already_satisfied:
                # add clause to candidates set
                self.walksat_candidates.add(clause)

        return satisfied

    # sets the current assignment to a random assignment
    def random_assignment(self):
        for i in range(len(self.assignment)):
            a = random.randint(0, 1)
            self.assignment[i] = a

    # writes the solution to a .sol file with given filename for use by other modules
    def write_solution(self, sol_filename):
        f = open(sol_filename, "w")

        # iterate through variables
        for i in range(len(self.assignment)):
            var = ""

            # if variable is negated, add a '-' sign
            if not self.assignment[i]:
                var += "-"

            # add corresponding clause variable (string), and newline
            var += self.index_to_var[i]
            var += "\n"

            f.write(var)

        f.close()
