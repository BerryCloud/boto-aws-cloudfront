from mock import patch

from boto_aws_cloudfront.cloudfront import CloudFront, get_aws_config, read_aws_config

class TestCloudFront:

    def test_get_config(self):
        assert get_aws_config({
            'domains': ['example.com', 'www.example.com'],
            'name': 'foo',
            's3_buckets': ['name-of-your-s3-bucket'],
        }) == {
            'Aliases': {
                'Quantity': 2,
                'Items': [
                    'example.com',
                    'www.example.com',
                ],
            },
            'CacheBehaviors': {'Quantity': 0},
            'Comment': 'foo',
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
                    'Cookies': {'Forward': 'none'},
                    'Headers': {'Quantity': 0},
                    'QueryString': False,
                    'QueryStringCacheKeys': {'Quantity': 0},
                },
        		'LambdaFunctionAssociations': {
        			'Quantity': 0
        		},
                'MaxTTL': 3600,
                'MinTTL': 0,
                'SmoothStreaming': False,
                'ViewerProtocolPolicy': 'redirect-to-https',
                'TargetOriginId': 'S3-name-of-your-s3-bucket',
                'TrustedSigners': {
                    'Enabled': False,
                    'Quantity': 0,
                    'Items': [],
                },
            },
            'DefaultRootObject': '',
            'Enabled': True,
            'HttpVersion': 'http2',
            'IsIPV6Enabled': True,
            'Logging': {
                'Enabled': False,
                'IncludeCookies': False,
                'Bucket': '',
                'Prefix': '',
            },
            'Origins': {
                'Quantity': 1,
                'Items': [
                    {
                        'DomainName': 'name-of-your-s3-bucket.s3.amazonaws.com',
                        'Id': 'S3-name-of-your-s3-bucket',
            			'S3OriginConfig': {
            				'OriginAccessIdentity': ''
            			},
            			'OriginPath': '',
            			'CustomHeaders': {
            				'Quantity': 0
            			},
                    },
                ]
            },
            'PriceClass': 'PriceClass_100',
            'ViewerCertificate': {
                'CloudFrontDefaultCertificate': True,
                'SSLSupportMethod': 'sni-only',
                'CertificateSource': '',
        		'MinimumProtocolVersion': 'TLSv1',
            },

        	'Restrictions': {
        		'GeoRestriction': {
        			'RestrictionType': 'none',
        			'Quantity': 0
        		}
        	},
            'WebACLId': '',
        }

    def test_read_config(self):
        assert read_aws_config({
            'Aliases': {
                'Quantity': 2,
                'Items': [
                    'example.com',
                    'www.example.com',
                ],
            },
            'CacheBehaviors': {'Quantity': 0},
            'Comment': 'foo',
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
                    'Cookies': {'Forward': 'none'},
                    'Headers': {'Quantity': 0},
                    'QueryString': False,
                    'QueryStringCacheKeys': {'Quantity': 0},
                },
        		'LambdaFunctionAssociations': {
        			'Quantity': 0
        		},
                'MaxTTL': 3600,
                'MinTTL': 0,
                'SmoothStreaming': False,
                'ViewerProtocolPolicy': 'redirect-to-https',
                'TargetOriginId': 'S3-name-of-your-s3-bucket',
                'TrustedSigners': {
                    'Enabled': False,
                    'Quantity': 0,
                    'Items': [],
                },
            },
            'DefaultRootObject': 'index.html',
            'Enabled': True,
            'HttpVersion': 'HTTP2',
            'IsIPV6Enabled': True,
            'Logging': {
                'Enabled': False,
                'IncludeCookies': False,
                'Bucket': '',
                'Prefix': '',
            },
            'Origins': {
                'Quantity': 1,
                'Items': [
                    {
                        'DomainName': 'name-of-your-s3-bucket.s3.amazonaws.com',
                        'Id': 'S3-name-of-your-s3-bucket',
            			'S3OriginConfig': {
            				'OriginAccessIdentity': ''
            			},
            			'OriginPath': '',
            			'CustomHeaders': {
            				'Quantity': 0
            			},
                    },
                ]
            },
            'PriceClass': 'PriceClass_100',
            'ViewerCertificate': {
                'CloudFrontDefaultCertificate': True,
                'SSLSupportMethod': 'sni-only',
                'CertificateSource': '',
        		'MinimumProtocolVersion': 'TLSv1',
            },

        	'Restrictions': {
        		'GeoRestriction': {
        			'RestrictionType': 'none',
        			'Quantity': 0
        		}
        	},
            'WebACLId': '',
        }) == {
            'domains': ['example.com', 'www.example.com'],
            'name': 'foo',
            's3_buckets': ['name-of-your-s3-bucket'],
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
            'root_object': 'index.html',
        }

    @patch.object(CloudFront, 'get_distro_config')
    @patch.object(CloudFront, 'get_all_distros')
    def test_find_distro(self, get_all_distros, get_distro_config):
        get_all_distros.return_value = [
            {
                'Id': 1,
                'Aliases': {
                    'Items': ['foo'],
                },
            },
            {
                'Id': 2,
                'Comment': 'static-cdn',
                'Aliases': {
                    'Items': ['example.com'],
                },
            },
        ]
        get_distro_config.return_value = {
            'Id': 2,
            'Comment': 'static-cdn',
            'Aliases': {
                'Items': ['example.com'],
            },
        }

        assert CloudFront().find_distro('static-cdn') == {
            'Id': 2,
            'Comment': 'static-cdn',
            'Aliases': {
                'Items': ['example.com'],
            },
        }

    @patch.object(CloudFront, 'get_all_distros')
    def test_find_distro_not_found(self, mock_method):
        mock_method.return_value = [
            {
                'Id': 1,
                'Aliases': {
                    'Items': ['foo'],
                },
            },
            {
                'Id': 2,
                'Aliases': {
                    'Items': ['bar'],
                },
            },
        ]
        assert CloudFront().find_distro('static-cdn') == None

    @patch.object(CloudFront, 'find_distro')
    @patch.object(CloudFront, 'did_distro_change')
    def test_ensure_distro_existence_exists_not_changed(
        self,
        did_distro_change,
        find_distro,
    ):
        find_distro.return_value = {
            'DistributionConfig': {
                'Enabled': True,
                'DomainName': 'DomainName',
                'DefaultRootObject': 'DefaultRootObject',
                'IsIPV6Enabled': True,
                'Aliases': {
                    'Items': ['foo'],
                },
            },
        }
        did_distro_change.return_value = False
        assert CloudFront().ensure_distro_existence({'domains': ['foo']}) == 3

        did_distro_change.assert_called_with(
            {
                'Enabled': True,
                'DomainName': 'DomainName',
                'DefaultRootObject': 'DefaultRootObject',
                'IsIPV6Enabled': True,
                'Aliases': {
                    'Items': ['foo'],
                },
            },
            {
                'domains': ['foo'],
            },
        )

    @patch.object(CloudFront, 'find_distro')
    @patch.object(CloudFront, 'create_distro')
    def test_ensure_distro_existence_does_not_exist(
        self,
        create_distro,
        find_distro,
    ):
        find_distro.return_value = None
        assert CloudFront().ensure_distro_existence({'names': ['foo']}) == 1
        create_distro.assert_called_with({'names': ['foo']})

    @patch.object(CloudFront, 'find_distro')
    @patch.object(CloudFront, 'did_distro_change')
    @patch.object(CloudFront, 'update_distro')
    def test_ensure_distro_existence_exists_changed(
        self,
        update_distro,
        did_distro_change,
        find_distro,
    ):
        find_distro.return_value = {
            'DistributionConfig': {
                'Enabled': True,
                'DomainName': 'DomainName',
                'DefaultRootObject': 'DefaultRootObject',
                'IsIPV6Enabled': True,
                'Aliases': {
                    'Items': ['foo'],
                },
            },
        }
        did_distro_change.return_value = True
        update_distro.return_value = True
        assert CloudFront().ensure_distro_existence({
            'domains': ['foo'],
        }) == 2

        update_distro.assert_called_with(
            {
                'DistributionConfig': {
                    'Enabled': True,
                    'DomainName': 'DomainName',
                    'DefaultRootObject': 'DefaultRootObject',
                    'IsIPV6Enabled': True,
                    'Aliases': {
                        'Items': ['foo'],
                    },
                },
            },
            {
                'domains': ['foo'],
            },
        )
