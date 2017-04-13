"""Simplify CloudFront managing for static websites"""
import boto3

DEFAULT_CONFIG = {
    'cache_forward_cookies_mode': 'none',
    'cache_forward_querystring': False,
    'cache_trusted_signers': [],
    'certificate_arn': None,
    'certificate_iam': None,
    'certificate_source': '',
    'enabled': True,
    'http_version': 'http2',
    'https_behavior': 'redirect-to-https',
    'ipv6': True,
    'price_class': 'PriceClass_100',
    'root_object': '',
}

def clear_dict(config):
    """Clear dictionary of null values"""
    return dict((k, v) for k, v in config.iteritems() if v != None)

def get_list_config(data):
    """Get typical AWS compatible list structure"""
    return {
        'Quantity': len(data),
        'Items': data,
    }

def map_bucket_to_s3_target(bucket_name, region):
    """Translate S3 bucket name into origin config base"""
    s3_source = '%s.s3-website-%s.amazonaws.com' % (bucket_name, region)
    return {
        'DomainName': s3_source,
        'Id': s3_source,
    }

def map_s3_target_to_origin(s3_target):
    """Translate target into AWS compatible origin config"""
    return {
        'DomainName': s3_target['DomainName'],
        'Id': s3_target['Id'],
        'CustomOriginConfig': {
            'HTTPPort': 80,
            'HTTPSPort': 443,
            'OriginProtocolPolicy': 'http-only',
            'OriginSslProtocols': {
                'Quantity': 3,
                'Items': ['TLSv1', 'TLSv1.1', 'TLSv1.2'],
            },
            'OriginReadTimeout': 30,
            'OriginKeepaliveTimeout': 5,
        },
        'OriginPath': '',
        'CustomHeaders': {
            'Quantity': 0,
        },
    }

def map_origin_to_bucket_name(origin):
    """Translate origin into S3 bucket name"""
    if '.s3-website-' in origin['Id']:
        index = origin['Id'].find('.s3-website-')
        return origin['Id'][:index]
    return origin['Id']

def normalize_config(desired_config):
    """Fill undefined config values with default config"""
    normalized_config = DEFAULT_CONFIG.copy()
    normalized_config.update(desired_config)
    return normalized_config

def get_aws_config(desired_config):
    """Get AWS config from module config"""
    distro_config = normalize_config(desired_config)
    buckets = [
        map_bucket_to_s3_target(bucket, distro_config.get('region'))
        for bucket in distro_config.get('s3_buckets')
    ]
    bucket_source = buckets[0]

    signers = distro_config.get('cache_trusted_signers')
    certificate_source = distro_config.get('certificate_source')
    use_default_certificate = False

    if certificate_source == 'acm':
        certificate = distro_config.get('certificate_arn')
    elif certificate_source == 'iam':
        certificate = distro_config.get('certificate_iam')
    else:
        certificate = None
        certificate_source = ''
        use_default_certificate = True

    config = {
        'CacheBehaviors': {'Quantity': 0},
        'Comment': distro_config.get('name'),
        'CustomErrorResponses': {'Quantity': 0},
        'DefaultCacheBehavior': {
            'AllowedMethods': {
                'Quantity': 2,
                'Items': ['GET', 'HEAD'],
                'CachedMethods': {
                    'Quantity': 2,
                    'Items': ['GET', 'HEAD'],
                },
            },
            'Compress': False,
            'DefaultTTL': 60,
            'ForwardedValues': {
                'Cookies': {'Forward': distro_config.get('cache_forward_cookies_mode')},
                'Headers': {'Quantity': 0},
                'QueryString': distro_config.get('cache_forward_querystring'),
                'QueryStringCacheKeys': {'Quantity': 0},
            },
            'LambdaFunctionAssociations': {
                'Quantity': 0
            },
            'MaxTTL': 3600,
            'MinTTL': 0,
            'SmoothStreaming': False,
            'ViewerProtocolPolicy': distro_config.get('https_behavior'),
            'TargetOriginId': bucket_source['Id'],
            'TrustedSigners': {
                'Enabled': len(signers) > 0,
                'Quantity': len(signers),
                'Items': signers,
            },
        },
        'DefaultRootObject': distro_config.get('root_object'),
        'Enabled': distro_config.get('enabled'),
        'HttpVersion': distro_config.get('http_version'),
        'IsIPV6Enabled': distro_config.get('ipv6'),
        'Logging': {
            'Enabled': False,
            'IncludeCookies': False,
            'Bucket': '',
            'Prefix': '',
        },
        'PriceClass': distro_config.get('price_class', 'PriceClass_100'),
        'Restrictions': {
            'GeoRestriction': {
                'RestrictionType': 'none',
                'Quantity': 0
            }
        },
        'ViewerCertificate': clear_dict({
            'CloudFrontDefaultCertificate': use_default_certificate,
            'Certificate': certificate,
            'IAMCertificateId': distro_config.get('certificate_iam'),
            'ACMCertificateArn': distro_config.get('certificate_arn'),
            'MinimumProtocolVersion': 'TLSv1',
            'SSLSupportMethod': 'sni-only',
            'CertificateSource': certificate_source,
        }),
        'WebACLId': '',
    }

    config['Aliases'] = get_list_config(distro_config.get('domains'))
    config['Origins'] = get_list_config(map(map_s3_target_to_origin, buckets))

    return clear_dict(config)

def read_aws_config(aws_config):
    """Get module config from AWS config"""
    config = DEFAULT_CONFIG.copy()
    domains = aws_config.get('Aliases')
    origins = aws_config.get('Origins')
    default_cache_behavior = aws_config.get('DefaultCacheBehavior')
    viewer_certificate = aws_config.get('ViewerCertificate')

    config['name'] = aws_config.get('Comment')
    config['enabled'] = aws_config.get('Enabled')
    config['http_version'] = aws_config.get('HttpVersion', '').lower()
    config['ipv6'] = aws_config.get('IsIPV6Enabled')
    config['price_class'] = aws_config.get('PriceClass')
    config['root_object'] = aws_config.get('DefaultRootObject')

    if default_cache_behavior:
        config['https_behavior'] = default_cache_behavior.get('ViewerProtocolPolicy')

        forwarded_values = default_cache_behavior.get('ForwardedValues')
        trusted_signers = default_cache_behavior.get('TrustedSigners')

        if forwarded_values:
            config['cache_forward_cookies_mode'] = (
                forwarded_values.get('Cookies').get('Forward')
            )
            config['cache_forward_querystring'] = (
                forwarded_values.get('QueryString')
            )
        if trusted_signers and trusted_signers.get('Items', None):
            config['cache_trusted_signers'] = forwarded_values.get('Items')
    if viewer_certificate:
        config['certificate_arn'] = viewer_certificate.get('ACMCertificateArn')
        config['certificate_iam'] = viewer_certificate.get('IAMCertificateId')
        config['certificate_source'] = viewer_certificate.get('CertificateSource')
    if origins:
        config['s3_buckets'] = map(map_origin_to_bucket_name, origins['Items'])
    if domains:
        config['domains'] = domains['Items']

    return config

class CloudFront(object):
    """Simplified CloudFront client"""
    def __init__(self):
        self.client = boto3.client('cloudfront')

    def find_distro(self, name):
        """Find distribution and fetch its config"""
        distro_list = self.get_all_distros()
        distro = None
        for item in distro_list:
            if item.get('Comment', None) == name:
                distro = item
                break

        if distro:
            config = self.get_distro_config(distro.get('Id'))
            config['Id'] = distro['Id']
            config['DomainName'] = distro['DomainName']
            return config
        return distro

    def get_distro_config(self, distro_id):
        """Load distribution config"""
        return self.client.get_distribution_config(Id=distro_id)

    def get_all_distros(self):
        """Get list of all distributions"""
        distro_list = self.client.list_distributions()
        return distro_list['DistributionList']['Items']

    def create_distro(self, distro_config):
        """Create distribution"""
        next_config = get_aws_config(distro_config)
        next_config['CallerReference'] = distro_config['name']
        self.client.create_distribution(DistributionConfig=next_config)

    def update_distro(self, distro, distro_config):
        """Update distribution config"""
        next_config = get_aws_config(distro_config)
        next_config['CallerReference'] = distro['DistributionConfig']['CallerReference']
        self.client.update_distribution(
            DistributionConfig=next_config,
            Id=distro['Id'],
            IfMatch=distro['ETag'],
        )

    @staticmethod
    def did_distro_change(distribution_config, user_config):
        """Compare distribution config"""
        return (
            dict(read_aws_config(distribution_config)) !=
            dict(normalize_config(user_config))
        )

    def ensure_distro_existence(self, distro_config):
        """Create distro if it does not exist, update its config otherwise"""
        distro = self.find_distro(distro_config.get('name'))
        if not distro:
            self.create_distro(distro_config)
            return 1
        if self.did_distro_change(distro['DistributionConfig'], distro_config):
            self.update_distro(distro, distro_config)
            return 2
        return 3
