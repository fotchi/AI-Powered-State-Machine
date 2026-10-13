"""
Agent dedicated to the flync_4_bus submodel. Thin wrapper around
ModuleAgent -- all shared behavior (prompting, LLM call, validation)
lives in base_agent.py.
"""
from phase1.agents.base_agent import ModuleAgent


def build_agent(llm_router) -> ModuleAgent:
    return ModuleAgent(
        submodel_name="flync_4_bus",
        focus="CANBus, LINBus, LIN Schedule Tables (order, timing)",
        llm_router=llm_router,
    )