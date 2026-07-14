# Stage 04 — Multi-Turn User Simulator

**Status:** Planned

## Purpose

Evaluate support-agent conversations involving clarification, policies, tool calls, and state changes.

## Entry Criteria

- Multi-turn agent exists
- Tools and state transitions exist
- Operational policies are explicit
- Single-turn benchmark is stable

## Planned Case Contract

- `initial_state`
- `user_goal`
- `hidden_information`
- `policy_rules`
- `available_tools`
- `expected_actions`
- `forbidden_actions`
- `expected_final_state`
- `conversation_rubric`

## Non-Goals

- No simulator for the current single-turn FAQ bot
- No subjective conversation score without task/state validation
- No multi-turn work before single-turn is stable
