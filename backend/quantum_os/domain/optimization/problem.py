from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, Union
from enum import Enum
import numpy as np

class ProblemType(str, Enum):
    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"

class SolverType(str, Enum):
    OR_TOOLS = "or_tools"
    PYOMO = "pyomo"
    SCIPY = "scipy"
    SIMULATED_ANNEALING = "simulated_annealing"
    GENETIC = "genetic"
    QAOA = "qaoa"
    QUANTUM_ANNEALING = "quantum_annealing"
    TENSOR_NETWORK = "tensor_network"

@dataclass
class OptimizationProblem:
    """Mathematical representation of any optimization problem"""
    
    # Core components
    variables: Dict[str, Any]
    objective: Callable
    constraints: List[Callable]
    
    # Optional components
    bounds: Optional[Dict[str, tuple]] = None
    costs: Optional[Dict[str, float]] = None
    rewards: Optional[Dict[str, float]] = None
    dependencies: Optional[List[tuple]] = None
    
    # Metadata
    problem_type: ProblemType = ProblemType.MINIMIZE
    name: str = ""
    description: str = ""
    
    def to_dict(self) -> Dict:
        """Serialize problem for storage"""
        return {
            "variables": self.variables,
            "objective": self.objective.__name__,
            "constraints": [c.__name__ for c in self.constraints],
            "bounds": self.bounds,
            "costs": self.costs,
            "rewards": self.rewards,
            "dependencies": self.dependencies,
            "problem_type": self.problem_type.value,
            "name": self.name,
            "description": self.description
        }
    
    def estimate_complexity(self) -> float:
        """Estimate computational complexity"""
        n_vars = len(self.variables)
        n_constraints = len(self.constraints)
        return n_vars * (1 + n_constraints * 0.1)

@dataclass
class OptimizationResult:
    """Standardized result format"""
    
    solution: Dict[str, Any]
    objective_value: float
    execution_time: float
    solver_type: SolverType
    iterations: int
    status: str
    metadata: Dict[str, Any] = field(default_factory=dict)
