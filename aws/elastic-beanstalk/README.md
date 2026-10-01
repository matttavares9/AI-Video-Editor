# AWS Elastic Beanstalk deployment

This repository deploys its Dockerized FastAPI service on **AWS Elastic
Beanstalk** for a simple preview. Docker Compose is for local development;
for production, deploy the API image to ECS Fargate and keep Django/Flask as
separate services only when those interfaces need to be public.

## Before deploying

1. Create an AWS account and set a billing budget/alarm. Free Tier benefits or
   promotional credits are account-specific and time-limited; a running EC2
   instance can incur charges after those benefits are exhausted.
2. Install the EB CLI: `pip install awsebcli`, or create an ECS cluster/service
   if using the GitHub Actions deployment workflow.
3. Authenticate locally with `aws configure` using an IAM identity that can
   administer Elastic Beanstalk, EC2, CloudFormation, and S3 for this project.

## First deployment

From the repository root:

```bash
eb init ai-video-editor --platform docker --region us-east-1
eb create ai-video-editor-dev --single --instance_type t3.micro
eb setenv DATA_DIR=/data VIDEO_ENGINE_BIN=/app/build/video_engine
eb open
```

Elastic Beanstalk detects the root `Dockerfile`; `.ebextensions/01-healthcheck.config`
uses `/health` for environment health. Confirm the public service responds at:

```bash
curl "$(eb status --verbose | grep CNAME | awk '{print $2}')/health"
```

For subsequent deployments:

```bash
eb deploy
```

## Data and production hardening

The first deployment intentionally uses SQLite in the container. It is suitable
for a demo but its database and uploaded videos are **not durable** if the
instance is replaced or the environment is recreated. Before accepting real
customer uploads, make these two changes:

1. Create Amazon RDS PostgreSQL and set `DATABASE_URL` to its private
   connection URL (the API automatically accepts PostgreSQL URLs).
2. Store originals and exports in S3 instead of the container `/data`
   directory, then give the EC2 instance role least-privilege access to that
   bucket.

Use a separate staging environment, restrict inbound access as appropriate,
and keep API keys in Elastic Beanstalk environment properties or AWS Secrets
Manager—never in this repository.

## GitHub Actions ECS deployment

The `.github/workflows/deploy-aws.yml` workflow uses GitHub OIDC instead of
long-lived access keys. Create an IAM role trusted by the repository's GitHub
Actions OIDC provider, with scoped ECR push and ECS update permissions. Then
configure these GitHub environment values:

- secret `AWS_ROLE_ARN`
- variable `AWS_REGION`
- variable `ECR_REPOSITORY`
- variable `ECS_CLUSTER`
- variable `ECS_SERVICE`

The ECS task definition should use the ECR `:latest` image, set
`DATABASE_URL`, `DATA_DIR`, and `VIDEO_ENGINE_BIN=/app/build/video_engine`, and
provide secrets through AWS Secrets Manager. Attach a least-privilege task role
for the media S3 bucket. The workflow also publishes a commit-SHA image for
traceability.
