import os
from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
IMG = os.path.join(HERE, "img")
REPO_URL = "https://github.com/SUB-Bzero/cloud-deploy-pipeline"

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
for m in ("left_margin", "right_margin"):
    setattr(sec, m, Cm(2.2))
sec.top_margin = Cm(2.0); sec.bottom_margin = Cm(2.0)

st = doc.styles
st["Normal"].font.name = "Calibri"; st["Normal"].font.size = Pt(11)
st["Normal"].element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
st["Normal"].paragraph_format.space_after = Pt(6)
st["Normal"].paragraph_format.line_spacing = 1.12
for name, size, color in (("Heading 1", 18, "1F3864"), ("Heading 2", 14, "2F5496"), ("Heading 3", 12, "2F5496")):
    s = st[name]; s.font.name = "Calibri"; s.font.size = Pt(size); s.font.bold = True
    s.font.color.rgb = RGBColor.from_string(color)
    s.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
    s.paragraph_format.space_before = Pt(14 if name != "Heading 3" else 10)
    s.paragraph_format.space_after = Pt(6); s.paragraph_format.keep_with_next = True


# ---------------------------------------------------------------- helpers
def shade(cell, hex_):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), hex_)
    tcPr.append(shd)

def para(text="", bold=False, italic=False, size=None, align=None, color=None, after=None, style=None):
    p = doc.add_paragraph(style=style)
    if text:
        add_runs(p, text, bold, italic, size, color)
    if align: p.alignment = align
    if after is not None: p.paragraph_format.space_after = Pt(after)
    return p

def add_runs(p, text, bold=False, italic=False, size=None, color=None):
    """**bold** and `code` inline markup."""
    import re
    for part in re.split(r"(\*\*.+?\*\*|`.+?`)", text):
        if not part: continue
        if part.startswith("**"):
            r = p.add_run(part[2:-2]); r.bold = True
        elif part.startswith("`"):
            r = p.add_run(part[1:-1]); r.font.name = "Consolas"; r.font.size = Pt(9.5)
            r._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
            r.font.color.rgb = RGBColor(0x9C, 0x1C, 0x1C)
        else:
            r = p.add_run(part); r.bold = bold
        if italic: r.italic = True
        if size and not part.startswith("`"): r.font.size = Pt(size)
        if color and not part.startswith("`"): r.font.color.rgb = RGBColor.from_string(color)

def bullets(items, style="List Bullet"):
    for it in items:
        p = doc.add_paragraph(style=style); add_runs(p, it)
        p.paragraph_format.space_after = Pt(2)

def h(text, lvl=1):
    return doc.add_heading(text, level=lvl)

def table(header, rows, widths=None, font=9.5):
    t = doc.add_table(rows=1, cols=len(header)); t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, x in enumerate(header):
        c = t.rows[0].cells[i]; c.text = ""; shade(c, "1F3864")
        r = c.paragraphs[0].add_run(x); r.bold = True; r.font.size = Pt(font); r.font.color.rgb = RGBColor(255, 255, 255)
    for ri, row in enumerate(rows):
        cells = t.add_row().cells
        for i, x in enumerate(row):
            cells[i].text = ""; p = cells[i].paragraphs[0]; p.paragraph_format.space_after = Pt(1)
            add_runs(p, x, size=font)
            if ri % 2: shade(cells[i], "EEF2F9")
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths): row.cells[i].width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t

def code(text, size=8):
    t = doc.add_table(rows=1, cols=1); t.style = "Table Grid"
    c = t.rows[0].cells[0]; shade(c, "F5F5F5"); c.text = ""
    lines = text.rstrip("\n").split("\n")
    p = c.paragraphs[0]
    for i, ln in enumerate(lines):
        r = p.add_run(ln if ln else " "); r.font.name = "Consolas"; r.font.size = Pt(size)
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
        if i < len(lines) - 1: r.add_break()
    p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.0
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

FIG = {"n": 0}
def caption(text):
    FIG["n"] += 1
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(f"Figure {FIG['n']}: "); r.bold = True; r.font.size = Pt(10)
    r2 = p.add_run(text); r2.italic = True; r2.font.size = Pt(10)
    p.paragraph_format.space_after = Pt(12)
    return FIG["n"]

def figure(path, cap, width=16.3):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True; p.paragraph_format.space_after = Pt(3)
    p.add_run().add_picture(os.path.join(IMG, path), width=Cm(width))
    caption(cap)

def placeholder(cap, what):
    t = doc.add_table(rows=1, cols=1); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = t.rows[0].cells[0]; shade(c, "FFF2CC"); c.text = ""
    p = c.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(18)
    r = p.add_run(f"[ INSERT SCREENSHOT - Figure {FIG['n'] + 1} ]"); r.bold = True; r.font.size = Pt(12)
    r.font.color.rgb = RGBColor(0xC0, 0x00, 0x00)
    p2 = c.add_paragraph(); p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p2.add_run("Capture: " + what); r.font.size = Pt(9.5)
    p3 = c.add_paragraph(); p3.alignment = WD_ALIGN_PARAGRAPH.CENTER; p3.paragraph_format.space_after = Pt(18)
    r = p3.add_run("(delete this box and paste the screenshot; keep the caption below)"); r.italic = True; r.font.size = Pt(8.5)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    caption(cap)

def page_break():
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

def add_field(run, instr):
    for t, txt in (("begin", None), (None, instr), ("end", None)):
        if t:
            e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), t)
        else:
            e = OxmlElement("w:instrText"); e.set(qn("xml:space"), "preserve"); e.text = txt
        run._r.append(e)

# footer page numbers
fp = sec.footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = fp.add_run("Capstone Project - Automated Cloud Deployment Pipeline  |  Page "); r.font.size = Pt(9)
r2 = fp.add_run(); r2.font.size = Pt(9); add_field(r2, "PAGE")

def read(rel):
    return open(os.path.join(ROOT, rel)).read()

# ================================================================= COVER
for _ in range(5): para("")
para("Capstone Project", bold=True, size=30, align=WD_ALIGN_PARAGRAPH.CENTER, color="1F3864", after=2)
para("Automated Cloud Deployment Pipeline", bold=True, size=24, align=WD_ALIGN_PARAGRAPH.CENTER, color="2F5496", after=10)
para("Containerised web application deployed to AWS with Terraform, GitHub Actions CI/CD and CloudWatch monitoring",
     italic=True, size=13, align=WD_ALIGN_PARAGRAPH.CENTER, after=40)
t = doc.add_table(rows=0, cols=2); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
for k, v in (("Student name", "Jeu Bulantulu"), ("Student number", "[ your student number ]"),
             ("Course / Module", "[ course name and code ]"), ("Lecturer / Assessor", "[ name ]"),
             ("Submission date", "[ date ]"), ("GitHub repository", REPO_URL)):
    cells = t.add_row().cells
    cells[0].text = ""; shade(cells[0], "DCE6F2")
    rr = cells[0].paragraphs[0].add_run(k); rr.bold = True
    cells[1].text = v
    cells[0].width = Cm(5); cells[1].width = Cm(10.5)
page_break()

# ================================================================= 0 overview
h("Project Overview")
para("This project builds, ships and operates a small containerised web application on Amazon Web Services "
     "without any manual console work. A `git push` to the `main` branch triggers a GitHub Actions pipeline that "
     "tests the code, builds a Docker image, pushes it to Amazon ECR, provisions or updates the cloud infrastructure "
     "with Terraform, and finally deploys the new container to an EC2 host. The application is health-checked "
     "continuously, CloudWatch alarms send an e-mail when CPU or HTTP 5xx errors exceed their limits, and a failed "
     "deployment is rolled back automatically.")
table(["Area", "Choice", "Why"], [
    ["Application", "Python 3.12, Flask, gunicorn, psycopg 3", "Small, fast to test; exposes `/health` and a notes REST API backed by PostgreSQL"],
    ["Containers", "Docker multi-stage build, Docker Compose", "Small non-root runtime image; one command local Web + DB stack"],
    ["IaC", "Terraform 1.9, modules: vpc, database, compute, monitoring", "Repeatable, reviewable infrastructure; remote state in S3 with DynamoDB locking"],
    ["Compute", "EC2 (Amazon Linux 2023) running Docker, behind an Application Load Balancer", "Simple host for the container; ALB provides health checks and the 5xx metrics"],
    ["Database", "Amazon RDS PostgreSQL 16 in private subnets", "Managed, encrypted database that is unreachable from the internet"],
    ["CI/CD", "GitHub Actions, Amazon ECR, AWS Systems Manager (SSM)", "Native to the repo; no SSH keys or open port 22 needed to deploy"],
    ["Monitoring", "CloudWatch Alarms, SNS e-mail", "CPU > 80 %, 5xx error-rate and unhealthy-host alarms notify the administrator"],
], widths=[2.8, 6.2, 7.5])

# ================================================================= 1 ARCH
h("1. Architecture Diagram")
para("Figure 1 shows how a user request travels through the system and how the delivery pipeline and monitoring "
     "services are connected. Arrows show the direction of communication.")
figure("architecture.png", "Architecture and traffic flow: Internet → Application Load Balancer → EC2 host (Docker container) → RDS PostgreSQL, "
       "with the CI/CD, Terraform state and monitoring paths.", width=16.6)
h("1.1 Traffic flow (Internet → Cloud Host → Database)", 2)
bullets([
    "**Step 1 - Internet → Load Balancer.** The user's browser sends HTTP on port 80. It enters the VPC through the Internet Gateway and reaches the Application Load Balancer in the public subnets.",
    "**Step 2 - Load Balancer → Cloud Host.** The ALB forwards the request on port 80 to the EC2 host (target group). Only the ALB's security group may reach the host, and the ALB only forwards while `/health` returns HTTP 200.",
    "**Step 3 - Cloud Host → Database.** The Flask container (port 8000, mapped to host port 80) opens an SSL connection to RDS PostgreSQL on port 5432. The database sits in private subnets with no internet route, and only the host's security group is allowed in.",
    "**Response.** The answer returns along the same path in the opposite direction.",
])
h("1.2 Components", 2)
table(["Component", "Role", "Key security setting"], [
    ["VPC 10.0.0.0/16", "Isolated network with 2 public + 2 private subnets in 2 Availability Zones", "Private subnets have no route to the Internet Gateway"],
    ["Application Load Balancer", "Public entry point, `/health` checks, 5xx metrics", "SG: port 80 from 0.0.0.0/0 only"],
    ["EC2 t3.micro (Docker)", "Runs the Flask container", "SG: port 80 from the ALB SG only; no SSH (SSM Session Manager); IMDSv2 required; encrypted disk"],
    ["RDS PostgreSQL 16", "Managed database", "Private, encrypted, SG: port 5432 from the host SG only, SSL enforced"],
    ["ECR", "Stores the Docker images", "Scan-on-push, lifecycle policy keeps last 15 images"],
    ["S3 + DynamoDB", "Terraform remote state and locking", "Versioned, encrypted, public access blocked"],
    ["CloudWatch + SNS", "Alarms and e-mail alerts", "Alarm and OK notifications to the admin e-mail"],
    ["SSM Parameter Store", "Holds the database connection string", "SecureString; the host role can read only that parameter"],
], widths=[3.8, 6.2, 6.5])
page_break()

# ================================================================= 2 STEPS
h("2. Implementation Steps")
para("Each task below states what was done, the main steps, the tools used and the purpose of the important settings. "
     "Evidence is referenced by figure number in Section 3. All source files are in the GitHub repository (Section 4).")

h("Task 1 - Application containerisation", 2)
para("**What was done.** A small Flask web application with a PostgreSQL back end was written, unit-tested, packaged "
     "into a lightweight multi-stage Docker image and run together with a PostgreSQL container using Docker Compose.")
para("**Tools:** Python 3.12, Flask, gunicorn, psycopg 3, pytest, flake8, Docker, Docker Compose.")
para("**Main steps**", after=2)
bullets([
    "Created `app/app.py` with routes `/` (landing page), `/health`, `GET/POST /api/notes`, and a `/boom` endpoint that returns HTTP 500 and is only enabled when `ENABLE_FAULT_ENDPOINT=true` (used later to trigger the 5xx alarm safely).",
    "Created `app/db.py` (PostgreSQL access layer) which creates the `notes` table on first use.",
    "Wrote 7 unit tests in `app/tests/test_app.py` (health up/down, create/list notes, validation, fault endpoint on/off). The database layer is replaced by a fake, so the tests run anywhere without a database (Figure 2).",
    "Wrote the **multi-stage `app/Dockerfile`** (see Appendix A): stage 1 (`builder`) creates a virtual environment and installs dependencies; stage 2 (`runtime`) starts from a clean `python:3.12-slim`, copies only the virtual environment and the two source files, and runs as a non-root user.",
    "Wrote `docker-compose.yml` with a `db` service (postgres:16-alpine, health check `pg_isready`) and a `web` service that waits until the database is healthy (`depends_on: condition: service_healthy`). Run with `docker compose up --build` and test with `curl localhost:8000/health` (Figures 3-5).",
])
para("**Purpose of important settings**", after=2)
table(["Setting", "Purpose"], [
    ["Multi-stage build", "Build tools and pip caches stay in the discarded builder stage, so the final image is small and has a smaller attack surface."],
    ["`USER appuser` (UID 10001)", "The container never runs as root."],
    ["`HEALTHCHECK` in the Dockerfile", "Docker marks the container unhealthy if `/health` stops answering 200."],
    ["`.dockerignore`", "Keeps tests, caches and dev files out of the image."],
    ["`DATABASE_URL` environment variable", "Connection details are injected at run time (Compose locally, SSM Parameter Store on AWS); nothing is hard-coded in the image."],
    ["`/health` returns 503 when the DB is down", "Load balancer and deploy script can tell a broken instance from a healthy one (Figure 3)."],
], widths=[5.2, 11.3])

h("Task 2 - Infrastructure as Code with Terraform", 2)
para("**What was done.** All AWS resources are defined as modular Terraform code. A one-time *bootstrap* configuration "
     "creates the remote-state bucket and the ECR repository; the main configuration then builds the network, database, "
     "compute and monitoring through four reusable modules.")
para("**Tools:** Terraform 1.9 (AWS provider 5.x, random provider), AWS CLI, S3, DynamoDB.")
code("""terraform/
├── bootstrap/            # run once: S3 state bucket + DynamoDB lock table + ECR repository
├── backend.tf            # S3 remote backend (bucket injected at init time)
├── main.tf               # wires the modules together
├── variables.tf  outputs.tf  versions.tf
└── modules/
    ├── vpc/         # VPC, 2 public + 2 private subnets, IGW, route tables, 3 security groups
    ├── database/    # RDS PostgreSQL, subnet group, random password, SSM SecureString URL
    ├── compute/     # EC2 + IAM role/profile, Application Load Balancer, target group, listener
    └── monitoring/  # SNS topic + e-mail subscription, CloudWatch alarms""", size=8.5)
para("**Main steps**", after=2)
bullets([
    "**Remote state (requirement: S3 bucket).** `terraform/bootstrap` creates the S3 bucket `capstone-app-tfstate-<account-id>` with versioning, AES-256 encryption and all public access blocked, plus a DynamoDB table for state locking. It is applied once with `terraform init && terraform apply` (Figure 7). The main configuration then uses `backend \"s3\"`; the pipeline passes the bucket, region and lock table with `-backend-config` flags.",
    "**VPC module.** Creates the VPC, two public subnets (ALB and EC2) and two private subnets (RDS) across two Availability Zones, an Internet Gateway and route tables. Only the public route table has a `0.0.0.0/0` route. Three chained security groups are created: `Internet → ALB-SG (80) → App-SG (80) → DB-SG (5432)` (Figure 8).",
    "**Database module.** Creates an encrypted, non-public RDS PostgreSQL 16 instance in the private subnets. The master password is generated by Terraform (`random_password`) and the full connection string is stored as an SSM SecureString, so no secret is committed to Git or printed in workflow logs (Figure 10).",
    "**Compute module.** Creates the EC2 instance (Amazon Linux 2023, IMDSv2 only, encrypted root disk) with an IAM role that allows SSM, pulling from ECR and reading only the database-URL parameter. `user_data` installs Docker once; image updates are deployed by the pipeline so they never replace the instance. It also creates the Application Load Balancer, target group (health check `GET /health` expecting 200) and HTTP listener (Figure 9).",
    "**Monitoring module.** Creates the SNS topic, e-mail subscription and CloudWatch alarms (Task 4).",
    "Ran `terraform fmt -check`, `terraform init -backend=false` and `terraform validate` on both configurations; both report *Success! The configuration is valid* (Figure 6).",
])
para("**Purpose of important settings**", after=2)
table(["Setting", "Purpose"], [
    ["S3 versioning + DynamoDB lock", "Every state revision is recoverable (rollback of infrastructure) and two applies can never run at once."],
    ["Private subnets without internet route", "The database cannot be reached from the internet even if a security group were misconfigured."],
    ["Security group referencing (`security_groups = [...]`)", "Least privilege: each tier only accepts traffic from the tier directly in front of it."],
    ["No SSH key, no port 22", "Administration and deployment go through SSM Session Manager/Run Command; nothing to brute-force."],
    ["`lifecycle { ignore_changes = [ami, user_data] }`", "Avoids replacing the running host when a newer AMI is published."],
    ["`sslmode=require` in the connection string", "RDS PostgreSQL 15+ enforces encrypted connections."],
    ["`default_tags`", "Every resource is tagged Project / Environment / ManagedBy for cost tracking."],
], widths=[5.8, 10.7])

h("Task 3 - Continuous Integration & Deployment (GitHub Actions)", 2)
para("**What was done.** `.github/workflows/deploy.yml` defines a four-stage pipeline that runs on every push to `main` "
     "(pull requests run only the test stage). The full file is in Appendix C.")
para("**Tools:** GitHub Actions, `aws-actions/configure-aws-credentials`, `amazon-ecr-login`, Docker Buildx, HashiCorp `setup-terraform`, AWS SSM Run Command.")
table(["Job", "What it does", "Fails the pipeline when"], [
    ["1. `test`", "Installs dependencies, runs `flake8` (lint) and `pytest` (unit tests)", "Lint error or failing test"],
    ["2. `build-and-push`", "Builds the multi-stage image, tags it with the short commit SHA and `latest`, pushes to Amazon ECR (Figure 13)", "Build or push error"],
    ["3. `terraform`", "`init` with the S3 backend, `fmt -check`, `validate`, `plan`, then `apply` of the saved plan (Figure 12)", "Invalid or failing infrastructure change"],
    ["4. `deploy`", "Waits for the host to register with SSM, sends `scripts/deploy.sh` via SSM Run Command, waits for the result, then smoke-tests `/health` through the load balancer (Figure 14)", "Health check fails (after automatic rollback) or smoke test fails"],
], widths=[3.2, 8.6, 4.7])
para("**Configuration.** Repository secrets: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `TF_STATE_BUCKET`, `TF_LOCK_TABLE`, `ALERT_EMAIL`. "
     "Repository variables: `AWS_REGION`, `ECR_REPOSITORY`, `ENABLE_FAULT_ENDPOINT`. The jobs are chained with `needs:` so a failing "
     "test stops everything; `concurrency` prevents two applies from overlapping; and the deployed image is identified by the commit SHA "
     "so every release is traceable (Figures 11-13).")

h("Task 4 - Monitoring and rollback", 2)
para("**What was done.** The application exposes `/health`, the load balancer and the deploy script use it, CloudWatch alarms watch "
     "CPU and 5xx errors and notify the administrator by e-mail through SNS, and a failed release is reverted automatically.")
para("**Tools:** Flask `/health` endpoint, ALB target-group health check, Amazon CloudWatch Alarms, Amazon SNS, `scripts/deploy.sh`.")
table(["Alarm", "Metric and condition", "Action"], [
    ["`…-ec2-cpu-high`", "EC2 `CPUUtilization` average > **80 %** for 2 consecutive 5-minute periods", "SNS → e-mail"],
    ["`…-http-5xx-rate`", "ALB `HTTPCode_Target_5XX_Count` ÷ `RequestCount` × 100 > **5 %** in 1 minute (evaluated only when ≥ 10 requests, to avoid false alarms on tiny traffic), via CloudWatch metric math", "SNS → e-mail"],
    ["`…-unhealthy-hosts`", "ALB `UnHealthyHostCount` > 0 for 2 minutes (the `/health` check is failing)", "SNS → e-mail"],
    ["`…-rds-cpu-high`", "RDS `CPUUtilization` > 80 %", "SNS → e-mail"],
], widths=[3.6, 10.2, 2.7])
para("**Main steps**", after=2)
bullets([
    "Implemented `GET /health`: returns `200 {\"status\":\"ok\",\"database\":\"up\"}` when PostgreSQL answers, otherwise `503`. Figure 3 shows the 503 when the database is unreachable; Figure 14 shows the 200 on AWS.",
    "Configured the ALB target group to call `/health` every 15 s; two successes mark the host healthy, three failures unhealthy.",
    "Created the SNS topic and e-mail subscription with Terraform (`alert_email` variable). The recipient must click *Confirm subscription* once in the e-mail AWS sends (Figure 16).",
    "Created the alarms above (Figure 15). To test the 5xx alarm the pipeline variable `ENABLE_FAULT_ENDPOINT=true` enables `/boom`; about 40 requests to `/boom` push the error rate above 5 % and the alarm e-mail arrives (Figure 16). The CPU alarm can be tested by running a CPU load through SSM Session Manager.",
    "**Rollback.** `scripts/deploy.sh` remembers the last healthy image. It starts the new container, polls `/health` for up to 60 s and, if the new version never becomes healthy, it restarts the previous image, prints the container logs and exits non-zero so the pipeline is marked failed while users keep getting the old, working version. The logic was verified with a simulated good release followed by a broken release (Figure 17). Infrastructure changes can be reverted by restoring the previous version of the state object in the versioned S3 bucket and re-running the pipeline with the previous commit.",
])
page_break()

# ================================================================= 3 SCREENSHOTS
h("3. Screenshots as Evidence")
para("Figure 1 is the architecture diagram. Figures 2, 3, 6 and 17 are real command output captured while developing and validating the project "
     "(unit tests, running application, Terraform validation and the rollback test of the deploy script). "
     "The remaining figures are screenshots of the AWS console, Docker and GitHub taken after the pipeline has run in the student's own AWS account.")

h("3.1 Application containerisation", 2)
figure("term_tests.png", "Linting (flake8) and all 7 unit tests passing - the first stage of the pipeline.")
figure("term_health.png", "Application served by gunicorn: `/` responds and `/health` correctly reports HTTP 503 / database \"down\" when no database is reachable.", width=15.5)
placeholder("`docker compose up --build` running the web and PostgreSQL containers locally; `curl localhost:8000/health` returns HTTP 200 with database \"up\".",
            "terminal showing `docker compose up -d`, `docker compose ps` (both containers Up/healthy) and `curl -i http://localhost:8000/health`.")
placeholder("Multi-stage image is lightweight: `docker images` shows the final runtime image size.",
            "terminal output of `docker images capstone-app` (or `docker compose images`) showing the size in MB.")

h("3.2 Infrastructure as Code", 2)
figure("term_terraform.png", "`terraform fmt -check` and `terraform validate` succeed for the main configuration and the bootstrap configuration.")
placeholder("S3 bucket holding the remote Terraform state (versioning enabled) and the `capstone/terraform.tfstate` object.",
            "AWS Console → S3 → `capstone-app-tfstate-…` → Objects tab and Properties tab (Bucket Versioning: Enabled).")
placeholder("VPC with public and private subnets and the three security groups created by Terraform.",
            "AWS Console → VPC → Your VPCs / Subnets (4 subnets) and EC2 → Security Groups (alb, app, db).")
placeholder("EC2 instance hosting the container in the `running` state with 2/2 status checks passed.",
            "AWS Console → EC2 → Instances showing `capstone-app-prod-app`.")
placeholder("RDS PostgreSQL database in the `Available` state, not publicly accessible, in the private subnets.",
            "AWS Console → RDS → Databases → `capstone-app-prod-pg` (Connectivity & security tab: Publicly accessible = No).")

h("3.3 CI/CD pipeline", 2)
placeholder("GitHub Actions run triggered by `git push`: all four jobs (test, build-and-push, terraform, deploy) completed successfully.",
            "GitHub → Actions → the latest run of \"CI/CD - Test, Build, Provision, Deploy\" showing 4 green jobs.")
placeholder("`terraform apply` step of the pipeline showing resources created and `Apply complete!`.",
            "GitHub → Actions → job `Terraform apply` → step \"Terraform apply\" log (scroll to the Apply complete line and outputs).")
placeholder("Docker image built by the pipeline is stored in Amazon ECR, tagged with the commit SHA and `latest`.",
            "AWS Console → ECR → repository `capstone-app` → Images.")
placeholder("Successful deployment of the application on the cloud host: `/health` answers HTTP 200 through the load balancer URL.",
            "browser (or `curl -i`) on `http://<alb-dns-name>/health`, plus the deploy job log showing \"SUCCESS … is healthy\".")

h("3.4 Monitoring and rollback", 2)
placeholder("CloudWatch alarms created by Terraform (CPU > 80 %, HTTP 5xx rate, unhealthy hosts, RDS CPU).",
            "AWS Console → CloudWatch → Alarms → All alarms (state OK; click the 5xx alarm and show its threshold).")
placeholder("E-mail alert received from Amazon SNS when an alarm fired (and/or the confirmed SNS subscription).",
            "your mailbox showing \"ALARM: capstone-app-prod-http-5xx-rate …\"; blur personal details if needed.")
figure("term_rollback.png", "Rollback test of `scripts/deploy.sh`: a healthy release is kept; a broken release fails the health check and the previous version is restored automatically.", width=15.5)
placeholder("(Optional) The same rollback in the real pipeline: deploy job log showing \"FAILED health check → ROLLING BACK\" while the site stays online.",
            "GitHub Actions → failed deploy job log after pushing a deliberately broken commit; then revert the commit.")
page_break()

# ================================================================= 4 REPO
h("4. GitHub Repository")
table(["Item", "Value"], [
    ["Repository link", REPO_URL],
    ["Visibility", "Public (or private with the assessor invited as a collaborator)"],
    ["Branch", "`main` (latest version of the project)"],
], widths=[4, 12.5])
para("Repository contents:", after=2)
code("""cloud-deploy-pipeline/
├── app/                      Flask app, unit tests, multi-stage Dockerfile
├── docker-compose.yml        local Web + PostgreSQL stack
├── terraform/                main configuration + modules (vpc, database, compute, monitoring)
│   └── bootstrap/            S3 state bucket, DynamoDB lock table, ECR repository
├── .github/workflows/deploy.yml   CI/CD pipeline
├── scripts/deploy.sh         on-host deploy with health check and automatic rollback
├── docs/                     architecture diagram, evidence and report generator
└── README.md                 run / deploy / tear-down instructions""", size=8.5)

# ================================================================= 5 CHECKLIST
h("5. Final Submission Checklist")
table(["Check", "Status"], [
    ["Architecture diagram is included (Figure 1)", "Done"],
    ["All implementation steps are documented (Tasks 1-4)", "Done"],
    ["Relevant screenshots are included, numbered and captioned (Section 3)", "Replace every yellow placeholder with your screenshot"],
    ["GitHub repository link is provided and accessible to the assessor", "Link added; open it in a private window to check it is public"],
    ["Word document converted to PDF", "File → Save As → PDF (after the two items above)"],
    ["PDF uploaded to the LMS portal", "Upload the PDF"],
], widths=[10.5, 6])
page_break()

# ================================================================= APPENDIX
h("Appendix A - Multi-stage Dockerfile (app/Dockerfile)")
code(read("app/Dockerfile"), size=8)
h("Appendix B - docker-compose.yml")
code(read("docker-compose.yml"), size=8)
h("Appendix C - CI/CD workflow (.github/workflows/deploy.yml)")
code(read(".github/workflows/deploy.yml"), size=7)
h("Appendix D - CloudWatch alarms (terraform/modules/monitoring/main.tf, excerpt)")
m = read("terraform/modules/monitoring/main.tf")
code(m[m.index("# 1) EC2 CPU"):m.index("# 3) Extra")], size=7.5)

out = os.path.join(ROOT, "Capstone_Project_Report.docx")
doc.save(out); print("saved", out, "figures:", FIG["n"])
