import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from . import models, crud

async def select_operator(db: AsyncSession, source_id: int) -> int | None:
    """
    Selects an operator for a new contact based on:
    1. Source configuration (weights)
    2. Operator activity status
    3. Operator workload limit
    """
    
    # 1. Get all operators configured for this source
    stmt = select(models.SourceOperatorConfig, models.Operator).join(
        models.Operator, models.SourceOperatorConfig.operator_id == models.Operator.id
    ).where(
        models.SourceOperatorConfig.source_id == source_id,
        models.Operator.is_active == True
    )
    
    result = await db.execute(stmt)
    configs = result.all() # List of (SourceOperatorConfig, Operator)
    
    if not configs:
        return None

    # 2. Filter by workload limit
    eligible_operators = []
    weights = []
    
    for config, operator in configs:
        current_workload = await crud.get_operator_workload(db, operator.id)
        if current_workload < operator.workload_limit:
            eligible_operators.append(operator)
            weights.append(config.weight)
    
    if not eligible_operators:
        return None
        
    # 3. Weighted random selection
    # random.choices returns a list, we take the first element
    selected_operator = random.choices(eligible_operators, weights=weights, k=1)[0]
    
    return selected_operator.id
