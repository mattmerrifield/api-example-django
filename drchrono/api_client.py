import requests
from social.apps.django_app.default.models import UserSocialAuth


class APIException(Exception): pass


class Forbidden(APIException): pass


class NotFound(APIException): pass


class Conflict(APIException): pass


ERROR_CODES = {
    403: Forbidden,
    404: NotFound,
    409: Conflict,
}


class BaseChronoResource(object):
    """
    A python wrapper for the basic rules of the drchrono API.

    Provides consistent, pythonic usage and return values from the API,

    Abstracts away:
     - base URL,
     - details of authentication

    All responses will be JSON content. Generally input may use the application/json, application/x-www-form-urlencoded
    or form/multipart content types

    Requests should make sure not to send Accept: test/html in the header, as the API only supports JSON responses.

    Subclasses should implement a specific endpoint, abstracting away unpleasant details of REST communication (like
    naming and iterating over resources that allow it)
    """
    BASE_URL = 'https://drchrono.com/api/'
    endpoint = None

    def __init__(self):
        """
        Creates an API client which will act on behalf of a specific user
        """
        self.oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
        self.access_token = self.oauth_provider.extra_data['access_token']

    def _url(self, id=""):
        if id:
            id = "/{}".format(id)
        return "{}{}".format(self.BASE_URL, self.endpoint, id)

    def _auth_headers(self, kwargs):
        """
        Adds auth information to the kwargs['header'], as expected by get/put/post/delete

        Modifies kwargs in place. Returns None.
        """
        kwargs['headers'] = kwargs.get('headers', {})
        kwargs['headers'].update({
            'Authorization': 'Bearer {}'.format(self.access_token),

        })

    def _content_or_exception(self, response):
        if response.ok:
            return response.content
        else:
            exe = ERROR_CODES.get(response.status_code, APIException)
            raise exe(response.content)

    def _request(self, method, *args, **kwargs):
        # dirty, universal way to use the requests library directly for debugging
        url = self._url(kwargs.pop(id, ''))
        self._auth_headers(kwargs)
        return getattr(requests, method)(url, *args, **kwargs)

    def list(self, params=None, **kwargs):
        """
        Returns an iterator to retrieve all objects at the specified resource. Waits to exhaust the current page before
        retrieving the next, which might result in choppy responses.
        """
        url = self._url()
        self._auth_headers(kwargs)
        # Response will be one page out of a paginated results list
        response = requests.get(url, params=params, **kwargs)
        if response.ok:
            while url:
                data = response.json()
                url = data['next']  # Same as the resource URL, but with the page query parameter present
                for result in data['results']:
                    yield result
        else:
            exe = ERROR_CODES.get(response.status_code, APIException)
            raise exe(response.content)


    def get(self, id, params=None, **kwargs):
        """
        Retrieve a specific object by ID
        """
        url = self._url(id)
        self._auth_headers(kwargs)
        response = requests.get(url, params=params, **kwargs)
        return self._content_or_exception(response)

    def create(self, data=None, json=None, **kwargs):
        """
        Used to create an object at a resource with the included values.

        Response body will be the requested object, with the ID it was assigned.

        Success: 201 (Created)
        Failure:
           - 400 (Bad Request)
           - 403 (Forbidden)
           - 409 (Conflict)
        """
        url = self._url(id)
        self._auth_headers(kwargs)
        response = requests.post(url, data=data, json=json, **kwargs)
        return self._content_or_exception(response)

    def update(self, id, data, partial=False, **kwargs):
        """
        Updates an object. Returns None.

        When partial=False, uses PUT to update the entire object at the given ID with the given values.

        When partial=TRUE [the default] uses PATCH to update only the given fields on the object.

        Response body will be empty.

        Success: 204 (No Content)
        Failure:
           - 400 (Bad Request)
           - 403 (Forbidden)
           - 409 (Conflict)
        """
        url = self._url(id)
        self._auth_headers(kwargs)
        if partial:
            response = requests.patch(url, data, **kwargs)
        else:
            response = requests.put(url, data, **kwargs)
        return self._content_or_exception(response)

    def delete(self, id, **kwargs):
        """
        Deletes the object at this resource with the given ID.

        Response body will be empty.

        Success: 204 (No Content)
        Failure:
           - 400 (Bad Request)
           - 403 (Forbidden)
        """
        url = self._url(id)
        self._auth_headers(kwargs)
        response = requests.delete(url)
        return self._content_or_exception(response)


class PatientResource(BaseChronoResource):
    endpoint = "patients"


class AppointmentResource(BaseChronoResource):
    endpoint = "appointments"

    # Special parameter requirements for a given resource should be explicity called out
    def list(self, params=None, date=None, start=None, end=None, **kwargs):
        """
        List appointments on a given date, or between two dates
        """
        params = params or {}
        if start and end:
            date_range = "{}/{}".format(start, end)
            params['date_range'] = date_range
        elif date:
            params['date'] = date
        if 'date' not in params and 'date_range' not in params:
            raise Exception("Must provide either start & end, or date argument")
        return super(AppointmentResource, self).list(params, **kwargs)


class AppointmentProfileResource(BaseChronoResource):
    endpoint = "appointment_profiles"
