# IAM Setup for Deployment

> **Relevant source files**
> * [.gitignore](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/.gitignore)
> * [docs/infrastucture/IAM_SETUP.md](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md)

## Purpose and Scope

This document provides a comprehensive guide for configuring AWS Identity and Access Management (IAM) permissions required to deploy the Architecture AI Assistant using Terraform. It covers the creation of a dedicated deployment user (`terraform-deploy-user`), the `TerraformDeploymentPolicy` with granular permissions, and AWS credential configuration.

For information about the actual deployment process using the configured credentials, see [Deployment Script](/dotpep/architecture-ai-assistant/6.1-deployment-script). For environment variables and secrets management, see [Environment Configuration](/dotpep/architecture-ai-assistant/6.3-environment-configuration). For the Lambda execution roles created during deployment, see [IAM Roles and Security](/dotpep/architecture-ai-assistant/5.4-iam-roles-and-security).

**Sources**: [docs/infrastucture/IAM_SETUP.md L1-L18](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L1-L18)

---

## Overview of IAM Requirements

The deployment process requires permissions to create and manage AWS resources across multiple services. The IAM setup consists of two distinct permission layers:

1. **Deployment User Permissions** - Required by the Terraform execution to provision infrastructure
2. **Lambda Execution Roles** - Created by Terraform for runtime access to DynamoDB, S3, and CloudWatch

### Deployment User Required Services

| AWS Service | Purpose | Key Resources |
| --- | --- | --- |
| Lambda | Function and layer management | `generate_diagram`, `chat_crud`, `get_history` |
| API Gateway | REST API provisioning | `/api/diagram/generate`, `/api/chat/save`, `/api/chat/history` |
| DynamoDB | Table creation | `chat_history` table with partition/sort keys |
| S3 | Bucket management | Frontend assets bucket, diagrams bucket |
| CloudFront | Distribution setup | Static content delivery, cache invalidation |
| IAM | Role and policy creation | Lambda execution roles |
| CloudWatch Logs | Log group configuration | `/aws/lambda/*` log groups |

**Sources**: [docs/infrastucture/IAM_SETUP.md L5-L15](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L5-L15)

---

## Deployment User Architecture

The following diagram shows how the `terraform-deploy-user` interacts with AWS services during Terraform execution:

### IAM Deployment Flow

```

```

**Sources**: [docs/infrastucture/IAM_SETUP.md L32-L60](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L32-L60)

 [infrastructure/scripts/deploy.sh L1-L150](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/scripts/deploy.sh#L1-L150)

---

## Creating the Deployment User

### Option 1: Existing Administrative User

If you have an existing IAM user with administrative access, you can use it directly. However, this is **not recommended for production** due to excessive permissions.

Verify existing permissions:

```

```

**Sources**: [docs/infrastucture/IAM_SETUP.md L20-L29](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L20-L29)

### Option 2: Dedicated Deployment User (Recommended)

Create a dedicated IAM user with minimum required permissions following the principle of least privilege.

#### Step 1: Create User

**Using AWS CLI:**

```

```

**Using AWS Console:**
Navigate to IAM → Users → Add users, select "Programmatic access"

**Sources**: [docs/infrastucture/IAM_SETUP.md L33-L44](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L33-L44)

#### Step 2: Generate Access Keys

**Using AWS CLI:**

```

```

**Output:**

```

```

**Important**: Save the `AccessKeyId` and `SecretAccessKey` immediately - the secret cannot be retrieved later.

**Sources**: [docs/infrastucture/IAM_SETUP.md L46-L58](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L46-L58)

---

## TerraformDeploymentPolicy Configuration

The `TerraformDeploymentPolicy` defines the minimum permissions required for Terraform to provision all infrastructure components. The policy is structured with separate statement blocks for each AWS service.

### Policy Structure Overview

```

```

**Sources**: [docs/infrastucture/IAM_SETUP.md L62-L250](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L62-L250)

### Policy Document

Save the following as `terraform-deploy-policy.json`:

| Statement Sid | Purpose | Key Actions |
| --- | --- | --- |
| `LambdaManagement` | Manage Lambda functions and layers | `lambda:CreateFunction`, `lambda:PublishLayerVersion`, `lambda:AddPermission` |
| `APIGatewayManagement` | Configure API Gateway | `apigateway:POST`, `apigateway:PUT`, `apigateway:DELETE` |
| `DynamoDBManagement` | Create and configure DynamoDB tables | `dynamodb:CreateTable`, `dynamodb:UpdateTimeToLive` |
| `S3Management` | Bucket creation and object management | `s3:CreateBucket`, `s3:PutBucketPolicy`, `s3:PutObject` |
| `CloudFrontManagement` | CloudFront distributions | `cloudfront:CreateDistribution`, `cloudfront:CreateOriginAccessControl` |
| `IAMManagement` | Create Lambda execution roles | `iam:CreateRole`, `iam:PassRole`, `iam:AttachRolePolicy` |
| `CloudWatchLogsManagement` | Log group configuration | `logs:CreateLogGroup`, `logs:PutRetentionPolicy` |
| `TerraformStateManagement` | S3 state backend access | `s3:GetObject`, `s3:PutObject` on `terraform-state-*` buckets |
| `EC2NetworkingForLambda` | VPC inspection for Lambda | `ec2:DescribeSecurityGroups`, `ec2:DescribeSubnets` |

**Full policy document**: [docs/infrastucture/IAM_SETUP.md L68-L250](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L68-L250)

### Applying the Policy

**Using AWS CLI:**

```

```

**Using AWS Console:**

1. IAM → Policies → Create policy
2. JSON tab → Paste policy document
3. Name: `TerraformDeploymentPolicy`
4. IAM → Users → terraform-deploy-user → Add permissions → Attach existing policies

**Sources**: [docs/infrastucture/IAM_SETUP.md L254-L275](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L254-L275)

---

## Lambda Execution Roles

The Terraform configuration creates three Lambda execution roles with least-privilege permissions. These roles are **created automatically** during deployment and should not be manually configured.

### Lambda IAM Role Architecture

```

```

**Sources**: [docs/infrastucture/IAM_SETUP.md L298-L320](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L298-L320)

 [infrastructure/terraform/iam.tf L1-L150](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/iam.tf#L1-L150)

### Role Permission Summary

#### 1. generate_diagram Lambda Role

**Purpose**: Generate diagrams via LLM, render to PNG, store in S3, persist metadata

**Permissions**:

* **DynamoDB**: `PutItem`, `GetItem` on `chat_history` table
* **S3**: `PutObject`, `GetObject` on `diagrams/*` prefix
* **CloudWatch Logs**: `CreateLogGroup`, `CreateLogStream`, `PutLogEvents`

**Terraform Resource**: [infrastructure/terraform/iam.tf L10-L45](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/iam.tf#L10-L45)

#### 2. chat_crud Lambda Role

**Purpose**: CRUD operations for chat messages

**Permissions**:

* **DynamoDB**: `PutItem`, `GetItem`, `UpdateItem`, `DeleteItem` on `chat_history` table
* **CloudWatch Logs**: `CreateLogGroup`, `CreateLogStream`, `PutLogEvents`

**Terraform Resource**: [infrastructure/terraform/iam.tf L47-L75](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/iam.tf#L47-L75)

#### 3. get_history Lambda Role

**Purpose**: Paginated retrieval of chat history

**Permissions**:

* **DynamoDB**: `Query`, `Scan` on `chat_history` table (read-only)
* **CloudWatch Logs**: `CreateLogGroup`, `CreateLogStream`, `PutLogEvents`

**Terraform Resource**: [infrastructure/terraform/iam.tf L77-L100](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/infrastructure/terraform/iam.tf#L77-L100)

**Sources**: [docs/infrastucture/IAM_SETUP.md L298-L320](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L298-L320)

---

## AWS CLI Configuration

Configure the AWS CLI to use the deployment user credentials for Terraform execution.

### Create Named Profile

```

```

**Prompts:**

```
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: us-east-1
Default output format [None]: json
```

### Profile Location

The profile is stored in `~/.aws/credentials`:

```

```

And `~/.aws/config`:

```

```

### Using the Profile

The `deploy.sh` script uses the profile via the `AWS_PROFILE` environment variable:

```

```

Or set it in `terraform.tfvars`:

```

```

**Sources**: [docs/infrastucture/IAM_SETUP.md L277-L283](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L277-L283)

---

## Permission Verification

Test the deployment user permissions before running Terraform to ensure all required access is configured.

### Basic Identity Verification

```

```

**Expected Output:**

```

```

### Service-Specific Permission Tests

| Service | Test Command | Purpose |
| --- | --- | --- |
| Lambda | `aws lambda list-functions --profile terraform-deploy` | Verify Lambda read access |
| S3 | `aws s3 ls --profile terraform-deploy` | Verify S3 bucket listing |
| DynamoDB | `aws dynamodb list-tables --profile terraform-deploy` | Verify DynamoDB access |
| API Gateway | `aws apigateway get-rest-apis --profile terraform-deploy` | Verify API Gateway access |
| CloudFront | `aws cloudfront list-distributions --profile terraform-deploy` | Verify CloudFront access |
| IAM | `aws iam list-roles --profile terraform-deploy` | Verify IAM read access |

### Policy Attachment Verification

```

```

**Sources**: [docs/infrastucture/IAM_SETUP.md L285-L296](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L285-L296)

 [docs/infrastucture/IAM_SETUP.md L373-L396](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L373-L396)

---

## Security Best Practices

### 1. Multi-Factor Authentication (MFA)

Enable MFA for the deployment user to require two-factor authentication:

```

```

**Sources**: [docs/infrastucture/IAM_SETUP.md L330-L338](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L330-L338)

### 2. Access Key Rotation

Rotate access keys every 90 days:

```

```

**Sources**: [docs/infrastucture/IAM_SETUP.md L340-L353](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L340-L353)

### 3. Environment Separation

Use separate AWS accounts for each environment:

| Environment | Account Purpose | Access Level |
| --- | --- | --- |
| Development | Feature development and testing | Unrestricted access |
| Staging | Pre-production validation | Limited access |
| Production | Live application | Highly restricted |

Each account should have its own `terraform-deploy-user` with environment-specific policies.

**Sources**: [docs/infrastucture/IAM_SETUP.md L323-L329](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L323-L329)

### 4. CloudTrail Monitoring

Enable CloudTrail to audit all API calls made by the deployment user:

```

```

Monitor for:

* Unauthorized API calls
* Failed authentication attempts
* Policy changes
* Resource deletions

**Sources**: [docs/infrastucture/IAM_SETUP.md L359-L368](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L359-L368)

### 5. AWS Organizations Service Control Policies (SCPs)

For enterprise deployments, use AWS Organizations with SCPs to enforce security boundaries:

```

```

**Sources**: [docs/infrastucture/IAM_SETUP.md L355-L357](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L355-L357)

---

## Troubleshooting

### Common Permission Errors

#### Error: "User is not authorized to perform: iam:PassRole"

**Cause**: Missing `iam:PassRole` permission in `TerraformDeploymentPolicy`

**Solution**: Verify the `IAMManagement` statement includes:

```

```

**Policy Location**: [docs/infrastucture/IAM_SETUP.md L185-L212](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L185-L212)

#### Error: "Access Denied" when creating CloudFront distribution

**Cause**: Missing CloudFront permissions

**Solution**: Ensure `CloudFrontManagement` statement is attached:

```

```

**Policy Location**: [docs/infrastucture/IAM_SETUP.md L163-L183](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L163-L183)

#### Error: "Cannot assume role for Lambda function"

**Cause**: Missing `iam:PassRole` or Lambda execution role not created

**Solution**:

1. Verify `iam:PassRole` permission exists
2. Check if Lambda execution roles exist:

```

```

**Sources**: [docs/infrastucture/IAM_SETUP.md L398-L409](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L398-L409)

### Diagnostic Commands

#### Check Current Identity

```

```

Verify the output shows `terraform-deploy-user`.

#### List Attached Policies

```

```

Should show `TerraformDeploymentPolicy` attached.

#### Test Specific Service Access

```

```

#### Review CloudTrail Logs

```

```

Look for events with `errorCode` field indicating denied actions.

**Sources**: [docs/infrastucture/IAM_SETUP.md L370-L398](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L370-L398)

### Testing Policy with IAM Policy Simulator

Use the AWS IAM Policy Simulator to test permissions without making actual API calls:

1. Navigate to: [https://policysim.aws.amazon.com/](https://policysim.aws.amazon.com/)
2. Select user: `terraform-deploy-user`
3. Select service: e.g., Lambda
4. Select actions: e.g., `CreateFunction`
5. Run simulation

**Sources**: [docs/infrastucture/IAM_SETUP.md L448-L450](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L448-L450)

---

## Minimal Testing Policy

For quick testing in isolated development accounts only (not recommended for production):

```

```

**Warning**: This policy grants broad permissions and should only be used for testing in isolated accounts. Never use in production.

**Sources**: [docs/infrastucture/IAM_SETUP.md L411-L434](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L411-L434)

---

## Additional Resources

* [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
* [Terraform AWS Provider Authentication](https://registry.terraform.io/providers/hashicorp/aws/latest/docs#authentication-and-configuration)
* [AWS Lambda Execution Role](https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html)
* [Least Privilege Principle](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html#grant-least-privilege)

**Sources**: [docs/infrastucture/IAM_SETUP.md L438-L443](https://github.com/dotpep/architecture-ai-assistant/blob/1285f968/docs/infrastucture/IAM_SETUP.md#L438-L443)