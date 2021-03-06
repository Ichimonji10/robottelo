# -*- encoding: utf-8 -*-
"""Test for Roles CLI

@Requirement: Role

@CaseAutomation: Automated

@CaseLevel: Acceptance

@CaseComponent: CLI

@TestType: Functional

@CaseImportance: High

@Upstream: No
"""
from fauxfactory import gen_string
from robottelo.cli.base import CLIReturnCodeError
from robottelo.cli.factory import make_filter, make_role
from robottelo.cli.filter import Filter
from robottelo.cli.role import Role
from robottelo.datafactory import generate_strings_list
from robottelo.decorators import tier1
from robottelo.test import CLITestCase


class RoleTestCase(CLITestCase):
    """Test class for Roles CLI"""

    @tier1
    def test_positive_create_with_name(self):
        """Create new roles with provided name

        @id: 6883177c-6926-428c-92ab-9effbe1372ae

        @Assert: Role is created and has correct name

        @BZ: 1138553
        """
        for name in generate_strings_list(length=10):
            with self.subTest(name):
                role = make_role({'name': name})
                self.assertEqual(role['name'], name)

    @tier1
    def test_positive_create_with_filter(self):
        """Create new role with a filter

        @id: 6c99ee25-4e58-496c-af42-f8ad2da6cf07

        @assert: Role is created and correct filter is assigned
        """
        role = make_role()
        # Pick permissions by its resource type
        permissions = [
            permission['name']
            for permission in Filter.available_permissions(
                {'resource-type': 'Organization'})
            ]
        # Assign filter to created role
        filter_ = make_filter({
            'role-id': role['id'],
            'permissions': permissions,
        })
        self.assertEqual(role['name'], filter_['role'])

    @tier1
    def test_positive_create_with_permission(self):
        """Create new role with a set of permission

        @id: 7cb2b2e2-ad4d-41e9-b6b2-c0366eb09b9a

        @assert: Role is created and has correct set of permissions
        """
        role = make_role()
        # Pick permissions by its resource type
        permissions = [
            permission['name']
            for permission in Filter.available_permissions(
                {'resource-type': 'Organization'})
            ]
        # Assign filter to created role
        make_filter({
            'role-id': role['id'],
            'permissions': permissions,
        })
        self.assertEqual(
            Role.filters({'id': role['id']})[0]['permissions'],
            permissions
        )

    @tier1
    def test_positive_delete_by_id(self):
        """Create a new role and then delete role by its ID

        @id: 351780b4-697c-4f87-b989-dd9a9a2ad012

        @Assert: Role is created and then deleted by its ID
        """
        for name in generate_strings_list(length=10):
            with self.subTest(name):
                role = make_role({'name': name})
                self.assertEqual(role['name'], name)
                Role.delete({'id': role['id']})
                with self.assertRaises(CLIReturnCodeError):
                    Role.info({'id': role['id']})

    @tier1
    def test_positive_update_name(self):
        """Create new role and update its name

        @id: 3ce1b337-fd52-4460-b8a8-df49c94ffed1

        @Assert: Role is created and its name is updated
        """
        role = make_role({'name': gen_string('alpha', 15)})
        for new_name in generate_strings_list(length=10):
            with self.subTest(new_name):
                Role.update({
                    'id': role['id'],
                    'new-name': new_name,
                })
                role = Role.info({'id': role['id']})
                self.assertEqual(role['name'], new_name)
