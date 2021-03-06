"""Unit tests for the ``activation_keys`` paths.

@Requirement: Activationkey

@CaseAutomation: Automated

@CaseLevel: Acceptance

@CaseComponent: API

@TestType: Functional

@CaseImportance: High

@Upstream: No
"""
from fauxfactory import gen_integer, gen_string
from nailgun import client, entities
from requests.exceptions import HTTPError
from robottelo.config import settings
from robottelo.datafactory import (
    filtered_datapoint,
    invalid_names_list,
    valid_data_list,
)
from robottelo.decorators import rm_bug_is_open, skip_if_bug_open, tier1, tier2
from robottelo.test import APITestCase
from six.moves import http_client


@filtered_datapoint
def _good_max_hosts():
    """Return a list of valid ``max_hosts`` values."""
    return [gen_integer(*limits) for limits in ((1, 20), (10000, 20000))]


@filtered_datapoint
def _bad_max_hosts():
    """Return a list of invalid ``max_hosts`` values."""
    return [gen_integer(-100, -1), 0, gen_string('alpha')]


class ActivationKeyTestCase(APITestCase):
    """Tests for the ``activation_keys`` path."""

    @tier1
    def test_positive_create_unlimited_hosts(self):
        """Create a plain vanilla activation key.

        @id: 1d73b8cc-a754-4637-8bae-d9d2aaf89003

        @Assert: Check that activation key is created and its "unlimited_hosts"
        attribute defaults to true.
        """
        self.assertTrue(
            entities.ActivationKey().create().unlimited_hosts
        )

    @tier1
    def test_positive_create_limited_hosts(self):
        """Create an activation key with limited hosts.

        @id: 9bbba620-fd98-4139-a44b-af8ce330c7a4

        @Assert: Check that activation key is created and that hosts number
        is limited
        """
        for max_host in _good_max_hosts():
            with self.subTest(max_host):
                act_key = entities.ActivationKey(
                    max_hosts=max_host, unlimited_hosts=False).create()
                self.assertEqual(act_key.max_hosts, max_host)
                self.assertFalse(act_key.unlimited_hosts)

    @tier1
    def test_positive_create_with_name(self):
        """Create an activation key providing the initial name.

        @id: 749e0d28-640e-41e5-89d6-b92411ce73a3

        @Assert: Activation key is created and contains provided name.
        """
        for name in valid_data_list():
            with self.subTest(name):
                act_key = entities.ActivationKey(name=name).create()
                self.assertEqual(name, act_key.name)

    @tier1
    def test_positive_create_with_description(self):
        """Create an activation key and provide a description.

        @id: 64d93726-6f96-4a2e-ab29-eb5bfa2ff8ff

        @Assert: Created entity contains the provided description.
        """
        for desc in valid_data_list():
            with self.subTest(desc):
                act_key = entities.ActivationKey(description=desc).create()
                self.assertEqual(desc, act_key.description)

    @tier1
    def test_negative_create_with_no_host_limit(self):
        """Create activation key without providing limitation for hosts number

        @id: a9e756e1-886d-4f0d-b685-36ce4247517d

        @Assert: Activation key is not created
        """
        with self.assertRaises(HTTPError):
            entities.ActivationKey(unlimited_hosts=False).create()

    @tier1
    def test_negative_create_with_invalid_host_limit(self):
        """Create activation key with invalid limit values for hosts number.

        @id: c018b177-2074-4f1a-a7e0-9f38d6c9a1a6

        @Assert: Activation key is not created
        """
        for max_host in _bad_max_hosts():
            with self.subTest(max_host):
                with self.assertRaises(HTTPError):
                    entities.ActivationKey(
                        max_hosts=max_host, unlimited_hosts=False).create()

    @tier1
    @skip_if_bug_open('bugzilla', 1156555)
    def test_negative_create_with_no_host_limit_set_max(self):
        """Create activation key with unlimited hosts and set max hosts of
        varied values.

        @id: 71b9b000-b978-4a95-b6f8-83c09ed39c01

        @Assert: Activation key is not created
        """
        for max_host in _bad_max_hosts():
            with self.subTest(max_host):
                with self.assertRaises(HTTPError):
                    entities.ActivationKey(
                        max_hosts=max_host, unlimited_hosts=True).create()

    @tier1
    def test_negative_create_with_invalid_name(self):
        """Create activation key providing an invalid name.

        @id: 5f7051be-0320-4d37-9085-6904025ad909

        @Assert: Activation key is not created
        """
        for name in invalid_names_list():
            with self.subTest(name):
                with self.assertRaises(HTTPError):
                    entities.ActivationKey(name=name).create()

    @tier1
    def test_positive_update_limited_host(self):
        """Create activation key then update it to limited hosts.

        @id: 34ca8303-8135-4694-9cf7-b20f8b4b0a1e

        @Assert: Activation key is created, updated to limited host
        """
        # unlimited_hosts defaults to True.
        act_key = entities.ActivationKey().create()
        for max_host in _good_max_hosts():
            want = {'max_hosts': max_host, 'unlimited_hosts': False}
            for key, value in want.items():
                setattr(act_key, key, value)
            with self.subTest(want):
                act_key = act_key.update(want.keys())
                actual = {attr: getattr(act_key, attr) for attr in want.keys()}
                self.assertEqual(want, actual)

    @tier1
    def test_positive_update_name(self):
        """Create activation key providing the initial name, then update
        its name to another valid name.

        @id: f219f2dc-8759-43ab-a277-fbabede6795e

        @Assert: Activation key is created, and its name can be updated.
        """
        act_key = entities.ActivationKey().create()
        for new_name in valid_data_list():
            with self.subTest(new_name):
                updated = entities.ActivationKey(
                    id=act_key.id, name=new_name).update(['name'])
                self.assertEqual(new_name, updated.name)

    @tier1
    def test_negative_update_limit(self):
        """Create activation key then update its limit to invalid value.

        @id: 0f857d2f-81ed-4b8b-b26e-34b4f294edbc

        @Assert:

        1. Activation key is created
        2. Update fails
        3. Record is not changed
        """
        act_key = entities.ActivationKey().create()
        want = {
            'max_hosts': act_key.max_hosts,
            'unlimited_hosts': act_key.unlimited_hosts,
        }
        for max_host in _bad_max_hosts():
            with self.subTest(max_host):
                act_key.max_hosts = max_host
                act_key.unlimited_hosts = False
                with self.assertRaises(HTTPError):
                    act_key.update(want.keys())
                act_key = act_key.read()
                actual = {attr: getattr(act_key, attr) for attr in want.keys()}
                self.assertEqual(want, actual)

    @tier1
    def test_negative_update_name(self):
        """Create activation key then update its name to an invalid name.

        @id: da85a32c-942b-4ab8-a133-36b028208c4d

        @Assert: Activation key is created, and its name is not updated.
        """
        act_key = entities.ActivationKey().create()
        for new_name in invalid_names_list():
            with self.subTest(new_name):
                with self.assertRaises(HTTPError):
                    entities.ActivationKey(
                        id=act_key.id, name=new_name).update(['name'])
                new_key = entities.ActivationKey(id=act_key.id).read()
                self.assertNotEqual(new_key.name, new_name)
                self.assertEqual(new_key.name, act_key.name)

    @tier1
    def test_negative_update_max_hosts(self):
        """Create an activation key with ``max_hosts == 1``, then update that
        field with a string value.

        @id: 3bcff792-105a-4577-b7c2-5b0de4f79c77

        @Assert: The update fails with an HTTP 422 return code.
        """
        act_key = entities.ActivationKey(max_hosts=1).create()
        with self.assertRaises(HTTPError):
            entities.ActivationKey(
                id=act_key.id, max_hosts='foo').update(['max_hosts'])
        self.assertEqual(act_key.read().max_hosts, 1)

    @tier2
    def test_positive_get_releases_status_code(self):
        """Get an activation key's releases. Check response format.

        @id: e1ea4797-8d92-4bec-ae6b-7a26599825ab

        @Assert: HTTP 200 is returned with an ``application/json`` content-type

        @CaseLevel: Integration
        """
        act_key = entities.ActivationKey().create()
        path = act_key.path('releases')
        response = client.get(
            path,
            auth=settings.server.get_credentials(),
            verify=False,
        )
        status_code = http_client.OK
        self.assertEqual(status_code, response.status_code)
        self.assertIn('application/json', response.headers['content-type'])

    @tier2
    def test_positive_get_releases_content(self):
        """Get an activation key's releases. Check response contents.

        @id: 2fec3d71-33e9-40e5-b934-90b03afc26a1

        @Assert: A list of results is returned.

        @CaseLevel: Integration
        """
        act_key = entities.ActivationKey().create()
        response = client.get(
            act_key.path('releases'),
            auth=settings.server.get_credentials(),
            verify=False,
        ).json()
        self.assertIn('results', response.keys())
        self.assertEqual(type(response['results']), list)

    @tier2
    def test_positive_add_host_collections(self):
        """Associate an activation key with several host collections.

        @id: 1538808c-621e-4cf9-9b9b-840c5dd54644

        @Assert:

        1. By default, an activation key is associated with no host
           collections.
        2. After associating an activation key with some set of host
           collections and reading that activation key, the correct host
           collections are listed.

        @CaseLevel: Integration
        """
        org = entities.Organization().create()  # re-use this to speed up test

        # An activation key has no host collections by default.
        act_key = entities.ActivationKey(organization=org).create()
        self.assertEqual(len(act_key.host_collection), 0)

        # Give activation key one host collection.
        act_key.host_collection.append(
            entities.HostCollection(organization=org).create()
        )
        act_key = act_key.update(['host_collection'])
        self.assertEqual(len(act_key.host_collection), 1)

        # Give activation key second host collection.
        act_key.host_collection.append(
            entities.HostCollection(organization=org).create()
        )
        act_key = act_key.update(['host_collection'])
        self.assertEqual(len(act_key.host_collection), 2)

    @tier2
    def test_positive_remove_host_collection(self):
        """Disassociate host collection from the activation key

        @id: 31992ac4-fe55-45bb-bd17-a191928ec2ab

        @Assert:

        1. By default, an activation key is associated with no host
           collections.
        2. Associating host collection with activation key add it to the list.
        3. Disassociating host collection from the activation key actually
           removes it from the list

        @CaseLevel: Integration
        """
        org = entities.Organization().create()

        # An activation key has no host collections by default.
        act_key = entities.ActivationKey(organization=org).create()
        self.assertEqual(len(act_key.host_collection), 0)

        host_collection = entities.HostCollection(organization=org).create()

        # Associate host collection with activation key.
        act_key.add_host_collection(data={
            'host_collection_ids': [host_collection.id],
        })
        self.assertEqual(len(act_key.read().host_collection), 1)

        # Disassociate host collection from the activation key.
        act_key.remove_host_collection(data={
            'host_collection_ids': [host_collection.id],
        })
        self.assertEqual(len(act_key.read().host_collection), 0)

    @tier1
    def test_positive_update_auto_attach(self):
        """Create an activation key, then update the auto_attach
        field with the inverse boolean value.

        @id: ec225dad-2d27-4b37-989d-1ba2c7f74ac4

        @Assert: The value is changed.
        """
        act_key = entities.ActivationKey().create()
        act_key_2 = entities.ActivationKey(
            id=act_key.id,
            auto_attach=(not act_key.auto_attach),
        ).update(['auto_attach'])
        self.assertNotEqual(act_key.auto_attach, act_key_2.auto_attach)

    @tier1
    def test_positive_delete(self):
        """Create activation key and then delete it.

        @id: aa28d8fb-e07d-45fa-b43a-fc90c706d633

        @Assert: Activation key is successfully deleted.
        """
        for name in valid_data_list():
            with self.subTest(name):
                act_key = entities.ActivationKey().create()
                act_key.delete()
                with self.assertRaises(HTTPError):
                    entities.ActivationKey(id=act_key.id).read()


class ActivationKeySearchTestCase(APITestCase):
    """Tests that search for activation keys."""

    @classmethod
    def setUpClass(cls):
        """Create an organization and an activation key belonging to it."""
        super(ActivationKeySearchTestCase, cls).setUpClass()
        cls.org = entities.Organization().create()
        cls.act_key = entities.ActivationKey(organization=cls.org).create()
        if rm_bug_is_open(4638):
            cls.act_key.read()  # Wait for elasticsearch to index new act key.

    @tier1
    def test_positive_search_by_org(self):
        """Search for all activation keys in an organization.

        @id: aedba598-2e47-44a8-826c-4dc304ba00be

        @Assert: Only activation keys in the organization are returned.
        """
        act_keys = entities.ActivationKey(organization=self.org).search()
        self.assertEqual(len(act_keys), 1)
        self.assertEqual(act_keys[0].id, self.act_key.id)
