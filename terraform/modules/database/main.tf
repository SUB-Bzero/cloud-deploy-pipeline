resource "random_password" "db" {
  length  = 24
  special = false # keeps the connection URL free of characters that need escaping
}

resource "aws_db_subnet_group" "this" {
  name       = "${var.name}-db-subnets"
  subnet_ids = var.private_subnet_ids
}

resource "aws_db_instance" "this" {
  identifier             = "${var.name}-pg"
  engine                 = "postgres"
  engine_version         = var.engine_version
  instance_class         = var.instance_class
  allocated_storage      = 20
  storage_type           = "gp3"
  storage_encrypted      = true
  db_name                = "appdb"
  username               = "appuser"
  password               = random_password.db.result
  db_subnet_group_name   = aws_db_subnet_group.this.name
  vpc_security_group_ids = [var.db_sg_id]
  publicly_accessible    = false
  multi_az               = false # set true for production HA

  backup_retention_period    = 1
  auto_minor_version_upgrade = true
  skip_final_snapshot        = true # capstone/demo only
  deletion_protection        = false
}

# The app reads its connection string from SSM Parameter Store at deploy time,
# so the password never appears in Git, GitHub secrets or the workflow logs.
# (RDS for PostgreSQL 15+ enforces SSL, hence sslmode=require.)
resource "aws_ssm_parameter" "database_url" {
  name  = "/${var.name}/database_url"
  type  = "SecureString"
  value = "postgresql://${aws_db_instance.this.username}:${random_password.db.result}@${aws_db_instance.this.address}:${aws_db_instance.this.port}/${aws_db_instance.this.db_name}?sslmode=require"
}
