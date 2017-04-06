import boto3

default_config = {
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
    return dict((k, v) for k, v in config.iteritems() if v != None)

def get_list_config(data):
    return {
        'Quantity': len(data),
        'Items': data,
    }

def map_bucket_to_s3_target(bucket_name):
    return {
        'DomainName': '%s.s3.amazonaws.com' % (bucket_name),
        'Id': 'S3-%s' % (bucket_name),
    }

def map_s3_target_to_origin(s3_target):
    return {
        'DomainName': s3_target['DomainName'],
        'Id': s3_target['Id'],
    	'S3OriginConfig': {
    		'OriginAccessIdentity': '',
    	},
    	'OriginPath': '',
    	'CustomHeaders': {
    		'Quantity': 0,
    	},
    }

def map_origin_to_bucket_name(origin):
    if origin['Id'].startswith('S3-'):
        return origin['Id'][3:]
    raise Exception('Origin is not S3!')

def normalize_config(desired_config):
    normalized_config = default_config.copy()
    normalized_config.update(desired_config)
    return normalized_config

def get_aws_config(desired_config):
    distro_config = normalize_config(desired_config)
    buckets = map(map_bucket_to_s3_target, distro_config.get('s3_buckets'))
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
    config = default_config.copy()
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

class CloudFront:
    def __init__(self, module):
        self.module = module
        if not HAS_BOTO3:
            self.module.fail_json(msg="boto3 is required for this module")
        self.client = boto3.client('cloudfront')

  @staticmethod
  def define_module_argument_spec():
    """
    Defines the module's argument spec
    :return: Dictionary defining module arguments
    """
    return dict(
        name=dict(required=True, aliases=['stage_name']),
        cache_forward_cookies_mode=dict(required=False),
        cache_forward_querystring=dict(required=False),
        cache_trusted_signers=dict(required=False),
        certificate_arn=dict(required=False),
        certificate_iam=dict(required=False),
        certificate_source=dict(required=False),
        enabled=dict(required=False),
        http_version=dict(required=False),
        https_behavior=dict(required=False),
        ipv6=dict(required=False),
        price_class=dict(
            required=False,
            choices=[
                'PriceClass_100',
                'PriceClass_All',
            ]),
        root_object=dict(required=False),
    )

    def find_distro(self, name):
        list = self.get_all_distros()
        distro = None
        for item in list:
            if item.get('Comment', None) == name:
                distro = item
                break

        if distro:
            config = self.get_distro_config(item.get('Id'))
            config['Id'] = distro['Id']
            config['DomainName'] = distro['DomainName']
            return config
        return distro

    def get_distro_config(self, id):
        return self.client.get_distribution_config(Id=id)

    def get_all_distros(self):
        distro_list = self.client.list_distributions()
        return distro_list['DistributionList']['Items']

    def did_distro_change(self, distribution_config, user_config):
        return (
            dict(read_aws_config(distribution_config)) !=
            dict(normalize_config(user_config))
        )

    def create_distro(self, distro_config):
        next_config = get_aws_config(distro_config)
        next_config['CallerReference'] = distro_config['name']
        self.client.create_distribution(DistributionConfig=next_config)

    def update_distro(self, distro, distro_config):
        next_config = get_aws_config(distro_config)
        next_config['CallerReference'] = distro['DistributionConfig']['CallerReference']
        self.client.update_distribution(
            DistributionConfig=next_config,
            Id=distro['Id'],
            IfMatch=distro['ETag'],
        )

    def ensure_distro_existence(self, distro_config):
        distro = self.find_distro(distro_config.get('name'))
        if not distro:
            self.create_distro(distro_config)
            return 1
        if self.did_distro_change(distro['DistributionConfig'], distro_config):
            self.update_distro(distro, distro_config)
            return 2
        return 0

    def process_request(self):
        params = self.module.params
        distro = None
        result = None

        if not self.module.check_mode:
            result = self.ensure_distro_existence(self.module.params)

        self.module.exit_json(changed=result > 0, distro=distro)


def main():
    module = AnsibleModule(
        argument_spec=CloudFront.define_module_argument_spec(),
        supports_check_mode=True
    )
    deployment = AnsibleModule(module)
    deployment.process_request()

from ansible.module_utils.basic import *  # pylint: disable=W0614
if __name__ == '__main__':
    main()
