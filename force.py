from __future__ import annotations
from typing import Tuple
from auxiliary.algebra import Vector3, Polynomial, integrate, psin, pcos, pcot

class Concentrated:
	def __init__(self, magnitude: float):
		self.magnitude: float = magnitude

	def forceVector(self, angle: float) -> Vector3:
		return Vector3(
			self.magnitude*pcos(angle),
			-self.magnitude*psin(angle),
			0
		)

class Distributed:
	def __init__(self, length: float, distribution: Polynomial):
		self.length: float = length
		self.distribution: Polynomial = Polynomial(distribution.coefficients.copy())

	def equivalent(self, l: float, u: float) -> Tuple[Concentrated, float]:  # tuple float is the equivalent force's point of application
		if l == u:
			return (Concentrated(0), 0)

		p1: Polynomial = Polynomial(self.distribution.coefficients.copy())
		p1.coefficients.insert(0, 0)
		p1.degree = self.distribution.degree + 1
		integral: float = integrate(self.distribution, l, u)
		return (
			Concentrated(integral),
			integrate(p1, l, u)/integral
		)

	def angledComponents(self, angle: float) -> Tuple[Distributed, Distributed]:  # the first load is applied in parallel to the referential axis, while the second one is applied perpendicularly
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

class Moment:
	def __init__(self, magnitude : float):
		self.magnitude: float = magnitude
