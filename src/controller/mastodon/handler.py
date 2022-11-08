# -*- coding: utf-8 -*-
import logging
from pubsub import pub
from sessions.twitter import utils

log = logging.getLogger("controller.mastodon.handler")

class Handler(object):

    def __init__(self):
        super(Handler, self).__init__()

    def create_buffers(self, session, createAccounts=True, controller=None):
        session.get_user_info()
        if createAccounts == True:
            pub.sendMessage("core.create_account", name=session.db["user_name"], session_id=session.session_id)
        root_position =controller.view.search(session.db["user_name"], session.db["user_name"])
        for i in session.settings['general']['buffer_order']:
            if i == 'home':
                pub.sendMessage("createBuffer", buffer_type="BaseBuffer", session_type=session.type, buffer_title=_("Home"), parent_tab=root_position, start=False, kwargs=dict(parent=controller.view.nb, function="timeline_home", name="home_timeline", sessionObject=session, account=session.db["user_name"], sound="tweet_received.ogg"))
            elif i == 'local':
                pub.sendMessage("createBuffer", buffer_type="BaseBuffer", session_type=session.type, buffer_title=_("Local"), parent_tab=root_position, start=False, kwargs=dict(parent=controller.view.nb, function="timeline_local", name="local_timeline", sessionObject=session, account=session.db["user_name"], sound="tweet_received.ogg"))
            elif i == 'federated':
                pub.sendMessage("createBuffer", buffer_type="BaseBuffer", session_type=session.type, buffer_title=_("Federated"), parent_tab=root_position, start=False, kwargs=dict(parent=controller.view.nb, function="timeline_public", name="federated_timeline", sessionObject=session, account=session.db["user_name"], sound="tweet_received.ogg"))
#            elif i == 'mentions':
#                pub.sendMessage("createBuffer", buffer_type="BaseBuffer", session_type=session.type, buffer_title=_("Mentions"), parent_tab=root_position, start=False, kwargs=dict(parent=controller.view.nb, function="mentions_timeline", name="mentions", sessionObject=session, account=session.db["user_name"], sound="mention_received.ogg", include_ext_alt_text=True, tweet_mode="extended"))
#            elif i == 'dm':
#                pub.sendMessage("createBuffer", buffer_type="DirectMessagesBuffer", session_type=session.type, buffer_title=_("Direct messages"), parent_tab=root_position, start=False, kwargs=dict(parent=controller.view.nb, function="get_direct_messages", name="direct_messages", sessionObject=session, account=session.db["user_name"], bufferType="dmPanel", compose_func="compose_direct_message", sound="dm_received.ogg"))
#            elif i == 'sent_dm':
#                pub.sendMessage("createBuffer", buffer_type="SentDirectMessagesBuffer", session_type=session.type, buffer_title=_("Sent direct messages"), parent_tab=root_position, start=False, kwargs=dict(parent=controller.view.nb, function=None, name="sent_direct_messages", sessionObject=session, account=session.db["user_name"], bufferType="dmPanel", compose_func="compose_direct_message"))
#            elif i == 'sent_tweets':
#                pub.sendMessage("createBuffer", buffer_type="BaseBuffer", session_type=session.type, buffer_title=_("Sent tweets"), parent_tab=root_position, start=False, kwargs=dict(parent=controller.view.nb, function="user_timeline", name="sent_tweets", sessionObject=session, account=session.db["user_name"], screen_name=session.db["user_name"], include_ext_alt_text=True, tweet_mode="extended"))
#            elif i == 'favorites':
#                pub.sendMessage("createBuffer", buffer_type="BaseBuffer", session_type=session.type, buffer_title=_("Likes"), parent_tab=root_position, start=False, kwargs=dict(parent=controller.view.nb, function="get_favorites", name="favourites", sessionObject=session, account=session.db["user_name"], sound="favourite.ogg", include_ext_alt_text=True, tweet_mode="extended"))
#            elif i == 'followers':
#                pub.sendMessage("createBuffer", buffer_type="PeopleBuffer", session_type=session.type, buffer_title=_("Followers"), parent_tab=root_position, start=False, kwargs=dict(parent=controller.view.nb, function="get_followers", name="followers", sessionObject=session, account=session.db["user_name"], sound="update_followers.ogg", screen_name=session.db["user_name"]))
#            elif i == 'friends':
#                pub.sendMessage("createBuffer", buffer_type="PeopleBuffer", session_type=session.type, buffer_title=_("Following"), parent_tab=root_position, start=False, kwargs=dict(parent=controller.view.nb, function="get_friends", name="friends", sessionObject=session, account=session.db["user_name"], screen_name=session.db["user_name"]))
#            elif i == 'blocks':
#                pub.sendMessage("createBuffer", buffer_type="PeopleBuffer", session_type=session.type, buffer_title=_("Blocked users"), parent_tab=root_position, start=False, kwargs=dict(parent=controller.view.nb, function="get_blocks", name="blocked", sessionObject=session, account=session.db["user_name"]))
#            elif i == 'muted':
#                pub.sendMessage("createBuffer", buffer_type="PeopleBuffer", session_type=session.type, buffer_title=_("Muted users"), parent_tab=root_position, start=False, kwargs=dict(parent=controller.view.nb, function="get_mutes", name="muted", sessionObject=session, account=session.db["user_name"]))
#        pub.sendMessage("createBuffer", buffer_type="EmptyBuffer", session_type="base", buffer_title=_("Timelines"), parent_tab=root_position, start=False, kwargs=dict(parent=controller.view.nb, name="timelines", account=session.db["user_name"]))
#        timelines_position =controller.view.search("timelines", session.db["user_name"])
#        for i in session.settings["other_buffers"]["timelines"]:
#            pub.sendMessage("createBuffer", buffer_type="BaseBuffer", session_type=session.type, buffer_title=_(u"Timeline for {}").format(i,), parent_tab=timelines_position, start=False, kwargs=dict(parent=controller.view.nb, function="user_timeline", name="%s-timeline" % (i,), sessionObject=session, account=session.db["user_name"], sound="tweet_timeline.ogg", bufferType=None, user_id=i, include_ext_alt_text=True, tweet_mode="extended"))
#        pub.sendMessage("createBuffer", buffer_type="EmptyBuffer", session_type="base", buffer_title=_("Likes timelines"), parent_tab=root_position, start=False, kwargs=dict(parent=controller.view.nb, name="favs_timelines", account=session.db["user_name"]))
#        favs_timelines_position =controller.view.search("favs_timelines", session.db["user_name"])
#        for i in session.settings["other_buffers"]["favourites_timelines"]:
#            pub.sendMessage("createBuffer", buffer_type="BaseBuffer", session_type=session.type, buffer_title=_("Likes for {}").format(i,), parent_tab=favs_timelines_position, start=False, kwargs=dict(parent=controller.view.nb, function="get_favorites", name="%s-favorite" % (i,), sessionObject=session, account=session.db["user_name"], bufferType=None, sound="favourites_timeline_updated.ogg", user_id=i, include_ext_alt_text=True, tweet_mode="extended"))
#        pub.sendMessage("createBuffer", buffer_type="EmptyBuffer", session_type="base", buffer_title=_("Followers timelines"), parent_tab=root_position, start=False, kwargs=dict(parent=controller.view.nb, name="followers_timelines", account=session.db["user_name"]))
#        followers_timelines_position =controller.view.search("followers_timelines", session.db["user_name"])
#        for i in session.settings["other_buffers"]["followers_timelines"]:
#            pub.sendMessage("createBuffer", buffer_type="PeopleBuffer", session_type=session.type, buffer_title=_("Followers for {}").format(i,), parent_tab=followers_timelines_position, start=False, kwargs=dict(parent=controller.view.nb, function="get_followers", name="%s-followers" % (i,), sessionObject=session, account=session.db["user_name"], sound="new_event.ogg", user_id=i))
#        pub.sendMessage("createBuffer", buffer_type="EmptyBuffer", session_type="base", buffer_title=_("Following timelines"), parent_tab=root_position, start=False, kwargs=dict(parent=controller.view.nb, name="friends_timelines", account=session.db["user_name"]))
#        friends_timelines_position =controller.view.search("friends_timelines", session.db["user_name"])
#        for i in session.settings["other_buffers"]["friends_timelines"]:
#            pub.sendMessage("createBuffer", buffer_type="PeopleBuffer", session_type=session.type, buffer_title=_(u"Friends for {}").format(i,), parent_tab=friends_timelines_position, start=False, kwargs=dict(parent=controller.view.nb, function="get_friends", name="%s-friends" % (i,), sessionObject=session, account=session.db["user_name"], sound="new_event.ogg", user_id=i))
#        pub.sendMessage("createBuffer", buffer_type="EmptyBuffer", session_type="base", buffer_title=_("Lists"), parent_tab=root_position, start=False, kwargs=dict(parent=controller.view.nb, name="lists", account=session.db["user_name"]))
#        lists_position =controller.view.search("lists", session.db["user_name"])
#        for i in session.settings["other_buffers"]["lists"]:
#            pub.sendMessage("createBuffer", buffer_type="ListBuffer", session_type=session.type, buffer_title=_(u"List for {}").format(i), parent_tab=lists_position, start=False, kwargs=dict(parent=controller.view.nb, function="list_timeline", name="%s-list" % (i,), sessionObject=session, account=session.db["user_name"], bufferType=None, sound="list_tweet.ogg", list_id=utils.find_list(i, session.db["lists"]), include_ext_alt_text=True, tweet_mode="extended"))
#        pub.sendMessage("createBuffer", buffer_type="EmptyBuffer", session_type="base", buffer_title=_("Searches"), parent_tab=root_position, start=False, kwargs=dict(parent=controller.view.nb, name="searches", account=session.db["user_name"]))
#        searches_position =controller.view.search("searches", session.db["user_name"])
#        for i in session.settings["other_buffers"]["tweet_searches"]:
#            pub.sendMessage("createBuffer", buffer_type="SearchBuffer", session_type=session.type, buffer_title=_(u"Search for {}").format(i), parent_tab=searches_position, start=False, kwargs=dict(parent=controller.view.nb, function="search_tweets", name="%s-searchterm" % (i,), sessionObject=session, account=session.db["user_name"], bufferType="searchPanel", sound="search_updated.ogg", q=i, include_ext_alt_text=True, tweet_mode="extended"))
#        for i in session.settings["other_buffers"]["trending_topic_buffers"]:
#            pub.sendMessage("createBuffer", buffer_type="TrendsBuffer", session_type=session.type, buffer_title=_("Trending topics for %s") % (i), parent_tab=root_position, start=False, kwargs=dict(parent=controller.view.nb, name="%s_tt" % (i,), sessionObject=session, account=session.db["user_name"], trendsFor=i, sound="trends_updated.ogg"))

    def start_buffer(self, controller, buffer):
        try:
            buffer.start_stream()
        except Exception as err:
            log.exception("Error %s starting buffer %s on account %s, with args %r and kwargs %r." % (str(err), buffer.name, buffer.account, buffer.args, buffer.kwargs))