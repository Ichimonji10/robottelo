"""Unit tests for the ``subscription`` paths.

A full API reference for subscriptions can be found here:
https://<sat6.com>/apidoc/v2/subscriptions.html


@Requirement: Subscription

@CaseAutomation: Automated

@CaseLevel: Acceptance

@CaseComponent: API

@TestType: Functional

@CaseImportance: High

@Upstream: No
"""
from nailgun import entities
from nailgun.entity_mixins import TaskFailedError
from robottelo.api.utils import upload_manifest
from robottelo import manifests
from robottelo.decorators import run_in_one_thread, skip_if_not_set, tier1
from robottelo.test import APITestCase


@run_in_one_thread
class SubscriptionsTestCase(APITestCase):
    """Tests for the ``subscriptions`` path."""

    @skip_if_not_set('fake_manifest')
    @tier1
    def test_positive_create(self):
        """Upload a manifest.

        @id: 6faf9d96-9b45-4bdc-afa9-ec3fbae83d41

        @Assert: Manifest is uploaded successfully
        """
        org = entities.Organization().create()
        with manifests.clone() as manifest:
            upload_manifest(org.id, manifest.content)

    @skip_if_not_set('fake_manifest')
    @tier1
    def test_positive_refresh(self):
        """Upload a manifest and refresh it afterwards.

        @id: cd195db6-e81b-42cb-a28d-ec0eb8a53341

        @Assert: Manifest is refreshed successfully
        """
        org = entities.Organization().create()
        sub = entities.Subscription(organization=org)
        with manifests.original_manifest() as manifest:
            upload_manifest(org.id, manifest.content)
        try:
            sub.refresh_manifest(data={'organization_id': org.id})
            self.assertGreater(len(sub.search()), 0)
        finally:
            sub.delete_manifest(data={'organization_id': org.id})

    @skip_if_not_set('fake_manifest')
    @tier1
    def test_positive_delete(self):
        """Delete an Uploaded manifest.

        @id: 4c21c7c9-2b26-4a65-a304-b978d5ba34fc

        @Assert: Manifest is Deleted successfully
        """
        org = entities.Organization().create()
        sub = entities.Subscription(organization=org)
        with manifests.clone() as manifest:
            upload_manifest(org.id, manifest.content)
        self.assertGreater(len(sub.search()), 0)
        sub.delete_manifest(data={'organization_id': org.id})
        self.assertEqual(len(sub.search()), 0)

    @skip_if_not_set('fake_manifest')
    @tier1
    def test_negative_upload(self):
        """Upload the same manifest to two organizations.

        @id: 60ca078d-cfaf-402e-b0db-34d8901449fe

        @Assert: The manifest is not uploaded to the second organization.
        """
        orgs = [entities.Organization().create() for _ in range(2)]
        with manifests.clone() as manifest:
            upload_manifest(orgs[0].id, manifest.content)
            with self.assertRaises(TaskFailedError):
                upload_manifest(orgs[1].id, manifest.content)
        self.assertEqual(
            len(entities.Subscription(organization=orgs[1]).search()), 0)
