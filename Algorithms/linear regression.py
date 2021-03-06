import matplotlib.pyplot as plt
import numpy as np
import time
# https://habr.com/ru/post/468295/


def generateData(startX, endX, step=0.1, spread=10, bias=0):
    x = np.arange(startX, endX, step)
    y = []
    for xi in x:
        y.append(xi**3 + np.random.randint(-1, 2) * np.random.random()*spread + bias)
    y = np.array(y)
    return x, y


def distance(x0, y0, k, b):
    return abs(-k*x0 + y0 - b) / (k**2 + 1)**0.5


def linRegStochasticGradWithMyFuncLoss(x, y):
    # cost func is func of distance
    k = 0
    b = 0
    epochs = 10000
    N = len(x)

    learningRate = 10
    colorInd = 0
    colors = ["red", "orange", "yellow", "green", "blue", "purple"]
    previousError = 2**64
    for epoch in range(epochs):
        nablaK = 0
        nablaB = 0
        error = 0
        for xi, yi in zip(x, y):
            error += distance(xi, yi, k, b) ** 2
            nablaK += ((-k*xi + yi - b) / (abs(-k*xi + yi - b)) * -xi * np.sqrt(k**2 + 1) - abs(k * xi - yi + b) * k / np.sqrt(k**2 + 1)) / (k**2 + 1)
            nablaB += -1 / np.sqrt(k**2 + 1) * (-k*xi + yi - b) / (abs(-k*xi + yi - b))

        error /= N
        if previousError < error and abs(error - previousError) > 1:
            learningRate /= 10
            print("CHANGE lr, epoch =", epoch, "because", previousError, error, abs(error - previousError), "\n")
        if abs(previousError - error) < 0.0000001 and error < 1:
            print(epoch, "stop because it's stoped")
            break
        k -= (nablaK / N) * learningRate
        b -= (nablaB / N) * learningRate
        previousError = error
    print("error", error)
    return k, b


def linRegStochasticSquareFuncLoss(x, y):
    # cost func is diffrence between yi and line
    N = len(x)
    k = 100
    b = 0
    epochs = 2000
    learningRate = 10
    colorInd = 0
    colors = ["red", "orange", "yellow", "green", "blue", "purple"]
    previousError = float("inf")
    for epoch in range(epochs):
        nablaK = 0
        nablaB = 0
        error = 0
        for xi, yi in zip(x, y):
            error += (yi - (xi*k + b)) ** 2
            nablaK += (yi - (xi*k + b)) * xi
            nablaB += (yi - (xi*k + b))

        error /= N
        if previousError < error and abs(error - previousError) > 1:
            learningRate /= 10
            print("CHANGE lr, epoch =", epoch, "because", previousError, error, abs(error - previousError), "\n")
        if abs(previousError - error) < 0.0000001 and error < 1:
            print(epoch, "stop because it's stoped")
            break
        k -= (-2 * nablaK / N) * learningRate
        b -= (-2 * nablaB / N) * learningRate
        previousError = error
        # plt.scatter(x, y, 5)
        # plt.plot([x[0], x[-1]], [x[0] * k + b, x[-1] * k + b], color="black", linestyle="-", linewidth=2)
        # plt.gca().set(xlim=(x[0] - 5, x[-1] + 5), ylim=(min(y) - 5, max(y) + 5))
        # plt.show()
        # sleep(1)
    print("error", error)
    return k, b


def linRegOfRazinkovWithRegularization(train, trainRes, M, koefOfReg=1000):
    # M- count of parameters of model
    # N- len(train)
    def getBasisFunc(degree):
        return lambda x: x**degree
    basisFunctions = [getBasisFunc(i) for i in range(M)]
    FI = lambda x: [func(x) for func in basisFunctions]
    matrixOfPlan = [FI(x) for x in train]
    matrixOfPlan = np.reshape(matrixOfPlan, (len(train), M))
    I = np.array([[int(i == j) for j in range(len(matrixOfPlan[0]))] for i in range(len(matrixOfPlan[0]))])
    I[0][0] = 0
    # we dont regularizate w0, because it's a bias, a bias maybe very big.
    # It's not a problem, cos our selection maybe be on 1000 above the 0X
    w = np.dot(
                np.dot(
                        np.linalg.inv(np.dot(matrixOfPlan.transpose(), matrixOfPlan) + I * koefOfReg),
                        matrixOfPlan.transpose()),
                trainRes)
    print(np.int32(w))
    return w, FI


def getModel(train, trainRes, M, koefOfReg=0):
    w, FI = linRegOfRazinkovWithRegularization(train, trainRes, M, koefOfReg)
    loss = 0
    for i in range(len(train)):
        loss += (trainRes[i] - np.dot(w.transpose(), FI(train[i])))**2
    loss = loss / 2
    print(M, "loss", loss)
    print()
    return lambda x: np.dot(w.transpose(), FI(x))


train, trainRes = generateData(0, 10, step=0.5, spread=150, bias=1000)

model = getModel(train, trainRes, 10)
plt.scatter(train, trainRes, 5)
plt.plot(train, [model(xi) for xi in train], color="black", linestyle="dotted", linewidth=2)
# plt.gca().set(xlim=(train[0]-5, train[-1]+5), ylim=(min(trainRes)-5, max(trainRes)+5))

model = getModel(train, trainRes, 10, koefOfReg=1000)
plt.scatter(train, trainRes, 5)
plt.plot(train, [model(xi) for xi in train], color="gray", linestyle="dashdot", linewidth=2)
# plt.gca().set(xlim=(train[0]-5, train[-1]+5), ylim=(min(trainRes)-5, max(trainRes)+5))

model = getModel(train, trainRes, 4, koefOfReg=1000)
plt.scatter(train, trainRes, 5)
plt.plot(train, [model(xi) for xi in train], color="blue", linestyle="solid", linewidth=2)
# plt.gca().set(xlim=(train[0]-5, train[-1]+5), ylim=(min(trainRes)-5, max(trainRes)+5))
plt.show()
