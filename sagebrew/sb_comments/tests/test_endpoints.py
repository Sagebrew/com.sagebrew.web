from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase

from plebs.neo_models import Pleb
from sb_posts.neo_models import Post
from sb_comments.neo_models import Comment
from sb_registration.utils import create_user_util_test


class TestCommentsRetrieveUpdateDestroy(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'comment'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"
        self.post = Post(content='test content',
                         owner_username=self.pleb.username).save()
        self.post.owned_by.connect(self.pleb)
        self.comment = Comment(content="test comment",
                               owner_username=self.pleb.username).save()
        self.comment.owned_by.connect(self.pleb)
        self.comment.comment_on.connect(self.post)
        self.post.comments.connect(self.comment)

    def test_unauthorized(self):
        url = reverse('comment-list')
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('comment-list')
        data = {'missing': 'test missing data'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('comment-list')
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('comment-list')
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('comment-list')
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('comment-list')
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_detail_unauthorized(self):
        url = reverse('comment-detail',
                      kwargs={'object_uuid': self.comment.object_uuid})
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_list_render(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-detail',
                      kwargs={"object_uuid": self.post.object_uuid}) + \
            "comments/render/?expedite=true&expand=true&" \
            "html=true&page_size=3"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_render_html_key(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-detail',
                      kwargs={"object_uuid": self.post.object_uuid}) + \
            "comments/render/?expedite=true&" \
            "expand=true&html=true&page_size=3"
        response = self.client.get(url)
        self.assertIn('html', response.data['results'])
        self.assertNotEqual([], response.data['results']['html'])

    def test_list_authenticated(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('comment-list')
        response = self.client.get(url)
        self.assertEqual(response.data['detail'],
                         "We do not allow users to query all the comments on "
                         "the site.")
        self.assertEqual(response.status_code, status.HTTP_501_NOT_IMPLEMENTED)

"""
from base64 import b64encode
from uuid import uuid1
from collections import OrderedDict
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User


from rest_framework import status
from rest_framework.test import APITestCase

from plebs.neo_models import Pleb
from sb_comments.neo_models import Comment


class CommentViewSetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='lauren',
                                             password='secret')
        self.pleb = Pleb(
            email=self.user.email, first_name=user.first_name,
            last_name=user.last_name, username=user.username,
            birthday=birthday)
        self.unit_under_test = Comment.objects.create(content="hello there")
        self.unit_under_test.owned_by.connect(pleb)
        self.unit_under_test.projects.add(self.project)
        self.unit_under_test_name = 'order'
        self.url = "http://testserver"
        self.project_uuids = []
        for project in self.unit_under_test.projects.all():
            self.project_uuids.append(project.uuid)

    def test_unauthorized(self):
        url = reverse('%s-list' % self.unit_under_test_name)
        data = {}
        response = self.client.post(url, data, format='json')
        unauthorized = {
            'detail': 'Authentication credentials were not provided.'
        }
        self.assertEqual(response.data, unauthorized)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-list' % self.unit_under_test_name)
        data = {'projects': ['This field is required.']}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-list' % self.unit_under_test_name)
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code, 400)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-list' % self.unit_under_test_name)
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code, 400)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-list' % self.unit_under_test_name)
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code, 400)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-list' % self.unit_under_test_name)
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code, 400)

    def test_save_image_data(self):
        with open(settings.PROJECT_DIR + "/images/test_image.jpg",
                  "rb") as image_file:
            image = b64encode(image_file.read())
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-list' % self.unit_under_test_name)
        response = self.client.post(url, image, format='json')
        self.assertEqual(response.status_code, 400)

    def test_create(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-list' % self.unit_under_test_name)
        data = {"projects": self.project_uuids}
        response = self.client.post(url, data=data, format='json')
        response_data = {
            'uuid': response.data["uuid"],
            'url': "%s/v1/orders/%s/" % (self.url, response.data["uuid"]),
            'facility': None, 'outsourced_order': False,
            'owner': self.user.pk, 'meta': None, 'address': None,
            'ship_from': None, 'external_orders': [],
            'projects': self.project_uuids
        }
        self.assertEqual(response.data, response_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_on_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-detail' % self.unit_under_test_name,
                                   kwargs={'uuid': self.unit_under_test.uuid})
        data = {"projects": self.project_uuids}
        response = self.client.post(url, data, format='json')
        response_data = {'detail': 'Method "POST" not allowed.'}
        self.assertEqual(response.data, response_data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-detail' % self.unit_under_test_name, kwargs={
            'uuid': self.unit_under_test.uuid})

        data = {'projects': self.project_uuids}
        response = self.client.put(url, data, format='json')
        response_data = {
            'uuid': self.unit_under_test.uuid,
            'url': "%s%s" % (self.url, url),
            'facility': None,
            'outsourced_order': False,
            'owner': self.user.pk,
            'meta': None,
            'address': None,
            'ship_from': None,
            'external_orders': [],
            'projects': self.project_uuids
        }
        self.assertEqual(response.data, response_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_does_not_exist(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={"uuid": str(uuid1())})
        data = {'detail': 'Not found.'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-list' % self.unit_under_test_name)
        data = {'detail': 'Method "PUT" not allowed.'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'uuid': self.unit_under_test.uuid})
        data = None
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-list' % self.unit_under_test_name)
        data = {'detail': 'Method "DELETE" not allowed.'}
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_read(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'uuid': self.unit_under_test.uuid})
        data = {
            'uuid': self.unit_under_test.uuid,
            'url': "%s%s" % (self.url, url),
            'facility': None, 'outsourced_order': False,
            'owner': self.user.pk, 'meta': None, 'address': None,
            'ship_from': None, 'external_orders': [],
            'projects': self.project_uuids
        }
        response = self.client.get(url, format='json')
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_read_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-list' % self.unit_under_test_name)

        response = self.client.get(url, format='json')
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={"uuid": self.unit_under_test})
        data = [
            OrderedDict([('uuid', self.unit_under_test.uuid),
                         ('url', "%s%s" % (self.url, url)),
                         ('meta', None),
                         ('projects', self.project_uuids),
                         ('external_orders', []), ('outsourced_order', False),
                         ('address', None), ('ship_from', None),
                         ('facility', None), ('owner', self.user.pk)])]
        self.assertEqual(response.data['results'], data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class OutsourcedOrderTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='lauren', password='secret')
        self.project = Project.objects.create(owner=self.user)
        self.order = Order.objects.create(owner=self.user)
        self.order.projects.add(self.project)
        self.unit_under_test = OutsourcedOrder.objects.create(
            owner=self.user, project=self.project,
            external_order_id="Z1243-001")
        self.order.external_orders.add(self.unit_under_test)
        self.order.save()
        self.unit_under_test_name = 'outsourcedorder'
        self.url = "http://testserver"
        self.project_url = reverse('project-detail',
                                  kwargs={'uuid': self.project.uuid})

        self.project_uuid = self.project.uuid

    def test_unauthorized(self):
        url = reverse('%s-list' % self.unit_under_test_name)
        data = {}
        response = self.client.post(url, data, format='json')
        unauthorized = {
            'detail': 'Authentication credentials were not provided.'
        }
        self.assertEqual(response.data, unauthorized)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-list' % self.unit_under_test_name)
        data = {'projects': ['This field is required.']}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-list' % self.unit_under_test_name)
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-list' % self.unit_under_test_name)
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-list' % self.unit_under_test_name)
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-list' % self.unit_under_test_name)
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_image_data(self):
        with open(settings.PROJECT_DIR + "/images/test_image.jpg",
                  "rb") as image_file:
            image = b64encode(image_file.read())
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-list' % self.unit_under_test_name)
        response = self.client.post(url, image, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-list' % self.unit_under_test_name)
        data = {"project": self.project_url}
        response = self.client.post(url, data=data, format='json')
        response_data = {'detail': 'Method "POST" not allowed.'}
        self.assertEqual(response.data, response_data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_on_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse(
            '%s-detail' % self.unit_under_test_name,
            kwargs={'external_order_id':
                        self.unit_under_test.external_order_id})
        data = {"projects": self.project_url}
        response = self.client.post(url, data, format='json')
        response_data = {'detail': 'Method "POST" not allowed.'}
        self.assertEqual(response.data, response_data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-detail' % self.unit_under_test_name, kwargs={
            'external_order_id': self.unit_under_test.external_order_id})

        data = {'projects': self.project_url}
        response = self.client.put(url, data, format='json')
        response_data = {'detail': 'Method "PUT" not allowed.'}
        self.assertEqual(response.data, response_data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_does_not_exist(self):
        # No updates are allowed on this object from the REST interface
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={"external_order_id": str(uuid1())})
        data = {'detail': 'Method "PUT" not allowed.'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-list' % self.unit_under_test_name)
        data = {'detail': 'Method "PUT" not allowed.'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'external_order_id':
                                  self.unit_under_test.external_order_id})
        data = {'detail': 'Method "DELETE" not allowed.'}
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-list' % self.unit_under_test_name)
        data = {'detail': 'Method "DELETE" not allowed.'}
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_read(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={'external_order_id':
                                  self.unit_under_test.external_order_id})
        data = {
            'project': self.project_uuid,
            'external_order_id': self.unit_under_test.external_order_id,
            'url': "%s%s" % (self.url, url),
            'tracking_number': None,
            'order_status_internal': None,
            'order_status': None
        }
        response = self.client.get(url, format='json')
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_read_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s-list' % self.unit_under_test_name)
        response = self.client.get(url, format='json')
        url = reverse('%s-detail' % self.unit_under_test_name,
                      kwargs={"external_order_id":
                                  self.unit_under_test.external_order_id})
        data = [OrderedDict([('external_order_id',
                              self.unit_under_test.external_order_id),
                             ('url', "%s%s" % (self.url, url)),
                             ('order_status', None),
                             ('order_status_internal', None),
                             ('tracking_number', None),
                             ('project', self.project_uuid)])]
        self.assertEqual(response.data['results'], data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class OrderRootTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='lauren', password='secret')

    def test_unauthorized(self):
        url = reverse("orders_root")
        response = self.client.get(url, format='json')
        unauthorized = {
            'detail': 'Authentication credentials were not provided.'
        }
        self.assertEqual(response.data, unauthorized)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("orders_root")
        data = {'projects': ['This field is required.']}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_authorized(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("orders_root")
        response = self.client.get(url, format='json')
        authorized = {
            'orders': 'http://testserver/v1/orders/',
            'outsourced_orders': 'http://testserver/v1/outsourced_orders/',
            'submit order': 'http://testserver/v1/orders/'
                            '4c132da0-1e02-11e3-8224-0800200c9a66/submit/'}
        self.assertEqual(response.data, authorized)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SubmitOrderTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='lauren', password='secret')
        self.project = Project.objects.create(owner=self.user)
        self.unit_under_test = Order.objects.create(owner=self.user)
        self.unit_under_test.projects.add(self.project)
        self.ship_from_address = Address.objects.create(
            company="Test Company", first_name="Tester", last_name="Test",
            address="300 Eagle Pond Dr.", address_additional="Apt 137",
            city="Walled Lake", state="MI", zipcode="48390", owner=self.user)
        self.ship_from_uuid = self.ship_from_address.uuid
        self.address = Address.objects.create(
            company="Test Company", first_name="Receiver", last_name="Test",
            address="300 Eagle Pond Dr.", address_additional="Apt 138",
            city="Walled Lake", state="MI", zipcode="48390", owner=self.user)
        self.fac_address = Address.objects.create(
            company="", first_name="", last_name="", city="Dayton",
            zipcode="45424", country="US", state="OH",
            address="7801 Technology Blvd", owner=self.user,
        )
        self.facility = Facility.objects.create(address=self.fac_address,
                                                facility_code="DAY")
        self.address_uuid = self.address.uuid
        self.facility_uuid = self.facility.uuid
        self.unit_under_test_name = 'submit_order'
        self.project_uuids = []
        for project in self.unit_under_test.projects.all():
            self.project_uuids.append(project.uuid)

    def test_unauthorized(self):
        url = reverse('%s' % self.unit_under_test_name,
                      kwargs={'uuid': self.unit_under_test.uuid})
        data = {}
        response = self.client.post(url, data, format='json')
        unauthorized = {
            'detail': 'Authentication credentials were not provided.'
        }
        self.assertEqual(response.data, unauthorized)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s' % self.unit_under_test_name,
                      kwargs={'uuid': self.unit_under_test.uuid})
        data = {'projects': ['This field is required.']}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s' % self.unit_under_test_name,
                      kwargs={'uuid': self.unit_under_test.uuid})
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s' % self.unit_under_test_name,
                      kwargs={'uuid': self.unit_under_test.uuid})
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s' % self.unit_under_test_name,
                      kwargs={'uuid': self.unit_under_test.uuid})
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s' % self.unit_under_test_name,
                      kwargs={'uuid': self.unit_under_test.uuid})
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_save_image_data(self):
        with open(settings.PROJECT_DIR + "/images/test_image.jpg",
                  "rb") as image_file:
            image = b64encode(image_file.read())
        self.client.force_authenticate(user=self.user)
        url = reverse('%s' % self.unit_under_test_name,
                      kwargs={'uuid': self.unit_under_test.uuid})
        response = self.client.post(url, image, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_create(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s' % self.unit_under_test_name,
                      kwargs={'uuid': self.unit_under_test.uuid})
        # TODO will need to update shipping code based on actual value returned
        # from 4Over for the address
        data = {
            "ship_from": self.ship_from_uuid,
            "address": self.address_uuid,
            "facility": self.facility_uuid,
            "shipping_code": "12"
        }
        response = self.client.post(url, data=data, format='json')
        response_data = {"detail": None}
        self.assertEqual(response.data, response_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_does_not_exist(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s' % self.unit_under_test_name,
                      kwargs={'uuid': str(uuid1())})
        # TODO will need to update shipping code based on actual value returned
        # from 4Over for the address
        data = {}
        response = self.client.post(url, data=data, format='json')
        response_data = {'detail': 'Order matching query does not exist.'}
        self.assertEqual(response.data, response_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s' % self.unit_under_test_name, kwargs={
            'uuid': self.unit_under_test.uuid})

        data = {'projects': self.project_uuids}
        response = self.client.put(url, data, format='json')
        response_data = {'detail': 'Method "PUT" not allowed.'}
        self.assertEqual(response.data, response_data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_does_not_exist(self):
        # No updates are allowed on this object from the REST interface
        self.client.force_authenticate(user=self.user)
        url = reverse('%s' % self.unit_under_test_name,
                      kwargs={"uuid": str(uuid1())})
        data = {'detail': 'Method "PUT" not allowed.'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s' % self.unit_under_test_name, kwargs={
            'uuid': self.unit_under_test.uuid})
        data = {'detail': 'Method "PUT" not allowed.'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s' % self.unit_under_test_name,
                      kwargs={'uuid':
                                  self.unit_under_test.uuid})
        data = {'detail': 'Method "DELETE" not allowed.'}
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s' % self.unit_under_test_name,
                      kwargs={'uuid': self.unit_under_test.uuid})
        data = {'detail': 'Method "DELETE" not allowed.'}
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_read(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('%s' % self.unit_under_test_name,
                      kwargs={'uuid':
                                  self.unit_under_test.uuid})
        data = {'detail': 'Method "GET" not allowed.'}
        response = self.client.get(url, format='json')
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
"""
