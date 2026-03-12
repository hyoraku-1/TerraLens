"""
state.py — TerraLens state management
Handles app config loading, sample state, state file loading, and value formatting.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


# ──────────────────────
# App config
# ──────────────────────
def load_app_config() -> dict:
    config_path = Path(__file__).parent / ".insight-tf.json"
    if config_path.exists():
        try:
            return json.loads(config_path.read_text())
        except Exception:
            pass
    return {}

APP_CONFIG = load_app_config()


# ─────────────────────────────────────────────
# Sample statefile (used when no real
# terraform.tfstate is found in cwd)
# ─────────────────────────────────────────────
SAMPLE_STATE: dict[str, Any] = {
    "version": 4,
    "terraform_version": "1.7.4",
    "serial": 42,
    "lineage": "abc123-def456",
    "resources": [
        {
            "type": "aws_instance",
            "name": "web_server",
            "provider": 'provider["registry.terraform.io/hashicorp/aws"]',
            "instances": [
                {
                    "attributes": {
                        "id": "i-0abc123def456789",
                        "ami": "ami-0c55b159cbfafe1f0",
                        "instance_type": "t3.micro",
                        "availability_zone": "us-east-1a",
                        "public_ip": "54.123.45.67",
                        "private_ip": "10.0.1.100",
                        "tags": {"Name": "WebServer", "Env": "prod"},
                    }
                }
            ],
        },
        {
            "type": "aws_s3_bucket",
            "name": "assets",
            "provider": 'provider["registry.terraform.io/hashicorp/aws"]',
            "instances": [
                {
                    "attributes": {
                        "id": "my-assets-bucket-prod",
                        "bucket": "my-assets-bucket-prod",
                        "region": "us-east-1",
                        "acl": "private",
                        "versioning": [{"enabled": True}],
                    }
                }
            ],
        },
        {
            "type": "aws_security_group",
            "name": "web_sg",
            "provider": 'provider["registry.terraform.io/hashicorp/aws"]',
            "instances": [
                {
                    "attributes": {
                        "id": "sg-0123456789abcdef0",
                        "name": "web-security-group",
                        "description": "Security group for web servers",
                        "vpc_id": "vpc-0a1b2c3d4e5f",
                        "ingress": [
                            {"from_port": 80, "to_port": 80, "protocol": "tcp"},
                            {"from_port": 443, "to_port": 443, "protocol": "tcp"},
                        ],
                    }
                }
            ],
        },
        {
            "type": "aws_db_instance",
            "name": "main_db",
            "provider": 'provider["registry.terraform.io/hashicorp/aws"]',
            "instances": [
                {
                    "attributes": {
                        "id": "main-db-prod",
                        "identifier": "main-db-prod",
                        "engine": "postgres",
                        "engine_version": "14.7",
                        "instance_class": "db.t3.medium",
                        "allocated_storage": 100,
                        "multi_az": True,
                    }
                }
            ],
        },
        {
            "type": "aws_vpc",
            "name": "main",
            "provider": 'provider["registry.terraform.io/hashicorp/aws"]',
            "instances": [
                {
                    "attributes": {
                        "id": "vpc-0a1b2c3d4e5f",
                        "cidr_block": "10.0.0.0/16",
                        "enable_dns_hostnames": True,
                        "enable_dns_support": True,
                        "tags": {"Name": "MainVPC"},
                    }
                }
            ],
        },
    ],
}


# ─────────────────────────────────────────────
# State loader
# ─────────────────────────────────────────────
def load_state(path: str = "terraform.tfstate") -> dict[str, Any]:
    p = Path(path)
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            pass
    return SAMPLE_STATE


def format_value(v: Any, indent: int = 0) -> str:
    pad = "  " * indent
    if isinstance(v, dict):
        lines = ["{"]
        for k, val in v.items():
            lines.append(f"{pad}  {k}: {format_value(val, indent+1)}")
        lines.append(pad + "}")
        return "\n".join(lines)
    elif isinstance(v, list):
        if not v:
            return "[]"
        lines = ["["]
        for item in v:
            lines.append(f"{pad}  {format_value(item, indent+1)}")
        lines.append(pad + "]")
        return "\n".join(lines)
    else:
        return str(v)
