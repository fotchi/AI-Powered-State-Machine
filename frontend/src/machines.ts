// Shared with ScenarioGeneration.tsx and StateMachine.tsx -- the 12 real
// State Machines from phase1/coverage/state_machines/, not a mock.
export const MACHINE_LABELS: Record<string, string> = {
  ecu: "ECU", controller: "Controller", ethernet: "Ethernet", can: "CAN",
  lin: "LIN", socket: "Socket", endpoint: "Endpoint", deployment: "Deployment",
  someip: "SOME/IP", pdu: "PDU", signal: "Signal", frame: "Frame",
};

export interface MachineState {
  on_pass: string;
  on_fail: string;
  coverage_tag?: string;
}

export interface MachineDef {
  id: string;
  phase1_module: string;
  states: Record<string, MachineState>;
  terminal_pass: string;
}

export type MachineMap = Record<string, MachineDef>;
