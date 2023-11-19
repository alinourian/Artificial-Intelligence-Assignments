from itsdangerous import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
import seaborn as sns, numpy as np
from scipy.stats import norm
from scipy.stats import expon
from collections import defaultdict
import enum
import os
import datetime
class Sample_Mode(enum.Enum):
    Prior = "prior"
    Rejection = "rejection"
    Weighting = "likelihood weighting"
    Gibbs = "gibbs"

class Node:
    def __init__(self,v,cpt,par_name):
        self.v = v
        self.cpt = cpt
        self.parent = []
        self.parent_name = par_name

    def get_prob(self,evidence):
        if self.parent_name:
            temp_table = self.cpt
            pval = {}
            for p in self.parent_name:
                pval[p] = evidence[p]
            for var, value in pval.items():
                temp_table = temp_table[temp_table[var] == value]
            return float(temp_table["prob"])
        else:
            return float(self.cpt)


    def __hash__(self):
        return hash(self.v)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.v == other.v
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __str__(self) :
        return str(self.v)

class Bayes_Network:
    def __init__(self):
        self.network = defaultdict(list)
        self.Vertices = []
        self.topological_sorted = None
        self.tables = None

    def add_edge(self,Unode,Vnode):
        self.topological_sorted = None
        self.network[Unode].append(Vnode)
        if not (Vnode in self.Vertices):
            self.Vertices.append(Vnode)
        if not (Unode in self.Vertices):
            self.Vertices.append(Unode)
        if not (Unode in Vnode.parent):
            Vnode.parent.append(Unode)

    def joint_prob(self,query:dict,evidence:dict):
        temp_table = self.tables
        for var, value in evidence.items():
            temp_table = temp_table[temp_table[var] == value]
        n = temp_table["prob"].sum()
        for var, value in query.items():
            temp_table = temp_table[temp_table[var] == value]
        m = temp_table["prob"].sum()
        return m/n
    def sample_from_prob(self,p):
        return int(np.random.random() < p)

    def prior_sampling(self,N=1000):
        samples = pd.DataFrame()
        for _ in range(N):
            temp = {}
            for node in self.topological_sorted:
                prob = node.get_prob(temp)
                temp[node.v] = self.sample_from_prob(prob)
            temp["weight"] = 1
            samples = samples.append(temp, ignore_index=True)
        return samples

    def rejection_sampling(self,evidence:dict,N=1000):
        samples = pd.DataFrame()
        for _ in range(N):
            temp = {}
            consictance = True
            for node in self.topological_sorted:
                prob = node.get_prob(temp)
                s = self.sample_from_prob(prob)
                if s != evidence.get(node.v,s):
                    consictance = False
                    break
                temp[node.v] = s
            if consictance:
                temp["weight"] = 1
                samples = samples.append(temp, ignore_index=True)
        return samples

    def weighting_sampling(self,evidence:dict,N=1000):
        samples = pd.DataFrame()
        for _ in range(N):
            temp = {}
            w = 1.0
            for node in self.topological_sorted:
                prob = node.get_prob(temp)
                fixed = evidence.get(node.v,None)
                if fixed:
                    w = prob*w
                    s = fixed
                else:
                    s = self.sample_from_prob(prob)
                temp["weight"] = float(w)
                temp[node.v] = s
            samples = samples.append(temp, ignore_index=True)
        return samples

    def gibbs_sampling(self,evidence:dict,N=1000,gibbs_n = 100):
        samples = pd.DataFrame()
        unfixed = [n for n in self.topological_sorted if n.v not in evidence.keys()]
        cur_sample = {n.v: (np.random.random() < 0.5 ) * 1  for n in unfixed}
        for e in evidence.keys():
            cur_sample[e] = evidence[e]
        for i in range(N+gibbs_n):
            for node in unfixed:
                prob = node.get_prob(cur_sample)
                cur_sample[node.v] = self.sample_from_prob(prob)
            cur_sample["weight"] = 1    
            if i >= gibbs_n:
                samples = samples.append(cur_sample, ignore_index=True)
        return samples

    def sample(self,evidence:dict,N=1000,mode = Sample_Mode.Gibbs,gibbs_n = 100) -> pd.DataFrame:
        np.random.seed(int(str(datetime.datetime.now().strftime("%H%M%S"))))
        if mode == Sample_Mode.Prior:
            return self.prior_sampling(N=N)
        elif mode == Sample_Mode.Rejection:
            return self.rejection_sampling(evidence=evidence,N=N)
        elif mode == Sample_Mode.Weighting:
            return self.weighting_sampling(evidence=evidence,N=N)
        elif mode == Sample_Mode.Gibbs:
            return self.gibbs_sampling(evidence=evidence,N=N,gibbs_n=gibbs_n)
        else:
            pass
        
    def get_prob_by_sample(self,query:dict,evidence:dict,N=1000,mode = Sample_Mode.Gibbs,gibbs_n = 100):
        samples = self.sample(evidence=evidence,N=N , mode= mode,gibbs_n=gibbs_n)
        if mode == Sample_Mode.Prior:
            for v,l in evidence.items():
                samples = samples[samples[v] == l]
            n = samples["weight"].sum()
            for v,l in query.items():
                samples = samples[samples[v] == l]
            m = samples["weight"].sum()
            return m/n if n > 0 else 0
        n = samples["weight"].sum()
        for v,l in query.items():
            samples = samples[samples[v] == l]
        m = samples["weight"].sum()
        return m/n if n > 0 else 0
    def recurs_sort(self,node,visited,stack):
        visited[node] = True
        
        for v in self.network[node]:
            if not visited[v]:
                self.recurs_sort(v,visited,stack)
        stack.insert(0,node)
        
    def topo_sort(self):
        false_return = lambda : False
        visited = defaultdict(false_return)
        stack =[]
        for node in self.Vertices:
            if not visited[node]:
                self.recurs_sort(node,visited,stack)
        self.topological_sorted = stack
        return stack
        
    def print_topo(self):
        result = ""
        for v in self.topological_sorted:
            result += str(v.v)+" "
        print(result)  
    
    def get_prob(self,all):
        p = 1
        for node in self.topological_sorted:
            prob = node.get_prob(all)
            p *= prob if all[node.v] == 1 else 1-prob
        return p


    def complete_table(self):
        self.tables = pd.DataFrame(columns=[n.v for n in self.network ])
        self.tables["prob"] = 0
        size = len(self.Vertices)
        for i in range(2**size):
            row = list(map(int,list(bin(i)[2:].zfill(size))))
            df2 = pd.DataFrame(columns=[n.v for n in self.network] , data=[row])
            df2["prob"] = self.get_prob({ n.v : df2[n.v].to_numpy()[0] for n in self.network })
            self.tables = self.tables.append(df2, ignore_index=True)

    def read_network(self,input_file):
        f = open(input_file,mode = "r")
        number_of_node = int(f.readline())
        node_dict = {}
        for  _ in range(number_of_node): 
            main_node = f.readline().strip()
            line = f.readline().strip()
            try:
                    float_p = float(line)
                    node_dict[main_node] = Node(main_node,float_p,None)
            except:
                col = line.strip().split(" ")
                col.append("prob")
                cpt = []
                for j in range(2**(len(col)-1)):
                    cpt.append(list(map(float,f.readline().strip().split(" "))))
                node_dict[main_node] = Node(main_node,pd.DataFrame(cpt,columns=col),col[:-1])
        f.close()
        for key in node_dict:
            main_node = node_dict[key]
            if main_node.parent_name:
                for p in main_node.parent_name:
                    self.add_edge(node_dict[p],main_node)
        self.topo_sort()
        self.complete_table()
if not os.path.isdir("output"):
    os.system("mkdir output")
for dir in  os.listdir("./inputs"):
    time_s = datetime.datetime.now()
    g= Bayes_Network()
    add = f"./inputs/{dir}"
    graph_path = f"{add}/input.txt"
    q_path = f"{add}/q_input.txt"
    if os.path.isfile(graph_path) and os.path.isfile(q_path):
        g.read_network(f"{add}/input.txt") 
        g.print_topo()
        queris = json.load(open(q_path,"r"))
        res = ""
        real_p = []
        p_p = []
        r_p = []
        w_p = []
        g_p = []
        for q in queris:
            print(f"file {dir} : q{len(real_p)+1}")
            query = q[0]
            evidence = q[1]
            r = np.round(g.joint_prob(query,evidence),5)
            real_p.append(r)
            p_p.append(np.round(np.abs(g.get_prob_by_sample(query,evidence,N = 1000 , mode= Sample_Mode.Prior) - r ),5))
            r_p.append(np.round(np.abs(g.get_prob_by_sample(query,evidence,N = 1000 , mode= Sample_Mode.Rejection)- r),5) )
            w_p.append(np.round(np.abs(g.get_prob_by_sample(query,evidence,N = 1000 , mode= Sample_Mode.Weighting )- r),5) )
            g_p.append(np.round(np.abs(g.get_prob_by_sample(query,evidence,N = 2000 , mode= Sample_Mode.Gibbs , gibbs_n=2000)- r),5) )
        for i in range(len(real_p)):
            res+= f"{real_p[i]} {p_p[i]} {r_p[i]} {w_p[i]} {g_p[i]}\n"
        print(res)
        f = open(f"output/{dir}.txt","w")
        f.write(res)
        f.close()
        index = list(range(1,len(queris)+1))
        plt.plot(index, p_p, '-o', c='r')
        plt.plot(index, r_p, '-o', c='g')
        plt.plot(index, w_p, '-o', c='b')
        plt.plot(index, g_p, '-o', c='y')
        plt.legend(['Prior','Rejection','Likelihood Weighting','Gibbs'])
        plt.ylabel('MAE')
        plt.xlabel('#Q')
        plt.savefig(f"output/{dir}.png")
        plt.clf() 
    time_e = datetime.datetime.now()
    print(f"network {dir} started at {time_s}\nnetwork {dir} ended at {time_e}\nwhole took {time_e-time_s}")

