from __future__ import annotations
from typing import Tuple
from auxiliary.algebra import Vector3, Polynomial, integrate, psin, pcos, pcot

# this class defines a concentrated force
class Concentrated:
	def __init__(self, magnitude: float):
		self.magnitude: float = magnitude

	# this function returns the vector that represents the concentrated force, given its angle
	def forceVector(self, angle: float) -> Vector3:
		return Vector3(
			self.magnitude*pcos(angle),
			-self.magnitude*psin(angle),
			0
		)

# this class defines a distributed force
class Distributed:
	def __init__(self, length: float, distribution: Polynomial):
		self.length: float = length
		self.distribution: Polynomial = Polynomial(distribution.coefficients.copy())

	# this function returns the concentrated force mechanically equivalent to the distributed force and its point of application, relative to its 0
	def equivalent(self) -> Tuple[Concentrated, float]:
		p1: Polynomial = Polynomial(self.distribution.coefficients.copy())
		p1.coefficients.insert(0, 0)
		p1.degree = self.distribution.degree + 1
		integral: float = integrate(self.distribution, 0, self.length)
		return (
			Concentrated(integral),
			integrate(p1, 0, self.length)/integral
		)

	# this function finds the distributed force's parallel and perpendicular components applied on a beam at a given angle
	def angledComponents(self, angle: float) -> Tuple[Distributed, Distributed]:
		basePolynomial: Polynomial = Polynomial(self.distribution.coefficients.copy())
		if self.distribution.degree < 1:
			basePolynomial.coefficients.append(pcot(angle))
			basePolynomial.degree = 1
		else:
			basePolynomial.coefficients[1] += pcot(angle)
		return (
			Distributed(self.length/psin(angle), pcos(angle)*basePolynomial),
			Distributed(self.length/psin(angle), psin(angle)*basePolynomial)
		)

# this class defines a moment or torque
class Moment:
	def __init__(self, magnitude : float):
		self.magnitude: float = magnitude
