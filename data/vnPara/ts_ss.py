import math
import numpy
from numpy import dot
from numpy.linalg import norm

class TS_SS:
    def Cosine(self, vec1, vec2) :
        return self.InnerProduct(vec1,vec2) / (self.VectorSize(vec1) * self.VectorSize(vec2))

    def VectorSize(self, vec) :
        return math.sqrt(sum(math.pow(v,2) for v in vec))

    def InnerProduct(self, vec1, vec2) :
        return sum(v1*v2 for v1,v2 in zip(vec1,vec2))

    def Euclidean(self, vec1, vec2) :
        return math.sqrt(sum(math.pow((v1-v2),2) for v1,v2 in zip(vec1, vec2)))

    def Theta(self, vec1, vec2) :
        return math.acos(self.Cosine(vec1,vec2)) + math.radians(10)

    def Triangle(self, vec1, vec2) :
        theta = math.radians(self.Theta(vec1,vec2))
        return (self.VectorSize(vec1) * self.VectorSize(vec2) * math.sin(theta)) / 2

    def Magnitude_Difference(self, vec1, vec2) :
        return abs(self.VectorSize(vec1) - self.VectorSize(vec2))

    def Sector(self, vec1, vec2) :
        ED = self.Euclidean(vec1, vec2)
        MD = self.Magnitude_Difference(vec1, vec2)
        theta = self.Theta(vec1, vec2)
        return math.pi * math.pow((ED+MD),2) * theta/360

    def __call__(self, vec1, vec2):
        return self.Triangle(vec1, vec2) * self.Sector(vec1, vec2)

# tsss = TS_SS()
print(math.radians(10))