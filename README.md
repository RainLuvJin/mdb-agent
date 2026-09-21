# MDB Agent

An LLM-powered Python application that converts Markdown documents into structured and validated SQLite database records.

> **Current version:** LLM-powered data pipeline
> **Planned evolution:** Tool-using Agent with dynamic orchestration

## Overview

MDB Agent helps users turn unstructured Markdown documents into records that can be safely stored in an existing SQLite database.

Instead of manually deciding which database table to use, mapping content to fields, and writing SQL statements, the system uses an LLM to perform semantic analysis and Python code to validate and safely execute the resulting database operation.

The current pipeline is:

```text
Markdown Document
       ↓
Read Document
       ↓
SQLite Schema Inspection
       ↓
LLM Analysis
       ↓
Structured JSON
       ↓
Schema Validation
       ↓
Parameterized SQL Generation
       ↓
Duplicate Detection
       ↓
Human Confirmation
       ↓
SQLite Database
```

## Motivation

Markdown is convenient for writing and maintaining content, but manually transferring that content into a structured database can be repetitive and error-prone.

For example, a project document might contain:

```markdown
# Campus Ride Sharing

A campus transportation project launched in September 2024.

Website: https://example.com
```

The application can identify that the document corresponds to the `projects` table and map the information to fields such as:

```text
title
category
content
website_url
start_date
```

The system then generates a parameterized SQL statement and asks for human confirmation before modifying the database.

## Architecture

```text
                    ┌──────────────────┐
                    │ Markdown Document│
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │  Document Reader │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │ Schema Inspector │
                    │     SQLite       │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │    DeepSeek LLM  │
                    │ Semantic Analysis │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │    Validator     │
                    │ Schema Checking   │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │  SQL Generator   │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │ Duplicate Check  │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │ Human Confirmation│
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │  SQLite Database │
                    └──────────────────┘
```

## Key Features

### 1. Dynamic SQLite Schema Inspection

The application reads the actual SQLite database schema instead of hard-coding the table structure.

It identifies:

* Table names
* Column names
* Data types
* Primary keys
* NOT NULL constraints
* Default values

This allows the LLM to reason about the current database structure.

### 2. LLM-Based Document Analysis

DeepSeek is used to analyze the Markdown document and determine:

* Which database table is appropriate
* Which document content maps to which fields
* Which values can be reliably extracted
* Which fields should remain `null`

The LLM is instructed not to invent information that cannot be found in the document.

### 3. Schema Validation

LLM output is treated as untrusted data.

Python validates the result before any database operation:

```text
AI Output
   ↓
Does the table exist?
   ↓
Do all fields exist?
   ↓
Is the primary key being modified?
   ↓
Validated Result
```

This separates semantic reasoning from deterministic validation.

### 4. Parameterized SQL Generation

The application generates parameterized SQL rather than allowing the LLM to directly execute arbitrary SQL.

Example:

```sql
INSERT INTO projects (title, category, website_url)
VALUES (?, ?, ?);
```

Values are passed separately to SQLite.

This provides a safer boundary between the LLM and the database.

### 5. Duplicate Detection

Before inserting a record, the application checks whether a likely duplicate already exists.

For example, projects and articles can be checked by title.

If a duplicate is detected, the system asks the user whether the new record should still be inserted.

### 6. Human-in-the-Loop

Database modification requires explicit user confirmation.

The system does not allow the LLM to directly modify the database without a human approval step.

```text
AI Decision
     ↓
SQL Preview
     ↓
Human Approval
     ↓
Database Write
```

## Project Structure

```text
mdb-agent/
│
├── agent.py
├── test.md
├── .env
├── .gitignore
│
└── tools/
    ├── schema.py
    ├── llm.py
    ├── validator.py
    └── database.py
```

### Components

| File                 | Responsibility                                         |
| -------------------- | ------------------------------------------------------ |
| `agent.py`           | Main application workflow                              |
| `tools/schema.py`    | Reads SQLite database schema                           |
| `tools/llm.py`       | Sends documents and schema to the LLM                  |
| `tools/validator.py` | Validates LLM output                                   |
| `tools/database.py`  | Generates SQL, checks duplicates, and executes inserts |

## Installation

Clone the repository:

```bash
git clone https://github.com/<your-username>/mdb-agent.git
cd office-agent
```

Create a virtual environment:

```bash
python -m venv .venvname
```

Activate it on Windows:

```powershell
.venvname\Scripts\activate
```

Install dependencies:

```bash
pip install openai python-dotenv
```

## Configuration

Create a `.env` file:

```env
DEEPSEEK_API_KEY=your_api_key_here
DATABASE_PATH=path/to/your/database.db
```

Do not commit `.env` or your database file to GitHub.

## Usage

Run the application with a Markdown file:

```bash
python mdbapp.py test.md
```

The application will:

1. Read the Markdown document.
2. Inspect the SQLite schema.
3. Ask the LLM to classify and extract the document.
4. Validate the LLM output.
5. Generate a parameterized SQL statement.
6. Check for possible duplicates.
7. Display the proposed database operation.
8. Ask for human confirmation.
9. Insert the record if approved.

Example output:

```text
========== AI Result ==========

{
    "table": "projects",
    "reason": "The document describes a project...",
    "fields": {
        "title": "title input",
        "category": "category",
        "website_url": "https://example.com"
    }
}

========== SQL Preview ==========

INSERT INTO projects (title, category, website_url)
VALUES (?, ?, ?);

是否写入数据库？(y/n):
```

## Design Principles

### LLM as Reasoning Component

The LLM is responsible for semantic tasks such as:

* Classification
* Information extraction
* Field mapping

### Python as Control and Safety Layer

Deterministic Python code is responsible for:

* Schema validation
* SQL construction
* Duplicate detection
* Database operations
* Human confirmation

This prevents the LLM from having unrestricted control over the database.

## Current Limitations

The current implementation is intentionally simple.

The workflow is still largely predetermined by Python:

```text
Read → Analyze → Validate → Generate SQL → Check → Insert
```

The LLM does not yet dynamically decide which tools to call or what action to take next.

Therefore, the current system is better described as an **LLM-powered application** rather than a fully autonomous Agent.

## Future Development

The project is designed to evolve toward a more complete Agentic system.

### Phase 1 — Tool Use

Expose database operations as tools:

```text
read_schema()
search_database()
create_record()
update_record()
delete_record()
```

The LLM will be able to decide which tool should be used.

### Phase 2 — Agent Loop

Replace the fixed workflow with an iterative decision loop:

```text
User Goal
   ↓
Agent
   ↓
Choose Tool
   ↓
Tool Result
   ↓
Agent
   ↓
Choose Next Action
   ↓
...
   ↓
Final Result
```

### Phase 3 — Memory

Add persistent memory for relevant user preferences and previous operations.

### Phase 4 — RAG

Add retrieval capabilities for large collections of Markdown documents and project knowledge.

### Phase 5 — Agent Orchestration

Experiment with frameworks such as LangGraph to manage:

* Agent state
* Tool calls
* Conditional routing
* Loops
* Human approval
* Persistent checkpoints

The goal is not to add frameworks for their own sake, but to evaluate when explicit agent orchestration becomes useful as system complexity increases.

## Tech Stack

* Python
* SQLite
* DeepSeek API
* OpenAI Python SDK
* python-dotenv
* Git / GitHub

## Learning Goal

This project serves as a practical exploration of the transition from traditional Python programs and LLM-powered applications toward agentic systems.

The development path is intentionally incremental:

```text
LLM API
   ↓
```
