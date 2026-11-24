---
name: log-incident-investigation
description: investigate application, kubernetes, and documentum logs using adaptive keyword generation, iterative evidence retrieval, exception-chain analysis, event correlation, and evidence-grounded root-cause identification. use when analyzing logs, troubleshooting incidents, investigating pod or application failures, identifying exceptions, correlating events, or recommending resolution steps.
---

# Log Incident Investigation

## Objective

Investigate application, Kubernetes, and Documentum incidents without loading
an entire large log file into the model context.

Use adaptive keyword generation and iterative search refinement to locate the
most relevant evidence.

## Workflow

### 1. Understand the incident request

Extract available investigation signals from the user query:

- Reported symptom
- Error message
- Application or product name
- Component or service name
- Pod, container, or host name
- Request ID or correlation ID
- User-provided timestamp or time range
- Operation that failed
- Relevant log filename

Do not assume values that the user did not provide.

### 2. Discover relevant logs

Use `glob` to locate candidate log files.

Prioritize:

1. Exact filenames provided by the user
2. Logs for the named pod, service, or component
3. Logs modified near the reported incident time
4. Application and platform logs related to the reported symptom

Inspect file size before requesting content.

### 3. Generate initial search keywords dynamically

Before calling `grep`, generate a small set of initial search terms from the
user request, discovered filenames, application context, and reported
symptoms.

The initial search plan should contain no more than 5 to 10 high-value terms.

Potential keyword categories include:

- Exact user-provided error text
- Exception class names
- Application or component names
- Pod, container, host, or service names
- Operation names
- Correlation IDs
- Request IDs
- Status codes
- Relevant timestamps
- General severity markers when no specific signal is available

General severity markers may include:

- `ERROR`
- `FATAL`
- `CRITICAL`
- `SEVERE`
- `Exception`
- `Traceback`
- `Caused by`
- `failed`
- `panic`

Do not search every generic keyword automatically. Select only keywords
relevant to the current incident.

### 4. Perform the first bounded search

Use `grep` with:

- An explicit file or glob filter
- A bounded `max_count`
- The most specific keywords first
- Content output only when needed
- No unrestricted recursive result collection

Example:

```json
{
  "pattern": "Smartview|Exception|ERROR",
  "path": "/",
  "glob": "pod0-D2-Smartview.log",
  "output_mode": "content",
  "max_count": 20
}