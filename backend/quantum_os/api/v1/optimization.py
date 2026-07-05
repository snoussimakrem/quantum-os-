from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from quantum_os.domain.optimization.problem import OptimizationProblem, ProblemType
from quantum_os.domain.optimization.engine import engine
from quantum_os.core.logging import log

router = APIRouter(prefix="/optimization", tags=["optimization"])

class OptimizationRequest(BaseModel):
    """Request model for optimization"""
    name: str
    description: str = ""
    problem_type: str = "minimize"
    variables: Dict[str, Any]
    objective: str
    constraints: list[str] = []
    bounds: Dict[str, tuple] = {}

class OptimizationResponse(BaseModel):
    """Response model for optimization"""
    success: bool
    solution: Dict[str, Any]
    objective_value: float
    execution_time: float
    solver_used: str
    iterations: int
    status: str
    metadata: Dict[str, Any]

@router.post("/solve")
async def solve_optimization(request: OptimizationRequest) -> OptimizationResponse:
    try:
        def objective(**kwargs):
            return sum(kwargs.values())
        
        def constraint_parser(constraint_str: str):
            return lambda **kwargs: True
        
        constraints = [constraint_parser(c) for c in request.constraints]
        
        problem = OptimizationProblem(
            variables=request.variables,
            objective=objective,
            constraints=constraints,
            bounds=request.bounds if request.bounds else None,
            problem_type=ProblemType(request.problem_type),
            name=request.name,
            description=request.description
        )
        
        result = engine.optimize(problem)
        
        return OptimizationResponse(
            success=result.status == "success",
            solution=result.solution,
            objective_value=result.objective_value,
            execution_time=result.execution_time,
            solver_used=result.solver_type.value,
            iterations=result.iterations,
            status=result.status,
            metadata=result.metadata
        )
        
    except Exception as e:
        log.error(f"Optimization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/solvers")
async def list_solvers():
    return {
        "solvers": [
            {
                "name": solver.name,
                "type": solver.solver_type.value,
                "description": solver.description
            }
            for solver in engine.solvers.values()
        ]
    }

@router.get("/statistics")
async def get_statistics():
    return engine.get_statistics()
