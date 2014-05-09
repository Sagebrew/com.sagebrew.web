from django.contrib.auth.models import User

from .models import Profile
from .forms import ProfileForm

class ProfileUtils(object):
    def __init__(self, user, page_user):
        self.profile_types = self.get_user_types()
        self.current_user = user
        self.page_user = page_user
        self.current_user_profile = self.get_user_profile(self.current_user)
        self.page_user_profile = self.get_user_profile(self.page_user)
        self.current_user_friends = self.current_user_profile.friends
        self.page_user_friends = self.page_user_profile.friends
        self.current_user_info = self.get_current_user_info()
        self.page_user_info = self.get_page_user_info()
    
    def add_profile_specifics(self, return_dict):
        pass
    
    def get_current_user_info(self):
        return_dict = {
            'full_name': self.current_user.get_full_name(),
            'username': self.current_user.username,
            'work_phone': self.current_user_profile.primary_phone,
            'user_type': self.current_user_profile.user_type,
            'friend_requests': self.current_user_friends.pending_received_list.all(),
            'sent_friend_requests': self.current_user_friends.pending_sent_list.all(),
            'friends':  self.current_user_friends.user_list.all(),
            'notifications': self.current_user_profile.notifications.all(),
            'owner': False,
            'friend': False,
        }
        return_dict = self.add_profile_specifics(return_dict)
        
        return return_dict

    def get_page_user_info(self):
        return_dict = {
                    'username':     self.page_user.username,
                    'full_name':    self.page_user.get_full_name(),
                    'work_phone':   self.page_user_profile.primary_phone,
                    'friends':      self.page_user_friends.user_list.all(),
                    'user_type':    self.page_user_profile.user_type,
                    'owner':        False,
                    'friend':       False,
                      }
        return_dict = self.add_profile_specifics(return_dict)
        
        return return_dict

    def get_user_types(self):
        return {'profile': 'PR'}

    def get_settings_form_post(self, post_info):
        return ProfileForm(post_info)

    def get_settings_form(self):
        return ProfileForm()

    def get_user_profile(self, user):
        '''
        Returns a user's profile based on what type of user they are.
        '''
        if(user.get_profile().user_type == self.profile_types['profile']):
            user_profile = Profile.objects.get(user__username=user.username)

        return user_profile

    def page_data(self):
        '''
        page_data(Profile, User) takes a Profile object (Customer, Employee,
        Company), the current signed in user object, and determines what
        permissions the signed in user has on the user's page they are
        attempting to access. It then pulls the necessary information needed
        for the determined permissions and returns them to the calling
        function.
        '''
        if(self.current_user.has_perm('user_profiles.view_own_profile',
                          self.page_user.get_profile())):
            return_dict = self.owner_info()
        elif(self.current_user.has_perm('user_profiles.view_friend_profile',
                            self.page_user.get_profile())):
            return_dict = self.friend_info()
        else:
            return_dict = self.page_info()

        template = 'user_profile.html'
        return {'template': template, 'return_dict': return_dict}

    def add_sublist_friends(self, return_dict):
        return return_dict

    def friend_info(self):
        '''
        friend_info(Profile) the user's profile (Company, Customer, Employee)
        that is associated with the page attempting to be loaded, organizes the
        information from the object into a dictionary and returns it to the
        calling function.
        '''
        return_dict = self.page_user_info
        return_dict['site_title'] = self.page_user.username
        return_dict['friend'] = True

        return return_dict

    def owner_info(self):
        '''
        owner_info(Profile, User) takes the current signed in user
        and their profile (Employee, Company, Customer), organizes the
        information in the two objects into a defined dictionary and returns
        it to the calling function.
        '''
        return_dict = self.current_user_info
        return_dict['site_title'] = self.page_user.username
        return_dict['owner'] = True
        self.add_sublist_friends(return_dict)

        return return_dict

    def page_info(self):
        '''
        page_info(Profile, User) takes a Profile object (Employee, Customer,
        Company), the current signed in user object, and ensures that the user
        associated with the profile is not friends with the currently signed in
        user and then creates a dictionary based on the two objects and returns
        it to the calling function.

        is_friend: A variable that provides an added check ontop of
        view_friend_profile made for companies
        and customers that are friends with the employee but do not gain access
        to friend benefits but do not need to see non-friend data such as the
        "Send Friend request" button. It might be easier to add an additional
        permission later but this works for now.
        '''
        return_dict = self.page_user_info
        friends = self.current_user_friends
        pending_sent = friends.check_sent_pending(self.page_user.username)
        pending_received = friends.check_received_pending(
                                                    self.page_user.username)

        return_dict['pending_sent_request'] = pending_sent
        return_dict['pending_received_request'] = pending_received
        return_dict['is_friend'] = self.current_user_friends.is_friend(
                                                    self.page_user)
        return return_dict

    def get_profile_pic(self):
        '''
        Retrieves the profile picture for the user's page that is currently
        being viewed.
        '''
        #user = get_object_or_404(User, username=self.page_user.username)
        profile_pic = None
        
        return profile_pic


class DebugProfileUtils(object):

    def set_user_profiles(self):
        '''
        Loades sample profiles associated with existing users into db for
        testing.
        '''
        sample_password = 'test'
        user1 = User.objects.get(username="this_test_user")
        user1.set_password(sample_password)
        user1.save()

        return True