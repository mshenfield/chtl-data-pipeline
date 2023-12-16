import json
import logging
import re
import requests

logger = logging.getLogger(__name__)
# Also configure urllib3
urllib3_logger = logging.getLogger('urllib3')

logger.setLevel(logging.DEBUG)
urllib3_logger.setLevel(logging.DEBUG)

class MyTurnBot:
    """A bot that can fetch and update information not available through MyTurn's bulk APIs"""
    def __init__(self, my_turn_subdomain):
        """Iniitalize the bot with a MyTurn subdomain (e.g. "mylibrary" in "mylibrary.myturn.com").
      
        Make sure to call start_session before calling other methods.
        """
        self.my_turn_url = f'https://{my_turn_subdomain}.myturn.com'
        self.session = None

    def _url(self, path):
        """Helper function that constructs a MyTurn URL for the given path, using the instance's MyTurn subdomain.

        The path may or may not contain a leading '/'. For consistency, try to use a leading '/' in the path argument.
        """
        return f'{self.my_turn_url}/{path.removeprefix("/")}'

    def get(self, path, *args, **kwargs):
        """Send a GET request to the instance's MyTurn domain, forwarding args and kwargs to requests.get."""
        return self._request('get', path, *args, **kwargs)

    def post(self, path, *args, **kwargs):
        """Send a POST request to MyTurn, forwarding args and kwargs to requests.post."""
        return self._request('post', path, *args, **kwargs)

    def _request(self, method, path, *args, **kwargs):
        """Send a request using METHOD to the instance's MyTurn domain, forwarding args and kwargs to requests.request.
    
        This convenience function does a number of things, including raising for error statuses, and
        using an underlying session.
        """
        r = self.session.request(method, self._url(path), *args, **kwargs)
        # urllib3 logs the status
        logger.debug(f'Response headers: {r.headers}')
        r.raise_for_status()
        return r

    def start_session(self, username, password):
        """Starts a new session in MyTurn, saving the session token for future requests.
    
        When using MyTurnBot, this should be the first call made.
    
            myturn = MyTurnBot('mars')
            myturn.start_session(os.env['MYTURN_PASSWORD'], os.env['MYTURN_USERNAME'])
        
        An error is thrown if starting the session fails. Sessions last for (TODO: how long?) minutes.

        TODO: Should this automatically handle when sessions expire?
        """
        self.session = requests.Session()
        r = self.session.post(
            self._url('/library/j_spring_security_check'),
            data={'j_username': username, 'j_password': password},
            # Don't follow the login redirect, it's unnecessary since the 302 gives the session cookie
            allow_redirects=False,
            timeout=5,
        )
        r.raise_for_status()
        # Detect authentication failures that redirect to '/library/login/authfail?login_error=1'.
        if 'fail' in r.headers['Location'] or 'error' in r.headers['Location']:
            raise ValueError(f'Error starting session. Bad username ({username}) or password.')
        self.session_id = r.cookies['JSESSIONID']

    def patch_member(self, member_id, patch):
        """Overwrites the member in MyTurn with the attributes in the provided "patch" dictionary.
    
        The patch attributes are currently sourced directly from MyTurn. Allowed attributes are:
    
            "password", "password2", "_disableCartEmail", "firstName", "lastName", "title", "organizationName", "address.street1", "address.street2", "address.city", "address.country" (three letter code), "address.principalSubdivision", "address.postalCode", "address.phone", "address.phone2", "address.notes", "url", "sex", "_dateOfBirth" (YYYY-MM-DD), "dateOfBirth_date" (M/D/YYYY), "dateOfBirth" (accepts the value "struct"), "dateOfBirth_tz", "dateOfBirth_time", "firstName2", "lastName2", "emailAddress2", "title2", "organizationName2", "address2.street1", "address2.street2", "address2.city", "address2.country", "address2.principalSubdivision", "address2.postalCode", "address2.phone", "address2.phone2", "address2.notes", "_dynamicFields.household_type", "_dynamicFields.ethnicity", "dynamicFields.disabled", "dynamicFields.household_size", "membershipId"
    
        All attribute values should be strings. The "2" fields like "address2" are for the secondary user on the account.

        TODO: Add a get_member that uses the CSV report and returns a member suitable for this. Right now callers need to download the user snapshot,
        then use that data to update the user.
        TODO: What will the member look like? For now just pass in required values directly instead of having our own data model.
        """
        logger.info(f'Patching member {member_id} with patch {patch}')
        # Normalize member_id to a string, since MyTurn internally represents it that way
        member_id = str(member_id)

        # Unfortunately this ain't easy. MyTurn does all the right things to make sure your user data is updated safely, but
        # this makes it hard for poor bots like us.
        #

        # Step 1: Use MyTurn's internal user search API to fetch the internal User ID for the given member. The search is an "includes" not an exact
        #   match, so filter down to row with the ID. The internal ID isn't included in any downloadable reports, but is required to visit the edit page.
        r = self.post(
            '/library/rpc/searchUsers',
            data={'membershipId': member_id},
            # Should be quick
            timeout=5,
        )
        search_matches = json.loads(r.text)
        # Filter down to the actual member. There should only be one match.
        # The response looks like: '{"data": [{"id": <internal id>", "membershipId": "<membershipId>", ..}, ...]}'
        member = [m for m in search_matches['data'] if m['membershipId'] == member_id][0]
        internal_id = member['id']
        logger.info(f'Found internal ID {internal_id} for member {member_id}')

        # Step 2: Visit the user details page to grab a synchronization token, which is required for updates.
        r = self.get(f'/library/orgMembership/userDetails?userId={internal_id}')
        # Rather than parse this as HTML, just try to regex out the bit with the SYNCHRONIZER value. The HTML looks
        # like: '<input type="hidden" name="SYNCHRONIZER_TOKEN" value="97d7312b-e6c2-4966-b54b-b3ebb597f336">'
        match = re.search('name="SYNCHRONIZER_TOKEN" value="([\d\w-]+)"', r.text)
        token = match.group(1)
        logger.debug(f'Found SYNCHRONIZER_TOKEN {token}')
      
        patch = dict(patch)
        patch.update({
            'SYNCHRONIZER_TOKEN': token,
            # Must exactly match where the path we got the token from
            'SYNCHRONIZER_URI': '/library/orgMembership/userDetails',
            'userId': str(internal_id),
        })

        # Step 3: Post the actual update with the synchronization token added on.
        r = self.post(
            '/library/orgMembership/saveUser',
            data=patch,
            # The result is a redirect
            allow_redirects=False,
            timeout=10,
        )
        # Successfull saves should redirect to the /library/orgMembership/userDetails
        if 'userDetails' not in r.headers['Location']:
            raise ValueError(f'Invalid response when saving user - unexpected redirect: {r.status} {r.headers} {r.text}')
