# Task 2 — Connect One App, Read-Only

## Connector Used

**Indeed Connector**

## Task Overview

In this task, I connected one real app to the AI using a connector. I used the Indeed connector to search for real job listings without manually copying and pasting data.

## Purpose of the Task

The purpose of this task was to understand how connectors work and how AI can safely retrieve live data from an external app using read-only access.

## What I Asked the AI To Do

I asked Claude to use the Indeed connector to find jobs posted in the last 2 days related to Senior Laravel Developer roles.

## Example Prompt

```text
Use my Indeed connector only. Find jobs posted in the last 2 days related to Senior Laravel Developer.

Search for these related titles:
- Senior Laravel Developer
- Senior PHP Developer Laravel
- Laravel Backend Developer
- Lead Laravel Developer
- PHP Laravel Engineer

Return the best 10 jobs only with title, company, location, posted date, salary if available, key requirements, apply link, and match score for my profile.
```

## Data Retrieved

The AI retrieved live job listing information from Indeed, such as job title, company name, location, posted date, job type, salary if available, key requirements, and apply link.

## Permission Statement

I granted Claude read-only access to my Indeed account so it could search and summarize recent Laravel senior developer jobs. I did not need write permission because I only wanted to view and review job listings.

## Learning Outcome

From this task, I learned that connectors allow AI to safely access real data from connected apps. I also learned the importance of understanding what permissions I am granting before connecting any app.
