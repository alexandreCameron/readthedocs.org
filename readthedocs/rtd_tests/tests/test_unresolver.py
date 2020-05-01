from django.test import override_settings
import django_dynamic_fixture as fixture

from readthedocs.rtd_tests.tests.test_resolver import ResolverBase
from readthedocs.core.unresolver import unresolve
from readthedocs.projects.models import Domain


@override_settings(
    PRODUCTION_DOMAIN='readthedocs.org',
    PUBLIC_DOMAIN='readthedocs.io',
    RTD_EXTERNAL_VERSION_DOMAIN='dev.readthedocs.build',
    PUBLIC_DOMAIN_USES_HTTPS=True,
    USE_SUBDOMAIN=True,
)
class UnResolverTests(ResolverBase):

    def test_unresolver(self):
        parts = unresolve('http://pip.readthedocs.io/en/latest/foo.html')
        self.assertEqual(parts[0].slug, 'pip')
        self.assertEqual(parts[1], 'en')
        self.assertEqual(parts[2], 'latest')
        self.assertEqual(parts[3], 'foo.html')

    def test_unresolver_subproject(self):
        parts = unresolve('http://pip.readthedocs.io/projects/sub/ja/latest/foo.html')
        self.assertEqual(parts[0].slug, 'sub')
        self.assertEqual(parts[1], 'ja')
        self.assertEqual(parts[2], 'latest')
        self.assertEqual(parts[3], 'foo.html')

    def test_unresolver_translation(self):
        parts = unresolve('http://pip.readthedocs.io/ja/latest/foo.html')
        self.assertEqual(parts[0].slug, 'trans')
        self.assertEqual(parts[1], 'ja')
        self.assertEqual(parts[2], 'latest')
        self.assertEqual(parts[3], 'foo.html')

    def test_unresolver_domain(self):
        self.domain = fixture.get(
            Domain,
            domain='docs.foobar.com',
            project=self.pip,
            canonical=True,
        )
        parts = unresolve('http://docs.foobar.com/en/latest/')
        self.assertEqual(parts[0].slug, 'pip')
        self.assertEqual(parts[1], 'en')
        self.assertEqual(parts[2], 'latest')
        self.assertEqual(parts[3], '')

    def test_unresolver_single_version(self):
        self.pip.single_version = True
        parts = unresolve('http://pip.readthedocs.io/')
        self.assertEqual(parts[0].slug, 'pip')
        self.assertEqual(parts[1], None)
        self.assertEqual(parts[2], None)
        self.assertEqual(parts[3], '')

    def test_unresolver_subproject_alias(self):
        relation = self.pip.subprojects.first()
        relation.alias = 'sub_alias'
        relation.save()
        parts = unresolve('http://pip.readthedocs.io/projects/sub_alias/ja/latest/')
        self.assertEqual(parts[0].slug, 'sub')
        self.assertEqual(parts[1], 'ja')
        self.assertEqual(parts[2], 'latest')
        self.assertEqual(parts[3], '')

    def test_unresolver_external_version(self):
        ver = self.pip.versions.first()
        ver.type = 'external'
        ver.slug = '10'
        parts = unresolve('http://project--10.dev.readthedocs.build/en/10/')
        self.assertEqual(parts[0].slug, 'pip')
        self.assertEqual(parts[1], 'en')
        self.assertEqual(parts[2], '10')
        self.assertEqual(parts[3], '')
