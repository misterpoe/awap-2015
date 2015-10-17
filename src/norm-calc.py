from scipy.stats import norm

print [norm.cdf((i+1)*0.001)-0.5 for i in xrange(5000)]
