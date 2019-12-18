# Modified by Paolo Takagi-Atilano, October 26, 2017

from display import display_sudoku_solution
import random, sys
import time
from SAT import SAT

if __name__ == "__main__":
    # for testing, always initialize the pseudorandom number generator to output the same sequence
    #  of values:
    random.seed(1)

    puzzle_name = str(sys.argv[1][:-4])
    sol_filename = puzzle_name + ".sol"

    sat = SAT(sys.argv[1])

    start_time = time.clock()

    #result = sat.aging_walksat()
    result = sat.reset_walksat()
    #result = sat.walksat()
    #result = sat.gsat()


    if result:
        print("--- %s seconds ---" % (time.clock() - start_time))
        sat.write_solution(sol_filename)
        display_sudoku_solution(sol_filename)
