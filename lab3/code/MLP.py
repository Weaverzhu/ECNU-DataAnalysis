# -*- coding: utf-8 -*-

# 导入库
import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation
from keras.optimizers import SGD

# 生成数据
import numpy as np
# x为（-0.5,0.5）内均匀生成，其中训练样本1000个，测试样本100个
x_train=np.linspace(-0.5,0.5,1000)
x_test=np.linspace(-0.5,0.5,100)
# y为x*x，并添加波动值作为噪音
y_train=np.square(x_train)+np.random.normal(0,0.02,x_train.shape)
y_test=np.square(x_test)+np.random.normal(0,0.02,x_test.shape)

# 简单搭建一个MLP（多层感知机）

# 模型初始化
model = Sequential()  
# 输入层（1个节点）到第一隐含层（64节点）的连接，使用relu作为激活函数
# 在第一层必须指定输入的大小，这里是1个隐藏单元
model.add(Dense(64, activation='relu', input_dim=1))  
# 使用Dropout防止过拟合
model.add(Dropout(0.5))  
# 添加输出层（1节点）
model.add(Dense(1, activation='relu'))  

# 打印模型信息以及参数数量
model.summary()

sgd = SGD(lr=0.3)  # 定义求解算法
model.compile(loss='mse',
              optimizer=sgd,
              metrics=['accuracy'])  # 编译生成模型

model.fit(x_train, y_train,
          epochs=10,
          batch_size=32)  # 训练模型
score = model.evaluate(x_test, y_test, batch_size=32)  # 测试模型
y_pred = model.predict(x_test)  #得到预测值


# 绘图
import matplotlib.pyplot as plt
# 将真实y值y_test绘制为散点图
plt.scatter(x_test,y_test)
# 将预测y值y_pred绘制为红色曲线
plt.plot(x_test,y_pred,'r-',lw=3)
plt.show()