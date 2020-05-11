from scipy.stats import genextreme
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import expon
data = pd.read_csv("times.csv")
data_list = data['data'].tolist()
parrams = genextreme.fit(data_list)

fig, ax = plt.subplots(1, 1)
c1 = -0.7776
scale1 = 15.08
loc1 = 13.16

rv1 = genextreme(c=c1, scale=scale1, loc=loc1)
rv2 = genextreme(c=parrams[0], scale=parrams[1], loc=parrams[2])

x1 = np.linspace(rv1.ppf(0.00001),
                 rv1.ppf(0.99999), 100)
x2 = np.linspace(rv2.ppf(0.00001),
                 rv2.ppf(0.99999), 100)

ax.plot(x2, rv2.pdf(x2), 'r-', lw=5, label='scipy')
ax.plot(x1, rv1.pdf(x1), 'k-', lw=2, label='matlab')
plt.show()
