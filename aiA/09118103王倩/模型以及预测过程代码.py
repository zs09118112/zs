import torch.nn as nn
import numpy as np
import heapq
import torch
from torch.nn import functional as F
import csv

# 读取大学数据
with open('colleges.csv') as f:
    reader = csv.reader(f)
    rows = [row for row in reader]

# 修改大学数据格式
schools = rows[1:]
for college in schools:
    college[1] = float(college[1])
    college[2] = float(college[2])
    college[3] = float(college[3])

# X 为当前学生数据 (经度，纬度，排名），为示范数据
X_np = np.array([0.4, 0.2, 0.1])  # np.ndarray格式
X = torch.from_numpy(X_np)  # torch.Tensor格式

###################################################################################
'''
流程1：输出预测的大学值
'''
class model1(nn.Module):
    '''
    输入：学生排名、学生经纬度
    输出：大学排名、大学经纬度
    '''
    def __init__(self, input_size=3, hidden1_size=4, hidden2_size=4, hidden3_size=4, output_size=3):
        super(model1, self).__init__()
        self.layer1 = nn.Sequential(nn.Linear(input_size, hidden1_size), nn.Sigmoid())
        self.layer2 = nn.Sequential(nn.Linear(hidden1_size, hidden2_size), nn.Sigmoid())
        self.layer3 = nn.Sequential(nn.Linear(hidden2_size, hidden3_size), nn.Sigmoid())
        self.layer4 = nn.Sequential(nn.Linear(hidden3_size, output_size))

    def forward(self, x):
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = F.softmax(x, dim=0)
        return x


mymodel1 = model1().double()
predict_school = mymodel1(X)
print('predict_school:', predict_school)

###################################################################################
'''
流程2：对于所有的大学，选与流程1输出大学距离最近的前10所大学
'''

# 下面利用流程1的预测大学值，从这些可选大学中再做筛选

distances = []  # 用于存储每所可选大学与预测大学的距离
for school in schools:
    school = torch.from_numpy(np.array(school[1:4]))
    distances.append(torch.dist(school, predict_school))

better_schools_index = list(map(distances.index, heapq.nsmallest(10, distances)))  # 选取可选大学中，与预测大学距离最近的10个大学索引
better_schools = []  # 可选大学中与预测大学最近的前十个大学命名为better_schools
for better_school_index in better_schools_index:
    better_schools.append(schools[better_school_index])

print('better_schools:', better_schools)

###################################################################################
'''
流程3：对于这10个大学，衡量它们的经纬度和排名因素，计算大学得分
'''
class model2(nn.Module):
    '''
    输入：大学经纬度和学生经纬度之差、大学排名
    输出：大学得分
    '''
    def __init__(self, input_size=2, hidden1_size=4, hidden2_size=4, output_size=1):
        super(model2, self).__init__()
        self.layer1 = nn.Sequential(nn.Linear(input_size, hidden1_size), nn.Sigmoid())
        self.layer2 = nn.Sequential(nn.Linear(hidden1_size, hidden2_size), nn.Sigmoid())
        self.layer3 = nn.Sequential(nn.Linear(hidden2_size, output_size))

    def forward(self, x):
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        return x

mymodel2 = model2().double()
scores = []  # 存储better大学们的得分
for school in better_schools:
    school_student_distance = np.sqrt((school[1]-X_np[0])**2+(school[2]-X_np[1])**2)
    school_info = [school_student_distance, school[3]]
    school_info_model = torch.from_numpy(np.array(school_info))
    scores.append(mymodel2(school_info_model))
print('scores:', scores)

# 现在scores里都是每个better_school的得分了
# 我们选取前5个得分最低的大学（越低越好，因为距离越小越好，排名越靠前越好）
best_schools_index = list(map(scores.index, heapq.nsmallest(5, scores)))
best_schools = []
for best_school_index in best_schools_index:
    best_schools.append(better_schools[best_school_index])

print('best_schools:', best_schools)

# 按照大学排名给最终预测的大学排序，以便为学生提供冲一冲稳一稳保一保结果
best_schools = np.array(best_schools)
rank_best_schools = best_schools[np.lexsort(best_schools.T)]

print("冲一冲：")
print(rank_best_schools[0][0])
print("稳一稳：")
for i in range(2):
    print(rank_best_schools[i+1][0])
print("保一保：")
for i in range(2):
    print(rank_best_schools[i+3][0])
