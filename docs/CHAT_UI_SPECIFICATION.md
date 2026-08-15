# Chat UI Specification

## Layout
Blender-native AI Workspace with:
- header
- conversation
- context indicator
- tool activity
- proposal cards
- approval controls
- composer

## Message Types
- user
- assistant
- tool started
- tool completed
- warning
- error
- action proposal
- approval request
- execution result

## Action Proposal
Show:
- what will change
- target count/names
- parameters
- risk level
- affected scene area
- Preview
- Apply
- Cancel

## State Model
`idle → thinking → tool_running → proposal → awaiting_approval → executing → completed/error`.

## UX Principles
- Never hide a destructive action.
- Keep tool activity understandable.
- Show the current scene/selection context.
- Make cancellation obvious.
- Preserve conversation history.
- Avoid forcing users to leave Blender.

## MVP
Do not build a complex web-style chat application inside Blender. Prioritise reliable native controls and clear action proposals.
