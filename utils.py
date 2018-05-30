def ranker(_input, mask = None):
  return list(sorted(zip(_input, map(lambda x: mask[x], range(len(_input))) if mask else range(len(_input))), key=lambda x: -x[0]))

import numpy as np
def ranki(_input, value):
  return int(np.sum(np.asarray(_input, dtype=float) > value, dtype=int))
