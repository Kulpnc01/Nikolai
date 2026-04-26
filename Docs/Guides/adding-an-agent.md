# Adding an Agent / Module to Nikolai 0.3

In Nikolai 0.3, agents are implemented as autonomous modules delivered via the GCLI pipeline.

## 1. Directory Structure
Create a new folder in `C:\Nikolai_0_3\modules\<AgentName>\`. 
Include the standard artifact subdirectories:
- `/pipeline/incoming`
- `/pipeline/outgoing`

## 2. The Integration Contract
Create a `module_contract.json` in the `/incoming` directory. This file must define:
- **Capabilities:** What the agent can do (e.g., `ocr`, `routing`).
- **Interfaces:** The communication protocols used (e.g., `grpc`, `json_rpc`).
- **Security Policy:** Which local directories the agent is allowed to access.

## 3. Activation
Once the contract and source ZIP (e.g., `agent_source.zip`) are placed in the incoming pipeline, Nikolai's **Phi Silica** layer will automatically detect, unpack, and register the agent.

## 4. Interaction
The **Executive Layer** will acknowledge the new capabilities and route relevant intents to the agent automatically based on the contract definitions.
