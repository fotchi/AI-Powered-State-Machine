"""
Agent dedicated to the flync_4_ecu submodel. Thin wrapper around
ModuleAgent -- all shared behavior (prompting, LLM call, validation)
lives in base_agent.py.
"""
from phase1.agents.base_agent import ModuleAgent


def build_agent(llm_router) -> ModuleAgent:
    return ModuleAgent(
        submodel_name="flync_4_ecu",
        focus="Controller, Switch/VirtualSwitch, Router, PHY config, internal topology, Sockets",
        llm_router=llm_router,
    )