#!/opt/anaconda2/bin/python
# -*- coding: utf-8 -*-
from keras.models import Sequential
from keras.layers import LSTM, Dense
import numpy as np
import codecs,csv

data_dim = 16
timesteps = 8
nb_classes = 10
filename = "LSTM-Outputs.txt"

# 简单搭建一个LSTM
model = Sequential()  # 模型初始化
# expected input data shape: (batch_size, timesteps, data_dim)
model.add(LSTM(32, return_sequences=True,
               input_shape=(timesteps, data_dim)))  # returns a sequence of vectors of dimension 32
model.add(LSTM(32, return_sequences=True))  # returns a sequence of vectors of dimension 32
model.add(LSTM(32))  # return a single vector of dimension 32
model.add(Dense(10, activation='softmax'))

model.compile(loss='categorical_crossentropy',
              optimizer='rmsprop',
              metrics=['accuracy'])

# 生成训练数据
x_train = np.random.random((1000, timesteps, data_dim))
y_train = np.random.random((1000, nb_classes))
# 生成验证数据
x_val = np.random.random((100, timesteps, data_dim))
y_val = np.random.random((100, nb_classes))
# 生成验证数据
x_test = np.random.random((100, timesteps, data_dim))
y_test = np.random.random((100, nb_classes))

# 训练模型
model.fit(x_train, y_train, batch_size=64, nb_epoch=5,validation_data=(x_val, y_val))
# 预测结果
results = model.predict(x_test, batch_size=32, verbose=0)
# 保存预测结果

with codecs.open(filename, 'w', encoding='utf-8') as f:
    f_csv = csv.writer(f)
    f_csv.writerows(results)
		
score = model.evaluate(x_test, y_test, batch_size=16) # 在test数据上评估模型
print("\nEvaluation Metrics：\n", model.metrics_names)
print(score)

