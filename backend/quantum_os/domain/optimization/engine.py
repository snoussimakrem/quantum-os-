from typing import Dict, Optional, List
import time
import hashlib
import json
from datetime import datetime
from quantum_os.domain.optimization.problem import OptimizationProblem, OptimizationResult, SolverType
from quantum_os.domain.optimization.solver import SolverInterface
from quantum_os.core.logging import log

class OptimizationEngine:
    """Core optimization engine with dynamic solver selection"""
    
    def __init__(self):
        self.solvers: Dict[SolverType, SolverInterface] = {}
        self.solver_history: List[Dict] = []
        self._initialize_solvers()
    
    def _initialize_solvers(self):
        """Initialize default solvers"""
        try:
            from quantum_os.domain.optimization.solvers.ortools_solver import ORToolsSolver
            self.register_solver(ORToolsSolver())
        except ImportError as e:
            log.warning(f"OR-Tools not available: {e}")
        
        try:
            from quantum_os.domain.optimization.solvers.simulated_annealing import SimulatedAnnealingSolver
            self.register_solver(SimulatedAnnealingSolver())
        except ImportError as e:
            log.warning(f"Simulated Annealing not available: {e}")
    
    def register_solver(self, solver: SolverInterface):
        """Register a new solver"""
        self.solvers[solver.solver_type] = solver
        log.info(f"Registered solver: {solver.name}")
    
    def analyze_problem(self, problem: OptimizationProblem) -> Dict:
        """Analyze problem characteristics for solver selection"""
        complexity = problem.estimate_complexity()
        
        analysis = {
            "n_variables": len(problem.variables),
            "n_constraints": len(problem.constraints),
            "has_bounds": bool(problem.bounds),
            "problem_type": problem.problem_type.value,
            "complexity_estimate": complexity,
            "recommended_solver": None,
            "available_solvers": []
        }
        
        # Get available solver recommendations
        for solver_type, solver in self.solvers.items():
            if solver.validate(problem):
                solver_complexity = solver.estimate_complexity(problem)
                analysis["available_solvers"].append({
                    "name": solver.name,
                    "type": solver_type.value,
                    "complexity": solver_complexity
                })
        
        # Determine best solver
        if analysis["available_solvers"]:
            # Sort by complexity
            sorted_solvers = sorted(
                analysis["available_solvers"],
                key=lambda x: x["complexity"]
            )
            analysis["recommended_solver"] = sorted_solvers[0]["type"]
        
        return analysis
    
    def select_solver(self, problem: OptimizationProblem) -> Optional[SolverInterface]:
        """Dynamic solver selection based on problem analysis"""
        analysis = self.analyze_problem(problem)
        
        # Check if we have a recommendation
        if analysis["recommended_solver"]:
            solver_type = SolverType(analysis["recommended_solver"])
            if solver_type in self.solvers:
                log.info(f"Selected solver: {self.solvers[solver_type].name}")
                return self.solvers[solver_type]
        
        # Check historical performance for similar problems
        historical_solver = self._check_historical_performance(problem)
        if historical_solver:
            return historical_solver
        
        # Fallback: choose first available solver
        if self.solvers:
            solver = next(iter(self.solvers.values()))
            log.warning(f"Falling back to: {solver.name}")
            return solver
        
        log.error("No solvers available!")
        return None
    
    def _check_historical_performance(self, problem: OptimizationProblem) -> Optional[SolverInterface]:
        """Check if we've solved similar problems before"""
        # Get problem signature
        problem_hash = self._get_problem_hash(problem)
        
        # Check history for similar problems
        for entry in self.solver_history:
            if entry.get("problem_hash") == problem_hash:
                solver_type = SolverType(entry["solver_type"])
                if solver_type in self.solvers:
                    return self.solvers[solver_type]
        
        return None
    
    def _get_problem_hash(self, problem: OptimizationProblem) -> str:
        """Generate a hash for the problem"""
        problem_dict = problem.to_dict()
        problem_str = json.dumps(problem_dict, sort_keys=True)
        return hashlib.md5(problem_str.encode()).hexdigest()
    
    def optimize(self, problem: OptimizationProblem) -> OptimizationResult:
        """Main entry point for optimization"""
        log.info(f"Optimizing problem: {problem.name}")
        
        # Select solver
        solver = self.select_solver(problem)
        if not solver:
            raise RuntimeError("No solver available")
        
        # Solve
        result = solver.solve(problem)
        
        # Log for learning
        self._log_optimization(problem, result)
        
        return result
    
    def _log_optimization(self, problem: OptimizationProblem, result: OptimizationResult):
        """Store optimization results for learning"""
        log_entry = {
            "problem_hash": self._get_problem_hash(problem),
            "problem_name": problem.name,
            "solver_type": result.solver_type.value,
            "execution_time": result.execution_time,
            "objective_value": result.objective_value,
            "status": result.status,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.solver_history.append(log_entry)
        log.debug(f"Logged optimization result: {log_entry}")
    
    def get_statistics(self) -> Dict:
        """Get solver statistics"""
        stats = {
            "total_problems": len(self.solver_history),
            "solvers": {},
            "average_execution_time": 0
        }
        
        for entry in self.solver_history:
            solver_type = entry["solver_type"]
            if solver_type not in stats["solvers"]:
                stats["solvers"][solver_type] = {
                    "count": 0,
                    "total_time": 0
                }
            stats["solvers"][solver_type]["count"] += 1
            stats["solvers"][solver_type]["total_time"] += entry["execution_time"]
        
        if stats["solvers"]:
            total_time = sum(s["total_time"] for s in stats["solvers"].values())
            stats["average_execution_time"] = total_time / len(self.solver_history)
        
        return stats

# Global engine instance
engine = OptimizationEngine()
