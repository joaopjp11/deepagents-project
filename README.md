# deepagents

Deepagents is a implementation of the deepagents package to apply deepagent architeture and other AI concepts in real code.

---

## 🧩 Table of Contents

- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Running the Project](#running-the-project)
- [Testing](#testing)
- [Git Workflow](#git-workflow)
- [Contributing Guidelines](#contributing-guidelines)
- [Code Standards](#code-standards)
- [FAQ](#faq)
- [License](#license)

---

## 🛠️ Getting Started

### Prerequisites

List what software or versions are needed:

```bash
npm >=11.6.0
Python >= 3.13.17
poetry >= 2.2.1
```

### How to install
In the directory where you normaly you store your projects run

```bash
git clone https://github.com/joaopjp11/deepagents-project.git
cd deepagents-project
poetry install

```

### The virtual enviroment
You can start the virtual enviroment in your shell with
```bash
.venv\Scripts\activate.bat #creates 
```
when you are in the virtual enviroment any code that is run as access to the packages that were installed

And you can end the virtual enviroment session with 
```bash
deactivate
```
You can also use the virtual enviroment for a single command by using poetry as a prefix to the command
```bash
#Example
poetry run python main.py

```

## Project Structure
```
project-root/
├── src/               # Source code
│   ├── llm/           # Deep agent configuration
│   ├── models/        #
│   ├── routers/       # Endpoints
│   ├── tools/         # Tools or deep agent and subagents
│   ├── workflow/      # Subagent and graphs
│   └── main.js
├── tests/             # Unit and integration tests
├── docs/              # Documentation
├── .github/           # GitHub workflows, issue templates
├── pyproject.toml     # File used by poetry to know what packages to install
├── README.md
```

## Running the Project
To run the project 
```bash
poetry run uvicorn src.api:app --reload
```
#### About this command 
*uvicorn* - An ASGI (Asynchronous Server Gateway Interface) server that runs async Python web applications. It's commonly used with FastAPI and other modern async frameworks.

*--reload* - Enables auto-reload during development. The server automatically restarts whenever you save changes to your code, so you don't have to manually stop and restart it.

## Testing 
Testing is crucial for code developing and mantainence, so the test will be design to be automatc through GitHub Actions, the test files should be located in the tests folder
```
project-root/
├── src/
├── tests/  
|   └──test_*.py
|...
```
with the name test_* so that it can be run by pytest 

## 🧭 Git Workflow

This project follows a feature-branch workflow to keep development organized, maintainable, and easy to review.

### 📚 Branch Naming Convention

Use descriptive names for branches based on the type of work you're doing:
| Type          | Prefix     | Example                     |
|----------------|------------|------------------------------|
| New Feature    | feature/   | feature/add-login-page       |
| Bug Fix        | fix/       | fix/navbar-overflow          |
| Documentation  | docs/      | docs/update-readme           |
| Refactor       | refactor/  | refactor/auth-service        |
| Testing        | test/      | test/add-user-api-tests      |

### 🧩 Workflow Steps

1. Pull the latest changes
```bash
git checkout main
git pull origin main 
```
2. Create a new branch
```bash
git checkout -b prefix/yourbranch
```
3. Make your changes
- Write clear, concise, and well documented code, hopefully.
- If you add a new featyre or module, **add corresponding tests in the  /tests folder, it can be an empty test, but in that case create a new issue on the Repo to track things
- Follow the project's linting rules

4. Commit your work
```bash´
git add .
git commit -m "feat: meaningull commit message
```
> Use Coventional Commits format 
> - feat: for new features
> - fix: for bug fixes
> - docs: for documentation changes
> - test: for adding or updating tests
> - refactor: for code improvements taht don't change behavior

A branch can have various commit types feat, fix, docs, test, only the main one should be in the name of the PR, but every type of commit should be respected for us to have a compreesible history of the develop, besides all the type of commits then can be added in the Summary of the Pull request
5. Sync your branch
```bash
git fetch origin
git rebase origin/main
```
> Rebasing helps keep history clean, Resolve conflicts if any occur.
This shoudl be done when our branch is behind the main branch in commits
6. Push 
```bash
git push -u origin feature/your-branch-name
```
7. Open a Pull Request
- Go to the ropository on GitHub.
- Open a PR to merge your branch into main.
- Include a clear description of what you changed and why.

Ex:
`````````
Title:feat: add login page with authentication logic
Description:
This PR introduces a new login page that allows users to authenticate using their email and password.
It integrates with the existing authentication API and adds form validation to prevent invalid submissions.

Changes Made:
- Added LoginPage component under src/pages/
- Implemented authentication service in src/services/auth.js
- Added form validation with error handling (empty fields, invalid email)
- Updated routes to include /login
- Created tests for login functionality in tests/login.test.js

Why This Change Was Made:
We needed a user login.
This is part of the onboarding milestone for Sprint 3.

Checklist:
 - Code builds and runs locally
 - Tests added for new functionality
 - Linting and formatting pass
 - Documentation updated (README + inline comments)
`````````
- Request reviews from a team member.
8. Code Review Merge
- Address review feedback promptly.
- Once approved and all tests pass, merge using “Squash and Merge” to keep commit history clean.
- Delete the feature branch after merging.

### GitActions
### GitHub Issues

The **Issues** tab in the project repository serves as our **centralized team-wide To-Do list**. Any team member with an idea, improvement, bug fix, or feature request should create an issue.  

- Issues can be **open-ended**, **small in scope**, or **larger projects**—all are welcome.  
- Each issue should include a **level of priority or importance**, so the team can focus on what matters most.  
- Properly described issues help **track progress, assign responsibilities, and plan future work** efficiently.  

> **Clarification:** GitHub Issues are meant for **team-level tracking**, not just personal thoughts. Each issue represents work to be done, a bug to fix, or a discussion to have. While small personal tasks can inspire issues, not every minor idea needs an issue.  

> **Tip:** When creating an issue, provide a **clear title, detailed description, and any relevant context** (like screenshots, references, or expected behavior). This ensures that anyone reading the issue understands it quickly and can contribute effectively.
