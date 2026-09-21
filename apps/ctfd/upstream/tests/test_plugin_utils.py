#!/usr/bin/env python
# -*- coding: utf-8 -*-
import zipfile

from CTFd.plugins import bypass_csrf_protection, override_function
from CTFd.utils.exports import export_ctf, import_ctf
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_challenge,
)


def test_bypass_csrf_protection():
    """
    Test that the bypass_csrf_protection decorator functions properly
    """
    app = create_ctfd()

    with app.app_context():
        with app.test_client() as client:
            r = client.post("/login")
            output = r.get_data(as_text=True)
            assert r.status_code == 403

        def bypass_csrf_protection_test_route():
            return "Success", 200

        # Hijack an existing route to avoid any kind of hacks to create a test route
        app.view_functions["auth.login"] = bypass_csrf_protection(
            bypass_csrf_protection_test_route
        )

        with app.test_client() as client:
            r = client.post("/login")
            output = r.get_data(as_text=True)
            assert r.status_code == 200
            assert output == "Success"
    destroy_ctfd(app)


def test_challenges_model_access_plugin_class():
    """
    Test that the Challenges model can access its plugin class
    """
    app = create_ctfd()

    with app.app_context():
        from CTFd.plugins.challenges import get_chal_class

        chal = gen_challenge(app.db)
        assert chal.plugin_class == get_chal_class("standard")
    destroy_ctfd(app)


def test_import_ctf_override():
    """Test that import_ctf can be overridden"""
    app = create_ctfd()
    if not app.config.get("SQLALCHEMY_DATABASE_URI").startswith("sqlite"):
        with app.app_context():

            def override_func(backup, *args, **kwargs):
                return "OVERRIDDEN"

            override_function("import_ctf", override_func)
            result = import_ctf("dummy_backup")
            assert result == "OVERRIDDEN"
            assert app.overridden_functions["import_ctf"] is override_func

            # Test real import_ctf can still be called
            try:
                import_ctf("dummy_backup", ignore_overrides=True)
            except zipfile.BadZipfile:
                # This is expected
                pass

    destroy_ctfd(app)


def test_export_ctf_override():
    """Test that export_ctf can be overridden"""
    app = create_ctfd()
    with app.app_context():

        def override_func():
            return "EXPORT_OVERRIDDEN"

        override_function("export_ctf", override_func)
        result = export_ctf()
        assert result == "EXPORT_OVERRIDDEN"
        assert app.overridden_functions["export_ctf"] is override_func

        # Test real export_ctf can still be called
        result = export_ctf(ignore_overrides=True)
        assert result != "EXPORT_OVERRIDDEN"
        assert hasattr(result, "read")

    destroy_ctfd(app)
