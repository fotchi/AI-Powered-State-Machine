"""
Agent dedicated to the flync_4_communication submodel. Thin wrapper around
ModuleAgent -- all shared behavior (prompting, LLM call, validation)
lives in base_agent.py.
"""
from agents.base_agent import ModuleAgent


def build_agent(llm_router) -> ModuleAgent:
    return ModuleAgent(
        submodel_name="flync_4_communication",
        focus="FLYNCChannelConfig, TCPOption, UDPOption",
        llm_router=llm_router,
    )