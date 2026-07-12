# Task 5 — Skill Safety Audit

## Skill Audited

**Skill Creator**

## Purpose of the Audit

The purpose of this task was to check whether a Skill is safe before enabling or using it. I audited the Skill in plain English to understand what it does, what data it touches, and whether it creates any privacy or security risk.

## What the Skill Does

The Skill Creator helps users create a new custom Skill. It asks clarifying questions about the task, understands the required format and rules, and then generates a `SKILL.md` file. The file usually includes the skill name, description, trigger phrases, and step-by-step instructions for how the AI should behave when the skill is used.

## What Data the Skill Touches

This skill only uses the information that I provide in the chat, such as:

- The task I want to automate
- My preferred output format
- My instructions and rules
- Example trigger phrases
- Any personal preferences I include for the skill

It does not need access to my Gmail, Drive, passwords, bank details, or any private app data.

## Sensitive Access Check

### Does it contact an external server?

I did not see any need for this skill to contact an external server. Its main purpose is to generate written instructions for a new Skill.

### Does it handle credentials or passwords?

No. This skill should not need or request passwords, API keys, login details, or private credentials.

### Does it send my data anywhere unexpected?

Based on the purpose of the skill, it should only use the information inside the current AI chat to generate the `SKILL.md`. I would still avoid giving it unnecessary personal or sensitive information.

### Does it modify files or accounts?

The skill can help create a `SKILL.md` file, but it should not directly modify my external accounts, send emails, delete files, or make changes in connected apps.

## Possible Risks

The main risk is that I may accidentally include sensitive information inside the skill instructions. Another risk is that the generated skill may be too broad and could trigger when I do not expect it. To avoid this, I should review the generated `SKILL.md` before enabling it and make sure the instructions are clear and limited.

## Safety Decision

I believe the Skill Creator is safe to enable for normal use because it only helps create skill instructions and does not require sensitive permissions. I would trust it for creating basic personal or study-related skills, but I would not include passwords, private account information, financial details, or confidential business data.

## Final Safety Statement

I would enable this skill because it does not appear to require external access, credentials, or write permissions. It only uses the information I provide and turns it into a reusable `SKILL.md` file, so it is safe as long as I review the output and avoid sharing sensitive data.
