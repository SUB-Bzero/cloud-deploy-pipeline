locals {
  name = "${var.project}-${var.environment}"
}

module "vpc" {
  source   = "./modules/vpc"
  name     = local.name
  vpc_cidr = var.vpc_cidr
}

module "database" {
  source             = "./modules/database"
  name               = local.name
  instance_class     = var.db_instance_class
  private_subnet_ids = module.vpc.private_subnet_ids
  db_sg_id           = module.vpc.db_sg_id
}

module "compute" {
  source            = "./modules/compute"
  name              = local.name
  instance_type     = var.instance_type
  vpc_id            = module.vpc.vpc_id
  public_subnet_ids = module.vpc.public_subnet_ids
  app_sg_id         = module.vpc.app_sg_id
  alb_sg_id         = module.vpc.alb_sg_id
  aws_region        = var.aws_region
  db_url_param_name = module.database.db_url_parameter_name
  db_url_param_arn  = module.database.db_url_parameter_arn
}

module "monitoring" {
  source                  = "./modules/monitoring"
  name                    = local.name
  alert_email             = var.alert_email
  instance_id             = module.compute.instance_id
  alb_arn_suffix          = module.compute.alb_arn_suffix
  target_group_arn_suffix = module.compute.target_group_arn_suffix
  db_instance_id          = module.database.db_instance_id
  cpu_threshold           = var.cpu_alarm_threshold
  http_5xx_rate_threshold = var.http_5xx_rate_threshold
}
