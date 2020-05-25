import numpy as np
from py_expression_eval import Parser
from goldenSection import goldenSectionSearch
from plot import plot

class GaussSeidel:
    def __init__(self, fun, g,startPoint, stepSize, epsilon, stepsLimit):
        self.fun = fun
        self.g = g
        self.epsilon = epsilon
        self.stepsLimit = stepsLimit
        self.stepSize = stepSize
        self.path = []
        self.stepNumber = 0
        self.currentPos = np.array(startPoint, dtype="float")
        self.variables = sorted(fun.variables())
        self.funResult = self.getFunctionResult()
        self.e= [np.array([1, 0]), np.array([0, 1])]
        self.logs = []
        self.vectors = []

    def __str__(self):
        parameters = dict(zip(self.variables, self.currentPos))
        strPoint = [str(round(axis, 3)) for axis in self.currentPos]
        strFVal = self.fun.evaluate(parameters)
        result = f"{self.stepNumber}: f({', '.join(strPoint)}) = {strFVal}"
        return result

    def calculatePunishment(self, parameters):
        sum = 0
        H = lambda x: 0 if x < 0 else 1
        delta=self.epsilon
        alpha = 100000
        for gi in self.g:
            gVal= gi.evaluate(parameters)
            gArg = gVal + delta
            deltaFun = alpha*(gArg**2)*H(gArg)
            # print(gVal, H(gVal), deltaFun)
            sum+=deltaFun

        return sum


    def getFunctionResult(self, replace_val=None):
        parameters = dict(zip(self.variables, self.currentPos))
        if replace_val:
            parameters.update(replace_val)
        return self.fun.evaluate(parameters)+ self.calculatePunishment(parameters)

    def getNextPosAndResult(self, pos, e):
        left = pos + e* (-self.stepSize)
        right = pos + e * (self.stepSize)
        left2 = pos + e* (-self.stepSize/4)
        right2 = pos + e * (self.stepSize/4)
        self.vectors.append([left, right])
        mini = goldenSectionSearch(self.getFunctionResult, left, right, self.epsilon)
        miniVal = self.getFunctionResult({"x1": mini[0], "x2": mini[1]})
        return mini, miniVal

    def getNewE(self):
        pos1, nextFunResult = self.getNextPosAndResult(self.currentPos, self.e[0])
        pos2, nextFunResult = self.getNextPosAndResult(pos1, self.e[1])
        diff = [pos2[0] - self.currentPos[0], pos2[1] - self.currentPos[1]]
        newE = diff/(np.linalg.norm(pos2 - self.currentPos))
        # print(diff, newE, (np.linalg.norm(pos2 - self.currentPos)))
        return newE


    def switchMoveDirection(self, newE):
        x= self.e[1]
        self.e[1] = self.e[0]
        self.e[0] = newE

    def getLowestPos(self):
        while True:
            self.logs.append(str(self))
            self.path.append(tuple(self.currentPos))
            localMinPosition, nextFunResult = self.getNextPosAndResult(self.currentPos, self.e[0])
            stepsLimitReached = self.stepNumber == self.stepsLimit
            minFunDifferenceReached = abs(self.funResult - nextFunResult) <= self.epsilon
            minPosDifferenceReached = np.linalg.norm(self.currentPos- localMinPosition) <= self.epsilon

            if stepsLimitReached or (minPosDifferenceReached and minFunDifferenceReached):
                return tuple(self.currentPos)

            self.currentPos = localMinPosition
            self.funResult = nextFunResult
            self.stepNumber += 1
            self.switchMoveDirection(self.getNewE())


if __name__ == '__main__':
    parser = Parser()
    functionStr = "(x1-2)^2+(x1-x2^2)^2"
    g=["x1+x2-2", "2*x1^2-x2"]
    # g=[]
    x0 = [3, -3]
    # print("function", function)
    function = parser.parse(functionStr)
    cg = GaussSeidel(function, [parser.parse(gi) for gi in g], x0, 0.5, 10e-3, 3000)
    pos = cg.getLowestPos()
    print('\n'.join(cg.logs))
    print("final pos: ", [round(x, 3) for x in pos])
    print("g(x): ", [parser.parse(gi).evaluate({"x1": pos[0], "x2": pos[1]}) for gi in g])
    plot(cg)
