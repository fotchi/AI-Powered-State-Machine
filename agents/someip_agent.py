"""
Agent dedicated to the flync_4_someip submodel. Thin wrapper around
ModuleAgent -- all shared behavior (prompting, LLM call, validation)
lives in base_agent.py.
"""
from agents.base_agent import ModuleAgent


def build_agent(llm_router) -> ModuleAgent:
    return ModuleAgent(
        submodel_name="flync_4_someip",
        focus="Services, Methods, Events, Fields, Service Discovery, datatypes",
        llm_router=llm_router,
    )