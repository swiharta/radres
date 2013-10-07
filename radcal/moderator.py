from moderation import moderation, moderator
from models import ShiftEvent

class MyModerator(moderator.GenericModerator):

    visibility_column = 'visible'
    pending_column = 'pending'
#    visible_until_rejected = True

    def inform_moderator(self, content_object, extra_context=None):
        '''Send notification to moderator'''
        extra_context={'test':'test'}
        super(MyModerator, self).inform_moderator(content_object, extra_context)

    def inform_user(self, content_object, user, extra_context=None):
        '''Send notification to user when object is approved or rejected'''
        extra_context={'test':'test'}
        super(MyModerator, self).inform_user(content_object, user, extra_context)

moderation.register(ShiftEvent, MyModerator)

#moderation.register(ShiftEvent)