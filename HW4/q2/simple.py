import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
import sys
import seaborn as sns, numpy as np
from scipy.stats import norm
import os
if not os.path.isdir("part1"):
    os.system("mkdir part1")
original_stdout = sys.stdout
file = open("part1/log.txt","w")
sys.stdout = file
def sample_single_gaussian(mean,var,N_semi_sample = 100):
    temp_var = np.sqrt(var * 12 * N_semi_sample)
    temp_mean = 2*mean
    a = (temp_mean-temp_var)/2
    b = (temp_var+temp_mean)/2
    return np.sum(np.random.uniform(a,b,N_semi_sample))/N_semi_sample
    
def sample_gaussian(mean,var,N):
    return [sample_single_gaussian(mean,var) for _ in range(N)]

def sample_exp_each(l):
    s_n = np.random.uniform(0,1,1)
    while s_n >= 1:
         s_n = np.random.uniform(0,1,1)
    return -(np.log(1-s_n)/l)[0]

def sample_exp(l,N):
    return [sample_exp_each(l) for _ in range(N)] 

def sample_geo_each(p):
    assert p > 0 and p < 1 ,"P should be between 0 and 1"
    s_n = np.round(np.log(np.random.uniform(0,1,1)) / np.log(1-p))[0]
    while s_n <=0 :
         s_n = np.round(np.log(np.random.uniform(0,1,1)) / np.log(1-p))[0]
    return s_n

def sample_geo(p,N):
    assert p >= 0 and p <= 1 ,"P should be between 0 and 1"
    return [sample_geo_each(p) for _ in range(N)] 

def sampling(p : np.array ,prob_s :list ,N):
    assert np.sum(p)==1 ,"coefs should add up to 1"
    s = [[] for _ in range(len(p))]
    for i,prob in enumerate(prob_s):
        f,args = prob
        args = list(args)
        args.append(N)
        s[i] = f(*tuple(args))
    rg = np.arange(0, len(p), 1, dtype=int)
    index_gen = lambda p : random.choices(population= rg,weights= p, k = 1)[0]
    sample = np.array([s[index_gen(p)][j] for j in range(N)])
    return sample

def pdf(p : np.array ,prob_pdf,x):
    assert np.sum(p)==1 ,"coefs should add up to 1"
    prob = 0
    for ind,P in enumerate(p):
        f,args = prob_pdf[ind]
        args = list(args)
        args.insert(0,x)
        prob+=P* f(*args)
    return prob#
exp_dist = lambda x,l: l*np.exp(-l*x) * (x>= 0)
geo_dist = lambda k,p: ((1-p)**(k-1))*p * ((int(k) == k) and (k >= 1))

prob_s = [(sample_gaussian,tuple((4,2))),(sample_gaussian,tuple((3,2))),(sample_exp,tuple((0.01,)))]
coef = [3/10,3/10,4/10]
sample = sampling(np.array(coef),prob_s,100000)
print(f"1 {np.round(np.mean(sample),4)} {np.round(np.std(sample),4)}")
fig = plt.figure(figsize=(20,10))
sns.set_theme()
sns.distplot(sample,bins=100)
plt.savefig("part1/pdf1_sample.png")
prob_pdf = [(norm.pdf,tuple((4,np.sqrt(2)))),(norm.pdf,tuple((3,np.sqrt(2)))),(exp_dist,tuple((0.01,)))]
x = np.arange(-20,100,0.1)
y = [pdf(coef,prob_pdf=prob_pdf,x = j) for j in x]
fig = plt.figure(figsize=(20,10))
plt.plot(x,y)
plt.savefig("part1/pdf1.png")

prob_s = [(sample_gaussian,tuple((0,10))),(sample_gaussian,tuple((20,15))),(sample_gaussian,tuple((-10,8))),(sample_gaussian,tuple((50,25)))]
coef = [2/10,2/10,3/10,3/10]
sample = sampling(np.array(coef),prob_s,100000)
print(f"2 {np.round(np.mean(sample),4)} {np.round(np.std(sample),4)}")
fig = plt.figure(figsize=(20,10))
sns.set_theme()
sns.distplot(sample,bins=150)
plt.savefig("part1/pdf2_sample.png")
prob_pdf = [(norm.pdf,tuple((0,np.sqrt(10)))),(norm.pdf,tuple((20,np.sqrt(15)))),(norm.pdf,tuple((-10,np.sqrt(8)))),(norm.pdf,tuple((50,5)))]
x = np.arange(-20,70,0.1)
y = [pdf(coef,prob_pdf=prob_pdf,x = j) for j in x]
fig = plt.figure(figsize=(20,10))
plt.plot(x,y)
plt.savefig("part1/pdf2.png")


coef = [2/10,2/10,2/10,4/10]
prob_s = [(sample_geo,tuple((0.1,))),(sample_geo,tuple((0.5,))),(sample_geo,tuple((0.3,))),(sample_geo,tuple((0.04,)))]
sample = sampling(np.array(coef),prob_s,100000)
print(f"3 {np.round(np.mean(sample),4)} {np.round(np.std(sample),4)}")
fig = plt.figure(figsize=(20,10))
sns.set_theme()
sns.distplot(sample,bins=150)
fig = plt.figure(figsize=(20,10))
sns.set_theme()
sns.distplot(sample,bins=150)
plt.savefig("part1/pdf3_sample.png")
prob_pdf = [(geo_dist,tuple((0.1,))),(geo_dist,tuple((0.5,))),(geo_dist,tuple((0.3,))),(geo_dist,tuple((0.04,)))]
x = np.arange(-5,100,1)
y = [pdf(coef,prob_pdf=prob_pdf,x = j) for j in x]
fig = plt.figure(figsize=(20,10))
plt.scatter(x,y)
plt.savefig("part1/pdf3.png")

sys.stdout = original_stdout
file.close()