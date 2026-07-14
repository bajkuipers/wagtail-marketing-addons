import pytest
from django.test import RequestFactory
from wagtail.models import Page

from tests.factories.accounts import UserFactory
from tests.factories.page import PageFactory
from wagtail_marketing.helpers import PageAdminURLHelper, UserCannotCreatePermissionHelper
from wagtail_marketing.wagtail_hooks import SeoListingAdmin


@pytest.mark.django_db
class TestWagtail7UpgradeCompatibility:
    def setup_method(self):
        self.seo_listing = SeoListingAdmin()
        self.request_factory = RequestFactory()

    def test_permission_helper_disables_copy_for_page_rows(self):
        user = UserFactory()
        page = PageFactory()
        permission_helper = UserCannotCreatePermissionHelper(Page)

        assert permission_helper.user_can_create(user) is False
        assert permission_helper.user_can_copy_obj(user, page) is False

    def test_edit_action_url_still_opens_promote_tab(self):
        url_helper = PageAdminURLHelper(model=Page)
        page = PageFactory()

        url = url_helper.get_action_url("edit", page.pk)

        assert "#tab-promote" in url

    def test_seo_listing_queryset_excludes_root_and_keeps_content_pages(self):
        Page.objects.all().delete()
        root_page = PageFactory(depth=1, path="0001")
        root_page.save()
        content_page = PageFactory(depth=2, path="00010001")

        queryset = self.seo_listing.get_queryset(self.request_factory.get("/cms/"))

        assert root_page not in queryset
        assert content_page in queryset
