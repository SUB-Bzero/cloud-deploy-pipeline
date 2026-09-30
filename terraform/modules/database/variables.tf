variable "name" { type = string }
variable "instance_class" { type = string }
variable "private_subnet_ids" { type = list(string) }
variable "db_sg_id" { type = string }

variable "engine_version" {
  type    = string
  default = "16"
}
