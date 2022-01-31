"""

"""

###############################################################################
# initial imports and set-up:

import numpy as np

from .. import synthetic_probability
from .. import utilities as utils

###############################################################################
# function to estimate the flow probability of zero shift:


def estimate_shift(flow, tol=0.05, max_iter=1000, step=100000):
    """
    Compute the normalizing flow estimate of the probability of a parameter shift given the input parameter difference chain. This is done with a Monte Carlo estimate by comparing the probability density at the zero-shift point to that at samples drawn from the normalizing flow approximation of the distribution.

    :param flow: the input flow for a parameter difference distribution.
    :param tol: absolute tolerance on the shift significance, defaults to 0.05.
    :type tol: float, optional
    :param max_iter: maximum number of sampling steps, defaults to 1000.
    :type max_iter: int, optional
    :param step: number of samples per step, defaults to 100000.
    :type step: int, optional
    :return: probability value and error estimate.
    """
    err = np.inf
    counter = max_iter

    _thres = flow.log_probability(flow.cast(np.zeros(flow.num_params)))

    _num_filtered = 0
    _num_samples = 0
    while err > tol and counter >= 0:
        counter -= 1
        _s = flow.sample(step)
        _s_prob = flow.log_probability(_s)
        _t = np.array(_s_prob > _thres)

        _num_filtered += np.sum(_t)
        _num_samples += step
        _P = float(_num_filtered)/float(_num_samples)
        _low, _upper = utils.clopper_pearson_binomial_trial(float(_num_filtered),
                                                            float(_num_samples),
                                                            alpha=0.32)

        err = np.abs(utils.from_confidence_to_sigma(_upper)-utils.from_confidence_to_sigma(_low))

    return _P, _low, _upper

###############################################################################
# helper function to compute tension with default MAF:


def flow_parameter_shift(diff_chain, cache_dir=None, root_name='sprob', tol=0.05, max_iter=1000, step=100000, **kwargs):
    """
    Wrapper function to compute a normalizing flow estimate of the probability of a parameter shift given the input parameter difference chain with a standard MAF. It creates a :class:`~.DiffFlowCallback` object with a :class:`~.SimpleMAF` model (to which kwargs are passed), trains the model and returns the estimated shift probability.
    The function accepts as kwargs all the ones that are relevant for :meth:`~synthetic_probability.flow_from_chain`.

    :param diff_chain: input parameter difference chain.
    :type diff_chain: :class:`~getdist.mcsamples.MCSamples`
    :param cache_dir: name of the directory to save training cache files. If none (default) does not cache.
    :param root_name: root name for the cache files.
    :param tol: absolute tolerance on the shift significance, defaults to 0.05.
    :type tol: float, optional
    :param max_iter: maximum number of sampling steps, defaults to 1000.
    :type max_iter: int, optional
    :param step: number of samples per step, defaults to 100000.
    :type step: int, optional
    :return: probability value and error estimate, then the parameter difference flow
    """

    # initialize and train parameter difference flow:
    diff_flow = synthetic_probability.flow_from_chain(diff_chain, cache_dir=cache_dir, root_name=root_name, **kwargs)
    # Compute tension:
    result = estimate_shift(diff_flow, tol=tol, max_iter=max_iter, step=step)
    #
    return result, diff_flow
