"""Exact binomial computations for rule 3's example and the H-03 record of record-format.md.

Run: python3 -I rule3_stats.py
"""
from math import comb


def pmf(n, p, k):
    return comb(n, k) * p**k * (1 - p) ** (n - k)


def fisher_one_sided(a, b, n1=10, n2=10):
    k, n = a + b, n1 + n2
    def h(x):
        return comb(k, x) * comb(n - k, n1 - x) / comb(n, n1) if 0 <= k - x <= n2 else 0.0
    return sum(h(x) for x in range(a, min(k, n1) + 1))


def fisher_two_sided(a, b, n1=10, n2=10):
    k, n = a + b, n1 + n2
    def h(x):
        return comb(k, x) * comb(n - k, n1 - x) / comb(n, n1) if 0 <= k - x <= n2 else 0.0
    obs = h(a)
    return sum(h(x) for x in range(0, n1 + 1) if h(x) <= obs + 1e-12)


print("rule 3 example 9/10 vs 4/10: Fisher one-sided p = %.4f, two-sided p = %.4f"
      % (fisher_one_sided(9, 4), fisher_two_sided(9, 4)))
for p in (0.5, 0.8):
    pr = sum(pmf(10, p, a) * pmf(10, p, b) for a in range(11) for b in range(11) if a - b >= 1)
    print("H-03, no effect, true share %.1f in both arms, 10 runs/arm: P(with-arm >= 10 points above) = %.3f" % (p, pr))
pw = sum(pmf(10, 0.9, a) * pmf(10, 0.4, b) for a in range(11) for b in range(11) if fisher_one_sided(a, b) <= 0.05)
print("power, one-sided Fisher at alpha 0.05, true 0.9 vs 0.4, 10 runs/arm = %.3f" % pw)
