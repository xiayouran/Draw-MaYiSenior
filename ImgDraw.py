# -*- coding: utf-8 -*-
# @Time    : 2020/10/17 13:16
# @Author  : XiaYouRan
# @Email   : youran.xia@foxmail.com
# @File    : ImgDraw.py
# @Software: PyCharm


import turtle
import cv2
import numpy as np
from bs4 import BeautifulSoup
import os
import re


class LineMethod(object):
    def __init__(self, width, height):
        # 贝塞尔函数的取样次数
        self.samples = 15
        self.width = width
        self.height = height

    def Bezier(self, p1, p2, t):
        # 一阶贝塞尔函数
        return p1 * (1 - t) + p2 * t

    def Bezier2(self, x1, y1, x2, y2, x3, y3):
        # 二阶贝塞尔函数
        turtle.goto(x1, y1)
        turtle.pendown()
        for t in range(0, self.samples + 1):
            x = self.Bezier(self.Bezier(x1, x2, t / self.samples),
                            self.Bezier(x2, x3, t / self.samples), t / self.samples)
            y = self.Bezier(self.Bezier(y1, y2, t / self.samples),
                            self.Bezier(y2, y3, t / self.samples), t / self.samples)
            turtle.goto(x, y)
        turtle.penup()

    def Bezier3(self, x1, y1, x2, y2, x3, y3, x4, y4):
        # 三阶贝塞尔函数
        x1 = - self.width / 2 + x1
        y1 = self.height / 2 - y1
        x2 = - self.width / 2 + x2
        y2 = self.height / 2 - y2
        x3 = - self.width / 2 + x3
        y3 = self.height / 2 - y3
        x4 = - self.width / 2 + x4
        y4 = self.height / 2 - y4  # 坐标变换
        turtle.goto(x1, y1)
        turtle.pendown()
        for t in range(0, self.samples + 1):
            x = self.Bezier(
                self.Bezier(self.Bezier(x1, x2, t / self.samples), self.Bezier(x2, x3, t / self.samples),
                            t / self.samples),
                self.Bezier(self.Bezier(x2, x3, t / self.samples), self.Bezier(x3, x4, t / self.samples),
                            t / self.samples),
                t / self.samples)
            y = self.Bezier(
                self.Bezier(self.Bezier(y1, y2, t / self.samples), self.Bezier(y2, y3, t / self.samples),
                            t / self.samples),
                self.Bezier(self.Bezier(y2, y3, t / self.samples), self.Bezier(y3, y4, t / self.samples),
                            t / self.samples),
                t / self.samples)
            turtle.goto(x, y)
        turtle.penup()

    def Moveto(self, x, y):
        # 绝对移动
        turtle.penup()
        turtle.goto(- self.width / 2 + x, self.height / 2 - y)
        turtle.pendown()

    def MovetoRelative(self, dx, dy):
        # 相对移动
        turtle.penup()
        turtle.goto(turtle.xcor() + dx, turtle.ycor() - dy)
        turtle.pendown()

    def Line(self, x1, y1, x2, y2):
        # 连接svg坐标下两点
        turtle.penup()
        turtle.goto(- self.width / 2 + x1, self.height / 2 - y1)
        turtle.pendown()
        turtle.goto(- self.width / 2 + x2, self.height / 2 - y2)
        turtle.penup()

    def Lineto(self, x, y):
        # 连接当前点和svg坐标下(x, y)
        turtle.pendown()
        turtle.goto(- self.width / 2 + x, self.height / 2 - y)
        turtle.penup()

    def LinetoRelative(self, dx, dy):
        # 连接当前点和相对坐标(dx, dy)的点
        turtle.pendown()
        turtle.goto(turtle.xcor() + dx, turtle.ycor() - dy)
        turtle.penup()

    def Curveto(self, x1, y1, x2, y2, x, y):
        # 三阶贝塞尔曲线到(x, y)
        turtle.penup()
        X_now = turtle.xcor() + self.width / 2
        Y_now = self.height / 2 - turtle.ycor()
        self.Bezier3(X_now, Y_now, x1, y1, x2, y2, x, y)

    def CurvetoRelative(self, x1, y1, x2, y2, x, y):
        # 三阶贝塞尔曲线到相对坐标(x, y)
        turtle.penup()
        X_now = turtle.xcor() + self.width / 2
        Y_now = self.height / 2 - turtle.ycor()
        self.Bezier3(X_now, Y_now, X_now + x1, Y_now + y1, X_now + x2, Y_now + y2, X_now + x, Y_now + y)


class DrawImg(object):
    def __init__(self, filename, rgb):
        self.initWH(filename)
        self.rgb = rgb

    def initWH(self, filename):
        with open(filename) as f:
            self.svg_html = BeautifulSoup(f.read(), 'lxml')
        self.width = float(self.svg_html.svg.attrs['width'][0: -2])
        self.height = float(self.svg_html.svg.attrs['height'][0: -2])
        self.transform = self.svg_html.g.attrs['transform']

        self.line_obj = LineMethod(width=self.width, height=self.height)

        pattern = re.compile('[\w()., ]*\(([\d.]*),-([\d.]*)\)')
        self.scale_value = re.match(pattern, self.transform)
        self.scale = (float(self.scale_value.group(1)), float(self.scale_value.group(2)))

    def readPathAttrD(self, path_d):
        """
        返回一个迭代器，随时获取数据
        :param path_d:
        :return:
        """
        path_dlist = path_d.split(' ')
        for i in path_dlist:
            if i.isdigit():
                yield float(i)
            elif i[0].isalpha():
                yield i[0]
                yield float(i[1:])
            elif i[-1].isalpha():
                yield float(i[: -1])
            elif i[0] == '-':
                yield float(i)

    def drawImg(self, path_diter):
        """
        大写字母绝对定位, 小写字母相对定位
        M Move to (x, y), 移动到(x, y)
        L Line to (x, y), 在当前位置(x, y)与上一个位置点画线段
        H Horizontal lineto, 绘制平行线
        V Vertical lineto, 绘制垂直线
        C Curveto, 三次贝塞尔曲线(x1, y1, x2, y2, x, y)
        S Smooth curveto 光滑三次贝塞尔曲线, 用来创建与之前曲线一样的贝塞尔曲线(x2, y2, x, y)
        Q Quadratic Bezier curve, 二次贝塞尔曲线(x1, y1, x, y)
        T Smooth quadratic Bezier curveto, 光滑二次贝塞尔曲线(x, y)
        A Elliptical Arc, 弧形()
        Z Closepath, 从当前点画一条直线到起点
        :param path_diter:
        :return:
        """
        lastI = ''
        for i in path_diter:
            if i == 'M':
                turtle.end_fill()
                self.line_obj.Moveto(next(path_diter) * self.scale[0], next(path_diter) * self.scale[1])
                turtle.begin_fill()
            elif i == 'm':
                turtle.end_fill()
                self.line_obj.MovetoRelative(next(path_diter) * self.scale[0], next(path_diter) * self.scale[1])
                turtle.begin_fill()
            elif i == 'C':
                self.line_obj.Curveto(next(path_diter) * self.scale[0], next(path_diter) * self.scale[1],
                                      next(path_diter) * self.scale[0], next(path_diter) * self.scale[1],
                                      next(path_diter) * self.scale[0], next(path_diter) * self.scale[1])
                lastI = i
            elif i == 'c':
                self.line_obj.CurvetoRelative(next(path_diter) * self.scale[0], next(path_diter) * self.scale[1],
                                              next(path_diter) * self.scale[0], next(path_diter) * self.scale[1],
                                              next(path_diter) * self.scale[0], next(path_diter) * self.scale[1])
                lastI = i
            elif i == 'L':
                self.line_obj.Lineto(next(path_diter) * self.scale[0], next(path_diter) * self.scale[1])
            elif i == 'l':
                self.line_obj.LinetoRelative(next(path_diter) * self.scale[0], next(path_diter) * self.scale[1])
                lastI = i
            elif lastI == 'C':
                self.line_obj.Curveto(i * self.scale[0], next(path_diter) * self.scale[1],
                                      next(path_diter) * self.scale[0], next(path_diter) * self.scale[1],
                                      next(path_diter) * self.scale[0], next(path_diter) * self.scale[1])
            elif lastI == 'c':
                self.line_obj.CurvetoRelative(i * self.scale[0], next(path_diter) * self.scale[1],
                                              next(path_diter) * self.scale[0], next(path_diter) * self.scale[1],
                                              next(path_diter) * self.scale[0], next(path_diter) * self.scale[1])
            elif lastI == 'L':
                self.line_obj.Lineto(i * self.scale[0], next(path_diter) * self.scale[1])
            elif lastI == 'l':
                self.line_obj.LinetoRelative(i * self.scale[0], next(path_diter) * self.scale[1])

    def start(self):
        # turtle.screensize(640, 480)
        turtle.setup(width=self.width, height=self.height)
        # 坐标轴对调, 否则画出来是反的
        turtle.setworldcoordinates(- self.width / 2, self.height / 2,
                                   self.width / 2, - self.height / 2)

        # # 每隔n次, 更新一下屏幕, 可以用来加速绘画速度
        turtle.tracer(100)
        # turtle.pensize(1)
        # turtle.speed(10)
        turtle.penup()
        turtle.color(self.rgb)

        for i in self.svg_html.find_all('path'):
            path_d = i.attrs['d'].replace('\n', ' ')
            path_diter = self.readPathAttrD(path_d)
            self.drawImg(path_diter)

        turtle.penup()
        # # 隐藏小乌龟
        # turtle.hideturtle()
        # turtle.update()


if __name__ == '__main__':
    # (B, G, R)
    img1 = cv2.imread('mayi_50.png')
    # img1 = cv2.imread('mayi_75.png')
    img2 = np.float32(img1.reshape((-1, 3)))
    # data：np.float32类型的数据，每个特征应该放在一列
    # K：聚类的最终数目
    # bestLabels：预设的分类标签，没有的话就设置为None
    # criteria：终止迭代的条件，当条件满足时算法的迭代就终止，它应该是一个含有三个成员的元组（type,max_iter,epsilon）
    # attempts：重复试验kmeans算法次数，将会返回最好的一次结果
    # flags：初始类中心选择，有两个选择：cv2.KMEANS_PP_CENTERS 和 cv2.KMEANS_RANDOM_CENTERS
    # compactness：紧密度，返回每个点到相应聚类中心距离的平方和, 一个值float
    # labels：标志数组
    # centers：有聚类中心组成的数组

    compactness, labels, centers = cv2.kmeans(data=img2, K=32, bestLabels=None, criteria=(cv2.TERM_CRITERIA_EPS, 10, 1.0),
                                              attempts=16, flags=cv2.KMEANS_RANDOM_CENTERS)

    centers = centers.astype(np.uint8)
    res = centers[labels.flatten()]
    res = res.reshape(img1.shape)
    count = 0
    for i in centers:
        # src: 原图
        # lowerb: 低于这个值变为0
        # upperb: 高于这个值变为0
        res2 = cv2.inRange(src=res, lowerb=i, upperb=i)
        # 将图片里像素值按位反向
        res2 = cv2.bitwise_not(res2)
        cv2.imwrite('test_{}.bmp'.format(count), res2)

        # 位图转为矢量图bmp-->svg
        os.system('Potrace.exe test_{}.bmp -s --flat'.format(count))

        # print('drawing %d' % count)
        # print(i)

        draw_obj = DrawImg('test_{}.svg'.format(count), rgb='#%02x%02x%02x' % (i[2], i[1], i[0]))
        draw_obj.start()

        # count += 1

    print('OK!')
    turtle.mainloop()
