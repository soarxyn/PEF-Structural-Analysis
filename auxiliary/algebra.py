from dataclasses import dataclass, field
from typing import List, Tuple
from itertools import product
from functools import reduce

@dataclass
class Vector3:
	x: float = field(default=0)
	y: float = field(default=0)
	z: float = field(default=0)

	def __copy__(self):
		return Vector3(self.x, self.y, self.z)

	def __add__(self, other):
		return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

	def __sub__(self, other):
		return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

	def __mul__(self, scalar: float):
		return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

	def __rmul__(self, scalar: float):
		return self.__mul__(scalar)

	def __neg__(self):
		return Vector3(-self.x, -self.y, -self.z)

	def __div__(self, scalar: float):
		return self.__copy__() * (1 / scalar)

	def cross(self, other):
		return Vector3(self.y * other.z - self.z * other.y, self.z * other.x - self.x * other.z, self.x * other.y - self.y * other.x)

	def dot(self, other) -> float:
		return self.x * other.x + self.y * other.y + self.z * other.z

	def magnitude(self) -> float:
		return self.dot(self) ** 0.5

	def normalize(self):
		return self / self.magnitude()


@dataclass
class Polynomial:
	coefficients: List[float] = field(default_factory=list)
	degree: int = field(default=0)

	def __post_init__(self):
		self.degree = len(self.coefficients) - 1

	def __add__(self, other):
		if isinstance(other, Polynomial):
			if other.degree != self.degree:
				raise Exception("Polynomials must have same degree!")
			return Polynomial(list(map(lambda pair: pair[0] + pair[1], zip(self.coefficients, other.coefficients))), self.degree)
		else:
			return Polynomial([coef + i for (coef, i) in zip(self.coefficients, [other] + [0] * self.degree)], self.degree)

	def __radd__(self, other):
		return self + other

	def __eq__(self, other):
		return reduce(lambda a, b : a and b, list(map(lambda pair : pair[0] == pair[1], zip(self.coefficients, other.coefficients))))

	def __sub__(self, other):
		if isinstance(other, Polynomial):
			if other.degree != self.degree:
				raise Exception("Polynomials must have same degree!")

			return Polynomial(list(map(lambda pair: pair[0] - pair[1], zip(self.coefficients, other.coefficients))), self.degree)
		else:
			return Polynomial([coef + i for (coef, i) in zip(self.coefficients, [-other] + [0] * self.degree)], self.degree)

	def __mul__(self, other):
		if isinstance(other, float) or isinstance(other, int):
			return Polynomial([coef * other for coef in self.coefficients], self.degree)

		elif isinstance(other, Polynomial):
			_coefs = [0] * (self.degree + other.degree + 2)

			for (i, coef_s) in enumerate(self.coefficients):
				for (j, coef_o) in enumerate(other.coefficients):
					_coefs[i + j] += coef_s * coef_o

			return Polynomial(_coefs, self.degree + other.degree)         
			
	def __rmul__(self, other):
		return self.__mul__(other)

	def __div__(self, other):
		return self * (1 / other)

	def __neg__(self):
		return Polynomial([-coef for coef in self.coefficients], self.degree)

	def __call__(self, x):
		return reduce(lambda a, b: a + b, [coef * (x**i) for (i, coef) in enumerate(self.coefficients)])

	def __repr__(self):
		printable: str = str(self.coefficients[0])

		for index in range(1, self.degree + 1):
			if self.coefficients[index] != 0:
				printable += f" {'+' if self.coefficients[index] > 0 else '-'} {abs(self.coefficients[index])}X^{index}"

		return printable

@dataclass 
class Matrix3x3:
	data : List[List[float]]= field(default_factory = list)

	def __getitem__(self, key):
		return self.data[key]

	def __add__(self, other):
		return Matrix3x3([[self.data[i][j] + other.data[i][j] for j in range(0, 3)] for i in range(0, 3)])

	def __sub__(self, other):
		return Matrix3x3([[self.data[i][j] - other.data[i][j] for j in range(0, 3)] for i in range(0, 3)])

	def __mul__(self, other):
		if isinstance(other, float) or isinstance(other, int):
			return Matrix3x3([[self.data[i][j] * other for j in range(0, 3)] for i in range(0, 3)])

		elif isinstance(other, Matrix3x3):
			return Matrix3x3([[reduce(lambda a, b: a + b, [self[i][k] * other[k][j] for k in range(0, 3)]) for j in range(0, 3)] for i in range(0, 3)])

		elif isinstance(other, Vector3):
			return Vector3(self[0][0] * other.x + self[0][1] * other.y + self[0][2] * other.z, self[1][0] * other.x + self[1][1] * other.y + self[1][2] * other.z, self[2][0] * other.x + self[2][1] * other.y + self[2][2] * other.z)

	def __rmul__(self, other):
		if isinstance(other, float) or isinstance(other, int):
			return self * other
		else:
			return other * self

	def __neg__(self):
		return Matrix3x3([[-self.data[i][j] for j in range(0, 3)] for i in range(0, 3)])

	def __repr__(self):
		printable: str = "( "

		for i in range(0, 3):
			for j in range(0, 3):
				printable += f"{self.data[i][j]} "
			printable += "// " if i != 2 else ""
		
		return printable + ")"

	def subcolumn(self, c : int, sub : Vector3):
		if c == 0:
			return Matrix3x3([[sub.x, self[0][1], self[0][2]], [sub.y, self[1][1], self[1][2]], [sub.z, self[2][1], self[2][2]]])
		elif c == 1:
			return Matrix3x3([[self[0][0], sub.x, self[0][2]], [self[1][0], sub.y, self[1][2]], [self[2][0], sub.z, self[2][2]]])
		else:
			return Matrix3x3([[self[0][0], self[0][1], sub.x], [self[1][0], self[1][1], sub.y], [self[2][0], self[2][1], sub.z]])

def differentiate(p : Polynomial):
	return Polynomial([coef * (i + 1) for (i, coef) in enumerate(p.coefficients[1:])])

def integrate(p : Polynomial, lower : float, upper : float):
	primitive = Polynomial([0] + [coef / (i + 1) for (i, coef) in enumerate(p.coefficients)], p.degree + 1)
	return primitive(upper) - primitive(lower)

def det(mat : Matrix3x3) -> float:
	return mat[0][0]*(mat[1][1]*mat[2][2] - mat[2][1]*mat[1][2]) + mat[0][1]*(mat[1][2]*mat[2][0] - mat[2][2]*mat[1][0]) + mat[0][2]*(mat[1][0]*mat[2][1] - mat[1][1]*mat[2][0])

def solve(coefs : Matrix3x3, b : Vector3) -> Vector3:
	D : float = det(coefs)
	Dx : float = det(coefs.subcolumn(0, b))
	Dy : float = det(coefs.subcolumn(1, b))
	Dz : float = det(coefs.subcolumn(2, b))

	if D == 0:
		return Vector3(0, 0, 0)

	return Vector3(Dx / D, Dy / D, Dz / D)

def invert(m : Matrix3x3) -> Matrix3x3:
	a : Vector3 = solve(m, Vector3(1, 0, 0))
	b : Vector3 = solve(m, Vector3(0, 1, 0))
	c : Vector3 = solve(m, Vector3(0, 0, 1))

	return Matrix3x3([[a.x, b.x, c.x], [a.y, b.y, c.y], [a.z, b.z, c.z]])
