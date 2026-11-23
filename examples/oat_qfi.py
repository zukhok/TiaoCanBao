import numpy as np
from scipy.special import gammaln

# ---- parameters ----
N = 100          # number of atoms
chi = 1.0        # one-axis twisting strength
t_max = 0.1      # final evolution time
n_t = 200        # number of time points
eps = 1e-12      # guard against division by zero


def css_x(N):
    # implements Eq.(2): coherent spin state along +x
    j = N / 2
    m = np.arange(-j, j + 1)
    k = (m + j).astype(int)
    logc = 0.5 * (gammaln(N + 1) - gammaln(k + 1) - gammaln(N - k + 1)) - 0.5 * N * np.log(2)
    return m, np.exp(logc).astype(complex)


def evolve(c, m, chi, t):
    # implements Eq.(3): psi_m(t) = c_m exp(-i chi t m^2)
    return c * np.exp(-1j * chi * t * m**2)


def covariance(psi, m, N):
    # implements Eq.(4): symmetrised covariance of (Jx, Jy, Jz)
    j = N / 2
    p = np.abs(psi) ** 2
    a = np.sqrt(j * (j + 1) - m[:-1] * (m[:-1] + 1))
    Jp = np.sum(a * np.conj(psi[1:]) * psi[:-1])
    Jp2 = np.sum(a[:-1] * a[1:] * np.conj(psi[2:]) * psi[:-2])
    JpJz = np.sum(a * np.conj(psi[1:]) * psi[:-1] * (2 * m[:-1] + 1))
    Jz, Jz2 = np.sum(p * m), np.sum(p * m**2)
    rest = j * (j + 1) - Jz2
    mean = np.array([Jp.real, Jp.imag, Jz])
    S = np.array([
        [(Jp2.real + rest) / 2, Jp2.imag / 2, JpJz.real / 2],
        [Jp2.imag / 2, (rest - Jp2.real) / 2, JpJz.imag / 2],
        [JpJz.real / 2, JpJz.imag / 2, Jz2],
    ])
    return mean, S - np.outer(mean, mean)


def qfi(cov):
    # implements Eq.(5): F_Q = 4 * largest eigenvalue of the covariance
    return 4 * np.linalg.eigvalsh(cov)[-1]


def squeezing(mean, cov, N):
    # implements Eq.(6): Wineland parameter, minimum variance orthogonal to <J>
    n0 = mean / (np.linalg.norm(mean) + eps)
    e1 = np.cross(n0, [0, 0, 1])
    if np.linalg.norm(e1) < 1e-6:
        e1 = np.cross(n0, [0, 1, 0])
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(n0, e1)
    B = np.array([e1, e2])
    var_min = np.linalg.eigvalsh(B @ cov @ B.T)[0]
    return N * var_min / (np.dot(mean, mean) + eps)


def run():
    m, c = css_x(N)
    ts = np.linspace(0, t_max, n_t)
    F, xi2 = [], []
    for t in ts:
        mean, cov = covariance(evolve(c, m, chi, t), m, N)
        F.append(qfi(cov) / N)
        xi2.append(squeezing(mean, cov, N))
    return ts, np.array(F), 1 / np.array(xi2)


if __name__ == "__main__":
    ts, F, inv_xi2 = run()
    print(f"max F_Q/N = {F.max():.2f}, max 1/xi^2 = {inv_xi2.max():.2f}")
