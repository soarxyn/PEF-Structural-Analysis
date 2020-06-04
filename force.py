from __future__ import annotations
from typing import Tuple
from auxiliary.algebra import Vector3, Polynomial, integrate, psin, pcos, pcot

class Concentrated:
	magnitude: float = None

	def __init__(self, magnitude: float):
		self.magnitude = magnitude

	def forceVector(self, angle: float) -> Vector3:
		return Vector3(
			-self.magnitude*pcos(angle),
			-self.magnitude*psin(angle),
			0
		)

class Distributed:
	length: float = None
	distribution: Polynomial = None

	def __init__(self, length: float, distribution: Polynomial):
		self.length = length
		self.distribution = distribution

	def equivalent(self) -> Tuple[Concentrated, float]:	# tuple float is the equivalent force's point of application
		p1: Polynomial = Polynomial(self.distribution.coefficients)
		p1.coefficients.insert(0, 0)
		p1.degree = self.distribution.degree + 1
		integral: float = integrate(self.distribution, 0, self.length)
		return tuple(
			Concentrated(integral),
			integrate(p1, 0, self.length)/integral
		)

	def angledComponents(self, angle: float) -> Tuple[Distributed, Distributed]:	# the first load is applied perpendicularly to the referential axis, while the second one is applied in parallel
		basePolynomial: Polynomial = Polynomial(self.distribution.coefficients)
		if self.distribution.degree < 1:
			basePolynomial.coefficients.append(-pcot(angle))
			basePolynomial.degree = 1
		else:
			basePolynomial.coefficients[1] -= pcot(angle)
		return tuple(
			Distributed(self.length/psin(angle), psin(angle)*basePolynomial),
			Distributed(self.length/psin(angle), -pcos(angle)*basePolynomial)
		)

class Moment:
	magnitude: float = None

	def __init__(self, magnitude : float):
		self.magnitude = magnitude
