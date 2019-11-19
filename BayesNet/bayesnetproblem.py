from .probability import BayesNet, elimination_ask

class Problem:
    def __init__(self, fh):
        # Place here your code to load problem from opened file object fh
        # and use probability.BayesNet() to create the Bayesian network
        pass
    def solve(self):
        # Place here your code to determine the maximum likelihood solution
        # returning the solution room name and likelihood
        # use probability.elimination_ask() to perform probabilistic inference
        room, likelihood = 0, 0
        return (room, likelihood)
    def solver(input_file):
        return Problem(input_file).solve()