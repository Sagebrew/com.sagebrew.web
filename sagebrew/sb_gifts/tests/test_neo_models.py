from uuid import uuid1
from django.test import TestCase

from sagebrew.sb_missions.neo_models import Mission
from sagebrew.sb_gifts.neo_models import Giftlist, Product


class TestGiftlistNeoModels(TestCase):
    def setUp(self):
        self.giftlist = Giftlist().save()

    def tearDown(self):
        self.giftlist.delete()

    def test_get_product(self):
        product = Product(vendor_id=str(uuid1())).save()
        product.giftlist.connect(self.giftlist)

        res = self.giftlist.get_product(product.vendor_id, product.vendor_name)
        self.assertEqual(res, product)
        product.delete()

    def test_get_products(self):
        product = Product(vendor_id=str(uuid1())).save()
        product.giftlist.connect(self.giftlist)

        res = self.giftlist.get_products()
        self.assertEqual(res, [product])
        product.delete()

    def test_get_product_vendor_ids(self):
        product = Product(vendor_id=str(uuid1())).save()
        product2 = Product(vendor_id=str(uuid1())).save()
        product.giftlist.connect(self.giftlist)
        product2.giftlist.connect(self.giftlist)

        res = self.giftlist.get_product_vendor_ids()

        self.assertIn(product.vendor_id, res)
        self.assertIn(product2.vendor_id, res)
        product.delete()
        product2.delete()

    def test_get_mission(self):
        mission = Mission().save()
        self.giftlist.mission.connect(mission)

        res = self.giftlist.get_mission()
        self.assertEqual(mission, res)


class TestProductNeoModels(TestCase):
    def setUp(self):
        self.giftlist = Giftlist().save()

    def tearDown(self):
        self.giftlist.delete()

    def test_get_giftlist(self):
        product = Product().save()
        product.giftlist.connect(self.giftlist)

        res = product.get_giftlist()
        self.assertEqual(self.giftlist, res)
        product.delete()
