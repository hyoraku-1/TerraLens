# Contributing to TerraLens

First off — thank you for taking the time to contribute! TerraLens is a community-driven project and every contribution, big or small, makes a difference.

---

## Table of Contents

- [Getting Started](#getting-started)
- [Priority Contributions](#priority-contributions)
- [Adding Cloud Resources](#adding-cloud-resources)
- [Adding Blueprints](#adding-blueprints)
- [Code Style](#code-style)
- [Running Tests](#running-tests)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Reporting Bugs](#reporting-bugs)
- [Feature Requests](#feature-requests)

---

## Ways to Contribute

You don't have to write code to contribute — there are many ways to help:

| Type | Examples |
|---|---|
| 🐛 **Bug reports** | Found something broken? Open an issue with steps to reproduce |
| 📖 **Documentation** | Fix typos, clarify confusing sections, improve the README |
| 💻 **Source code** | Fix bugs, add features, refactor existing code |
| ☁️ **Cloud resources** | Add missing AWS, Azure, or GCP resources to the catalog |
| 🏗️ **Blueprints** | Add new infrastructure blueprints to `blueprints.py` |
| 🧪 **Tests** | Write new tests, improve coverage, add edge case handling |
| 🎨 **UI improvements** | Improve the Textual layout, fix alignment issues, enhance the visual design |
| 💡 **Feature ideas** | Open an issue to suggest new features or improvements |
| 🔍 **Code review** | Review open pull requests and leave feedback |

Every contribution matters — even fixing a single typo in the README is genuinely appreciated.

---

## Getting Started

```bash
# 1. Fork the repository on GitHub

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/TerraLens.git
cd TerraLens

# 3. Create a virtual environment
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 4. Install in editable mode
pip install -e .
pip install pytest pytest-cov

# 5. Create a feature branch
git checkout -b feature/your-feature-name

# 6. Make your changes, then run tests
pytest tests/ -v

# 7. Push and open a Pull Request
git push origin feature/your-feature-name
```

---

## Priority Contributions

### 🔥 #1 — Add Azure and GCP Provider Support

Currently TerraLens only supports AWS in the Add Resource wizard. The provider selection screen already shows Azure, GCP, Oracle, Docker, and Kubernetes marked as "coming soon". The goal is to make at least **Azure and GCP** fully functional.

**What needs to be done:**

Add a resource catalog for each provider in `catalog.py`:

```python
AZURE_RESOURCE_CATALOG: dict[str, list[dict]] = {
    "Compute": [
        {"type": "azurerm_virtual_machine",       "description": "Azure virtual machine"},
        {"type": "azurerm_linux_virtual_machine",  "description": "Linux virtual machine"},
        # ...
    ],
    "Storage": [
        {"type": "azurerm_storage_account", "description": "Azure storage account"},
        # ...
    ],
    # ...
}
```

Then wire up the provider picker in `cli.py` to route to the correct catalog screen when Azure or GCP is selected. Suggested categories to cover:

**Azure** — Compute, Storage, Networking, Database, IAM, Containers (AKS), Serverless (Azure Functions)

**GCP** — Compute Engine, Cloud Storage, VPC, Cloud SQL, IAM, GKE, Cloud Functions

---

### 🏗️ #2 — Add More Infrastructure Blueprints

TerraLens ships with 8 blueprints in `blueprints.py`. There is a lot of room to grow. Some ideas:

| Blueprint | Components |
|---|---|
| **Private ECS Cluster** | VPC, private subnets, ECS cluster, ECR, ALB, ECS service + task definition |
| **Data Pipeline** | S3 (raw + processed), Glue job, Glue crawler, Athena workgroup |
| **Event-Driven Architecture** | SNS topic, SQS queue, Lambda consumer, DLQ |
| **CI/CD Pipeline** | CodeCommit, CodeBuild, CodePipeline, S3 artifact store, IAM roles |
| **Monitoring Stack** | CloudWatch log group, metric alarms, SNS notification, CloudTrail |
| **RDS with Read Replica** | VPC, private subnets, primary RDS, read replica, subnet group |
| **Redis Cache Layer** | VPC, private subnets, ElastiCache replication group, security group |

See [Adding Blueprints](#adding-blueprints) below for the format.

---

### 🧪 #3 — Expand Test Coverage

The current test suite covers `state.py` and `catalog.py`. These areas need tests:

- `blueprints.py` — test that every blueprint renders valid HCL with default values, all field names resolve, no missing `{placeholders}`
- `cli.py` screens — basic Textual app mount/compose tests using `pytest-asyncio` and Textual's test helpers
- Edge cases — empty state file, malformed state file, missing `.insight-tf.json` config

```bash
# Run with coverage to see what's missing
pytest tests/ -v --cov=src/insight_tf --cov-report=term-missing
```

---

### 🎨 #4 — Windows Binary Fix

The Windows binary (`insight-tf-windows-latest.exe`) has historically had issues with PyInstaller bundling. If you have a Windows machine, testing the binary end-to-end and reporting or fixing any issues is very valuable.

Known areas to check:
- Emoji rendering in Windows Terminal vs CMD vs PowerShell
- `which terraform` vs `where terraform` on Windows (the app uses `which` which may not work on Windows CMD)
- File path separators in state file loading

---

## Adding Cloud Resources

**Adding a basic catalog entry** (shows up in the picker, generates a scaffold):
```python
# In catalog.py → AWS_RESOURCE_CATALOG, find the right category:
{"type": "aws_your_resource", "description": "Short description of what it does"},
```

**Adding a guided form** (fills fields interactively in the wizard):
```python
# In catalog.py → RESOURCE_TEMPLATES:
RESOURCE_TEMPLATES["aws_your_resource"] = {
    "description": "Short description",
    "fields": [
        {"name": "resource_name", "label": "Resource name (TF identifier)",
         "placeholder": "my_resource", "required": True, "default": ""},
        {"name": "some_field",    "label": "Some field label",
         "placeholder": "example-value", "required": True, "default": ""},
    ],
    "template": 'resource "aws_your_resource" "{resource_name}" {{\n  some_field = "{some_field}"\n}}\n',
}
```

Please keep resources in **alphabetical order** within their category.

---

## Adding Blueprints

Blueprints live in `src/insight_tf/blueprints.py`. Each blueprint is a dict in the `BLUEPRINTS` list with this structure:

```python
{
    "id": "my_blueprint",           # unique snake_case ID
    "name": "My Blueprint",         # display name in the picker
    "icon": "🏗️",                   # emoji shown next to the name
    "description": "Short description of what this blueprint provisions",
    "resources": [                  # list shown in the picker card
        "aws_vpc", "aws_subnet", "aws_instance",
    ],
    "fields": [
        {
            "name":        "vpc_name",       # used as {vpc_name} in template
            "label":       "VPC resource name",
            "placeholder": "main",
            "default":     "main",
            "required":    True,
        },
        # ... more fields
    ],
    "template": '''\
resource "aws_vpc" "{vpc_name}" {{
  cidr_block = "{vpc_cidr}"
}}
# ... more resources, referencing each other by Terraform expressions
''',
}
```

**Rules for blueprint HCL:**
- Always use Terraform resource references — `aws_vpc.{vpc_name}.id` not hardcoded IDs
- Every `{placeholder}` in the template must have a matching field `name`
- Use `{{` and `}}` to escape literal curly braces in HCL (Python `.format()` syntax)
- Test your blueprint renders cleanly before submitting:

```python
from insight_tf.blueprints import build_blueprint_hcl
values = {f["name"]: f["default"] or f["placeholder"] for f in blueprint["fields"]}
print(build_blueprint_hcl("my_blueprint", values))
```

---

## Code Style

- Follow existing code style — the project uses standard Python formatting
- Keep individual files under 500 lines where possible
- Add a short docstring to any new class or function
- Use type hints for function signatures
- The codebase is split into `state.py`, `catalog.py`, `blueprints.py`, and `cli.py` — keep concerns in the right file
- Do not introduce new dependencies without discussing in an issue first

---

## Running Tests

```bash
# Run the full test suite
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src/insight_tf --cov-report=term-missing

# Run a specific test file
pytest tests/test_catalog.py -v
```

All pull requests must pass the test suite before being merged. If you add a new feature, please add corresponding tests in the `tests/` directory.

---

## Submitting a Pull Request

1. Make sure your branch is up to date with `main`:
   ```bash
   git fetch origin
   git rebase origin/main
   ```
2. Run the full test suite and ensure everything passes
3. Write a clear PR title and description explaining what you changed and why
4. Reference any related issues with `Fixes #123` or `Closes #123`
5. Keep PRs focused — one feature or fix per PR makes review much easier

---

## Reporting Bugs

Open a [GitHub Issue](https://github.com/bhuvan-raj/TerraLens/issues) and include:

- Your OS and Python version
- How you installed TerraLens (binary / pip / source)
- Steps to reproduce the bug
- The full error message or traceback
- Your `terraform version` output if the bug involves plan/apply/destroy

---

## Feature Requests

Open a [GitHub Issue](https://github.com/bhuvan-raj/TerraLens/issues) with the `enhancement` label. Describe:

- What you want TerraLens to do
- Why it would be useful
- Any implementation ideas you have

---

## Questions?

If you're unsure about anything, open an issue and ask. No question is too small.

---

<div align="center">
  <sub>Thank you for helping make TerraLens better ❤️</sub>
</div>
