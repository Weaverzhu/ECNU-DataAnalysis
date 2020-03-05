# -*- coding: utf-8 -*-

while True:
    age = int(input("请输入你的年龄： "))
    if age >= 18:
        print("你是个adult.") 
    elif age >= 12:  # 可以有多个elif语句
        print("You are a teenager.")
    elif age > 0:
        print("你还是个小朋友呦.")
    else: 
        break