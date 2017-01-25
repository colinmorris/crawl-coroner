# Credit goes to http://stackoverflow.com/a/24023800/262271
import math

def binconf(p, n, c=0.95):
  '''
  Calculate binomial confidence interval based on the number of positive and
  negative events observed.

  Parameters
  ----------
  p: int
      number of positive events observed
  n: int
      number of negative events observed
  c : optional, [0,1]
      confidence percentage. e.g. 0.95 means 95% confident the probability of
      success lies between the 2 returned values

  Returns
  -------
  theta_low  : float
      lower bound on confidence interval
  theta_high : float
      upper bound on confidence interval
  '''
  p, n = float(p), float(n)
  N    = p + n

  if N == 0.0: return (0.0, 1.0)

  p = p / N
  z = normcdfi(1 - 0.5 * (1-c))

  a1 = 1.0 / (1.0 + z * z / N)
  a2 = p + z * z / (2 * N)
  a3 = z * math.sqrt(p * (1-p) / N + z * z / (4 * N * N))

  return (a1 * (a2 - a3), a1 * (a2 + a3))


def erfi(x):
  """Approximation to inverse error function"""
  a  = 0.147  # MAGIC!!!
  a1 = math.log(1 - x * x)
  a2 = (
    2.0 / (math.pi * a)
    + a1 / 2.0
  )

  return (
    sign(x) *
    math.sqrt( math.sqrt(a2 * a2 - a1 / a) - a2 )
  )


def sign(x):
  if x  < 0: return -1
  if x == 0: return  0
  if x  > 0: return  1


def normcdfi(p, mu=0.0, sigma2=1.0):
  """Inverse CDF of normal distribution"""
  if mu == 0.0 and sigma2 == 1.0:
    return math.sqrt(2) * erfi(2 * p - 1)
  else:
    return mu + math.sqrt(sigma2) * normcdfi(p)
