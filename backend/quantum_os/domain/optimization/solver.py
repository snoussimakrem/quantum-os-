from abc import ABC, abstractmethod
from typing import Optional
from quantum_os.domain.optimization.problem import OptimizationProblem, OptimizationResult, SolverType

class SolverInterface(ABC):
    """Abstract interface for all optimization solvers"""
    
    @abstractmethod
    def solve(self, problem: OptimizationProblem) -> OptimizationResult:
        """Solve the optimization problem"""
        pass
    
    @abstractmethod
    def validate(self, problem: OptimizationProblem) -> bool:
        """Validate problem can be solved by this solver"""
        pass
    
    @abstractmethod
    def estimate_complexity(self, problem: OptimizationProblem) -> float:
        """Estimate computational complexity for this solver"""
        pass
    
    @property
    @abstractmethod
    def solver_type(self) -> SolverType:
        """Return the solver type"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the solver name"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Return the solver description"""
        pass
