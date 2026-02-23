import math
import random
import matplotlib.pyplot as plt

n=10000
lambda_parametr=5
srednia_parametr=10
sigma_parametr=2

def generator_poissona(lam, n):
    wyniki=[]
    q=math.exp(-lam)
    for _ in range(n):
        X=-1
        S=1
        while S>q:
            S=S*random.random()
            X+=1
        wyniki.append(X)
    return wyniki

def generator_normalny(mu, sigma, n):
    wyniki=[]
    for _ in range(n):
        liczba=random.gauss(mu,sigma)
        wyniki.append(liczba)
    return wyniki

dane_poisson=generator_poissona(lambda_parametr, n)
dane_normal=generator_normalny(srednia_parametr, sigma_parametr, n)


plt.figure(figsize=(10,8))

plt.subplot(1,2,1)
plt.hist(dane_poisson, bins=range(min(dane_poisson),max(dane_poisson)+2))
plt.title("Rozkład Poissona")

plt.subplot(1,2,2)
plt.hist(dane_normal, bins=50)
plt.title("Rozkład Normalny")


plt.tight_layout()
plt.show()
