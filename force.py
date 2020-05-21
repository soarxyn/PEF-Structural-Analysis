from __future__ import annotations
import math
from typing import Tuple
from auxiliary.algebra import Vector3, Polynomial, integrate

class Concentrated:
	magnitude: float = None

	def __init__(self, magnitude: float):
		self.magnitude = magnitude

	def forceVector(self, angle: float) -> Vector3:
		return Vector3(
			-self.magnitude*math.cos(angle),
			-self.magnitude*math.sin(angle),
			0
		)

class Distributed:
	length: float = None
	distribution: Polynomial = None

	def __init__(self, length: float, distribution: Polynomial):
		self.length = length
		self.distribution = distribution

	def equivalent(self) -> Tuple[Concentrated, float]:				# tuple float is the equivalent force's point of application
		integral = integrate(self.distribution, 0, self.length)
		return [
			Concentrated(integral),
			integrate(self.distribution*Polynomial([0, 1]), 0, self.length)/integral
		]

	def angledComponents(self, angle: float) -> Tuple[Distributed, Distributed]:					# the first load is applied perpendicularly to the referential axis, while the second one is applied in parallel
		basePolynomial: Polynomial = self.distribution - Polynomial([0, 1/math.tan(angle)])
		return [
			Distributed(self.length/math.sin(angle), math.sin(angle)*basePolynomial),
			Distributed(self.length/math.sin(angle), -math.cos(angle)*basePolynomial)
		]

class Moment:
	magnitude: float = None

	def __init__(self, magnitude : float):
		self.magnitude = magnitude
