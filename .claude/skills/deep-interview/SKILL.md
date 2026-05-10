---
name: deep-interview
description: Ambiguity gate. Before acting on a request without specificity, ask 3-5 clarifying questions.
trigger: interview, requirements, clarify, ambiguous
---

# deep-interview

Loaded when the request lacks specificity signals — no file path, no function name, no numbered step, no error message. Default reaction is to clarify, not to guess.

## When this fires automatically

A request has zero specificity signals. Examples:

- "Make it faster"
- "Fix the bug"
- "Refactor this"
- "Add tests"
- "It's broken"

A request can bypass this skill by including the prefix `force:` (the user has already decided and wants execution).

## Output shape

3-5 questions, each:

1. Numbered.
2. Surfacing one specific assumption you would have to make to proceed.
3. Offering 2-3 candidate answers when the question has obvious shapes (multiple-choice format saves the user typing).

## Question categories

- **Scope**: which file, which function, which user, which environment?
- **Success criteria**: how do we know it is done? What test should pass?
- **Constraints**: what should NOT change?
- **Tradeoffs**: cost / time / quality — which axis matters most here?
- **Reversibility**: if this fails, can we roll back, and how?

## Banned questions

- "What do you want?" — too open, restate as scoped multiple choice.
- "Are you sure?" — assume the user is sure of what they said; clarify what they did not say.
- "Should I do X?" — anchors on your candidate. Ask "should this be X or Y or Z?" instead.

## Exit criteria

- User answers the questions.
- Or user adds the `force:` prefix and tells you to proceed with stated assumptions.
- Or you reach 5 questions and the user has not answered any — at that point, stop asking and produce a stated-assumptions report so the user can react.

## Anti-pattern: questions for the sake of questions

If the request has clear specificity, do NOT load this skill. The skill exists to prevent silent guesses, not to add a hurdle to every prompt.
