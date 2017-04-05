[![CircleCI](https://circleci.com/gh/BerryCloud/boto-aws-cloudfront.svg?style=shield)](https://circleci.com/gh/BerryCloud/boto-aws-cloudfront)

# Boto CloudFront wrapper

This [boto3](https://github.com/boto/boto3) wrapper oversimplifies configuration
of AWS CloudFront by providing default values for configuration and flattening
the configuration tree. It is meant to be used by future ansible cloudfront
module.

## Features

* Simplified python interface to create CloudFront Distribution
* Quick way to create CloudFront distribution for your S3 static hosted website
* Only supported origin is S3 bucket at the moment

## Dependencies

* boto3

## Required configuration

### name: string, required

Name your distribution so it can be found later.

`Example: {'name':'assets-cdn'}`

### domains: list[string], required

List CNAME domain names that will be targetting this distribution.

`Example: {'domains':['improliga.cz']}`

### s3_buckets: list[string], required

List of S3 buckets that will be used as origin - data source for this distribution.

`Example: {'s3_buckets':['name-of-your-s3-bucket']}`

## Optional Configuration

### enabled: bool, default: True

Is this distribution enabled?

`Example: {'enabled': False}`

### root_object: string, default: ''

This configuration affects what file will be used as server index. When user
enters your site, he will see this file. You must make sure that the file is
present at origin.

`Example: {'root_object': 'index.html'}`

### certificate_source, enum('default', 'acm', 'iam'), default: ''

Indicates source of your SSL certificate used for this distribution. Value can
be one of:

* **default**: Uses the default CloudFront certificate
* **acm**: Uses certificate provided by `certificate_arn`
* **iam**: Uses certificate provided by `certificate_iam`

### certificate_iam, string, default: None

ID of certificate saved in AWS IAM.

### certificate_arn, string, default: None

ARN of certificate saved in AWS ACM.

### cache_forward_querystring, bool, default: False

Should the distribution forward QueryString?

### cache_forward_cookies_mode, string, default: 'none'

Should the distribution forward cookies? See AWS docs.

### cache_trusted_signers, list(string), default: []

List of trusted signers. See AWS docs.

## Examples

Ensuring that CloudFront distribution exists is relatively easy, same goes for creating and updating.

### Ensure S3 distribution existence

```python
from cloudfront import CloudFront

cl.ensure_distro_existence(
  {
    'domains': ['example.com', 'foo.bar'],
    'name': 'example',
    's3_buckets': ['name-of-your-s3-bucket'],
    'root_object': 'index.html',
  }
)
```
