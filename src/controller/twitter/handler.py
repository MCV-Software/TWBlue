# -*- coding: utf-8 -*-
import logging
import widgetUtils
import output
from pubsub import pub
from tweepy.errors import TweepyException, Forbidden
from mysc import restart
from sessions.twitter import utils, compose
from controller import userSelector
from wxUI import dialogs, commonMessageDialogs
from . import filters, lists, settings, userActions, trendingTopics, user

log = logging.getLogger("controller.twitter.handler")

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
                pub.sendMessage("createBuffer", buffer_type="BaseBuffer", session_type=session.type, buffer_title=_("Home"), parent_tab=root_position, start=False, kwargs=dict(parent=controller.view.nb, function="home_timeline", name="home_timeline", sessionObject=session, account=session.db["user_name"], sound="tweet_received.ogg", include_ext_alt_text=True, tweet_mode="extended"))
            elif i == 'mentions':
                pub.sendMessage("createBuffer", buffer_type="BaseBuffer", session_type=session.type, buffer_title=_("Mentions"), parent_tab=root_position, start=False, kwargs=dict(parent=controller.view.nb, function="mentions_timeline", name="mentions", sessionObject=session, account=session.db["user_name"], sound="mention_received.ogg", include_ext_alt_text=True, tweet_mode="extended"))
            elif i == 'dm':
                pub.sendMessage("createBuffer", buffer_type="DirectMessagesBuffer", session_type=session.type, buffer_title=_("Direct messages"), parent_tab=root_position, start=False, kwargs=dict(parent=controller.view.nb, function="get_direct_messages", name="direct_messages", sessionObject=session, account=session.db["user_name"], bufferType="dmPanel", compose_func="compose_direct_message", sound="dm_received.ogg"))
            elif i == 'sent_dm':
                pub.sendMessage("createBuffer", buffer_type="SentDirectMessagesBuffer", session_type=session.type, buffer_title=_("Sent direct messages"), parent_tab=root_position, start=False, kwargs=dict(parent=controller.view.nb, function=None, name="sent_direct_messages", sessionObject=session, account=session.db["user_name"], bufferType="dmPanel", compose_func="compose_direct_message"))
            elif i == 'sent_tweets':
                pub.sendMessage("createBuffer", buffer_type="BaseBuffer", session_type=session.type, buffer_title=_("Sent tweets"), parent_tab=root_position, start=False, kwargs=dict(parent=controller.view.nb, function="user_timeline", name="sent_tweets", sessionObject=session, account=session.db["user_name"], screen_name=session.db["user_name"], include_ext_alt_text=True, tweet_mode="extended"))
            elif i == 'favorites':
                pub.sendMessage("createBuffer", buffer_type="BaseBuffer", session_type=session.type, buffer_title=_("Likes"), parent_tab=root_position, start=False, kwargs=dict(parent=controller.view.nb, function="get_favorites", name="favourites", sessionObject=session, account=session.db["user_name"], sound="favourite.ogg", include_ext_alt_text=True, tweet_mode="extended"))
            elif i == 'followers':
                pub.sendMessage("createBuffer", buffer_type="PeopleBuffer", session_type=session.type, buffer_title=_("Followers"), parent_tab=root_position, start=False, kwargs=dict(parent=controller.view.nb, function="get_followers", name="followers", sessionObject=session, account=session.db["user_name"], sound="update_followers.ogg", screen_name=session.db["user_name"]))
            elif i == 'friends':
                pub.sendMessage("createBuffer", buffer_type="PeopleBuffer", session_type=session.type, buffer_title=_("Following"), parent_tab=root_position, start=False, kwargs=dict(parent=controller.view.nb, function="get_friends", name="friends", sessionObject=session, account=session.db["user_name"], screen_name=session.db["user_name"]))
            elif i == 'blocks':
                pub.sendMessage("createBuffer", buffer_type="PeopleBuffer", session_type=session.type, buffer_title=_("Blocked users"), parent_tab=root_position, start=False, kwargs=dict(parent=controller.view.nb, function="get_blocks", name="blocked", sessionObject=session, account=session.db["user_name"]))
            elif i == 'muted':
                pub.sendMessage("createBuffer", buffer_type="PeopleBuffer", session_type=session.type, buffer_title=_("Muted users"), parent_tab=root_position, start=False, kwargs=dict(parent=controller.view.nb, function="get_mutes", name="muted", sessionObject=session, account=session.db["user_name"]))
        pub.sendMessage("createBuffer", buffer_type="EmptyBuffer", session_type="base", buffer_title=_("Timelines"), parent_tab=root_position, start=False, kwargs=dict(parent=controller.view.nb, name="timelines", account=session.db["user_name"]))
        timelines_position =controller.view.search("timelines", session.db["user_name"])
        for i in session.settings["other_buffers"]["timelines"]:
            pub.sendMessage("createBuffer", buffer_type="BaseBuffer", session_type=session.type, buffer_title=_(u"Timeline for {}").format(i,), parent_tab=timelines_position, start=False, kwargs=dict(parent=controller.view.nb, function="user_timeline", name="%s-timeline" % (i,), sessionObject=session, account=session.db["user_name"], sound="tweet_timeline.ogg", bufferType=None, user_id=i, include_ext_alt_text=True, tweet_mode="extended"))
        pub.sendMessage("createBuffer", buffer_type="EmptyBuffer", session_type="base", buffer_title=_("Likes timelines"), parent_tab=root_position, start=False, kwargs=dict(parent=controller.view.nb, name="favs_timelines", account=session.db["user_name"]))
        favs_timelines_position =controller.view.search("favs_timelines", session.db["user_name"])
        for i in session.settings["other_buffers"]["favourites_timelines"]:
            pub.sendMessage("createBuffer", buffer_type="BaseBuffer", session_type=session.type, buffer_title=_("Likes for {}").format(i,), parent_tab=favs_timelines_position, start=False, kwargs=dict(parent=controller.view.nb, function="get_favorites", name="%s-favorite" % (i,), sessionObject=session, account=session.db["user_name"], bufferType=None, sound="favourites_timeline_updated.ogg", user_id=i, include_ext_alt_text=True, tweet_mode="extended"))
        pub.sendMessage("createBuffer", buffer_type="EmptyBuffer", session_type="base", buffer_title=_("Followers timelines"), parent_tab=root_position, start=False, kwargs=dict(parent=controller.view.nb, name="followers_timelines", account=session.db["user_name"]))
        followers_timelines_position =controller.view.search("followers_timelines", session.db["user_name"])
        for i in session.settings["other_buffers"]["followers_timelines"]:
            pub.sendMessage("createBuffer", buffer_type="PeopleBuffer", session_type=session.type, buffer_title=_("Followers for {}").format(i,), parent_tab=followers_timelines_position, start=False, kwargs=dict(parent=controller.view.nb, function="get_followers", name="%s-followers" % (i,), sessionObject=session, account=session.db["user_name"], sound="new_event.ogg", user_id=i))
        pub.sendMessage("createBuffer", buffer_type="EmptyBuffer", session_type="base", buffer_title=_("Following timelines"), parent_tab=root_position, start=False, kwargs=dict(parent=controller.view.nb, name="friends_timelines", account=session.db["user_name"]))
        friends_timelines_position =controller.view.search("friends_timelines", session.db["user_name"])
        for i in session.settings["other_buffers"]["friends_timelines"]:
            pub.sendMessage("createBuffer", buffer_type="PeopleBuffer", session_type=session.type, buffer_title=_(u"Friends for {}").format(i,), parent_tab=friends_timelines_position, start=False, kwargs=dict(parent=controller.view.nb, function="get_friends", name="%s-friends" % (i,), sessionObject=session, account=session.db["user_name"], sound="new_event.ogg", user_id=i))
        pub.sendMessage("createBuffer", buffer_type="EmptyBuffer", session_type="base", buffer_title=_("Lists"), parent_tab=root_position, start=False, kwargs=dict(parent=controller.view.nb, name="lists", account=session.db["user_name"]))
        lists_position =controller.view.search("lists", session.db["user_name"])
        for i in session.settings["other_buffers"]["lists"]:
            pub.sendMessage("createBuffer", buffer_type="ListBuffer", session_type=session.type, buffer_title=_(u"List for {}").format(i), parent_tab=lists_position, start=False, kwargs=dict(parent=controller.view.nb, function="list_timeline", name="%s-list" % (i,), sessionObject=session, account=session.db["user_name"], bufferType=None, sound="list_tweet.ogg", list_id=utils.find_list(i, session.db["lists"]), include_ext_alt_text=True, tweet_mode="extended"))
        pub.sendMessage("createBuffer", buffer_type="EmptyBuffer", session_type="base", buffer_title=_("Searches"), parent_tab=root_position, start=False, kwargs=dict(parent=controller.view.nb, name="searches", account=session.db["user_name"]))
        searches_position =controller.view.search("searches", session.db["user_name"])
        for i in session.settings["other_buffers"]["tweet_searches"]:
            pub.sendMessage("createBuffer", buffer_type="SearchBuffer", session_type=session.type, buffer_title=_(u"Search for {}").format(i), parent_tab=searches_position, start=False, kwargs=dict(parent=controller.view.nb, function="search_tweets", name="%s-searchterm" % (i,), sessionObject=session, account=session.db["user_name"], bufferType="searchPanel", sound="search_updated.ogg", q=i, include_ext_alt_text=True, tweet_mode="extended"))
        for i in session.settings["other_buffers"]["trending_topic_buffers"]:
            pub.sendMessage("createBuffer", buffer_type="TrendsBuffer", session_type=session.type, buffer_title=_("Trending topics for %s") % (i), parent_tab=root_position, start=False, kwargs=dict(parent=controller.view.nb, name="%s_tt" % (i,), sessionObject=session, account=session.db["user_name"], trendsFor=i, sound="trends_updated.ogg"))

    def filter(self, buffer):
        # Let's prevent filtering of some buffers (people buffers, direct messages, events and sent items).
        if (buffer.name == "direct_messages" or buffer.name == "sent_tweets") or buffer.type == "people":
            output.speak(_("Filters cannot be applied on this buffer"))
            return
        new_filter = filters.filter(buffer)

    def manage_filters(self, session):
        manage_filters = filters.filterManager(session)

    def view_user_lists(self, buffer):
        if not hasattr(buffer, "get_right_tweet"):
            return
        tweet = buffer.get_right_tweet()
        if buffer.type == "people":
            users = [tweet.screen_name]
        elif buffer.type == "dm":
            users = [buffer.session.get_user(tweet.message_create["sender_id"]).screen_name]
        else:
            users = utils.get_all_users(tweet, buffer.session)
        selector = userSelector.userSelector(users=users, session_id=buffer.session.session_id)
        user = selector.get_user()
        if user == None:
            return
        l = lists.listsController(buffer.session, user=user)

    def add_to_list(self, controller, buffer):
        if not hasattr(buffer, "get_right_tweet"):
            return
        tweet = buffer.get_right_tweet()
        if buffer.type == "people":
            users = [tweet.screen_name]
        elif buffer.type == "dm":
            users = [buffer.session.get_user(tweet.message_create["sender_id"]).screen_name]
        else:
            users = utils.get_all_users(tweet, buffer.session)
        selector = userSelector.userSelector(users=users, session_id=buffer.session.session_id)
        user = selector.get_user()
        if user == None:
            return
        dlg = dialogs.lists.addUserListDialog()
        dlg.populate_list([compose.compose_list(item) for item in buffer.session.db["lists"]])
        if dlg.get_response() == widgetUtils.OK:
            try:
                list = buffer.session.twitter.add_list_member(list_id=buffer.session.db["lists"][dlg.get_item()].id, screen_name=user)
                older_list = utils.find_item(buffer.session.db["lists"][dlg.get_item()].id, buffer.session.db["lists"])
                listBuffer = controller.search_buffer("%s-list" % (buffer.session.db["lists"][dlg.get_item()].name.lower()), buff.session.db["user_name"])
                if listBuffer != None:
                    listBuffer.get_user_ids()
                buffer.session.db["lists"].pop(older_list)
                buffer.session.db["lists"].append(list)
            except TweepyException as e:
                log.exception("error %s" % (str(e)))
                output.speak("error %s" % (str(e)))

    def remove_from_list(self, controller, buffer):
        if not hasattr(buffer, "get_right_tweet"):
            return
        tweet = buffer.get_right_tweet()
        if buffer.type == "people":
            users = [tweet.screen_name]
        elif buffer.type == "dm":
            users = [buffer.session.get_user(tweet.message_create["sender_id"]).screen_name]
        else:
            users = utils.get_all_users(tweet, buffer.session)
        selector = userSelector.userSelector(users=users, session_id=buffer.session.session_id)
        user = selector.get_user()
        if user == None:
            return
        dlg = dialogs.lists.removeUserListDialog()
        dlg.populate_list([compose.compose_list(item) for item in buffer.session.db["lists"]])
        if dlg.get_response() == widgetUtils.OK:
            try:
                list = buffer.session.twitter.remove_list_member(list_id=buffer.session.db["lists"][dlg.get_item()].id, screen_name=user)
                older_list = utils.find_item(buffer.session.db["lists"][dlg.get_item()].id, buffer.session.db["lists"])
                listBuffer = controller.search_buffer("%s-list" % (buffer.session.db["lists"][dlg.get_item()].name.lower()), buffer.session.db["user_name"])
                if listBuffer != None:
                    listBuffer.get_user_ids()
                buffer.session.db["lists"].pop(older_list)
                buffer.session.db["lists"].append(list)
            except TweepyException as e:
                output.speak("error %s" % (str(e)))
                log.exception("error %s" % (str(e)))

    def list_manager(self, session):
        return lists.listsController(session=session)

    def account_settings(self, buffer, controller):
        d = settings.accountSettingsController(buffer, controller)
        if d.response == widgetUtils.OK:
            d.save_configuration()
            if d.needs_restart == True:
                commonMessageDialogs.needs_restart()
                buffer.session.settings.write()
                buffer.session.save_persistent_data()
                restart.restart_program()

    def follow(self, buffer):
        if not hasattr(buffer, "get_right_tweet"):
            return
        tweet = buffer.get_right_tweet()
        if buffer.type == "people":
            users = [tweet.screen_name]
        elif buffer.type == "dm":
            users = [buffer.session.get_user(tweet.message_create["sender_id"]).screen_name]
        else:
            users = utils.get_all_users(tweet, buffer.session)
        u = userActions.userActionsController(buffer, users)

    def add_alias(self, buffer):
        if not hasattr(buffer, "get_right_tweet"):
            return
        tweet = buffer.get_right_tweet()
        if buffer.type == "people":
            users = [tweet.screen_name]
        elif buffer.type == "dm":
            users = [buffer.session.get_user(tweet.message_create["sender_id"]).screen_name]
        else:
            users = utils.get_all_users(tweet, buffer.session)
        dlg = dialogs.userAliasDialogs.addAliasDialog(_("Add an user alias"), users)
        if dlg.get_response() == widgetUtils.OK:
            user, alias = dlg.get_user()
            if user == "" or alias == "":
                return
            user_id = buffer.session.get_user_by_screen_name(user)
            buffer.session.settings["user-aliases"][str(user_id)] = alias
            buffer.session.settings.write()
            output.speak(_("Alias has been set correctly for {}.").format(user))
            pub.sendMessage("alias-added")

    # ToDo: explore how to play sound & save config differently.
    # currently, TWBlue will play the sound and save the config for the timeline even if the buffer did not load or something else.
    def open_timeline(self, controller, buffer, default="tweets"):
        if not hasattr(buffer, "get_right_tweet"):
            return
        tweet = buffer.get_right_tweet()
        if buffer.type == "people":
            users = [tweet.screen_name]
        elif buffer.type == "dm":
            users = [buffer.session.get_user(tweet.message_create["sender_id"]).screen_name]
        else:
            users = utils.get_all_users(tweet, buffer.session)
        dlg = dialogs.userSelection.selectUserDialog(users=users, default=default)
        if dlg.get_response() == widgetUtils.OK:
            usr = utils.if_user_exists(buffer.session.twitter, dlg.get_user())
            if usr != None:
                if usr == dlg.get_user():
                    commonMessageDialogs.suspended_user()
                    return
                if usr.protected == True:
                    if usr.following == False:
                        commonMessageDialogs.no_following()
                        return
                tl_type = dlg.get_action()
                if tl_type  == "tweets":
                    if usr.statuses_count == 0:
                        commonMessageDialogs.no_tweets()
                        return
                    if usr.id_str in buffer.session.settings["other_buffers"]["timelines"]:
                        commonMessageDialogs.timeline_exist()
                        return
                    timelines_position =controller.view.search("timelines", buffer.session.db["user_name"])
                    pub.sendMessage("createBuffer", buffer_type="BaseBuffer", session_type=buffer.session.type, buffer_title=_("Timeline for {}").format(usr.screen_name,), parent_tab=timelines_position, start=True, kwargs=dict(parent=controller.view.nb, function="user_timeline", name="%s-timeline" % (usr.id_str,), sessionObject=buffer.session, account=buffer.session.db["user_name"], sound="tweet_timeline.ogg", bufferType=None, user_id=usr.id_str, include_ext_alt_text=True, tweet_mode="extended"))
                    buffer.session.settings["other_buffers"]["timelines"].append(usr.id_str)
                    buffer.session.sound.play("create_timeline.ogg")
                elif tl_type == "favourites":
                    if usr.favourites_count == 0:
                        commonMessageDialogs.no_favs()
                        return
                    if usr.id_str in buffer.session.settings["other_buffers"]["favourites_timelines"]:
                        commonMessageDialogs.timeline_exist()
                        return
                    favs_timelines_position =controller.view.search("favs_timelines", buffer.session.db["user_name"])
                    pub.sendMessage("createBuffer", buffer_type="BaseBuffer", session_type=buffer.session.type, buffer_title=_("Likes for {}").format(usr.screen_name,), parent_tab=favs_timelines_position, start=True, kwargs=dict(parent=controller.view.nb, function="get_favorites", name="%s-favorite" % (usr.id_str,), sessionObject=buffer.session, account=buffer.session.db["user_name"], bufferType=None, sound="favourites_timeline_updated.ogg", user_id=usr.id_str, include_ext_alt_text=True, tweet_mode="extended"))
                    buffer.session.settings["other_buffers"]["favourites_timelines"].append(usr.id_str)
                    buffer.session.sound.play("create_timeline.ogg")
                elif tl_type == "followers":
                    if usr.followers_count == 0:
                        commonMessageDialogs.no_followers()
                        return
                    if usr.id_str in buffer.session.settings["other_buffers"]["followers_timelines"]:
                        commonMessageDialogs.timeline_exist()
                        return
                    followers_timelines_position =controller.view.search("followers_timelines", buffer.session.db["user_name"])
                    pub.sendMessage("createBuffer", buffer_type="PeopleBuffer", session_type=buffer.session.type, buffer_title=_("Followers for {}").format(usr.screen_name,), parent_tab=followers_timelines_position, start=True, kwargs=dict(parent=controller.view.nb, function="get_followers", name="%s-followers" % (usr.id_str,), sessionObject=buffer.session, account=buffer.session.db["user_name"], sound="new_event.ogg", user_id=usr.id_str))
                    buffer.session.settings["other_buffers"]["followers_timelines"].append(usr.id_str)
                    buffer.session.sound.play("create_timeline.ogg")
                elif tl_type == "friends":
                    if usr.friends_count == 0:
                        commonMessageDialogs.no_friends()
                        return
                    if usr.id_str in buffer.session.settings["other_buffers"]["friends_timelines"]:
                        commonMessageDialogs.timeline_exist()
                        return
                    friends_timelines_position =controller.view.search("friends_timelines", buffer.session.db["user_name"])
                    pub.sendMessage("createBuffer", buffer_type="PeopleBuffer", session_type=buffer.session.type, buffer_title=_("Friends for {}").format(usr.screen_name,), parent_tab=friends_timelines_position, start=True, kwargs=dict(parent=controller.view.nb, function="get_friends", name="%s-friends" % (usr.id_str,), sessionObject=buffer.session, account=buffer.session.db["user_name"], sound="new_event.ogg", user_id=usr.id_str))
                    buffer.session.settings["other_buffers"]["friends_timelines"].append(usr.id_str)
                    buffer.session.sound.play("create_timeline.ogg")
            else:
                commonMessageDialogs.user_not_exist()
        buffer.session.settings.write()

    def open_conversation(self, controller, buffer):
        tweet = buffer.get_right_tweet()
        if hasattr(tweet, "retweeted_status") and tweet.retweeted_status != None:
            tweet = tweet.retweeted_status
        user = buffer.session.get_user(tweet.user).screen_name
        searches_position =controller.view.search("searches", buffer.session.db["user_name"])
        pub.sendMessage("createBuffer", buffer_type="ConversationBuffer", session_type=buffer.session.type, buffer_title=_(u"Conversation with {0}").format(user), parent_tab=searches_position, start=True, kwargs=dict(tweet=tweet, parent=controller.view.nb, function="search_tweets", name="%s-searchterm" % (tweet.id,), sessionObject=buffer.session, account=buffer.session.db["user_name"], bufferType="searchPanel", sound="search_updated.ogg", since_id=tweet.id, q="@{0}".format(user)))

    def get_trending_topics(self, controller, session):
        trends = trendingTopics.trendingTopicsController(session)
        if trends.dialog.get_response() == widgetUtils.OK:
            woeid = trends.get_woeid()
            if woeid in session.settings["other_buffers"]["trending_topic_buffers"]:
                return
            root_position =controller.view.search(session.db["user_name"], session.db["user_name"])
            pub.sendMessage("createBuffer", buffer_type="TrendsBuffer", session_type=session.type, buffer_title=_("Trending topics for %s") % (trends.get_string()), parent_tab=root_position, start=True, kwargs=dict(parent=controller.view.nb, name="%s_tt" % (woeid,), sessionObject=session, account=session.db["user_name"], trendsFor=woeid, sound="trends_updated.ogg"))
            session.settings["other_buffers"]["trending_topic_buffers"].append(woeid)
            session.settings.write()

    def start_buffer(self, controller, buffer):
        if hasattr(buffer, "finished_timeline") and buffer.finished_timeline == False:
            change_title = True
        else:
            change_title = False
        try:
            if "mentions" in buffer.name or "direct_messages" in buffer.name:
                buffer.start_stream()
            else:
                buffer.start_stream(play_sound=False)
        except TweepyException as err:
            log.exception("Error %s starting buffer %s on account %s, with args %r and kwargs %r." % (str(err), buffer.name, buffer.account, buffer.args, buffer.kwargs))
            # Determine if this error was caused by a block applied to the current user (IE permission errors).
            if type(err) == Forbidden:
                buff = controller.view.search(buffer.name, buffer.account)
                buffer.remove_buffer(force=True)
                commonMessageDialogs.blocked_timeline()
                if controller.get_current_buffer() == buffer:
                    controller.right()
                controller.view.delete_buffer(buff)
                controller.buffers.remove(buffer)
                del buffer
        if change_title:
            pub.sendMessage("buffer-title-changed", buffer=buffer)

    def update_profile(self, session):
        r = user.profileController(session)
