"""
cli.py — TerraLens UI
All Textual screens, widgets, the InsightTF app class, and the CLI entry point.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    RichLog,
    Static,
    TabbedContent,
    TabPane,
    TextArea,
    Tree,
)
from textual.widgets.tree import TreeNode
from rich.table import Table
from rich import box

from .state import APP_CONFIG, SAMPLE_STATE, load_state, format_value
from .catalog import (
    AWS_RESOURCE_CATALOG,
    ALL_AWS_RESOURCES,
    PROVIDERS,
    RESOURCE_TEMPLATES,
    _cat_id,
    _build_tf_block,
)


# ─────────────────────────────────────────────
# Overview Page
# ─────────────────────────────────────────────
class StatCard(Static):
    DEFAULT_CSS = """
    StatCard {
        border: tall $accent;
        padding: 1 2;
        margin: 1;
        width: 1fr;
        background: $surface;
        height: 7;
    }
    StatCard .card-label {
        color: $text-muted;
        text-style: italic;
    }
    StatCard .card-value {
        text-style: bold;
        color: $accent;
        content-align: center middle;
        text-align: center;
        padding-top: 1;
    }
    """

    def __init__(self, label: str, value: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._label = label
        self._value = value

    def compose(self) -> ComposeResult:
        yield Label(self._label, classes="card-label")
        yield Label(self._value, classes="card-value")


class OverviewPage(Container):
    DEFAULT_CSS = """
    OverviewPage {
        padding: 1 2;
    }
    #cards-row {
        height: auto;
        margin-bottom: 1;
    }
    #resource-table {
        border: tall $panel;
        padding: 1 2;
        background: $surface;
        height: 1fr;
    }
    .section-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }
    """

    def __init__(self, state: dict[str, Any], **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._state = state

    def compose(self) -> ComposeResult:
        resources = self._state.get("resources", [])
        tf_ver = self._state.get("terraform_version", "N/A")
        serial = self._state.get("serial", "N/A")
        total = len(resources)

        yield Label("📊  Infrastructure Overview", classes="section-title")
        with Horizontal(id="cards-row"):
            yield StatCard("Terraform Version", tf_ver)
            yield StatCard("State Serial", str(serial))
            yield StatCard("Total Resources", str(total))
            yield StatCard(
                "Providers",
                str(len({r.get("provider", "").split("/")[-1] for r in resources})),
            )

        yield Label("Resource Summary", classes="section-title")
        yield self._build_table(resources)

    def _build_table(self, resources: list[dict]) -> Static:
        table = Table(
            "Type", "Name", "Provider", "Instances",
            box=box.SIMPLE_HEAVY,
            border_style="cyan",
            header_style="bold cyan",
            show_lines=True,
        )
        for r in resources:
            rtype = r.get("type", "N/A")
            name = r.get("name", "N/A")
            provider = r.get("provider", "N/A").split("/")[-1].replace('"', "")
            instances = str(len(r.get("instances", [])))
            table.add_row(rtype, name, provider, instances)
        return Static(table)


# ─────────────────────────────────────────────
# Manage Page — widgets
# ─────────────────────────────────────────────
class ResourceTree(Tree):
    DEFAULT_CSS = """
    ResourceTree {
        border: tall $panel;
        background: $surface;
        padding: 0 1;
        width: 35;
    }
    """


class AttributePanel(ScrollableContainer):
    DEFAULT_CSS = """
    AttributePanel {
        border: tall $panel;
        background: $surface;
        padding: 1 2;
        width: 1fr;
    }
    #attr-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }
    #attr-content {
        color: $text;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("Select a resource →", id="attr-title")
        yield Label("", id="attr-content")

    def show_resource(self, resource: dict, instance_attrs: dict) -> None:
        title = f"{resource['type']}.{resource['name']}"
        self.query_one("#attr-title", Label).update(f"📦  {title}")
        lines = []
        for k, v in instance_attrs.items():
            val_str = format_value(v)
            lines.append(f"[bold cyan]{k}[/bold cyan]:  {val_str}")
        self.query_one("#attr-content", Label).update("\n".join(lines))


# ─────────────────────────────────────────────
# Manage Page
# ─────────────────────────────────────────────
class ManagePage(Container):
    DEFAULT_CSS = """
    ManagePage {
        padding: 0 1;
    }
    #top-controls {
        height: auto;
        padding: 1 0;
        margin-bottom: 1;
    }
    #top-controls Button {
        margin-right: 1;
    }
    #main-split {
        height: 1fr;
    }
    #output-panel {
        border: tall $panel;
        background: $surface;
        padding: 1;
        height: 12;
        margin-top: 1;
    }
    #output-label {
        text-style: bold;
        color: $warning;
        margin-bottom: 1;
    }
    Button.-success { background: $success; }
    Button.-warning { background: $warning; }
    Button.-error   { background: $error; }
    """

    def __init__(self, state: dict[str, Any], **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._state = state
        self._resource_map: dict[str, tuple[dict, dict]] = {}

    def compose(self) -> ComposeResult:
        with Horizontal(id="top-controls"):
            yield Button("➕  Add Resource",    id="btn-add",       variant="success")
            yield Button("🔍  Plan",            id="btn-plan",      variant="primary")
            yield Button("💰  Cost Estimate",   id="btn-cost",      variant="default")
            yield Button("🔄  Detect Drift",    id="btn-drift",     variant="warning")
            yield Button("🗑️  Destroy Selected", id="btn-destroy",  variant="error")
            yield Button("⚡  Apply Now",        id="btn-apply-now", variant="success")

        with Horizontal(id="main-split"):
            yield ResourceTree("Resources", id="resource-tree")
            yield AttributePanel(id="attr-panel")

        yield Label("Output", id="output-label")
        yield RichLog(id="output-log", highlight=True, markup=True)

    def on_mount(self) -> None:
        self._populate_tree()

    def _populate_tree(self) -> None:
        tree = self.query_one("#resource-tree", ResourceTree)
        tree.clear()
        root = tree.root
        root.expand()

        resources = self._state.get("resources", [])
        type_nodes: dict[str, TreeNode] = {}

        for resource in resources:
            rtype = resource.get("type", "unknown")
            rname = resource.get("name", "unknown")

            if rtype not in type_nodes:
                icon = self._type_icon(rtype)
                node = root.add(f"{icon} {rtype}", expand=True)
                type_nodes[rtype] = node

            instances = resource.get("instances", [{}])
            attrs = instances[0].get("attributes", {}) if instances else {}
            leaf = type_nodes[rtype].add_leaf(f"  {rname}")
            self._resource_map[leaf.label.plain.strip()] = (resource, attrs)

    def _type_icon(self, rtype: str) -> str:
        icons = {
            "aws_instance":            "🖥️",
            "aws_s3_bucket":           "🪣",
            "aws_security_group":      "🛡️",
            "aws_db_instance":         "🗄️",
            "aws_vpc":                 "🌐",
            "aws_subnet":              "📡",
            "aws_iam_role":            "👤",
            "aws_lambda_function":     "⚡",
            "google_compute_instance": "🖥️",
            "azurerm_virtual_machine": "🖥️",
        }
        return icons.get(rtype, "📦")

    @on(Tree.NodeSelected)
    def on_node_selected(self, event: Tree.NodeSelected) -> None:
        label = event.node.label.plain.strip()
        if label in self._resource_map:
            resource, attrs = self._resource_map[label]
            self.query_one("#attr-panel", AttributePanel).show_resource(resource, attrs)

    # ── Plan ─────────────────────────────────────────────────────────────
    @on(Button.Pressed, "#btn-plan")
    def run_plan(self) -> None:
        log = self.query_one("#output-log", RichLog)
        log.clear()
        log.write("[bold green]▶ Running terraform plan...[/bold green]")
        self._run_real_plan(log)

    @work(thread=True)
    def _run_real_plan(self, log: RichLog) -> None:
        tf_dir = self.app._tf_dir
        which = subprocess.run(["which", "terraform"], capture_output=True, text=True)
        if which.returncode != 0:
            self.app.call_from_thread(log.write, "[bold red]✖ 'terraform' not found in PATH.[/bold red]")
            return
        try:
            proc = subprocess.Popen(
                ["terraform", "plan", "-no-color"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=tf_dir,
            )
            for line in proc.stdout:
                stripped = line.rstrip()
                if stripped:
                    self.app.call_from_thread(log.write, stripped)
            proc.wait()
            if proc.returncode == 0:
                self.app.call_from_thread(log.write, "\n[bold green]✅ Plan complete (no changes).[/bold green]")
            elif proc.returncode == 2:
                self.app.call_from_thread(log.write, "\n[bold yellow]⚠ Plan complete (changes detected).[/bold yellow]")
            else:
                self.app.call_from_thread(log.write, f"\n[bold red]✖ terraform plan exited with code {proc.returncode}[/bold red]")
        except Exception as e:
            self.app.call_from_thread(log.write, f"[bold red]✖ Error: {e}[/bold red]")

    # ── Cost Estimate ─────────────────────────────────────────────────────
    @on(Button.Pressed, "#btn-cost")
    def show_cost(self) -> None:
        log = self.query_one("#output-log", RichLog)
        log.clear()
        log.write("[bold cyan]💰 Running Infracost estimate...[/bold cyan]")
        self._run_infracost(log)

    @work(thread=True)
    def _run_infracost(self, log: RichLog) -> None:
        import shutil
        tf_dir = self.app._tf_dir

        infracost_bin = (
            APP_CONFIG.get("infracost_path")
            or shutil.which("infracost")
            or str(Path.home() / ".local" / "bin" / "infracost")
        )
        if not Path(infracost_bin).exists() and not shutil.which(infracost_bin):
            self.app.call_from_thread(log.write, "[bold red]✖ Infracost not found.[/bold red]")
            self.app.call_from_thread(log.write, "  [bold cyan]python installer.py[/bold cyan]")
            return

        creds_path = Path.home() / ".config" / "infracost" / "credentials.yml"
        if not creds_path.exists():
            self.app.call_from_thread(log.write, "[bold yellow]⚠ Infracost is not authenticated.[/bold yellow]")
            self.app.call_from_thread(log.write, "Run:  [bold cyan]infracost auth login[/bold cyan]")
            return

        try:
            self.app.call_from_thread(log.write, "[dim]Fetching cloud pricing data...[/dim]")
            proc = subprocess.run(
                [infracost_bin, "breakdown", "--path", tf_dir, "--format", "json", "--no-color"],
                capture_output=True, text=True,
            )
            if proc.returncode != 0:
                self.app.call_from_thread(log.write, "[bold red]✖ Infracost error:[/bold red]")
                for line in proc.stderr.splitlines():
                    if line.strip():
                        self.app.call_from_thread(log.write, line)
                return

            data = json.loads(proc.stdout)
            projects = data.get("projects", [])
            if not projects:
                self.app.call_from_thread(log.write, "[yellow]No projects found.[/yellow]")
                return

            resources = projects[0].get("breakdown", {}).get("resources", [])
            self.app.call_from_thread(log.write, "")
            self.app.call_from_thread(log.write, f"  {'Resource':<50} {'Monthly':>12}")
            self.app.call_from_thread(log.write, "  " + "─" * 64)

            total = 0.0
            for r in resources:
                name = r.get("name", "unknown")
                cost = r.get("monthlyCost")
                if cost is None:
                    cost_str = "[dim]usage-based[/dim]"
                else:
                    cost = float(cost)
                    total += cost
                    cost_str = f"[green]${cost:>10.2f}[/green]"
                self.app.call_from_thread(log.write, f"  {name:<50} {cost_str}")

            self.app.call_from_thread(log.write, "  " + "─" * 64)
            unsupported = data.get("summary", {}).get("totalUnsupportedResources", 0)
            self.app.call_from_thread(
                log.write,
                f"  [bold]{'TOTAL MONTHLY ESTIMATE':<50}[/bold] [bold green]${total:>10.2f}[/bold green]"
            )
            if unsupported:
                self.app.call_from_thread(log.write, f"  [dim]{unsupported} resource(s) not supported by Infracost[/dim]")
            self.app.call_from_thread(log.write, "")
            self.app.call_from_thread(log.write, "[bold green]✅ Estimate complete.[/bold green]")

        except json.JSONDecodeError:
            self.app.call_from_thread(log.write, "[bold red]✖ Failed to parse Infracost output.[/bold red]")
        except Exception as e:
            self.app.call_from_thread(log.write, f"[bold red]✖ Error: {e}[/bold red]")

    # ── Drift Detection ───────────────────────────────────────────────────
    @on(Button.Pressed, "#btn-drift")
    def detect_drift(self) -> None:
        log = self.query_one("#output-log", RichLog)
        log.clear()
        log.write("[bold yellow]🔄 Detecting infrastructure drift...[/bold yellow]")
        log.write("[dim]Running: terraform plan -refresh-only -detailed-exitcode[/dim]")
        log.write("")
        self._run_drift_detection(log)

    @work(thread=True)
    def _run_drift_detection(self, log: RichLog) -> None:
        tf_dir = self.app._tf_dir
        which = subprocess.run(["which", "terraform"], capture_output=True, text=True)
        if which.returncode != 0:
            self.app.call_from_thread(log.write, "[bold red]✖ 'terraform' not found in PATH.[/bold red]")
            return
        try:
            proc = subprocess.Popen(
                ["terraform", "plan", "-refresh-only", "-detailed-exitcode", "-no-color"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=tf_dir,
            )
            stdout_lines = []
            for line in proc.stdout:
                stripped = line.rstrip()
                if stripped:
                    stdout_lines.append(stripped)
                    self.app.call_from_thread(log.write, stripped)
            proc.wait()
            stderr_out = proc.stderr.read().strip()

            self.app.call_from_thread(log.write, "")
            self.app.call_from_thread(log.write, "─" * 60)

            if proc.returncode == 0:
                self.app.call_from_thread(log.write, "[bold green]✅ No drift detected — infrastructure matches state.[/bold green]")
            elif proc.returncode == 2:
                self.app.call_from_thread(log.write, "[bold yellow]⚠  Drift detected! Real infrastructure differs from state.[/bold yellow]")
                self.app.call_from_thread(log.write, "")
                drifted = []
                for line in stdout_lines:
                    if " has changed" in line or " has been deleted" in line or " has been created" in line:
                        resource = line.strip().lstrip("# ").split(" ")[0]
                        if "." in resource:
                            status = "deleted outside Terraform" if "deleted" in line else \
                                     "created outside Terraform" if "created" in line else "changed"
                            drifted.append((resource, status))
                if drifted:
                    self.app.call_from_thread(log.write, "[bold]Drifted resources:[/bold]")
                    for resource, status in drifted:
                        icon = "🟡" if status == "changed" else "🔴"
                        self.app.call_from_thread(log.write, f"  {icon}  [cyan]{resource}[/cyan]  →  {status}")
                    self.app.call_from_thread(log.write, "")
                    self.app.call_from_thread(log.write, "[dim]To fix: run terraform apply -refresh-only[/dim]")
                else:
                    self.app.call_from_thread(log.write, "[dim]See full output above for details.[/dim]")
            else:
                self.app.call_from_thread(log.write, f"[bold red]✖ terraform exited with code {proc.returncode}[/bold red]")
                if stderr_out:
                    self.app.call_from_thread(log.write, "[red]Error output:[/red]")
                    for line in stderr_out.splitlines():
                        self.app.call_from_thread(log.write, f"  {line}")
        except Exception as e:
            self.app.call_from_thread(log.write, f"[bold red]✖ Error: {e}[/bold red]")

    # ── Add Resource ──────────────────────────────────────────────────────
    @on(Button.Pressed, "#btn-add")
    def add_resource(self) -> None:
        log = self.query_one("#output-log", RichLog)
        tf_dir = self.app._tf_dir

        def on_wizard_done(result: tuple[str, str, bool] | None) -> None:
            if result is None:
                log.clear(); log.write("[dim]Add resource cancelled.[/dim]"); return
            filepath, hcl, apply = result
            log.clear()
            log.write(f"[bold green]➕ Writing resource to {filepath}...[/bold green]")
            try:
                Path(filepath).write_text(hcl)
                log.write(f"[green]✔  File written: {filepath}[/green]")
                log.write("")
                if apply:
                    log.write("[bold yellow]🚀 Running terraform apply...[/bold yellow]")
                    self._apply_new_resource(filepath, log)
                else:
                    log.write("[dim]Running terraform plan to validate...[/dim]")
                    self._validate_new_resource(filepath, log)
            except Exception as e:
                log.write(f"[bold red]✖ Failed to write file: {e}[/bold red]")

        def on_resource_picked(rtype: str | None) -> None:
            if rtype is None:
                self.app.push_screen(ProviderSelectScreen(), on_provider_selected); return
            self.app.push_screen(AddResourceWizard(tf_dir, preselected=rtype), on_wizard_done)

        def on_provider_selected(provider: str | None) -> None:
            if provider is None:
                log.clear(); log.write("[dim]Add resource cancelled.[/dim]"); return
            if provider == "aws":
                self.app.push_screen(AWSResourcePickerScreen(), on_resource_picked)

        self.app.push_screen(ProviderSelectScreen(), on_provider_selected)

    @work(thread=True)
    def _validate_new_resource(self, filepath: str, log: RichLog) -> None:
        tf_dir = self.app._tf_dir
        try:
            proc = subprocess.Popen(
                ["terraform", "plan", "-no-color"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=tf_dir,
            )
            for line in proc.stdout:
                stripped = line.rstrip()
                if stripped:
                    self.app.call_from_thread(log.write, stripped)
            proc.wait()
            if proc.returncode in (0, 2):
                self.app.call_from_thread(log.write, "\n[bold green]✅ Resource validated.[/bold green]")
            else:
                self.app.call_from_thread(log.write, f"\n[bold red]✖ Plan failed (exit {proc.returncode}).[/bold red]")
        except Exception as e:
            self.app.call_from_thread(log.write, f"[bold red]✖ {e}[/bold red]")

    @work(thread=True)
    def _apply_new_resource(self, filepath: str, log: RichLog) -> None:
        tf_dir = self.app._tf_dir
        try:
            self.app.call_from_thread(log.write, "[dim]Planning changes...[/dim]")
            plan_proc = subprocess.Popen(
                ["terraform", "plan", "-no-color"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=tf_dir,
            )
            for line in plan_proc.stdout:
                stripped = line.rstrip()
                if stripped:
                    self.app.call_from_thread(log.write, stripped)
            plan_proc.wait()
            if plan_proc.returncode not in (0, 2):
                self.app.call_from_thread(log.write, f"\n[bold red]✖ Plan failed (exit {plan_proc.returncode}).[/bold red]")
                return

            self.app.call_from_thread(log.write, "")
            self.app.call_from_thread(log.write, "─" * 60)
            self.app.call_from_thread(log.write, "[bold yellow]🚀 Applying changes...[/bold yellow]")
            self.app.call_from_thread(log.write, "")

            apply_proc = subprocess.Popen(
                ["terraform", "apply", "-auto-approve", "-no-color"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=tf_dir,
            )
            for line in apply_proc.stdout:
                stripped = line.rstrip()
                if stripped:
                    self.app.call_from_thread(log.write, stripped)
            apply_proc.wait()
            if apply_proc.returncode == 0:
                self.app.call_from_thread(log.write, "\n[bold green]✅ Resource applied successfully![/bold green]")
                self.app.call_from_thread(self.app.action_reload_state)
            else:
                self.app.call_from_thread(log.write, f"\n[bold red]✖ Apply failed (exit {apply_proc.returncode}).[/bold red]")
        except FileNotFoundError:
            self.app.call_from_thread(log.write, "[bold red]✖ 'terraform' not found in PATH.[/bold red]")
        except Exception as e:
            self.app.call_from_thread(log.write, f"[bold red]✖ {e}[/bold red]")

    # ── Apply Now ─────────────────────────────────────────────────────────
    @on(Button.Pressed, "#btn-apply-now")
    def apply_now(self) -> None:
        log = self.query_one("#output-log", RichLog)
        log.clear()
        log.write("[bold green]⚡ Running terraform apply --auto-approve...[/bold green]")
        log.write("")
        self._run_apply_now(log)

    @work(thread=True)
    def _run_apply_now(self, log: RichLog) -> None:
        tf_dir = self.app._tf_dir
        which = subprocess.run(["which", "terraform"], capture_output=True, text=True)
        if which.returncode != 0:
            self.app.call_from_thread(log.write, "[bold red]✖ 'terraform' not found in PATH.[/bold red]")
            return
        try:
            proc = subprocess.Popen(
                ["terraform", "apply", "-auto-approve", "-no-color"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=tf_dir,
            )
            for line in proc.stdout:
                stripped = line.rstrip()
                if stripped:
                    self.app.call_from_thread(log.write, stripped)
            proc.wait()
            if proc.returncode == 0:
                self.app.call_from_thread(log.write, "\n[bold green]✅ Apply complete![/bold green]")
                self.app.call_from_thread(self.app.action_reload_state)
            else:
                self.app.call_from_thread(log.write, f"\n[bold red]✖ Apply failed (exit {proc.returncode})[/bold red]")
        except Exception as e:
            self.app.call_from_thread(log.write, f"[bold red]✖ Error: {e}[/bold red]")

    # ── Destroy Selected ──────────────────────────────────────────────────
    @on(Button.Pressed, "#btn-destroy")
    def destroy_selected(self) -> None:
        log = self.query_one("#output-log", RichLog)
        tree = self.query_one("#resource-tree", ResourceTree)
        selected = tree.cursor_node
        if not selected or selected.allow_expand:
            log.clear()
            log.write("[red]✖ No leaf resource selected. Select a resource in the tree first.[/red]")
            return

        label = selected.label.plain.strip()
        parent = selected.parent
        rtype = parent.label.plain.strip() if parent else "unknown"
        rtype = " ".join(rtype.split()[1:]) if rtype else rtype
        resource_addr = f"{rtype}.{label}"

        def on_confirm(confirmed: bool) -> None:
            if confirmed:
                log.clear()
                log.write(f"[bold red]🗑️  Destroying {resource_addr}...[/bold red]")
                self._run_destroy(resource_addr, log)
            else:
                log.clear()
                log.write("[dim]Destroy cancelled.[/dim]")

        self.app.push_screen(ConfirmDestroyScreen(resource_addr), on_confirm)

    @work(thread=True)
    def _run_destroy(self, resource_addr: str, log: RichLog) -> None:
        tf_dir = self.app._tf_dir
        try:
            proc = subprocess.Popen(
                ["terraform", "destroy", f"-target={resource_addr}", "-auto-approve", "-no-color"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=tf_dir,
            )
            for line in proc.stdout:
                stripped = line.rstrip()
                if stripped:
                    self.app.call_from_thread(log.write, stripped)
            proc.wait()
            if proc.returncode == 0:
                self.app.call_from_thread(log.write, "\n[bold green]✅ Resource destroyed successfully.[/bold green]")
                self.app.call_from_thread(self.app.action_reload_state)
            else:
                self.app.call_from_thread(log.write, f"\n[bold red]✖ Destroy failed (exit {proc.returncode})[/bold red]")
        except Exception as e:
            self.app.call_from_thread(log.write, f"[bold red]✖ Error: {e}[/bold red]")


# ─────────────────────────────────────────────
# Provider Selection Screen
# ─────────────────────────────────────────────
class ProviderSelectScreen(ModalScreen[str | None]):
    DEFAULT_CSS = """
    ProviderSelectScreen { align: center middle; }
    #provider-container {
        width: 72; height: auto;
        border: tall $accent; background: $surface; padding: 0;
    }
    #provider-header {
        background: $accent; color: $background;
        padding: 0 2; height: 3;
        content-align: left middle; text-style: bold;
    }
    #provider-body { padding: 1 2; }
    #provider-subtitle { color: $text-muted; margin-bottom: 1; }
    .provider-btn { width: 1fr; height: 4; margin-bottom: 1; text-align: left; }
    .provider-btn-unsupported { width: 1fr; height: 4; margin-bottom: 1; text-align: left; opacity: 60%; }
    #provider-cancel-row { height: 3; align: right middle; margin-top: 1; }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="provider-container"):
            yield Label("➕  Add Resource  —  Select Provider", id="provider-header")
            with Vertical(id="provider-body"):
                yield Label("Choose the cloud provider for your new resource:", id="provider-subtitle")
                for p in PROVIDERS:
                    label = f"{p['icon']}  {p['name']}"
                    if not p["supported"]:
                        label += "  [dim](coming soon)[/dim]"
                    yield Button(
                        label,
                        id=f"provider-{p['id']}",
                        variant="primary" if p["supported"] else "default",
                        classes="provider-btn" if p["supported"] else "provider-btn-unsupported",
                    )
                with Horizontal(id="provider-cancel-row"):
                    yield Button("Cancel", id="provider-cancel", variant="default")

    @on(Button.Pressed)
    def handle_press(self, event: Button.Pressed) -> None:
        btn_id = event.button.id or ""
        if btn_id == "provider-cancel":
            self.dismiss(None); return
        if not btn_id.startswith("provider-"):
            return
        provider_id = btn_id[len("provider-"):]
        provider = next((p for p in PROVIDERS if p["id"] == provider_id), None)
        if not provider:
            return
        if not provider["supported"]:
            self.notify(f"{provider['name']} support coming soon! 🚧", severity="warning", timeout=3)
            return
        self.dismiss(provider_id)
        event.stop()

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)


# ─────────────────────────────────────────────
# AWS Resource Picker Screen
# ─────────────────────────────────────────────
class AWSResourcePickerScreen(ModalScreen[str | None]):
    DEFAULT_CSS = """
    AWSResourcePickerScreen { align: center middle; }
    #picker-container { width: 96; height: 44; border: tall $accent; background: $surface; padding: 0; }
    #picker-header { background: $accent; color: $background; padding: 0 2; height: 3; content-align: left middle; text-style: bold; }
    #picker-search { margin: 1 2 0 2; }
    #picker-stats { color: $text-muted; margin: 0 2; height: 1; }
    #picker-split { height: 1fr; margin: 1 0 0 0; }
    #category-list { width: 28; border-right: solid $panel; overflow-y: auto; }
    .cat-btn { width: 1fr; height: 3; text-align: left; background: $surface; border: none; margin: 0; }
    .cat-btn.--active { background: $accent 30%; color: $accent; text-style: bold; }
    #resource-list { width: 1fr; overflow-y: auto; padding: 0 1; }
    .resource-btn { width: 1fr; height: 3; text-align: left; background: $surface; border: none; margin-bottom: 0; }
    .resource-btn:hover { background: $accent 20%; }
    #picker-footer { height: 4; padding: 1 2; border-top: solid $panel; align: right middle; }
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._active_category = "All"
        self._search_query = ""

    def compose(self) -> ComposeResult:
        total = len(ALL_AWS_RESOURCES)
        with Vertical(id="picker-container"):
            yield Label(f"🟠  AWS Resource Catalog  —  {total} resources available", id="picker-header")
            yield Input(placeholder="🔍  Search resources...", id="picker-search")
            yield Label(f"Showing all {total} resources across {len(AWS_RESOURCE_CATALOG)} categories", id="picker-stats")
            with Horizontal(id="picker-split"):
                with ScrollableContainer(id="category-list"):
                    yield Button("All", id="cat-All", classes="cat-btn --active")
                    for cat in AWS_RESOURCE_CATALOG:
                        count = len(AWS_RESOURCE_CATALOG[cat])
                        yield Button(f"{cat} ({count})", id=_cat_id(cat), classes="cat-btn")
                with ScrollableContainer(id="resource-list"):
                    yield from self._resource_buttons(ALL_AWS_RESOURCES)
            with Horizontal(id="picker-footer"):
                yield Button("← Back", id="picker-back", variant="default")

    def _resource_buttons(self, resources: list[dict]):
        for r in resources:
            yield Button(
                f"[bold]{r['type']}[/bold]\n[dim]{r['description']}[/dim]",
                name=r["type"],
                classes="resource-btn",
            )

    def _update_resource_list(self) -> None:
        results = ALL_AWS_RESOURCES
        if self._search_query:
            q = self._search_query.lower()
            results = [r for r in results if q in r["type"] or q in r["description"].lower() or q in r["category"].lower()]
        if self._active_category != "All":
            results = [r for r in results if r["category"] == self._active_category]
        try:
            self.query_one("#picker-stats", Label).update(
                f"Showing {len(results)} of {len(ALL_AWS_RESOURCES)} resources"
                + (f" in [bold]{self._active_category}[/bold]" if self._active_category != "All" else "")
            )
        except Exception:
            pass
        try:
            container = self.query_one("#resource-list", ScrollableContainer)
            container.remove_children()
            if results:
                container.mount(*list(self._resource_buttons(results)))
            else:
                container.mount(Label("[dim]No resources match your search.[/dim]"))
        except Exception:
            pass

    @on(Input.Changed, "#picker-search")
    def on_search(self, event: Input.Changed) -> None:
        self._search_query = event.value
        self._update_resource_list()

    @on(Button.Pressed)
    def on_button(self, event: Button.Pressed) -> None:
        btn_id = event.button.id or ""
        if btn_id == "picker-back":
            self.dismiss(None); return
        if btn_id.startswith("cat-"):
            slug = btn_id[4:]
            cat = "All" if slug == "All" else next((c for c in AWS_RESOURCE_CATALOG if _cat_id(c) == btn_id), slug)
            self._active_category = cat
            for c in list(AWS_RESOURCE_CATALOG.keys()) + ["All"]:
                try:
                    b = self.query_one(f"#cat-{c}", Button)
                    b.add_class("--active") if c == cat else b.remove_class("--active")
                except Exception:
                    pass
            self._update_resource_list()
            event.stop(); return
        if event.button.name and not btn_id.startswith("cat-") and btn_id != "picker-back":
            self.dismiss(event.button.name)
            event.stop()

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)


# ─────────────────────────────────────────────
# Add Resource Wizard
# ─────────────────────────────────────────────
class AddResourceWizard(ModalScreen[tuple[str, str, bool] | None]):
    DEFAULT_CSS = """
    AddResourceWizard { align: center middle; }
    #wizard-container { width: 90; height: 38; border: tall $accent; background: $surface; padding: 0; }
    #wizard-header { background: $accent; color: $background; padding: 0 2; height: 3; content-align: left middle; text-style: bold; }
    #wizard-body { padding: 1 2; height: 1fr; }
    #wizard-footer { height: 4; padding: 1 2; border-top: solid $panel; align: right middle; }
    #wizard-footer Button { margin-left: 1; }
    #btn-wiz-apply { display: none; }
    #btn-wiz-apply:enabled { display: block; }
    #search-input { margin-bottom: 1; width: 1fr; }
    #type-list { height: 1fr; border: solid $panel; overflow-y: auto; }
    .type-item { width: 1fr; height: 3; background: $surface; border: none; text-align: left; margin: 0; }
    .type-item:hover { background: $accent 20%; }
    .type-item.--selected { background: $accent; color: $background; text-style: bold; }
    .field-label { color: $accent; margin-top: 1; }
    .field-required { color: $error; }
    .field-input { margin-bottom: 0; width: 1fr; }
    #preview-area { height: 1fr; border: solid $panel; overflow-y: auto; padding: 1; }
    #filename-input { width: 1fr; margin-top: 1; }
    """

    def __init__(self, tf_dir: str, preselected: str = "", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._tf_dir = tf_dir
        self._field_inputs: dict[str, Input] = {}
        if preselected:
            self._selected_type = preselected
            self._step = 2
        else:
            self._selected_type = ""
            self._step = 1

    def compose(self) -> ComposeResult:
        header_text = (
            f"➕  Configure  [cyan]{self._selected_type}[/cyan]"
            if self._step == 2
            else "➕  Add Resource  —  Step 1 of 3: Choose resource type"
        )
        with Vertical(id="wizard-container"):
            yield Label(header_text, id="wizard-header")
            with ScrollableContainer(id="wizard-body"):
                if self._step == 2:
                    yield from self._compose_step2()
                else:
                    yield from self._compose_step1()
            with Horizontal(id="wizard-footer"):
                yield Button("← Back",           id="btn-wiz-cancel", variant="default")
                yield Button("Next →",            id="btn-wiz-next",   variant="primary")
                yield Button("🚀  Write & Apply", id="btn-wiz-apply",  variant="warning", disabled=(self._step != 3))

    def _compose_step1(self) -> ComposeResult:
        yield Input(placeholder="Search resource type...", id="search-input")
        with ScrollableContainer(id="type-list"):
            for rtype, meta in RESOURCE_TEMPLATES.items():
                yield Button(f"{rtype}  —  {meta['description']}", id=f"type-{rtype}", classes="type-item", variant="default")

    def _get_fields(self) -> list[dict]:
        if self._selected_type in RESOURCE_TEMPLATES:
            return RESOURCE_TEMPLATES[self._selected_type]["fields"]
        return [{"name": "resource_name", "label": "Resource name (TF identifier)", "placeholder": "my_resource", "required": True, "default": ""}]

    def _compose_step2(self) -> ComposeResult:
        self._field_inputs = {}
        fields = self._get_fields()
        if self._selected_type not in RESOURCE_TEMPLATES:
            res_info = next((r for r in ALL_AWS_RESOURCES if r["type"] == self._selected_type), None)
            desc = res_info["description"] if res_info else ""
            yield Label(f"[bold cyan]{self._selected_type}[/bold cyan]  —  {desc}", classes="field-label")
            yield Label("[yellow]ℹ  Generic template — edit HCL in step 3.[/yellow]", classes="field-label")
            yield Label("", classes="field-label")
        for field in fields:
            req = "[bold red]*[/bold red] " if field["required"] else ""
            yield Label(f"{req}{field['label']}", classes="field-label")
            inp = Input(value=field["default"], placeholder=field["placeholder"], id=f"field-{field['name']}", classes="field-input")
            self._field_inputs[field["name"]] = inp
            yield inp

    def _compose_step3(self, hcl: str, filename: str) -> ComposeResult:
        yield Label("📄  Generated Terraform HCL:", classes="field-label")
        yield TextArea(hcl, id="preview-area", read_only=True, language="css")
        yield Label("💾  Save to filename:", classes="field-label")
        yield Input(value=filename, id="filename-input")

    def _go_to_step(self, step: int, hcl: str = "", filename: str = "") -> None:
        self._step = step
        header = self.query_one("#wizard-header", Label)
        body = self.query_one("#wizard-body", ScrollableContainer)
        body.remove_children()
        if step == 1:
            header.update("➕  Add Resource  —  Step 1 of 3: Choose resource type")
            body.mount(*list(self._compose_step1()))
        elif step == 2:
            header.update(f"➕  Add Resource  —  Step 2 of 3: Configure  [cyan]{self._selected_type}[/cyan]")
            body.mount(*list(self._compose_step2()))
        elif step == 3:
            header.update("➕  Add Resource  —  Step 3 of 3: Preview & Save")
            body.mount(*list(self._compose_step3(hcl, filename)))
        next_btn = self.query_one("#btn-wiz-next", Button)
        apply_btn = self.query_one("#btn-wiz-apply", Button)
        if step == 3:
            next_btn.label = "💾  Write File"; next_btn.variant = "success"; apply_btn.disabled = False
        else:
            next_btn.label = "Next →"; next_btn.variant = "primary"; apply_btn.disabled = True

    @on(Input.Changed, "#search-input")
    def filter_types(self, event: Input.Changed) -> None:
        query = event.value.lower()
        for rtype in RESOURCE_TEMPLATES:
            try:
                item = self.query_one(f"#type-{rtype}", Button)
                item.display = query in rtype or query in RESOURCE_TEMPLATES[rtype]["description"].lower()
            except Exception:
                pass

    @on(Button.Pressed)
    def select_type(self, event: Button.Pressed) -> None:
        if self._step != 1:
            return
        btn_id = event.button.id or ""
        if not btn_id.startswith("type-"):
            return
        rtype = btn_id[len("type-"):]
        if rtype not in RESOURCE_TEMPLATES:
            return
        for rt in RESOURCE_TEMPLATES:
            try:
                self.query_one(f"#type-{rt}", Button).remove_class("--selected")
            except Exception:
                pass
        event.button.add_class("--selected")
        self._selected_type = rtype
        event.stop()

    @on(Button.Pressed, "#btn-wiz-next")
    def next_step(self) -> None:
        if self._step == 1:
            if not self._selected_type:
                self.notify("Please select a resource type first.", severity="warning"); return
            self._go_to_step(2)
        elif self._step == 2:
            values: dict[str, str] = {}
            fields = self._get_fields()
            missing = []
            for field in fields:
                try:
                    val = self.query_one(f"#field-{field['name']}", Input).value.strip()
                except Exception:
                    val = field["default"]
                if field["required"] and not val:
                    missing.append(field["label"])
                values[field["name"]] = val or field["default"]
            if missing:
                self.notify(f"Required: {', '.join(missing)}", severity="error"); return
            self._collected_values = values
            if self._selected_type in RESOURCE_TEMPLATES:
                hcl = _build_tf_block(self._selected_type, values)
            else:
                rname = values.get("resource_name", "my_resource")
                hcl = (
                    f'resource "{self._selected_type}" "{rname}" {{\n'
                    f'  # TODO: fill in required arguments\n'
                    f'  # Docs: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/{self._selected_type.replace("aws_", "")}\n'
                    f'}}\n'
                )
            filename = f"{values.get('resource_name', 'resource')}_{self._selected_type}.tf"
            self._generated_hcl = hcl
            self._go_to_step(3, hcl, filename)
        elif self._step == 3:
            self._write_and_dismiss(apply=False)

    @on(Button.Pressed, "#btn-wiz-apply")
    def write_and_apply(self) -> None:
        if self._step == 3:
            self._write_and_dismiss(apply=True)

    def _write_and_dismiss(self, apply: bool) -> None:
        try:
            filename = self.query_one("#filename-input", Input).value.strip() or "new_resource.tf"
            if not filename.endswith(".tf"):
                filename += ".tf"
            filepath = Path(self._tf_dir) / filename
            hcl = self.query_one("#preview-area", TextArea).text
            self.dismiss((str(filepath), hcl, apply))
        except Exception as e:
            self.notify(f"Error: {e}", severity="error")

    @on(Button.Pressed, "#btn-wiz-cancel")
    def cancel(self) -> None:
        if self._step > 1:
            self._go_to_step(self._step - 1)
            cancel_btn = self.query_one("#btn-wiz-cancel", Button)
            cancel_btn.label = "Cancel" if self._step == 1 else "← Back"
        else:
            self.dismiss(None)

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)


# ─────────────────────────────────────────────
# Confirm Destroy Modal
# ─────────────────────────────────────────────
class ConfirmDestroyScreen(ModalScreen[bool]):
    DEFAULT_CSS = """
    ConfirmDestroyScreen { align: center middle; }
    #dialog { width: 64; height: auto; border: tall $error; background: $surface; padding: 2 4; }
    #dialog-title { text-style: bold; color: $error; margin-bottom: 1; }
    .dialog-body { color: $text-muted; margin-bottom: 2; }
    #dialog-addr { text-style: bold italic; color: $warning; margin-bottom: 2; }
    #btn-row { height: auto; align: right middle; }
    #btn-cancel { margin-right: 2; }
    """

    def __init__(self, resource_addr: str) -> None:
        super().__init__()
        self._addr = resource_addr

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label("⚠️  Confirm Destroy", id="dialog-title")
            yield Label("You are about to permanently destroy:", classes="dialog-body")
            yield Label(self._addr, id="dialog-addr")
            yield Label("This will run terraform destroy -target and cannot be undone.", classes="dialog-body")
            with Horizontal(id="btn-row"):
                yield Button("Cancel",  id="btn-cancel",  variant="default")
                yield Button("Destroy", id="btn-confirm", variant="error")

    @on(Button.Pressed, "#btn-confirm")
    def confirm(self) -> None:
        self.dismiss(True)

    @on(Button.Pressed, "#btn-cancel")
    def cancel(self) -> None:
        self.dismiss(False)

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(False)


# ─────────────────────────────────────────────
# Main App
# ─────────────────────────────────────────────
class InsightTF(App):
    TITLE = "TerraLens"
    SUB_TITLE = "Terraform TUI Dashboard"

    CSS = """
    Screen { background: $background; }
    TabbedContent { height: 1fr; }
    TabPane { padding: 0; }
    #tab-overview { padding: 0; }
    #tab-manage { padding: 0; }
    """

    BINDINGS = [
        Binding("1", "switch_tab('overview')", "Overview",     show=True),
        Binding("2", "switch_tab('manage')",   "Manage",       show=True),
        Binding("r", "reload_state",           "Reload State", show=True),
        Binding("q", "quit",                   "Quit",         show=True),
    ]

    def __init__(self, state_path: str = "terraform.tfstate") -> None:
        super().__init__()
        self._state_path = state_path
        self._state = load_state(state_path)
        self._tf_dir = str(Path(state_path).parent.resolve()) if Path(state_path).exists() else str(Path.cwd())

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with TabbedContent(initial="overview"):
            with TabPane("📊  Overview", id="overview"):
                yield OverviewPage(self._state, id="overview-page")
            with TabPane("⚙️   Manage", id="manage"):
                yield ManagePage(self._state, id="manage-page")
        yield Footer()

    def action_switch_tab(self, tab: str) -> None:
        self.query_one(TabbedContent).active = tab

    def action_reload_state(self) -> None:
        self._state = load_state(self._state_path)
        self.call_after_refresh(self._rebuild_pages)

    def _rebuild_pages(self) -> None:
        try:
            manage = self.query_one("#manage-page", ManagePage)
            manage._state = self._state
            manage.query_one("#resource-tree", ResourceTree).clear()
            manage._resource_map = {}
            manage._populate_tree()
            manage.query_one("#attr-panel", AttributePanel).query_one("#attr-title", Label).update("Select a resource →")
            manage.query_one("#attr-panel", AttributePanel).query_one("#attr-content", Label).update("")
        except Exception:
            pass
        try:
            overview = self.query_one("#overview-page", OverviewPage)
            overview.remove()
            self.query_one("#overview", TabPane).mount(OverviewPage(self._state, id="overview-page"))
        except Exception:
            pass
        self.notify("✅ State refreshed", severity="information")


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────
def main():
    import sys
    state_path = sys.argv[1] if len(sys.argv) > 1 else "terraform.tfstate"
    InsightTF(state_path).run()


if __name__ == "__main__":
    main()
