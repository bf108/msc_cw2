import scipy.stats as stats
import math


class SampleSizeCalculator:

    def __init__(self, alpha=None, beta=None):

        if alpha:
            self.alpha = alpha
        else:
            self.alpha = 0.05

        if beta:
            self.beta = beta
        else:
            self.beta = 0.2

    def update_alpha(self, alpha_new):
        self.alpha = alpha_new

    def update_beta(self, beta_new):
        self.beta = beta_new

    def sample_size_continuous(self, mu_a, mu_b, std_a, std_b, samp_ratio, alpha=None, beta=None):
        """
        Sample size required to measure difference between two continuous variables.
        
        Assume variable follow a normal distribution.

        :param mu_a: float: mean of variable a
        :param mu_b: float: mean of variable b
        :param std_a: float:standard deviation of variable a
        :param std_b: float: standard deviation of variable b
        :param samp_ratio: float: ratio of samples n_a/n_b
        :param alpha: float: significance level (type I error) typically 0.05
        :param beta: float: type II error typically 0.2. 1 - beta = Power
        :return: tuple (int, int): sample size required for n_a, n_b respectively
        """
        if not alpha:
            alpha = self.alpha

        if not beta:
            beta = self.beta

        std = (std_a**2 + (std_b**2)/samp_ratio)
        z = stats.norm.ppf(1-alpha) + stats.norm.ppf(1-beta)
        d = mu_a - mu_b

        n_a = std*((z/d)**2)
        n_b = samp_ratio*n_a

        return (math.ceil(n_a), math.ceil(n_b))

