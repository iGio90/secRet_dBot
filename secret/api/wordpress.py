import json
import re
import discord
import os
import requests

from lxml import etree
from random import randint
from secret import utils


async def on_message(message, secret_context):
    parts = message.content.split(" ")
    if len(parts) < 2:
        # print the help
        secret_context.bus.emit('secret_command', command='!help wpscan')
    else:
        if parts[1] == 'update':
            await update_vuln_db(message, secret_context)
        else:
            if not os.path.exists('secret/api/wordpress'):
                await update_vuln_db(message, secret_context)

            user_agent = get_random_agent()
            target = parts[1]

            if target[-1] != '/':
                target = target + '/'

            index = requests.get(target, headers={"User-Agent": user_agent}, verify=False)
            if "wp-" not in index.text:
                embed = utils.simple_embed('**%s**' % target, 'does not appear to be powered by wordpress',
                                           discord.Color.red())
                await secret_context.discord_client.send_message(message.channel, embed=embed)
            else:
                version = await check_version(target, user_agent, index)
                embed = utils.simple_embed('**%s**' % target, 'wordpress version found: **%s**' % version,
                                           discord.Color.green())
                await secret_context.discord_client.send_message(message.channel, embed=embed)

                await check_backup_files(message, secret_context, target, user_agent)
                await check_xml_rpc(message, secret_context, target, user_agent)
                await check_directory_listing(message, secret_context, target, user_agent)
                await check_robots(message, secret_context, target, user_agent)
                await full_path_disclose(message, secret_context, target, user_agent)
                await enumerate_users(message, secret_context, target, user_agent)

                if version is not None:
                    await list_wp_version_vuln(message, secret_context, target, version)
                    await enumerate_plugins(message, secret_context, index)
                    await enumerate_themes(message, secret_context, index)


async def enumerate_themes(message, secret_context, index):
    regex = re.compile('wp-content/themes/(.*?)/.*?[css|js].*?ver=([0-9\.]*)')
    match = regex.findall(index.text)
    theme = {}

    for m in match:
        theme_name = m[0]
        theme_name = theme_name.replace('-master', '')
        theme_name = theme_name.replace('.min', '')
        theme_version = m[1]

        if m[0] not in theme.keys():
            theme[m[0]] = m[1]
            with open('secret/api/wordpress/themes.json') as data_file:
                data = json.load(data_file)

            embed = utils.simple_embed(theme_name, theme_version,
                                       utils.random_color())
            if theme_name in data.keys():
                if is_lower(theme_version, data[theme_name]['latest_version'], False):
                    embed.add_field(name='latest version', value=data[theme_name]['latest_version'], inline=False)

            for vuln in data[theme_name]['vulnerabilities']:
                if 'fixed_in' in vuln.keys() and (vuln['fixed_in'] is None or
                                                  is_lower(theme_version, vuln['fixed_in'], True)):
                    embed.add_field(name=vuln['vuln_type'] + ' | ' + vuln['title'] + ' (' + vuln['id'] + ')',
                                    value="fixed in %s" % vuln['fixed_in'], inline=False)
                    for ref_key in vuln['references'].keys():
                        for ref in vuln['references'][ref_key]:
                            if ref_key != 'url':
                                embed.add_field(name='reference', value=ref_key.capitalize() + ' - ' + ref)
                            else:
                                embed.add_field(name='reference', value=ref)
            await secret_context.discord_client.send_message(message.channel, embed=embed)


async def enumerate_plugins(message, secret_context, index):
    regex = re.compile('wp-content/plugins/(.*?)/.*?[css|js].*?ver=([0-9\.]*)')
    match = regex.findall(index.text)
    plugin = {}
    for m in match:
        plugin_name = m[0]
        plugin_name = plugin_name.replace('-master', '')
        plugin_name = plugin_name.replace('.min', '')
        plugin_version = m[1]
        if plugin_name not in plugin.keys() and m[1] != '1':
            plugin[plugin_name] = m[1]

            with open('secret/api/wordpress/plugins.json') as data_file:
                data = json.load(data_file)

            embed = utils.simple_embed(plugin_name, plugin_version,
                                       utils.random_color())
            if plugin_name in data.keys():
                if is_lower(plugin_version, data[plugin_name]['latest_version'], False):
                    embed.add_field(name='latest version', value=data[plugin_name]['latest_version'], inline=False)

            for vuln in data[plugin_name]['vulnerabilities']:
                if 'fixed_in' in vuln.keys() and (vuln['fixed_in'] is None or
                                                  is_lower(plugin_version, vuln['fixed_in'], True)):
                    embed.add_field(name=vuln['vuln_type'] + ' | ' + vuln['title'] + ' (' + vuln['id'] + ')',
                                    value="fixed in %s" % vuln['fixed_in'], inline=False)
                    for ref_key in vuln['references'].keys():
                        for ref in vuln['references'][ref_key]:
                            if ref_key != 'url':
                                embed.add_field(name='reference', value=ref_key.capitalize() + ' - ' + ref)
                            else:
                                embed.add_field(name='reference', value=ref)
            await secret_context.discord_client.send_message(message.channel, embed=embed)


async def list_wp_version_vuln(message, secret_context, target, version):
    # Load json file
    with open('secret/api/wordpress/wordpresses.json') as data_file:
        data = json.load(data_file)

    if version not in data:
        embed = utils.simple_embed('**%s**' % target,
                                   'wordpress version not in db. update wordpress vuln db and try again',
                                   discord.Color.red())
        await secret_context.discord_client.send_message(message.channel, embed=embed)

    if not data[version]["vulnerabilities"]:
        versions = data.keys()
        for v in versions:
            if v[:4] in version and is_lower(version, v, False):
                version = v

    embed = utils.simple_embed('**%s**' % target,
                               'wordpress core vulnerabilities',
                               discord.Color.green())

    for vuln in data[version]["vulnerabilities"]:
        embed.add_field(name=vuln['vuln_type'], value=vuln['title'] + ' - ' + vuln['id'], inline=False)

        for ref_key in vuln['references'].keys():
            for ref in vuln['references'][ref_key]:
                if ref_key != 'url':
                    embed.add_field(name='reference', value=ref_key.capitalize() + ' - ' + ref)
                else:
                    embed.add_field(name='reference', value=ref)
    await secret_context.discord_client.send_message(message.channel, embed=embed)


async def enumerate_users(message, secret_context, target, user_agent):
    r = requests.get(target + "wp-json/wp/v2/users", headers={"User-Agent": user_agent}, verify=False)
    if "200" in str(r):
        embed = utils.simple_embed('**%s**' % target, 'enumerated users', discord.Color.green())
        users = json.loads(r.text)
        for user in users:
            embed.add_field(name=user['name'] + " - " + user['slug'], value=user['id'])
        await secret_context.discord_client.send_message(message.channel, embed=embed)


async def full_path_disclose(message, secret_context, target, user_agent):
    r = requests.get(target + "wp-includes/rss-functions.php", headers={"User-Agent": user_agent}, verify=False).text
    regex = re.compile("Fatal error:.*? in (.*?) on", re.S)
    matches = regex.findall(r)
    if matches:
        embed = utils.simple_embed('**%s**' % target, 'full path disclose in **%s** exposing: %s'
                                   % (target + "wp-includes/rss-functions.php", matches[0].replace('\n', '')),
                                   discord.Color.green())
        await secret_context.discord_client.send_message(message.channel, embed=embed)


async def check_robots(message, secret_context, target, user_agent):
    r = requests.get(target + "robots.txt", headers={"User-Agent": user_agent}, verify=False)
    if "200" in str(r) and not "404" in r.text:
        embed = utils.simple_embed('**%s**' % target, 'robots is available at: **%s**' % target + "robots.txt",
                                   discord.Color.green())
        lines = r.text.split('\n')
        for l in lines:
            if "Disallow:" in l:
                embed.add_field(name='disallow', value=l, inline=False)
        await secret_context.discord_client.send_message(message.channel, embed=embed)


async def check_directory_listing(message, secret_context, target, user_agent):
    directories = ["wp-content/uploads/", "wp-content/plugins/", "wp-content/themes/", "wp-includes/", "wp-admin/"]
    dir_name = ["Uploads", "Plugins", "Themes", "Includes", "Admin"]

    for directory, name in zip(directories, dir_name):
        r = requests.get(target + directory, headers={"User-Agent": user_agent}, verify=False)
        if "Index of" in r.text:
            embed = utils.simple_embed('**%s**' % target,
                                       'directory listing is enabled for: **%s**' % target + directory,
                                       discord.Color.green())
            await secret_context.discord_client.send_message(message.channel, embed=embed)


async def check_xml_rpc(message, secret_context, target, user_agent):
    r = requests.get(target + "xmlrpc.php", headers={"User-Agent": user_agent}, verify=False)
    if "200" in str(r) and "404" in r.text:
        embed = utils.simple_embed('**%s**' % target, 'found xml-rpc interface: **%s**' % target + "xmlrpc.php",
                                   discord.Color.green())
        await secret_context.discord_client.send_message(message.channel, embed=embed)


async def check_backup_files(message, secret_context, target, user_agent):
    backup = ['wp-config.php~', 'wp-config.php.save', '.wp-config.php.bck', 'wp-config.php.bck', '.wp-config.php.swp',
              'wp-config.php.swp', 'wp-config.php.swo', 'wp-config.php_bak', 'wp-config.bak', 'wp-config.php.bak',
              'wp-config.save', 'wp-config.old', 'wp-config.php.old', 'wp-config.php.orig', 'wp-config.orig',
              'wp-config.php.original', 'wp-config.original', 'wp-config.txt', 'wp-config.php.txt', 'wp-config.backup',
              'wp-config.php.backup', 'wp-config.copy', 'wp-config.php.copy', 'wp-config.tmp', 'wp-config.php.tmp',
              'wp-config.zip', 'wp-config.php.zip', 'wp-config.db', 'wp-config.php.db', 'wp-config.dat',
              'wp-config.php.dat', 'wp-config.tar.gz', 'wp-config.php.tar.gz', 'wp-config.back', 'wp-config.php.back',
              'wp-config.test', 'wp-config.php.test']
    for b in backup:
        r = requests.get(target + b, headers={"User-Agent": user_agent}, verify=False)
        if "200" in str(r) and not "404" in r.text:
            embed = utils.simple_embed('**%s**' % target, 'found config backup: **%s**' % target + b,
                                       discord.Color.green())
            await secret_context.discord_client.send_message(message.channel, embed=embed)


async def check_version(target, user_agent, index):
    v = fingerprint_wp_version_meta_based(index)
    if v is None:
        v = fingerprint_wp_version_feed_based(target, user_agent)
        if v is None:
            v = fingerprint_wp_version_hash_based(target)
            if v is None:
                r = requests.get(target + 'readme.html', headers={"User-Agent": user_agent}, verify=False)
                if "200" in str(r):
                    regex = 'Version (.*)'
                    regex = re.compile(regex)
                    matches = regex.findall(r.text)
                    if len(matches) > 0 and matches[0] is not None and matches[0] != "":
                        return matches[0]
    return v


def fingerprint_wp_version_meta_based(index):
    regex = re.compile('meta name="generator" content="WordPress (.*?)"')
    match = regex.findall(index.text)
    if match:
        return match[0]
    return None


def fingerprint_wp_version_feed_based(target, user_agent):
    r = requests.get(target + "index.php/feed", headers={"User-Agent": user_agent}, verify=False).text
    regex = re.compile('generator>https://wordpress.org/\?v=(.*?)<\/generator')
    match = regex.findall(r)
    if match:
        return match[0]
    return None


def fingerprint_wp_version_hash_based(target):
    tree = etree.parse("secret/api/wordpress/wp_versions.xml")
    root = tree.getroot()
    for i in range(len(root)):
        ddl_url = (target + root[i].get('src')).replace('$', '')
        ddl_name = "/tmp/" + (root[i].get('src').replace('/', '-'))
        utils.download_file(ddl_url, ddl_name)
        ddl_hash = utils.md5_hash(ddl_name)

        try:
            os.remove(ddl_name)
        except Exception:
            pass

        for j in range(len(root[i])):
            if "Element" in str(root[i][j]):
                if ddl_hash == root[i][j].get('md5'):
                    return root[i][j][0].text
    return None


def get_random_agent():
    with open('secret/api/wordpress/user-agents.txt', 'r') as f:
        uas = f.read()
        uas = re.sub("#.*", "", uas)
        uas = uas.replace("\n\n", "")
        uas = uas.split('\n')

    random = randint(0, len(uas))
    return uas[random]


async def update_vuln_db(message, secret_context):
    if not os.path.exists('secret/api/wordpress'):
        os.mkdir('secret/api/wordpress')

    update_url = "https://data.wpscan.org/"
    update_files = ['local_vulnerable_files.xml', 'local_vulnerable_files.xsd',
                    'timthumbs.txt', 'user-agents.txt', 'wp_versions.xml', 'wp_versions.xsd',
                    'wordpresses.json', 'plugins.json', 'themes.json']

    embed = utils.simple_embed('wordpress', 'updating vulnerability database',
                               discord.Color.green())
    await secret_context.discord_client.send_message(message.channel, embed=embed)
    for f in update_files:
        embed = utils.simple_embed('wordpress', 'downloading %s' % f,
                                   utils.random_color())
        await secret_context.discord_client.send_message(message.channel, embed=embed)
        utils.download_raw_file(update_url + f, "secret/api/wordpress/" + f)

    unzip_file("secret/api/wordpress/user-agents.txt")
    unzip_file("secret/api/wordpress/timthumbs.txt")


def unzip_file(filename):
    os.system('mv ' + filename + ' ' + filename + ".gz")
    os.system('gzip -d ' + filename + ".gz")


def is_lower(str_one, str_two, equal):
    sum_one = 0
    sum_two = 0

    if str_one is None:
        if str_two is None:
            return False
        else:
            return True

    if str_two is None:
        if str_one is None:
            return False
        else:
            return True

    if len(str_one) < 5:
        str_one += '.0'
    if len(str_two) < 5:
        str_two += '.0'

    str_one = str_one[::-1].split('.')
    str_two = str_two[::-1].split('.')

    for i in range(len(str_one)):
        try:
            sum_one += ((i + 1) ** 10) * (int(str_one[i]))
            sum_two += ((i + 1) ** 10) * (int(str_two[i]))
        except Exception:
            return True

    if sum_one < sum_two:
        return True
    if equal and sum_one == sum_two:
        return True
    return False
