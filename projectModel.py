# import sympy
import numpy as np
import math
import csv
from collections import defaultdict
import matplotlib.pyplot as plt
from scipy.optimize import leastsq


def dict2csv(record_dic):
    with open('record_data.csv', 'w', newline = '') as f:
        w = csv.writer(f, record_dic.keys(),  quotechar = '|', delimiter = ',', quoting = csv.QUOTE_ALL)
        for key, value in record_dic.items():
            w.writerow((key, value))
        f.close()

def csv2dict(file_name):
    model_dict = defaultdict(list)
    with open(file_name, 'r') as f:
        w = csv.reader(f, quotechar = '|', delimiter = ',', quoting = csv.QUOTE_ALL)
        for eachline in w:
            dic_key = int(eachline[0])
            dic_value =eachline[1]
            dic_value = dic_value.replace('[', '')
            dic_value = dic_value.replace(']', '')
            dic_value = dic_value.split(',')
            model_dict[dic_key] = [int(n) for n in dic_value]
        f.close()
    return model_dict


def dis_RSSI_func(p, R):
    #  A is the signal strength of 1m
    # N is the Environmental attenuation factor
    A,N = p
    return 10 ** ((abs(R) - A) / (10 * N))


def error(p,R,D):
    return dis_RSSI_func(p,R) - D



# NEED DONE SOON
def RSSI_leastsq(model_dic):
    dis_list = []
    RSSI_list = []
    key_list = list(model_dic.keys())
    key_list.sort()
    for eachkey in key_list:
        value_list = model_dic[eachkey]
        dis = eachkey
        avg_RSSI = np.mean(value_list)
        dis_list.append(dis)
        RSSI_list.append(avg_RSSI)

    plt.xlim((-100, 0))
    plt.ylim((0, 800))
    Di = np.array(dis_list)
    Ri = np.array(RSSI_list)

    p0 = [-20,4] #start value area of N, A

    para = leastsq(error, p0, args=(Ri,Di))


    plt.figure

    R = np.linspace(-101,-1, 100)
    p_value = [-16.5, 3.45]
    D = dis_RSSI_func(p_value, R)
    D_fitted = dis_RSSI_func(para[0], R)


    plt.plot(R, D,  label = 'correct curve', color = 'b')
    plt.plot(R, D_fitted, label = 'Fitted curve', color = 'r')
    plt.plot(RSSI_list, dis_list, 'o' )

    plt.legend
    print(para[0])

    plt.show()


file_name = 'record_data.csv'
model_dic = csv2dict(file_name)

RSSI_leastsq(model_dic)

