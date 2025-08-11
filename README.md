# ai-db-review

# Database Change Analyzer

## Overview

The **Database Change Analyzer** is a GitHub Action designed to analyze database schema changes, SQL query differences, and provide insightful recommendations using OpenAI's GPT models. It helps developers gain a better understanding of database modifications and their potential impact.

## Key Features
- **Schema and Query Analysis**: Compares database schemas and SQL queries to identify differences.
- **AI-Powered Recommendations**: Utilizes OpenAI models to provide useful suggestions and insights.
- **Seamless CI/CD Integration**: Easily integrates into GitHub workflows to provide automated analysis during pull requests.
- **LaunchDarkly AI Support**: Dogfooding AI Configs, making it easy to tweak prompts and models being used for recommendations across multiple database engines.

## Features in the works
- Load testing query performance before and after proposed changes with recommendation output based on real-world conditions
  - Detailed explanation of proposed query plan
  - Regression testing of proposed query compared to existing query performance
- Recommendations around catching breaking-changes and best practices in architectural changes

## How It Works
1. The tool connects to our database and retrieves information about schemas and queries.
2. It compares changes in database structure (`schema_diff`) and query behavior (`queries_diff`) between versions.
3. Insightful recommendations are generated using OpenAI's GPT models.
4. Results are posted as a comment in the related pull request, enabling developers to review directly in the code review process.

## Prerequisites
- The tool runs within a GitHub Actions workflow.
- Required secrets:
  - **OPENAI_API_KEY**: API key for OpenAI.
  - **GITHUB_TOKEN**: Token for GitHub comment management.
  - **LAUNCHDARKLY_SDK_KEY** for LaunchDarkly AI integration.

## Outputs
- AI-generated recommendations are added as a pull request comment.
- Logs and debug outputs are available in the workflow logs.