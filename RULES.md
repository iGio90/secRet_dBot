## Goal
The challenge is to keep this up, at first, and to give everyone something fun to play with.
When I started my little discord server was mainly to have a peaceful place to reverse engineer and share stuff with friends.
Then it grows a bit, more in terms of brains that people actually, but maybe one day it will have hundred of users... or maybe not!
So i started this project in which I try to provide a solid base that people can use to code whatever functionality inside.
In the moment I'm writing this, the bot is running on my macbook pro (debian) and allows admin to exec system().
Another goal is to run this soon on a vm with root access to all the users.

## Good stuffs
I don't know how to call this. A bot, an AI (it will be a fu*@!-c2ing AI) so from now on I will call it ``the baby``.

The baby can
* auto update himself every hour from his git repo
* auto merge pull requests after a vote from our discord server
* provide lot of stuffs to your fantasy (mongodb, discord api, github api, a web and restful server).
Read more in the documentation to find out more things.


## Voting
At the moment, I left for myself a little "space" to control it, also, because it's actually running in front of my eye and i got an ide ready to fix anything wrong.
Another goal is to totally remove this "space" and set my self as a normal user. Any eventual hard fix should be provided from something we will code in, the baby will learn to fix himself.
Voting system is very basic... I'm not best in math but I'm sure later someone will improve it if needed.
It is mostly based on the len of the members inside the discords.
* To merge a PR voted only by normal users, 100 users needs to vote on a server with 70 users only.
So that, admins and devs votes will grant way more point.
* In any case, a single vote from an admin, **can't** merge it - at least 2 people are required to vote.
* Getting a pull request merged will give the author some points which will increase his vote on other people pulls.
* As said.. math there is pretty terrible... we will improve this.

## Rules

There is no restriction on coding stuffs inside. The baby will learn one day to understand if someone is trying to play with him, but also, you don't want to fuck with a community full of hackers and developers with different backgrounds.
As a developer, I eventually accept and upvote ddos stuffs and penetration testing things, but.. other people may get angry to see their stuffs not working properly because of this, and so, I'm gonna eventually upvote an eventual overwrite.
As usual, have fun and play hard!