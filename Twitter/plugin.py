# coding=utf8
###
# Copyright (c) 2011, Terje Hoås
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import urllib2
import json
import datetime
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks


class Twitter(callbacks.Plugin):
    """Add the help for "@plugin help Twitter" here
    This should describe *how* to use this plugin."""
    threaded = True

    def twitter(self, irc, msg, args, nick, reply, rt):
        """<nick> [--reply] [--rt]

        Returns last tweet (which is not an @reply) by <nick>. If --reply is given the last tweet will be replied regardless of if it was an @reply or not. Same goes for --rt and retweets.
        """
        url = "http://api.twitter.com/1/statuses/user_timeline/" + nick + ".json"

        if rt:
            url += "?include_rts=true"

        try:
            req = urllib2.Request(url)
            stream = urllib2.urlopen(req)
            datas = stream.read()
        except urllib2.URLError, (err):
            if (err.code and err.code == 404):
                irc.reply("User not found.")
            elif (err.code and err.code == 401):
                irc.reply("Not authorized. Protected tweets?")
            else:
                if (err.code):
                    irc.reply("Error: Looks like I haven't bothered adding a special case for http error #" + str(err.code))
                else:
                    irc.reply("Error: Failed to open url. API might be unavailable.")
            return
        try:
            data = json.loads(datas)
        except:
            irc.reply("Error: Failed to parsed receive data.")
            self.log.warning("Plugin Twitter failed to parse json-data. Here are the data:")
            self.log.warning(data)
            return

#        self.log.info("--------- This is the full json ---------")
#        self.log.info(json.dumps(data, sort_keys=True, indent=4))
#        self.log.info("--------- That was it! ---------")

        if len(data) == 0:
            irc.reply("User has not tweeted yet.")
            return
        # Loop over all tweets
        for i in range(len(data)):
            # If we don't want @replies
            if (not reply and not data[i]["in_reply_to_screen_name"]):
                index = i
                break
            # If we want the last tweet even if it is an @reply
            elif (reply):
                index = i
                break

        name = data[index]["user"]["screen_name"]
        text = data[index]["text"]
        date = data[index]["created_at"]
        retvalue = "Tweeted by " + name + ", " + date + ": " + text

#        date_object = datetime.strptime(date,  "%a %b %d %H:%M:%S +0000 %Y")

        irc.reply(retvalue.encode("utf-8"))
    twitter = wrap(twitter, [('something'), optional(('literal', '--reply')), optional(('literal', '--rt'))])


Class = Twitter


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
