# IAM Setup Guide for Architecture AI Assistant

This guide provides detailed instructions for setting up IAM permissions required to deploy the Architecture AI Assistant using Terraform.

## Overview

The deployment requires permissions to create and manage the following AWS resources:
- Lambda functions and layers
- API Gateway REST APIs
- DynamoDB tables
- S3 buckets
- CloudFront distributions
- IAM roles and policies
- CloudWatch log groups

## Requirements: 6.3

This document addresses Requirement 6.3: "WHEN Lambda_Functions are deployed THEN the Architecture_AI_Assistant SHALL configure IAM roles with least-privilege permissions for DynamoDB, S3, and CloudWatch"

## Option 1: Using an Existing IAM User

If you have an existing IAM user with administrative access, you can use it directly. However, for production deployments, we recommend creating a dedicated deployment user with limited permissions (see Option 2).

### Verify Existing Permissions

```bash
aws iam get-user
aws iam list-attached-user-policies --user-name <your-username>
```

## Option 2: Create a Dedicated Deployment User (Recommended)

### Step 1: Create IAM User

Using AWS Console:
1. Navigate to IAM → Users → Add users
2. User name: `terraform-deploy-user`
3. Select "Programmatic access"
4. Click "Next: Permissions"

Using AWS CLI:
```bash
aws iam create-user --user-name terraform-deploy-user
```

### Step 2: Create Access Keys

Using AWS Console:
1. Select the user → Security credentials tab
2. Create access key → CLI
3. Save the Access Key ID and Secret Access Key

Using AWS CLI:
```bash
aws iam create-access-key --user-name terraform-deploy-user
```

Save the output - you'll need these credentials.

### Step 3: Attach Deployment Policy

Create a custom policy with the minimum required permissions:

#### Create Policy File

Save the following as `terraform-deploy-policy.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "LambdaManagement",
      "Effect": "Allow",
      "Action": [
        "lambda:CreateFunction",
        "lambda:DeleteFunction",
        "lambda:GetFunction",
        "lambda:GetFunctionConfiguration",
        "lambda:UpdateFunctionCode",
        "lambda:UpdateFunctionConfiguration",
        "lambda:ListFunctions",
        "lambda:ListVersionsByFunction",
        "lambda:PublishVersion",
        "lambda:CreateAlias",
        "lambda:DeleteAlias",
        "lambda:GetAlias",
        "lambda:UpdateAlias",
        "lambda:AddPermission",
        "lambda:RemovePermission",
        "lambda:GetPolicy",
        "lambda:PublishLayerVersion",
        "lambda:DeleteLayerVersion",
        "lambda:GetLayerVersion",
        "lambda:ListLayers",
        "lambda:ListLayerVersions"
      ],
      "Resource": "*"
    },
    {
      "Sid": "APIGatewayManagement",
      "Effect": "Allow",
      "Action": [
        "apigateway:GET",
        "apigateway:POST",
        "apigateway:PUT",
        "apigateway:DELETE",
        "apigateway:PATCH",
        "apigateway:UpdateRestApiPolicy"
      ],
      "Resource": "*"
    },
    {
      "Sid": "DynamoDBManagement",
      "Effect": "Allow",
      "Action": [
        "dynamodb:CreateTable",
        "dynamodb:DeleteTable",
        "dynamodb:DescribeTable",
        "dynamodb:UpdateTable",
        "dynamodb:ListTables",
        "dynamodb:TagResource",
        "dynamodb:UntagResource",
        "dynamodb:DescribeTimeToLive",
        "dynamodb:UpdateTimeToLive",
        "dynamodb:DescribeContinuousBackups",
        "dynamodb:UpdateContinuousBackups"
      ],
      "Resource": "*"
    },
    {
      "Sid": "S3Management",
      "Effect": "Allow",
      "Action": [
        "s3:CreateBucket",
        "s3:DeleteBucket",
        "s3:ListBucket",
        "s3:GetBucketLocation",
        "s3:GetBucketPolicy",
        "s3:PutBucketPolicy",
        "s3:DeleteBucketPolicy",
        "s3:GetBucketAcl",
        "s3:PutBucketAcl",
        "s3:GetBucketCORS",
        "s3:PutBucketCORS",
        "s3:GetBucketWebsite",
        "s3:PutBucketWebsite",
        "s3:DeleteBucketWebsite",
        "s3:GetBucketVersioning",
        "s3:PutBucketVersioning",
        "s3:GetBucketPublicAccessBlock",
        "s3:PutBucketPublicAccessBlock",
        "s3:GetBucketTagging",
        "s3:PutBucketTagging",
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListAllMyBuckets"
      ],
      "Resource": "*"
    },
    {
      "Sid": "CloudFrontManagement",
      "Effect": "Allow",
      "Action": [
        "cloudfront:CreateDistribution",
        "cloudfront:DeleteDistribution",
        "cloudfront:GetDistribution",
        "cloudfront:GetDistributionConfig",
        "cloudfront:UpdateDistribution",
        "cloudfront:ListDistributions",
        "cloudfront:TagResource",
        "cloudfront:UntagResource",
        "cloudfront:CreateInvalidation",
        "cloudfront:GetInvalidation",
        "cloudfront:ListInvalidations",
        "cloudfront:CreateOriginAccessControl",
        "cloudfront:DeleteOriginAccessControl",
        "cloudfront:GetOriginAccessControl",
        "cloudfront:UpdateOriginAccessControl"
      ],
      "Resource": "*"
    },
    {
      "Sid": "IAMManagement",
      "Effect": "Allow",
      "Action": [
        "iam:CreateRole",
        "iam:DeleteRole",
        "iam:GetRole",
        "iam:UpdateRole",
        "iam:ListRoles",
        "iam:PassRole",
        "iam:AttachRolePolicy",
        "iam:DetachRolePolicy",
        "iam:PutRolePolicy",
        "iam:DeleteRolePolicy",
        "iam:GetRolePolicy",
        "iam:ListRolePolicies",
        "iam:ListAttachedRolePolicies",
        "iam:CreatePolicy",
        "iam:DeletePolicy",
        "iam:GetPolicy",
        "iam:GetPolicyVersion",
        "iam:ListPolicies",
        "iam:ListPolicyVersions",
        "iam:TagRole",
        "iam:UntagRole",
        "iam:TagPolicy",
        "iam:UntagPolicy"
      ],
      "Resource": "*"
    },
    {
      "Sid": "CloudWatchLogsManagement",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:DeleteLogGroup",
        "logs:DescribeLogGroups",
        "logs:PutRetentionPolicy",
        "logs:DeleteRetentionPolicy",
        "logs:TagLogGroup",
        "logs:UntagLogGroup",
        "logs:ListTagsLogGroup"
      ],
      "Resource": "*"
    },
    {
      "Sid": "TerraformStateManagement",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::terraform-state-*/*"
    },
    {
      "Sid": "EC2NetworkingForLambda",
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeSecurityGroups",
        "ec2:DescribeSubnets",
        "ec2:DescribeVpcs"
      ],
      "Resource": "*"
    }
  ]
}
```

#### Apply the Policy

Using AWS Console:
1. IAM → Policies → Create policy
2. JSON tab → Paste the policy above
3. Name: `TerraformDeploymentPolicy`
4. Create policy
5. IAM → Users → terraform-deploy-user
6. Add permissions → Attach policies directly
7. Select `TerraformDeploymentPolicy`

Using AWS CLI:
```bash
# Create the policy
aws iam create-policy \
    --policy-name TerraformDeploymentPolicy \
    --policy-document file://terraform-deploy-policy.json

# Get the policy ARN from the output, then attach it
aws iam attach-user-policy \
    --user-name terraform-deploy-user \
    --policy-arn arn:aws:iam::<your-account-id>:policy/TerraformDeploymentPolicy
```

### Step 4: Configure AWS CLI

```bash
aws configure --profile terraform-deploy
```

Enter the Access Key ID and Secret Access Key from Step 2.

### Step 5: Test Permissions

```bash
# Test basic access
aws sts get-caller-identity --profile terraform-deploy

# Test Lambda permissions
aws lambda list-functions --profile terraform-deploy

# Test S3 permissions
aws s3 ls --profile terraform-deploy
```

## Lambda Execution Roles (Created by Terraform)

The Terraform configuration creates three Lambda execution roles with least-privilege permissions:

### 1. Generate Diagram Lambda Role

Permissions:
- **DynamoDB**: PutItem, GetItem on chat_history table
- **S3**: PutObject, GetObject on diagrams/* prefix
- **CloudWatch Logs**: CreateLogGroup, CreateLogStream, PutLogEvents

### 2. Chat CRUD Lambda Role

Permissions:
- **DynamoDB**: PutItem, GetItem, UpdateItem, DeleteItem on chat_history table
- **CloudWatch Logs**: CreateLogGroup, CreateLogStream, PutLogEvents

### 3. Get History Lambda Role

Permissions:
- **DynamoDB**: Query, Scan on chat_history table
- **CloudWatch Logs**: CreateLogGroup, CreateLogStream, PutLogEvents

## Security Best Practices

### 1. Use Separate Accounts for Environments

For production deployments:
- Development account: For testing and development
- Staging account: For pre-production testing
- Production account: For live application

### 2. Enable MFA for Deployment User

```bash
aws iam enable-mfa-device \
    --user-name terraform-deploy-user \
    --serial-number arn:aws:iam::<account-id>:mfa/terraform-deploy-user \
    --authentication-code1 <code1> \
    --authentication-code2 <code2>
```

### 3. Rotate Access Keys Regularly

```bash
# Create new access key
aws iam create-access-key --user-name terraform-deploy-user

# Update AWS CLI configuration with new keys
aws configure --profile terraform-deploy

# Delete old access key
aws iam delete-access-key \
    --user-name terraform-deploy-user \
    --access-key-id <old-access-key-id>
```

### 4. Use AWS Organizations and SCPs

For enterprise deployments, use AWS Organizations with Service Control Policies (SCPs) to enforce security boundaries.

### 5. Enable CloudTrail

Monitor all API calls:
```bash
aws cloudtrail create-trail \
    --name architecture-ai-assistant-trail \
    --s3-bucket-name <your-cloudtrail-bucket>

aws cloudtrail start-logging --name architecture-ai-assistant-trail
```

## Troubleshooting

### Permission Denied Errors

If you encounter permission errors during deployment:

1. **Check current identity:**
   ```bash
   aws sts get-caller-identity
   ```

2. **List attached policies:**
   ```bash
   aws iam list-attached-user-policies --user-name terraform-deploy-user
   ```

3. **Test specific permissions:**
   ```bash
   # Test Lambda
   aws lambda list-functions
   
   # Test S3
   aws s3 ls
   
   # Test DynamoDB
   aws dynamodb list-tables
   ```

4. **Review CloudTrail logs** for denied API calls

### Common Issues

**Error: "User is not authorized to perform: iam:PassRole"**
- Solution: Add `iam:PassRole` permission to the deployment policy

**Error: "Access Denied" when creating CloudFront distribution**
- Solution: Ensure CloudFront permissions are included in the policy

**Error: "Cannot create Lambda function in VPC"**
- Solution: Add EC2 networking permissions for VPC-enabled Lambdas

## Minimal Policy for Testing

For quick testing (not recommended for production):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lambda:*",
        "apigateway:*",
        "dynamodb:*",
        "s3:*",
        "cloudfront:*",
        "iam:*",
        "logs:*"
      ],
      "Resource": "*"
    }
  ]
}
```

**Warning**: This policy grants broad permissions and should only be used for testing in isolated accounts.

## Additional Resources

- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [Terraform AWS Provider Authentication](https://registry.terraform.io/providers/hashicorp/aws/latest/docs#authentication-and-configuration)
- [AWS Lambda Execution Role](https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html)
- [Least Privilege Principle](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html#grant-least-privilege)

## Support

For issues with IAM setup:
1. Review CloudTrail logs for denied API calls
2. Check AWS IAM Policy Simulator
3. Consult AWS Support or documentation
