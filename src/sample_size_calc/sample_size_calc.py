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

    def statistical_power(self, n, p_intervention,p_control, alpha=None):
        """
        Calculate the Statistical Power for two sample one side t-test for RCT

        Assumptions:
         sample size in control and intervention are equal
         variance of intervention and control are equal

        :param n: int - sample size per arm
        :param p_intervention: float - proportion of intervention e.g 0.1
        :param p_control: float - proportion of control e.g 0.05
        :param alpha: float - type I error rate. default 0.05
        :return: power: float - power (1-beta)
        """


        if not alpha:
            alpha = self.alpha

        var = (p_intervention * (1 - p_intervention)) + (p_control * (1 - p_control))
        d = p_intervention - p_control
        z_beta = (d * math.sqrt(n/var)) - stats.norm.ppf(1-alpha)
        power = 1-stats.norm.sf(abs(z_beta))
        return power

    def sample_size_continuous(self, mu_a, mu_b, std_a, std_b, samp_ratio, alpha=None, beta=None):
        """
        Sample size required to measure difference between to continuous variables

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

    def sample_size_rct(self,
                        d,
                        p_intervention,
                        p_control,
                        alpha=None,
                        beta=None,
                        super_margin=0):

        """
        Provides sample size for RCT (This is the total patients in the control + intervention arm)

        Sample size required to detect difference "d" to a specific type I error rate, and a given power.

        Two samples, one-sided test. We are only interested in measuring

        params:
            d - float: detectable difference between control and intervention e.g d = $\mu_1$ - $\mu_0$ = 0.10
            p_intervention - float:  expected proportion of interest in the intervention group.
            p_control - float: expected proportion of interest in the control group.
            alpha - float, default = 0.05 type I error rate
            beta - float, default = 0.2: type II error rate (1-beta) = Power
            super_margin - float, default = 0: superiority margin e.g requiring the intervention to be greater than control by some fixed amount.

        return:
            n - int - sample size
        """

        if not alpha:
            alpha = self.alpha

        if not beta:
            beta = self.beta

        # Variance of dichotomous outcome
        # (dropped 1/2, cancels with 2 from Zscore / d)
        var = (p_intervention * (1 - p_intervention)) + (p_control * (1 - p_control))

        # Zscore / detectable diff
        # (dropped factor of 2, cancels with 1/2 from variance)
        z_d = ((stats.norm.ppf(1 - alpha) + stats.norm.ppf(1-beta)) / (d - super_margin)) ** 2

        # Sample size rounded up to next whole person.
        # multiplied by 2 because we need this many patients for control and intervention arm
        n = math.ceil(var * z_d) * 2

        if n % 2 == 0:
            return n
        else:
            return n+1

    def detectable_diff_rct(self, n, p_intervention, p_control, alpha=None, beta=None, super_margin=0):

        """
        Provides the detectable difference "d" for RCT

        difference between control and intervention group, given a type I error rate, power and sample size

        params:
            n - int: sample size per arm in RCT
            p_intervention - float:  expected proportion of interest in the intervention group.
            p_control - float: expected proportion of interest in the control group.
            alpha - float, default = 0.05: type I error rate
            beta - float, default = 0.2: type II error rate (1-beta) = Power
            super_margin - float, default = 0: superiority margin e.g requiring the intervention to be greater than control by some fixed amount.

        return:
            d - float -  diff (3 sig fig)
        """

        if not alpha:
            alpha = self.alpha

        if not beta:
            beta = self.beta

            # Variance of dichotomous outcome (dropped 1/2, cancels with 2 from Zscore / d)
        var = (p_intervention * (1 - p_intervention)) + (p_control * (1 - p_control))

        # Zscore / detectable diff (dropped factor of 2, cancels with 1/2 from variance)
        z = stats.norm.ppf(1 - alpha) + stats.norm.ppf(1-beta)

        # Sample size rounded up to next whole person.
        d = math.sqrt(var / n) * z

        return round(d, 3)

    def VIF(self, m, p, cv=None):
        """
        Variance Inflation Factor

        params:
            m - int: average patients per cluser
            p - float: inter cluster correlation coefficient
            cv - float: coefficient of variantion within cluster

        returns:
            vif - float: Variance Inflation Factor

        """
        if cv:
            vif = 1 + ((1 + cv ** 2) * m - 1) * p
        else:
            vif = 1 + (m - 1) * p

        return vif

    def sample_size_crct(self,
                         d,
                         p_intervention,
                         p_control,
                         m,
                         p,
                         cv=None,
                         alpha=None,
                         beta=None,
                         super_margin=0):

        """

        Sample size required for CRCT (This is the total patients in the control + intervention arm)

        Sample size required for CRCT to detect difference "d" to a specifief type I error rate, and a given power.

        params:
            d - float: detectable difference between control and intervention e.g d = $\mu_1$ - $\mu_0$ = 0.10
            p_intervention - float:  expected proportion of interest in the intervention group.
            p_control - float: expected proportion of interest in the control group.
            m - int: Average cluster size
            p - float: Intra cluster correlation
            cv - float: Coefficient of variation
            alpha - float, default = 0.05: type I error rate
            beta - float, default = 0.2: type II error rate (1-beta) = Power
            super_margin - float, default = 0: superiority margin e.g requiring the intervention to be greater than control by some fixed amount.

        return:
            n - int - sample size
        """

        n = math.ceil(self.sample_size_rct(d,
                                              p_intervention,
                                              p_control,
                                              alpha,
                                              beta,
                                              super_margin) * self.VIF(m, p, cv))

        if n % 2 == 0:
            return n
        else:
            return n+1

    def detectable_diff_crct(self,
                             k,
                             p_control,
                             p,
                             alpha=None,
                             beta=None):
        """
        Provides the detectable difference "d" for CRCT

        Detectable difference between control and intervention group, given a type I error rate, power

        params:
            k - int: Number of clusters
            p_control - float: expected proportion of interest in the control group.
            p - float: Intra cluster correlation
            alpha - float, default = 0.05: type I error rate
            beta - float, default = 0.2: type II error rate (1-beta) = Power

        return:
            d - float -  diff (3 sig fig)
        """
        if not alpha:
            alpha = self.alpha

        if not beta:
            beta = self.beta

        z = stats.norm.ppf(1 - alpha) + stats.norm.ppf(1-beta)
        w = (p*z**2)/k

        a = -(1+w)
        b = 2*p_control + w
        c = w*p_control*(1-p_control)-p_control**2

        p_intervention_1 = (-b + math.sqrt((b ** 2) - 4 * a * c)) / 2 * a
        p_intervention_2 = (-b - math.sqrt((b ** 2) - 4 * a * c)) / 2 * a

        d = max(abs(p_intervention_1-p_control), abs(p_intervention_2-p_control))

        return round(d, 3)


    def num_cluster_required(self, d,
                             p_intervention,
                             p_control,
                             m,
                             p,
                             cv=None,
                             alpha=None,
                             beta=None,
                             super_margin=0):
        """
        Number of clusters required to detect diff at a given alpha beta with an average num of pat per cluster

        params:
            d - float: detectable difference between control and intervention e.g d = $\mu_1$ - $\mu_0$ = 0.10
            p_intervention - float:  expected proportion of interest in the intervention group.
            p_control - float: expected proportion of interest in the control group.
            m - int: Average cluster size
            p - float: Intra cluster correlation
            cv - float: Coefficient of variation
            alpha - float, default = 0.05: type I error rate
            beta - float, default = 0.2: type II error rate (1-beta) = Power
            super_margin - float, default = 0: superiority margin e.g requiring the intervention to be greater than control by some fixed amount.

        returns:
            k - int: number of clusters (requires an even number so it can be split between control and intervention)

        """

        nc = self.sample_size_rct(d,
                                  p_intervention,
                                  p_control,
                                  alpha,
                                  beta,
                                  super_margin) * self.VIF(m, p, cv)

        if math.ceil(nc / m) % 2 == 0:
            return math.ceil(nc / m)
        else:
            return math.ceil(nc / m) + 1

    def avg_pat_per_cluster_required(self, n, k, p, cv=None):
        """
        Number of clusters required to detect diff at a given alpha beta with an average num of pat per cluster

        params:
            n - int: sample size for RCT
            k - int: num of clusters per arm
            p - float: Inter-cluster correlation coefficient

        returns:
            m_avg - int: average number of patients per cluster

        """

        if cv:
            m_avg = n*(1 - p) / (k - n*p*(1 + cv**2))
        else:
            m_avg = n*(1 - p) / (k - n*p)

        if m_avg < 0:
            return 'Insufficient number of Clusters'

        return math.ceil(m_avg)
