import time
import random
import math
from typing import Dict, Any
from quantum_os.domain.optimization.problem import OptimizationProblem, OptimizationResult, SolverType
from quantum_os.domain.optimization.solver import SolverInterface
from quantum_os.core.logging import log

class SimulatedAnnealingSolver(SolverInterface):
    """Simulated Annealing solver for non-linear and discrete problems"""
    
    def __init__(self, initial_temp=100, cooling_rate=0.95, iterations=1000):
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.iterations = iterations
    
    @property
    def solver_type(self) -> SolverType:
        return SolverType.SIMULATED_ANNEALING
    
    @property
    def name(self) -> str:
        return "Simulated Annealing"
    
    @property
    def description(self) -> str:
        return "Simulated annealing for non-linear and discrete optimization"
    
    def validate(self, problem: OptimizationProblem) -> bool:
        """Validate if problem is suitable for simulated annealing"""
        return True  # Works with most problems
    
    def estimate_complexity(self, problem: OptimizationProblem) -> float:
        """Estimate complexity for simulated annealing"""
        return problem.estimate_complexity() * 2.0  # SA is slower
    
    def solve(self, problem: OptimizationProblem) -> OptimizationResult:
        """Solve using simulated annealing"""
        log.info(f"Solving with Simulated Annealing: {problem.name}")
        start_time = time.time()
        iterations = 0
        
        try:
            # Get initial solution
            current_solution = {}
            for var_name, var in problem.variables.items():
                if isinstance(var, int):
                    current_solution[var_name] = random.randint(0, 100)
                else:
                    current_solution[var_name] = random.uniform(0, 100)
            
            # Evaluate initial solution
            current_value = problem.objective(**current_solution)
            best_solution = current_solution.copy()
            best_value = current_value
            
            # Simulated annealing loop
            temperature = self.initial_temp
            
            for i in range(self.iterations):
                iterations += 1
                
                # Generate neighbor solution
                neighbor = current_solution.copy()
                var_to_change = random.choice(list(neighbor.keys()))
                if isinstance(neighbor[var_to_change], int):
                    neighbor[var_to_change] += random.randint(-10, 10)
                else:
                    neighbor[var_to_change] += random.uniform(-10, 10)
                
                # Evaluate neighbor
                try:
                    neighbor_value = problem.objective(**neighbor)
                except Exception:
                    continue
                
                # Decide whether to accept
                delta = neighbor_value - current_value
                accept = False
                
                if delta < 0:  # Improvement
                    accept = True
                else:
                    probability = math.exp(-delta / temperature)
                    if random.random() < probability:
                        accept = True
                
                if accept:
                    current_solution = neighbor
                    current_value = neighbor_value
                    
                    if current_value < best_value:  # Minimize
                        best_solution = current_solution.copy()
                        best_value = current_value
                
                # Cool down
                temperature *= self.cooling_rate
                
                # Stop if temperature is very low
                if temperature < 0.001:
                    break
            
            execution_time = time.time() - start_time
            
            return OptimizationResult(
                solution=best_solution,
                objective_value=best_value,
                execution_time=execution_time,
                solver_type=self.solver_type,
                iterations=iterations,
                status="success",
                metadata={
                    "initial_temperature": self.initial_temp,
                    "cooling_rate": self.cooling_rate,
                    "iterations_performed": iterations
                }
            )
            
        except Exception as e:
            log.error(f"Simulated Annealing failed: {str(e)}")
            return OptimizationResult(
                solution={},
                objective_value=0,
                execution_time=time.time() - start_time,
                solver_type=self.solver_type,
                iterations=iterations,
                status="error",
                metadata={"error": str(e)}
            )
