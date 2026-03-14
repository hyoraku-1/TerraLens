"""
blueprints.py — TerraLens Infrastructure Blueprints
Pre-built, interconnected multi-resource Terraform configurations.
"""

from __future__ import annotations


BLUEPRINTS: list[dict] = [

    # ─────────────────────────────────────────────
    # 1. Public Web Server Architecture
    # ─────────────────────────────────────────────
    {
        "id": "public_web_server",
        "name": "Public Web Server",
        "icon": "🌐",
        "description": "Simple website accessible from the internet — VPC, public subnet, IGW, security group and EC2",
        "resources": [
            "aws_vpc", "aws_subnet (public)", "aws_internet_gateway",
            "aws_route_table", "aws_route_table_association",
            "aws_security_group", "aws_instance",
        ],
        "fields": [
            {"name": "vpc_name",      "label": "VPC resource name",       "placeholder": "main",                  "default": "main",                  "required": True},
            {"name": "vpc_cidr",      "label": "VPC CIDR block",          "placeholder": "10.0.0.0/16",           "default": "10.0.0.0/16",           "required": True},
            {"name": "subnet_cidr",   "label": "Public subnet CIDR",      "placeholder": "10.0.1.0/24",           "default": "10.0.1.0/24",           "required": True},
            {"name": "az",            "label": "Availability zone",       "placeholder": "us-east-1a",            "default": "us-east-1a",            "required": True},
            {"name": "instance_name", "label": "EC2 resource name",       "placeholder": "web_server",            "default": "web_server",            "required": True},
            {"name": "ami",           "label": "AMI ID",                  "placeholder": "ami-0c55b159cbfafe1f0", "default": "ami-0c55b159cbfafe1f0", "required": True},
            {"name": "instance_type", "label": "Instance type",           "placeholder": "t3.micro",              "default": "t3.micro",              "required": True},
            {"name": "tags_env",      "label": "Environment tag",         "placeholder": "prod",                  "default": "prod",                  "required": False},
        ],
        "template": '''\
resource "aws_vpc" "{vpc_name}" {{
  cidr_block           = "{vpc_cidr}"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {{
    Name = "{vpc_name}"
    Env  = "{tags_env}"
  }}
}}

resource "aws_internet_gateway" "{vpc_name}_igw" {{
  vpc_id = aws_vpc.{vpc_name}.id

  tags = {{
    Name = "{vpc_name}-igw"
    Env  = "{tags_env}"
  }}
}}

resource "aws_subnet" "{vpc_name}_public" {{
  vpc_id                  = aws_vpc.{vpc_name}.id
  cidr_block              = "{subnet_cidr}"
  availability_zone       = "{az}"
  map_public_ip_on_launch = true

  tags = {{
    Name = "{vpc_name}-public"
    Env  = "{tags_env}"
  }}
}}

resource "aws_route_table" "{vpc_name}_public_rt" {{
  vpc_id = aws_vpc.{vpc_name}.id

  route {{
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.{vpc_name}_igw.id
  }}

  tags = {{
    Name = "{vpc_name}-public-rt"
    Env  = "{tags_env}"
  }}
}}

resource "aws_route_table_association" "{vpc_name}_public_rta" {{
  subnet_id      = aws_subnet.{vpc_name}_public.id
  route_table_id = aws_route_table.{vpc_name}_public_rt.id
}}

resource "aws_security_group" "{instance_name}_sg" {{
  name        = "{instance_name}-sg"
  description = "Allow HTTP and SSH inbound traffic"
  vpc_id      = aws_vpc.{vpc_name}.id

  ingress {{
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  ingress {{
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  tags = {{
    Name = "{instance_name}-sg"
    Env  = "{tags_env}"
  }}
}}

resource "aws_instance" "{instance_name}" {{
  ami                    = "{ami}"
  instance_type          = "{instance_type}"
  subnet_id              = aws_subnet.{vpc_name}_public.id
  vpc_security_group_ids = [aws_security_group.{instance_name}_sg.id]

  tags = {{
    Name = "{instance_name}"
    Env  = "{tags_env}"
  }}
}}
''',
    },

    # ─────────────────────────────────────────────
    # 2. Public + Private with NAT (Bastion)
    # ─────────────────────────────────────────────
    {
        "id": "public_private_nat",
        "name": "Public + Private with NAT",
        "icon": "🔒",
        "description": "Bastion host in public subnet, private app server with outbound internet via NAT Gateway",
        "resources": [
            "aws_vpc", "aws_subnet (public + private)", "aws_internet_gateway",
            "aws_eip", "aws_nat_gateway", "aws_route_table (x2)",
            "aws_security_group (x2)", "aws_instance (bastion + app)",
        ],
        "fields": [
            {"name": "vpc_name",           "label": "VPC resource name",           "placeholder": "main",                  "default": "main",                  "required": True},
            {"name": "vpc_cidr",           "label": "VPC CIDR block",              "placeholder": "10.0.0.0/16",           "default": "10.0.0.0/16",           "required": True},
            {"name": "public_cidr",        "label": "Public subnet CIDR",          "placeholder": "10.0.1.0/24",           "default": "10.0.1.0/24",           "required": True},
            {"name": "private_cidr",       "label": "Private subnet CIDR",         "placeholder": "10.0.2.0/24",           "default": "10.0.2.0/24",           "required": True},
            {"name": "az",                 "label": "Availability zone",           "placeholder": "us-east-1a",            "default": "us-east-1a",            "required": True},
            {"name": "bastion_name",       "label": "Bastion EC2 resource name",   "placeholder": "bastion",               "default": "bastion",               "required": True},
            {"name": "app_name",           "label": "App EC2 resource name",       "placeholder": "app_server",            "default": "app_server",            "required": True},
            {"name": "ami",                "label": "AMI ID (both instances)",     "placeholder": "ami-0c55b159cbfafe1f0", "default": "ami-0c55b159cbfafe1f0", "required": True},
            {"name": "bastion_type",       "label": "Bastion instance type",       "placeholder": "t3.micro",              "default": "t3.micro",              "required": True},
            {"name": "app_type",           "label": "App instance type",           "placeholder": "t3.small",              "default": "t3.small",              "required": True},
            {"name": "tags_env",           "label": "Environment tag",             "placeholder": "prod",                  "default": "prod",                  "required": False},
        ],
        "template": '''\
resource "aws_vpc" "{vpc_name}" {{
  cidr_block           = "{vpc_cidr}"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {{
    Name = "{vpc_name}"
    Env  = "{tags_env}"
  }}
}}

resource "aws_internet_gateway" "{vpc_name}_igw" {{
  vpc_id = aws_vpc.{vpc_name}.id

  tags = {{
    Name = "{vpc_name}-igw"
    Env  = "{tags_env}"
  }}
}}

resource "aws_subnet" "{vpc_name}_public" {{
  vpc_id                  = aws_vpc.{vpc_name}.id
  cidr_block              = "{public_cidr}"
  availability_zone       = "{az}"
  map_public_ip_on_launch = true

  tags = {{
    Name = "{vpc_name}-public"
    Env  = "{tags_env}"
  }}
}}

resource "aws_subnet" "{vpc_name}_private" {{
  vpc_id            = aws_vpc.{vpc_name}.id
  cidr_block        = "{private_cidr}"
  availability_zone = "{az}"

  tags = {{
    Name = "{vpc_name}-private"
    Env  = "{tags_env}"
  }}
}}

resource "aws_eip" "{vpc_name}_nat_eip" {{
  domain = "vpc"

  tags = {{
    Name = "{vpc_name}-nat-eip"
    Env  = "{tags_env}"
  }}
}}

resource "aws_nat_gateway" "{vpc_name}_nat" {{
  allocation_id = aws_eip.{vpc_name}_nat_eip.id
  subnet_id     = aws_subnet.{vpc_name}_public.id

  tags = {{
    Name = "{vpc_name}-nat"
    Env  = "{tags_env}"
  }}

  depends_on = [aws_internet_gateway.{vpc_name}_igw]
}}

resource "aws_route_table" "{vpc_name}_public_rt" {{
  vpc_id = aws_vpc.{vpc_name}.id

  route {{
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.{vpc_name}_igw.id
  }}

  tags = {{
    Name = "{vpc_name}-public-rt"
    Env  = "{tags_env}"
  }}
}}

resource "aws_route_table_association" "{vpc_name}_public_rta" {{
  subnet_id      = aws_subnet.{vpc_name}_public.id
  route_table_id = aws_route_table.{vpc_name}_public_rt.id
}}

resource "aws_route_table" "{vpc_name}_private_rt" {{
  vpc_id = aws_vpc.{vpc_name}.id

  route {{
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.{vpc_name}_nat.id
  }}

  tags = {{
    Name = "{vpc_name}-private-rt"
    Env  = "{tags_env}"
  }}
}}

resource "aws_route_table_association" "{vpc_name}_private_rta" {{
  subnet_id      = aws_subnet.{vpc_name}_private.id
  route_table_id = aws_route_table.{vpc_name}_private_rt.id
}}

resource "aws_security_group" "{bastion_name}_sg" {{
  name        = "{bastion_name}-sg"
  description = "Allow SSH inbound to bastion"
  vpc_id      = aws_vpc.{vpc_name}.id

  ingress {{
    description = "SSH from internet"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  tags = {{
    Name = "{bastion_name}-sg"
    Env  = "{tags_env}"
  }}
}}

resource "aws_security_group" "{app_name}_sg" {{
  name        = "{app_name}-sg"
  description = "Allow SSH only from bastion"
  vpc_id      = aws_vpc.{vpc_name}.id

  ingress {{
    description     = "SSH from bastion"
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [aws_security_group.{bastion_name}_sg.id]
  }}

  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  tags = {{
    Name = "{app_name}-sg"
    Env  = "{tags_env}"
  }}
}}

resource "aws_instance" "{bastion_name}" {{
  ami                    = "{ami}"
  instance_type          = "{bastion_type}"
  subnet_id              = aws_subnet.{vpc_name}_public.id
  vpc_security_group_ids = [aws_security_group.{bastion_name}_sg.id]

  tags = {{
    Name = "{bastion_name}"
    Role = "bastion"
    Env  = "{tags_env}"
  }}
}}

resource "aws_instance" "{app_name}" {{
  ami                    = "{ami}"
  instance_type          = "{app_type}"
  subnet_id              = aws_subnet.{vpc_name}_private.id
  vpc_security_group_ids = [aws_security_group.{app_name}_sg.id]

  tags = {{
    Name = "{app_name}"
    Role = "app"
    Env  = "{tags_env}"
  }}
}}
''',
    },

    # ─────────────────────────────────────────────
    # 3. Load Balanced Web Application
    # ─────────────────────────────────────────────
    {
        "id": "load_balanced_web",
        "name": "Load Balanced Web Application",
        "icon": "⚖️",
        "description": "High availability web tier with ALB, Auto Scaling Group across 2 AZs",
        "resources": [
            "aws_vpc", "aws_subnet (2 public + 2 private)", "aws_internet_gateway",
            "aws_nat_gateway", "aws_lb (ALB)", "aws_lb_target_group",
            "aws_lb_listener", "aws_autoscaling_group", "aws_launch_template",
        ],
        "fields": [
            {"name": "vpc_name",      "label": "VPC resource name",       "placeholder": "main",                  "default": "main",                  "required": True},
            {"name": "vpc_cidr",      "label": "VPC CIDR block",          "placeholder": "10.0.0.0/16",           "default": "10.0.0.0/16",           "required": True},
            {"name": "pub1_cidr",     "label": "Public subnet 1 CIDR",    "placeholder": "10.0.1.0/24",           "default": "10.0.1.0/24",           "required": True},
            {"name": "pub2_cidr",     "label": "Public subnet 2 CIDR",    "placeholder": "10.0.2.0/24",           "default": "10.0.2.0/24",           "required": True},
            {"name": "priv1_cidr",    "label": "Private subnet 1 CIDR",   "placeholder": "10.0.3.0/24",           "default": "10.0.3.0/24",           "required": True},
            {"name": "priv2_cidr",    "label": "Private subnet 2 CIDR",   "placeholder": "10.0.4.0/24",           "default": "10.0.4.0/24",           "required": True},
            {"name": "az1",           "label": "Availability zone 1",     "placeholder": "us-east-1a",            "default": "us-east-1a",            "required": True},
            {"name": "az2",           "label": "Availability zone 2",     "placeholder": "us-east-1b",            "default": "us-east-1b",            "required": True},
            {"name": "ami",           "label": "AMI ID",                  "placeholder": "ami-0c55b159cbfafe1f0", "default": "ami-0c55b159cbfafe1f0", "required": True},
            {"name": "instance_type", "label": "Instance type",           "placeholder": "t3.micro",              "default": "t3.micro",              "required": True},
            {"name": "min_size",      "label": "ASG min size",            "placeholder": "2",                     "default": "2",                     "required": True},
            {"name": "max_size",      "label": "ASG max size",            "placeholder": "4",                     "default": "4",                     "required": True},
            {"name": "app_name",      "label": "App name (used in tags)", "placeholder": "myapp",                 "default": "myapp",                 "required": True},
            {"name": "tags_env",      "label": "Environment tag",         "placeholder": "prod",                  "default": "prod",                  "required": False},
        ],
        "template": '''\
resource "aws_vpc" "{vpc_name}" {{
  cidr_block           = "{vpc_cidr}"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {{ Name = "{vpc_name}", Env = "{tags_env}" }}
}}

resource "aws_internet_gateway" "{vpc_name}_igw" {{
  vpc_id = aws_vpc.{vpc_name}.id
  tags   = {{ Name = "{vpc_name}-igw", Env = "{tags_env}" }}
}}

resource "aws_subnet" "{vpc_name}_pub1" {{
  vpc_id                  = aws_vpc.{vpc_name}.id
  cidr_block              = "{pub1_cidr}"
  availability_zone       = "{az1}"
  map_public_ip_on_launch = true
  tags = {{ Name = "{vpc_name}-pub-1", Env = "{tags_env}" }}
}}

resource "aws_subnet" "{vpc_name}_pub2" {{
  vpc_id                  = aws_vpc.{vpc_name}.id
  cidr_block              = "{pub2_cidr}"
  availability_zone       = "{az2}"
  map_public_ip_on_launch = true
  tags = {{ Name = "{vpc_name}-pub-2", Env = "{tags_env}" }}
}}

resource "aws_subnet" "{vpc_name}_priv1" {{
  vpc_id            = aws_vpc.{vpc_name}.id
  cidr_block        = "{priv1_cidr}"
  availability_zone = "{az1}"
  tags = {{ Name = "{vpc_name}-priv-1", Env = "{tags_env}" }}
}}

resource "aws_subnet" "{vpc_name}_priv2" {{
  vpc_id            = aws_vpc.{vpc_name}.id
  cidr_block        = "{priv2_cidr}"
  availability_zone = "{az2}"
  tags = {{ Name = "{vpc_name}-priv-2", Env = "{tags_env}" }}
}}

resource "aws_eip" "{vpc_name}_nat_eip" {{
  domain = "vpc"
  tags   = {{ Name = "{vpc_name}-nat-eip", Env = "{tags_env}" }}
}}

resource "aws_nat_gateway" "{vpc_name}_nat" {{
  allocation_id = aws_eip.{vpc_name}_nat_eip.id
  subnet_id     = aws_subnet.{vpc_name}_pub1.id
  depends_on    = [aws_internet_gateway.{vpc_name}_igw]
  tags          = {{ Name = "{vpc_name}-nat", Env = "{tags_env}" }}
}}

resource "aws_route_table" "{vpc_name}_public_rt" {{
  vpc_id = aws_vpc.{vpc_name}.id
  route {{
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.{vpc_name}_igw.id
  }}
  tags = {{ Name = "{vpc_name}-public-rt", Env = "{tags_env}" }}
}}

resource "aws_route_table_association" "{vpc_name}_pub1_rta" {{
  subnet_id      = aws_subnet.{vpc_name}_pub1.id
  route_table_id = aws_route_table.{vpc_name}_public_rt.id
}}

resource "aws_route_table_association" "{vpc_name}_pub2_rta" {{
  subnet_id      = aws_subnet.{vpc_name}_pub2.id
  route_table_id = aws_route_table.{vpc_name}_public_rt.id
}}

resource "aws_route_table" "{vpc_name}_private_rt" {{
  vpc_id = aws_vpc.{vpc_name}.id
  route {{
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.{vpc_name}_nat.id
  }}
  tags = {{ Name = "{vpc_name}-private-rt", Env = "{tags_env}" }}
}}

resource "aws_route_table_association" "{vpc_name}_priv1_rta" {{
  subnet_id      = aws_subnet.{vpc_name}_priv1.id
  route_table_id = aws_route_table.{vpc_name}_private_rt.id
}}

resource "aws_route_table_association" "{vpc_name}_priv2_rta" {{
  subnet_id      = aws_subnet.{vpc_name}_priv2.id
  route_table_id = aws_route_table.{vpc_name}_private_rt.id
}}

resource "aws_security_group" "{app_name}_alb_sg" {{
  name        = "{app_name}-alb-sg"
  description = "Allow HTTP inbound to ALB"
  vpc_id      = aws_vpc.{vpc_name}.id

  ingress {{
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  tags = {{ Name = "{app_name}-alb-sg", Env = "{tags_env}" }}
}}

resource "aws_security_group" "{app_name}_ec2_sg" {{
  name        = "{app_name}-ec2-sg"
  description = "Allow traffic from ALB only"
  vpc_id      = aws_vpc.{vpc_name}.id

  ingress {{
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.{app_name}_alb_sg.id]
  }}

  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  tags = {{ Name = "{app_name}-ec2-sg", Env = "{tags_env}" }}
}}

resource "aws_lb" "{app_name}_alb" {{
  name               = "{app_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.{app_name}_alb_sg.id]
  subnets            = [aws_subnet.{vpc_name}_pub1.id, aws_subnet.{vpc_name}_pub2.id]

  tags = {{ Name = "{app_name}-alb", Env = "{tags_env}" }}
}}

resource "aws_lb_target_group" "{app_name}_tg" {{
  name     = "{app_name}-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.{vpc_name}.id

  health_check {{
    path                = "/"
    healthy_threshold   = 2
    unhealthy_threshold = 2
    interval            = 30
  }}

  tags = {{ Name = "{app_name}-tg", Env = "{tags_env}" }}
}}

resource "aws_lb_listener" "{app_name}_listener" {{
  load_balancer_arn = aws_lb.{app_name}_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {{
    type             = "forward"
    target_group_arn = aws_lb_target_group.{app_name}_tg.arn
  }}
}}

resource "aws_launch_template" "{app_name}_lt" {{
  name_prefix   = "{app_name}-"
  image_id      = "{ami}"
  instance_type = "{instance_type}"

  vpc_security_group_ids = [aws_security_group.{app_name}_ec2_sg.id]

  tag_specifications {{
    resource_type = "instance"
    tags = {{ Name = "{app_name}-instance", Env = "{tags_env}" }}
  }}
}}

resource "aws_autoscaling_group" "{app_name}_asg" {{
  name                = "{app_name}-asg"
  min_size            = {min_size}
  max_size            = {max_size}
  desired_capacity    = {min_size}
  vpc_zone_identifier = [aws_subnet.{vpc_name}_priv1.id, aws_subnet.{vpc_name}_priv2.id]
  target_group_arns   = [aws_lb_target_group.{app_name}_tg.arn]

  launch_template {{
    id      = aws_launch_template.{app_name}_lt.id
    version = "$Latest"
  }}

  tag {{
    key                 = "Name"
    value               = "{app_name}-asg-instance"
    propagate_at_launch = true
  }}
}}
''',
    },

    # ─────────────────────────────────────────────
    # 4. Three-Tier Architecture
    # ─────────────────────────────────────────────
    {
        "id": "three_tier",
        "name": "Three-Tier Architecture",
        "icon": "🏛️",
        "description": "Classic enterprise architecture — ALB, private app EC2 servers, private RDS database",
        "resources": [
            "aws_vpc", "aws_subnet (2 public + 2 app + 2 db)", "aws_internet_gateway",
            "aws_nat_gateway", "aws_lb (ALB)", "aws_lb_target_group",
            "aws_lb_listener", "aws_instance (app servers)",
            "aws_db_subnet_group", "aws_db_instance (RDS)",
        ],
        "fields": [
            {"name": "vpc_name",          "label": "VPC resource name",        "placeholder": "main",                  "default": "main",                  "required": True},
            {"name": "vpc_cidr",          "label": "VPC CIDR block",           "placeholder": "10.0.0.0/16",           "default": "10.0.0.0/16",           "required": True},
            {"name": "pub1_cidr",         "label": "Public subnet 1 CIDR",     "placeholder": "10.0.1.0/24",           "default": "10.0.1.0/24",           "required": True},
            {"name": "pub2_cidr",         "label": "Public subnet 2 CIDR",     "placeholder": "10.0.2.0/24",           "default": "10.0.2.0/24",           "required": True},
            {"name": "app1_cidr",         "label": "App subnet 1 CIDR",        "placeholder": "10.0.3.0/24",           "default": "10.0.3.0/24",           "required": True},
            {"name": "app2_cidr",         "label": "App subnet 2 CIDR",        "placeholder": "10.0.4.0/24",           "default": "10.0.4.0/24",           "required": True},
            {"name": "db1_cidr",          "label": "DB subnet 1 CIDR",         "placeholder": "10.0.5.0/24",           "default": "10.0.5.0/24",           "required": True},
            {"name": "db2_cidr",          "label": "DB subnet 2 CIDR",         "placeholder": "10.0.6.0/24",           "default": "10.0.6.0/24",           "required": True},
            {"name": "az1",               "label": "Availability zone 1",      "placeholder": "us-east-1a",            "default": "us-east-1a",            "required": True},
            {"name": "az2",               "label": "Availability zone 2",      "placeholder": "us-east-1b",            "default": "us-east-1b",            "required": True},
            {"name": "app_name",          "label": "App name",                 "placeholder": "myapp",                 "default": "myapp",                 "required": True},
            {"name": "ami",               "label": "App server AMI ID",        "placeholder": "ami-0c55b159cbfafe1f0", "default": "ami-0c55b159cbfafe1f0", "required": True},
            {"name": "app_instance_type", "label": "App instance type",        "placeholder": "t3.small",              "default": "t3.small",              "required": True},
            {"name": "db_identifier",     "label": "RDS identifier",           "placeholder": "myapp-db-prod",         "default": "myapp-db-prod",         "required": True},
            {"name": "db_engine",         "label": "DB engine",                "placeholder": "postgres",              "default": "postgres",              "required": True},
            {"name": "db_version",        "label": "DB engine version",        "placeholder": "14",                    "default": "14",                    "required": True},
            {"name": "db_class",          "label": "DB instance class",        "placeholder": "db.t3.micro",           "default": "db.t3.micro",           "required": True},
            {"name": "db_storage",        "label": "DB allocated storage (GB)","placeholder": "20",                    "default": "20",                    "required": True},
            {"name": "db_username",       "label": "DB master username",       "placeholder": "admin",                 "default": "admin",                 "required": True},
            {"name": "db_password",       "label": "DB master password",       "placeholder": "changeme123",           "default": "",                      "required": True},
            {"name": "tags_env",          "label": "Environment tag",          "placeholder": "prod",                  "default": "prod",                  "required": False},
        ],
        "template": '''\
resource "aws_vpc" "{vpc_name}" {{
  cidr_block           = "{vpc_cidr}"
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = {{ Name = "{vpc_name}", Env = "{tags_env}" }}
}}

resource "aws_internet_gateway" "{vpc_name}_igw" {{
  vpc_id = aws_vpc.{vpc_name}.id
  tags   = {{ Name = "{vpc_name}-igw", Env = "{tags_env}" }}
}}

# ── Public subnets (ALB tier) ──
resource "aws_subnet" "{vpc_name}_pub1" {{
  vpc_id                  = aws_vpc.{vpc_name}.id
  cidr_block              = "{pub1_cidr}"
  availability_zone       = "{az1}"
  map_public_ip_on_launch = true
  tags = {{ Name = "{vpc_name}-pub-1", Env = "{tags_env}" }}
}}

resource "aws_subnet" "{vpc_name}_pub2" {{
  vpc_id                  = aws_vpc.{vpc_name}.id
  cidr_block              = "{pub2_cidr}"
  availability_zone       = "{az2}"
  map_public_ip_on_launch = true
  tags = {{ Name = "{vpc_name}-pub-2", Env = "{tags_env}" }}
}}

# ── App subnets (EC2 tier) ──
resource "aws_subnet" "{vpc_name}_app1" {{
  vpc_id            = aws_vpc.{vpc_name}.id
  cidr_block        = "{app1_cidr}"
  availability_zone = "{az1}"
  tags = {{ Name = "{vpc_name}-app-1", Env = "{tags_env}" }}
}}

resource "aws_subnet" "{vpc_name}_app2" {{
  vpc_id            = aws_vpc.{vpc_name}.id
  cidr_block        = "{app2_cidr}"
  availability_zone = "{az2}"
  tags = {{ Name = "{vpc_name}-app-2", Env = "{tags_env}" }}
}}

# ── DB subnets (RDS tier) ──
resource "aws_subnet" "{vpc_name}_db1" {{
  vpc_id            = aws_vpc.{vpc_name}.id
  cidr_block        = "{db1_cidr}"
  availability_zone = "{az1}"
  tags = {{ Name = "{vpc_name}-db-1", Env = "{tags_env}" }}
}}

resource "aws_subnet" "{vpc_name}_db2" {{
  vpc_id            = aws_vpc.{vpc_name}.id
  cidr_block        = "{db2_cidr}"
  availability_zone = "{az2}"
  tags = {{ Name = "{vpc_name}-db-2", Env = "{tags_env}" }}
}}

resource "aws_eip" "{vpc_name}_nat_eip" {{
  domain = "vpc"
  tags   = {{ Name = "{vpc_name}-nat-eip" }}
}}

resource "aws_nat_gateway" "{vpc_name}_nat" {{
  allocation_id = aws_eip.{vpc_name}_nat_eip.id
  subnet_id     = aws_subnet.{vpc_name}_pub1.id
  depends_on    = [aws_internet_gateway.{vpc_name}_igw]
  tags          = {{ Name = "{vpc_name}-nat", Env = "{tags_env}" }}
}}

resource "aws_route_table" "{vpc_name}_public_rt" {{
  vpc_id = aws_vpc.{vpc_name}.id
  route {{
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.{vpc_name}_igw.id
  }}
  tags = {{ Name = "{vpc_name}-public-rt" }}
}}

resource "aws_route_table_association" "{vpc_name}_pub1_rta" {{
  subnet_id      = aws_subnet.{vpc_name}_pub1.id
  route_table_id = aws_route_table.{vpc_name}_public_rt.id
}}

resource "aws_route_table_association" "{vpc_name}_pub2_rta" {{
  subnet_id      = aws_subnet.{vpc_name}_pub2.id
  route_table_id = aws_route_table.{vpc_name}_public_rt.id
}}

resource "aws_route_table" "{vpc_name}_private_rt" {{
  vpc_id = aws_vpc.{vpc_name}.id
  route {{
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.{vpc_name}_nat.id
  }}
  tags = {{ Name = "{vpc_name}-private-rt" }}
}}

resource "aws_route_table_association" "{vpc_name}_app1_rta" {{
  subnet_id      = aws_subnet.{vpc_name}_app1.id
  route_table_id = aws_route_table.{vpc_name}_private_rt.id
}}

resource "aws_route_table_association" "{vpc_name}_app2_rta" {{
  subnet_id      = aws_subnet.{vpc_name}_app2.id
  route_table_id = aws_route_table.{vpc_name}_private_rt.id
}}

# ── Security Groups ──
resource "aws_security_group" "{app_name}_alb_sg" {{
  name        = "{app_name}-alb-sg"
  description = "Allow HTTP from internet"
  vpc_id      = aws_vpc.{vpc_name}.id
  ingress {{
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}
  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}
  tags = {{ Name = "{app_name}-alb-sg", Env = "{tags_env}" }}
}}

resource "aws_security_group" "{app_name}_app_sg" {{
  name        = "{app_name}-app-sg"
  description = "Allow traffic from ALB"
  vpc_id      = aws_vpc.{vpc_name}.id
  ingress {{
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.{app_name}_alb_sg.id]
  }}
  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}
  tags = {{ Name = "{app_name}-app-sg", Env = "{tags_env}" }}
}}

resource "aws_security_group" "{app_name}_db_sg" {{
  name        = "{app_name}-db-sg"
  description = "Allow DB traffic from app tier"
  vpc_id      = aws_vpc.{vpc_name}.id
  ingress {{
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.{app_name}_app_sg.id]
  }}
  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}
  tags = {{ Name = "{app_name}-db-sg", Env = "{tags_env}" }}
}}

# ── ALB ──
resource "aws_lb" "{app_name}_alb" {{
  name               = "{app_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.{app_name}_alb_sg.id]
  subnets            = [aws_subnet.{vpc_name}_pub1.id, aws_subnet.{vpc_name}_pub2.id]
  tags = {{ Name = "{app_name}-alb", Env = "{tags_env}" }}
}}

resource "aws_lb_target_group" "{app_name}_tg" {{
  name     = "{app_name}-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.{vpc_name}.id
  health_check {{
    path = "/"
    healthy_threshold   = 2
    unhealthy_threshold = 2
    interval            = 30
  }}
  tags = {{ Name = "{app_name}-tg" }}
}}

resource "aws_lb_listener" "{app_name}_listener" {{
  load_balancer_arn = aws_lb.{app_name}_alb.arn
  port              = 80
  protocol          = "HTTP"
  default_action {{
    type             = "forward"
    target_group_arn = aws_lb_target_group.{app_name}_tg.arn
  }}
}}

# ── App EC2 Instances ──
resource "aws_instance" "{app_name}_app1" {{
  ami                    = "{ami}"
  instance_type          = "{app_instance_type}"
  subnet_id              = aws_subnet.{vpc_name}_app1.id
  vpc_security_group_ids = [aws_security_group.{app_name}_app_sg.id]
  tags = {{ Name = "{app_name}-app-1", Role = "app", Env = "{tags_env}" }}
}}

resource "aws_instance" "{app_name}_app2" {{
  ami                    = "{ami}"
  instance_type          = "{app_instance_type}"
  subnet_id              = aws_subnet.{vpc_name}_app2.id
  vpc_security_group_ids = [aws_security_group.{app_name}_app_sg.id]
  tags = {{ Name = "{app_name}-app-2", Role = "app", Env = "{tags_env}" }}
}}

resource "aws_lb_target_group_attachment" "{app_name}_tga1" {{
  target_group_arn = aws_lb_target_group.{app_name}_tg.arn
  target_id        = aws_instance.{app_name}_app1.id
  port             = 80
}}

resource "aws_lb_target_group_attachment" "{app_name}_tga2" {{
  target_group_arn = aws_lb_target_group.{app_name}_tg.arn
  target_id        = aws_instance.{app_name}_app2.id
  port             = 80
}}

# ── RDS (DB tier) ──
resource "aws_db_subnet_group" "{app_name}_db_subnet_group" {{
  name       = "{app_name}-db-subnet-group"
  subnet_ids = [aws_subnet.{vpc_name}_db1.id, aws_subnet.{vpc_name}_db2.id]
  tags = {{ Name = "{app_name}-db-subnet-group" }}
}}

resource "aws_db_instance" "{app_name}_db" {{
  identifier             = "{db_identifier}"
  engine                 = "{db_engine}"
  engine_version         = "{db_version}"
  instance_class         = "{db_class}"
  allocated_storage      = {db_storage}
  db_name                = "{app_name}"
  username               = "{db_username}"
  password               = "{db_password}"
  db_subnet_group_name   = aws_db_subnet_group.{app_name}_db_subnet_group.name
  vpc_security_group_ids = [aws_security_group.{app_name}_db_sg.id]
  multi_az               = true
  skip_final_snapshot    = true
  tags = {{ Name = "{db_identifier}", Env = "{tags_env}" }}
}}
''',
    },

    # ─────────────────────────────────────────────
    # 5. Static Website (S3 + CloudFront + Route53 + ACM)
    # ─────────────────────────────────────────────
    {
        "id": "static_website",
        "name": "Static Website Hosting",
        "icon": "☁️",
        "description": "Scalable static site — S3 origin, CloudFront CDN, Route53 DNS, ACM SSL certificate",
        "resources": [
            "aws_s3_bucket", "aws_s3_bucket_public_access_block",
            "aws_cloudfront_origin_access_identity", "aws_s3_bucket_policy",
            "aws_cloudfront_distribution", "aws_acm_certificate",
            "aws_route53_zone", "aws_route53_record",
        ],
        "fields": [
            {"name": "bucket_name",  "label": "S3 resource name",            "placeholder": "website_bucket",        "default": "website_bucket",        "required": True},
            {"name": "bucket_id",    "label": "S3 bucket name (globally unique)", "placeholder": "my-website-prod", "default": "my-website-prod",       "required": True},
            {"name": "domain_name",  "label": "Your domain name",            "placeholder": "example.com",           "default": "example.com",           "required": True},
            {"name": "cf_comment",   "label": "CloudFront comment",          "placeholder": "Website CDN",           "default": "Website CDN",           "required": True},
            {"name": "tags_env",     "label": "Environment tag",             "placeholder": "prod",                  "default": "prod",                  "required": False},
        ],
        "template": '''\
resource "aws_s3_bucket" "{bucket_name}" {{
  bucket = "{bucket_id}"
  tags   = {{ Name = "{bucket_id}", Env = "{tags_env}" }}
}}

resource "aws_s3_bucket_public_access_block" "{bucket_name}_pab" {{
  bucket                  = aws_s3_bucket.{bucket_name}.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}}

resource "aws_cloudfront_origin_access_identity" "{bucket_name}_oai" {{
  comment = "OAI for {bucket_id}"
}}

resource "aws_s3_bucket_policy" "{bucket_name}_policy" {{
  bucket = aws_s3_bucket.{bucket_name}.id

  policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [{{
      Sid       = "AllowCloudFront"
      Effect    = "Allow"
      Principal = {{ AWS = aws_cloudfront_origin_access_identity.{bucket_name}_oai.iam_arn }}
      Action    = "s3:GetObject"
      Resource  = "${{aws_s3_bucket.{bucket_name}.arn}}/*"
    }}]
  }})
}}

# ACM certificate must be in us-east-1 for CloudFront
resource "aws_acm_certificate" "{bucket_name}_cert" {{
  domain_name       = "{domain_name}"
  validation_method = "DNS"

  subject_alternative_names = ["www.{domain_name}"]

  lifecycle {{
    create_before_destroy = true
  }}

  tags = {{ Name = "{domain_name}-cert", Env = "{tags_env}" }}
}}

resource "aws_cloudfront_distribution" "{bucket_name}_cdn" {{
  enabled             = true
  default_root_object = "index.html"
  comment             = "{cf_comment}"
  aliases             = ["{domain_name}", "www.{domain_name}"]

  origin {{
    domain_name = aws_s3_bucket.{bucket_name}.bucket_regional_domain_name
    origin_id   = "s3-{bucket_id}"

    s3_origin_config {{
      origin_access_identity = aws_cloudfront_origin_access_identity.{bucket_name}_oai.cloudfront_access_identity_path
    }}
  }}

  default_cache_behavior {{
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "s3-{bucket_id}"
    viewer_protocol_policy = "redirect-to-https"

    forwarded_values {{
      query_string = false
      cookies {{ forward = "none" }}
    }}

    min_ttl     = 0
    default_ttl = 3600
    max_ttl     = 86400
  }}

  custom_error_response {{
    error_code         = 404
    response_code      = 200
    response_page_path = "/index.html"
  }}

  restrictions {{
    geo_restriction {{ restriction_type = "none" }}
  }}

  viewer_certificate {{
    acm_certificate_arn      = aws_acm_certificate.{bucket_name}_cert.arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }}

  tags = {{ Name = "{bucket_id}-cdn", Env = "{tags_env}" }}
}}

resource "aws_route53_zone" "{bucket_name}_zone" {{
  name = "{domain_name}"
  tags = {{ Name = "{domain_name}", Env = "{tags_env}" }}
}}

resource "aws_route53_record" "{bucket_name}_apex" {{
  zone_id = aws_route53_zone.{bucket_name}_zone.zone_id
  name    = "{domain_name}"
  type    = "A"

  alias {{
    name                   = aws_cloudfront_distribution.{bucket_name}_cdn.domain_name
    zone_id                = aws_cloudfront_distribution.{bucket_name}_cdn.hosted_zone_id
    evaluate_target_health = false
  }}
}}

resource "aws_route53_record" "{bucket_name}_www" {{
  zone_id = aws_route53_zone.{bucket_name}_zone.zone_id
  name    = "www.{domain_name}"
  type    = "CNAME"
  ttl     = 300
  records = [aws_cloudfront_distribution.{bucket_name}_cdn.domain_name]
}}
''',
    },

    # ─────────────────────────────────────────────
    # 6. Serverless Architecture
    # ─────────────────────────────────────────────
    {
        "id": "serverless",
        "name": "Serverless API",
        "icon": "⚡",
        "description": "Fully serverless — API Gateway, Lambda, DynamoDB table, S3 bucket for assets",
        "resources": [
            "aws_iam_role", "aws_iam_role_policy_attachment",
            "aws_lambda_function", "aws_apigatewayv2_api",
            "aws_apigatewayv2_stage", "aws_apigatewayv2_integration",
            "aws_apigatewayv2_route", "aws_lambda_permission",
            "aws_dynamodb_table", "aws_s3_bucket",
        ],
        "fields": [
            {"name": "app_name",     "label": "App name (used everywhere)",  "placeholder": "myapi",          "default": "myapi",          "required": True},
            {"name": "fn_name",      "label": "Lambda function name (AWS)",  "placeholder": "myapi-handler",  "default": "myapi-handler",  "required": True},
            {"name": "runtime",      "label": "Lambda runtime",              "placeholder": "python3.11",     "default": "python3.11",     "required": True},
            {"name": "handler",      "label": "Lambda handler",              "placeholder": "index.handler",  "default": "index.handler",  "required": True},
            {"name": "filename",     "label": "Lambda ZIP filename",         "placeholder": "lambda.zip",     "default": "lambda.zip",     "required": True},
            {"name": "table_name",   "label": "DynamoDB table name",        "placeholder": "myapi-items",    "default": "myapi-items",    "required": True},
            {"name": "bucket_id",    "label": "S3 bucket name (globally unique)", "placeholder": "myapi-assets-prod", "default": "myapi-assets-prod", "required": True},
            {"name": "tags_env",     "label": "Environment tag",             "placeholder": "prod",           "default": "prod",           "required": False},
        ],
        "template": '''\
# ── IAM Role for Lambda ──
resource "aws_iam_role" "{app_name}_lambda_role" {{
  name = "{app_name}-lambda-role"

  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [{{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = {{ Service = "lambda.amazonaws.com" }}
    }}]
  }})

  tags = {{ Name = "{app_name}-lambda-role", Env = "{tags_env}" }}
}}

resource "aws_iam_role_policy_attachment" "{app_name}_lambda_basic" {{
  role       = aws_iam_role.{app_name}_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}}

resource "aws_iam_role_policy_attachment" "{app_name}_lambda_dynamo" {{
  role       = aws_iam_role.{app_name}_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}}

resource "aws_iam_role_policy_attachment" "{app_name}_lambda_s3" {{
  role       = aws_iam_role.{app_name}_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}}

# ── Lambda Function ──
resource "aws_lambda_function" "{app_name}_fn" {{
  function_name = "{fn_name}"
  runtime       = "{runtime}"
  handler       = "{handler}"
  role          = aws_iam_role.{app_name}_lambda_role.arn
  filename      = "{filename}"

  environment {{
    variables = {{
      TABLE_NAME  = aws_dynamodb_table.{app_name}_table.name
      BUCKET_NAME = aws_s3_bucket.{app_name}_assets.bucket
      ENV         = "{tags_env}"
    }}
  }}

  tags = {{ Name = "{fn_name}", Env = "{tags_env}" }}
}}

# ── API Gateway v2 (HTTP API) ──
resource "aws_apigatewayv2_api" "{app_name}_api" {{
  name          = "{app_name}-api"
  protocol_type = "HTTP"

  cors_configuration {{
    allow_headers = ["Content-Type", "Authorization"]
    allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_origins = ["*"]
  }}

  tags = {{ Name = "{app_name}-api", Env = "{tags_env}" }}
}}

resource "aws_apigatewayv2_integration" "{app_name}_integration" {{
  api_id             = aws_apigatewayv2_api.{app_name}_api.id
  integration_type   = "AWS_PROXY"
  integration_uri    = aws_lambda_function.{app_name}_fn.invoke_arn
  integration_method = "POST"
}}

resource "aws_apigatewayv2_route" "{app_name}_route" {{
  api_id    = aws_apigatewayv2_api.{app_name}_api.id
  route_key = "$default"
  target    = "integrations/${{aws_apigatewayv2_integration.{app_name}_integration.id}}"
}}

resource "aws_apigatewayv2_stage" "{app_name}_stage" {{
  api_id      = aws_apigatewayv2_api.{app_name}_api.id
  name        = "{tags_env}"
  auto_deploy = true

  tags = {{ Name = "{app_name}-stage", Env = "{tags_env}" }}
}}

resource "aws_lambda_permission" "{app_name}_apigw_permission" {{
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.{app_name}_fn.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${{aws_apigatewayv2_api.{app_name}_api.execution_arn}}/*/*"
}}

# ── DynamoDB Table ──
resource "aws_dynamodb_table" "{app_name}_table" {{
  name         = "{table_name}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {{
    name = "id"
    type = "S"
  }}

  tags = {{ Name = "{table_name}", Env = "{tags_env}" }}
}}

# ── S3 Bucket for assets ──
resource "aws_s3_bucket" "{app_name}_assets" {{
  bucket = "{bucket_id}"
  tags   = {{ Name = "{bucket_id}", Env = "{tags_env}" }}
}}

resource "aws_s3_bucket_public_access_block" "{app_name}_assets_pab" {{
  bucket                  = aws_s3_bucket.{app_name}_assets.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}}
''',
    },

    # ─────────────────────────────────────────────
    # 7. EKS Cluster (Bonus)
    # ─────────────────────────────────────────────
    {
        "id": "eks_cluster",
        "name": "EKS Kubernetes Cluster",
        "icon": "☸️",
        "description": "Production-ready EKS cluster with managed node group, VPC and IAM roles",
        "resources": [
            "aws_vpc", "aws_subnet (2 public + 2 private)", "aws_internet_gateway",
            "aws_nat_gateway", "aws_iam_role (cluster + node)",
            "aws_eks_cluster", "aws_eks_node_group",
        ],
        "fields": [
            {"name": "vpc_name",       "label": "VPC resource name",       "placeholder": "eks_vpc",       "default": "eks_vpc",       "required": True},
            {"name": "vpc_cidr",       "label": "VPC CIDR block",          "placeholder": "10.0.0.0/16",   "default": "10.0.0.0/16",   "required": True},
            {"name": "pub1_cidr",      "label": "Public subnet 1 CIDR",    "placeholder": "10.0.1.0/24",   "default": "10.0.1.0/24",   "required": True},
            {"name": "pub2_cidr",      "label": "Public subnet 2 CIDR",    "placeholder": "10.0.2.0/24",   "default": "10.0.2.0/24",   "required": True},
            {"name": "priv1_cidr",     "label": "Private subnet 1 CIDR",   "placeholder": "10.0.3.0/24",   "default": "10.0.3.0/24",   "required": True},
            {"name": "priv2_cidr",     "label": "Private subnet 2 CIDR",   "placeholder": "10.0.4.0/24",   "default": "10.0.4.0/24",   "required": True},
            {"name": "az1",            "label": "Availability zone 1",     "placeholder": "us-east-1a",    "default": "us-east-1a",    "required": True},
            {"name": "az2",            "label": "Availability zone 2",     "placeholder": "us-east-1b",    "default": "us-east-1b",    "required": True},
            {"name": "cluster_name",   "label": "EKS cluster name",        "placeholder": "my-eks-cluster","default": "my-eks-cluster","required": True},
            {"name": "k8s_version",    "label": "Kubernetes version",      "placeholder": "1.29",          "default": "1.29",          "required": True},
            {"name": "node_name",      "label": "Node group name",         "placeholder": "main_nodes",    "default": "main_nodes",    "required": True},
            {"name": "node_type",      "label": "Node instance type",      "placeholder": "t3.medium",     "default": "t3.medium",     "required": True},
            {"name": "node_min",       "label": "Min nodes",               "placeholder": "1",             "default": "1",             "required": True},
            {"name": "node_max",       "label": "Max nodes",               "placeholder": "3",             "default": "3",             "required": True},
            {"name": "node_desired",   "label": "Desired nodes",           "placeholder": "2",             "default": "2",             "required": True},
            {"name": "tags_env",       "label": "Environment tag",         "placeholder": "prod",          "default": "prod",          "required": False},
        ],
        "template": '''\
resource "aws_vpc" "{vpc_name}" {{
  cidr_block           = "{vpc_cidr}"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {{
    Name                                        = "{vpc_name}"
    "kubernetes.io/cluster/{cluster_name}"      = "shared"
    Env                                         = "{tags_env}"
  }}
}}

resource "aws_internet_gateway" "{vpc_name}_igw" {{
  vpc_id = aws_vpc.{vpc_name}.id
  tags   = {{ Name = "{vpc_name}-igw" }}
}}

resource "aws_subnet" "{vpc_name}_pub1" {{
  vpc_id                  = aws_vpc.{vpc_name}.id
  cidr_block              = "{pub1_cidr}"
  availability_zone       = "{az1}"
  map_public_ip_on_launch = true
  tags = {{
    Name                                        = "{vpc_name}-pub-1"
    "kubernetes.io/cluster/{cluster_name}"      = "shared"
    "kubernetes.io/role/elb"                    = "1"
  }}
}}

resource "aws_subnet" "{vpc_name}_pub2" {{
  vpc_id                  = aws_vpc.{vpc_name}.id
  cidr_block              = "{pub2_cidr}"
  availability_zone       = "{az2}"
  map_public_ip_on_launch = true
  tags = {{
    Name                                        = "{vpc_name}-pub-2"
    "kubernetes.io/cluster/{cluster_name}"      = "shared"
    "kubernetes.io/role/elb"                    = "1"
  }}
}}

resource "aws_subnet" "{vpc_name}_priv1" {{
  vpc_id            = aws_vpc.{vpc_name}.id
  cidr_block        = "{priv1_cidr}"
  availability_zone = "{az1}"
  tags = {{
    Name                                        = "{vpc_name}-priv-1"
    "kubernetes.io/cluster/{cluster_name}"      = "shared"
    "kubernetes.io/role/internal-elb"           = "1"
  }}
}}

resource "aws_subnet" "{vpc_name}_priv2" {{
  vpc_id            = aws_vpc.{vpc_name}.id
  cidr_block        = "{priv2_cidr}"
  availability_zone = "{az2}"
  tags = {{
    Name                                        = "{vpc_name}-priv-2"
    "kubernetes.io/cluster/{cluster_name}"      = "shared"
    "kubernetes.io/role/internal-elb"           = "1"
  }}
}}

resource "aws_eip" "{vpc_name}_nat_eip" {{
  domain = "vpc"
  tags   = {{ Name = "{vpc_name}-nat-eip" }}
}}

resource "aws_nat_gateway" "{vpc_name}_nat" {{
  allocation_id = aws_eip.{vpc_name}_nat_eip.id
  subnet_id     = aws_subnet.{vpc_name}_pub1.id
  depends_on    = [aws_internet_gateway.{vpc_name}_igw]
  tags          = {{ Name = "{vpc_name}-nat" }}
}}

resource "aws_route_table" "{vpc_name}_public_rt" {{
  vpc_id = aws_vpc.{vpc_name}.id
  route {{
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.{vpc_name}_igw.id
  }}
  tags = {{ Name = "{vpc_name}-public-rt" }}
}}

resource "aws_route_table_association" "{vpc_name}_pub1_rta" {{
  subnet_id      = aws_subnet.{vpc_name}_pub1.id
  route_table_id = aws_route_table.{vpc_name}_public_rt.id
}}

resource "aws_route_table_association" "{vpc_name}_pub2_rta" {{
  subnet_id      = aws_subnet.{vpc_name}_pub2.id
  route_table_id = aws_route_table.{vpc_name}_public_rt.id
}}

resource "aws_route_table" "{vpc_name}_private_rt" {{
  vpc_id = aws_vpc.{vpc_name}.id
  route {{
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.{vpc_name}_nat.id
  }}
  tags = {{ Name = "{vpc_name}-private-rt" }}
}}

resource "aws_route_table_association" "{vpc_name}_priv1_rta" {{
  subnet_id      = aws_subnet.{vpc_name}_priv1.id
  route_table_id = aws_route_table.{vpc_name}_private_rt.id
}}

resource "aws_route_table_association" "{vpc_name}_priv2_rta" {{
  subnet_id      = aws_subnet.{vpc_name}_priv2.id
  route_table_id = aws_route_table.{vpc_name}_private_rt.id
}}

# ── IAM — EKS Cluster Role ──
resource "aws_iam_role" "{cluster_name}_cluster_role" {{
  name = "{cluster_name}-cluster-role"

  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [{{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = {{ Service = "eks.amazonaws.com" }}
    }}]
  }})

  tags = {{ Name = "{cluster_name}-cluster-role" }}
}}

resource "aws_iam_role_policy_attachment" "{cluster_name}_cluster_policy" {{
  role       = aws_iam_role.{cluster_name}_cluster_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}}

# ── IAM — EKS Node Role ──
resource "aws_iam_role" "{cluster_name}_node_role" {{
  name = "{cluster_name}-node-role"

  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [{{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = {{ Service = "ec2.amazonaws.com" }}
    }}]
  }})

  tags = {{ Name = "{cluster_name}-node-role" }}
}}

resource "aws_iam_role_policy_attachment" "{cluster_name}_node_policy" {{
  role       = aws_iam_role.{cluster_name}_node_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
}}

resource "aws_iam_role_policy_attachment" "{cluster_name}_cni_policy" {{
  role       = aws_iam_role.{cluster_name}_node_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
}}

resource "aws_iam_role_policy_attachment" "{cluster_name}_ecr_policy" {{
  role       = aws_iam_role.{cluster_name}_node_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}}

# ── EKS Cluster ──
resource "aws_eks_cluster" "{cluster_name}" {{
  name     = "{cluster_name}"
  version  = "{k8s_version}"
  role_arn = aws_iam_role.{cluster_name}_cluster_role.arn

  vpc_config {{
    subnet_ids = [
      aws_subnet.{vpc_name}_priv1.id,
      aws_subnet.{vpc_name}_priv2.id,
      aws_subnet.{vpc_name}_pub1.id,
      aws_subnet.{vpc_name}_pub2.id,
    ]
    endpoint_private_access = true
    endpoint_public_access  = true
  }}

  depends_on = [aws_iam_role_policy_attachment.{cluster_name}_cluster_policy]

  tags = {{ Name = "{cluster_name}", Env = "{tags_env}" }}
}}

# ── EKS Managed Node Group ──
resource "aws_eks_node_group" "{node_name}" {{
  cluster_name    = aws_eks_cluster.{cluster_name}.name
  node_group_name = "{node_name}"
  node_role_arn   = aws_iam_role.{cluster_name}_node_role.arn
  subnet_ids      = [aws_subnet.{vpc_name}_priv1.id, aws_subnet.{vpc_name}_priv2.id]
  instance_types  = ["{node_type}"]

  scaling_config {{
    min_size     = {node_min}
    max_size     = {node_max}
    desired_size = {node_desired}
  }}

  update_config {{
    max_unavailable = 1
  }}

  depends_on = [
    aws_iam_role_policy_attachment.{cluster_name}_node_policy,
    aws_iam_role_policy_attachment.{cluster_name}_cni_policy,
    aws_iam_role_policy_attachment.{cluster_name}_ecr_policy,
  ]

  tags = {{ Name = "{node_name}", Env = "{tags_env}" }}
}}
''',
    },

    # ─────────────────────────────────────────────
    # 8. Lambda + IAM (kept simple)
    # ─────────────────────────────────────────────
    {
        "id": "lambda_iam",
        "name": "Lambda + IAM Role",
        "icon": "🔑",
        "description": "IAM execution role with basic policy and a Lambda function wired to it",
        "resources": [
            "aws_iam_role", "aws_iam_role_policy_attachment", "aws_lambda_function",
        ],
        "fields": [
            {"name": "role_name",  "label": "IAM role resource name",  "placeholder": "lambda_role",        "default": "lambda_role",        "required": True},
            {"name": "role_id",    "label": "IAM role name (AWS)",     "placeholder": "lambda-exec-role",   "default": "lambda-exec-role",   "required": True},
            {"name": "fn_name",    "label": "Lambda resource name",    "placeholder": "my_lambda",          "default": "my_lambda",          "required": True},
            {"name": "fn_id",      "label": "Lambda function name",    "placeholder": "my-lambda-function", "default": "my-lambda-function", "required": True},
            {"name": "runtime",    "label": "Runtime",                 "placeholder": "python3.11",         "default": "python3.11",         "required": True},
            {"name": "handler",    "label": "Handler",                 "placeholder": "index.handler",      "default": "index.handler",      "required": True},
            {"name": "filename",   "label": "ZIP filename",            "placeholder": "lambda.zip",         "default": "lambda.zip",         "required": True},
            {"name": "tags_env",   "label": "Environment tag",         "placeholder": "prod",               "default": "prod",               "required": False},
        ],
        "template": '''\
resource "aws_iam_role" "{role_name}" {{
  name = "{role_id}"

  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [{{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = {{ Service = "lambda.amazonaws.com" }}
    }}]
  }})

  tags = {{ Name = "{role_id}", Env = "{tags_env}" }}
}}

resource "aws_iam_role_policy_attachment" "{role_name}_basic_execution" {{
  role       = aws_iam_role.{role_name}.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}}

resource "aws_lambda_function" "{fn_name}" {{
  function_name = "{fn_id}"
  runtime       = "{runtime}"
  handler       = "{handler}"
  role          = aws_iam_role.{role_name}.arn
  filename      = "{filename}"

  tags = {{ Name = "{fn_id}", Env = "{tags_env}" }}
}}
''',
    },

]


def get_blueprint(blueprint_id: str) -> dict | None:
    return next((b for b in BLUEPRINTS if b["id"] == blueprint_id), None)


def build_blueprint_hcl(blueprint_id: str, values: dict[str, str]) -> str:
    blueprint = get_blueprint(blueprint_id)
    if not blueprint:
        raise ValueError(f"Unknown blueprint: {blueprint_id}")
    return blueprint["template"].format(**values)
