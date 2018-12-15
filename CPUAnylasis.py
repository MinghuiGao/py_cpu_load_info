# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
# https://blog.csdn.net/qq_29721419/article/details/71638912
name_list = ['Monday', 'Tuesday', 'Friday', 'Sunday']

num_list = [1.5, 0.6, 7.8, 6]
num_list1 = [1, 2, 3, 1]
plt.bar(range(len(num_list)), num_list, label='boy', fc='y')
plt.bar(range(len(num_list)), num_list1, bottom=num_list, label='girl', tick_label=name_list,
        fc='r')
plt.bar(range(len(num_list)), num_list1, bottom=num_list, label='robot', tick_label=name_list,
        fc='r')
plt.bar()
plt.legend()
plt.show()

