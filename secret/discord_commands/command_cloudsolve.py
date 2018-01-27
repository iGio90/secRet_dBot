import censys.certificates
import censys.ipv4
import censys
import dns
import ipaddress

import requests
from html_similarity import similarity

from secret import utils

cloudflare_ip_ranges = [
    "103.21.244.0/22",
    "103.22.200.0/22",
    "103.31.4.0/22",
    "104.16.0.0/12",
    "108.162.192.0/18",
    "131.0.72.0/22",
    "141.101.64.0/18",
    "162.158.0.0/15",
    "172.64.0.0/13",
    "173.245.48.0/20",
    "188.114.96.0/20",
    "190.93.240.0/20",
    "197.234.240.0/22",
    "198.41.128.0/17"
]


async def on_message(message, secret_context):
    parts = message.content.split(" ")
    if len(parts) < 2:
        # print the help
        secret_context.bus.emit('secret_command', command='!help cloudsolve')
    else:
        domain = str(parts[1])
        if domain.startswith('http://'):
            domain.replace('http://', '')
        elif domain.startswith('https://'):
            domain.replace('https://', '')
        if not utils.is_valid_domain(domain):
            embed = utils.simple_embed('cloudsolve', ('**%s** is not a valid domain' % domain), utils.random_color())
            await secret_context.discord_client.send_message(message.channel, embed=embed)
        elif not uses_cloudflare(domain):
            embed = utils.simple_embed('cloudsolve', ('"%s" is not behind CloudFlare' % domain), utils.random_color())
            await secret_context.discord_client.send_message(message.channel, embed=embed)
        else:
            embed = utils.simple_embed('cloudsolve', ('**%s** appear to be behind CloudFlare' % domain),
                                       utils.random_color())
            await secret_context.discord_client.send_message(message.channel, embed=embed)
            embed = utils.simple_embed('cloudsolve', ('trying to exploit **%s** certificates' % domain),
                                       utils.random_color())
            await secret_context.discord_client.send_message(message.channel, embed=embed)
            certs = exploit_certificates(domain, secret_context)
            if len(certs) > 0:
                embed = utils.simple_embed('cloudsolve',
                                           ('%d certificates matching **%s** found' % (len(certs), domain)),
                                           utils.random_color())
                await secret_context.discord_client.send_message(message.channel, embed=embed)
                embed = utils.simple_embed('cloudsolve',
                                           ('looking for ipv4 hosts on **%s**' % domain),
                                           utils.random_color())
                await secret_context.discord_client.send_message(message.channel, embed=embed)
                hosts = find_ipv4_hosts(certs, secret_context)
                hosts = filter_cloudflare_ips(hosts)

                if len(hosts) is 0:
                    embed = utils.simple_embed('cloudsolve',
                                               ('**%s** looks not exploitable. todo: bruteforce domain' % domain),
                                               utils.random_color())
                    await secret_context.discord_client.send_message(message.channel, embed=embed)
                else:
                    embed = utils.simple_embed('cloudsolve',
                                               ('%d ipv4 hosts found on **%s**' % (len(hosts), domain)),
                                               utils.random_color())
                    for h in hosts:
                        embed.add_field(name=h, value='ipv4', inline=True)
                    await secret_context.discord_client.send_message(message.channel, embed=embed)
                    origins = find_origins(domain, hosts)
                    embed = utils.simple_embed('cloudsolve',
                                               ('looking for origins on **%s**' % domain),
                                               utils.random_color())
                    await secret_context.discord_client.send_message(message.channel, embed=embed)
                    if len(origins) is 0:
                        embed = utils.simple_embed('cloudsolve',
                                                   ('did not found any origin server for **%s**. todo: bruteforce '
                                                    'domain' % domain),
                                                   utils.random_color())
                        await secret_context.discord_client.send_message(message.channel, embed=embed)
                    else:
                        embed = utils.simple_embed('cloudsolve',
                                                   ('found %d origins for **%s**' % (len(origins), domain)),
                                                   utils.random_color())
                        for o in origins:
                            embed.add_field(name=o[0], value=o[1], inline=False)
                        await secret_context.discord_client.send_message(message.channel, embed=embed)
            else:
                embed = utils.simple_embed('cloudsolve',
                                           ('no certificates found for **%s**' % domain),
                                           utils.random_color())
                await secret_context.discord_client.send_message(message.channel, embed=embed)


def exploit_certificates(domain, secret_context):
    try:
        censys_certificates = censys.certificates.CensysCertificates(
            api_id=secret_context.api_keys['csys_app_id'],
            api_secret=secret_context.api_keys['csys_sec'])
        requested_fields = [
            'parsed.names',
            'parsed.fingerprint_sha256'
        ]
        certificate_query = 'parsed.names: %s AND tags.raw: trusted AND NOT parsed.names: cloudflaressl.com' % domain
        certificates_search_results = censys_certificates.search(certificate_query, fields=requested_fields)
        return set([cert['parsed.fingerprint_sha256'] for cert in certificates_search_results])
    except Exception as e:
        return set([])


def find_ipv4_hosts(cert_fingerprints, secret_context):
    try:
        censys_hosts = censys.ipv4.CensysIPv4(
            api_id=secret_context.api_keys['csys_app_id'],
            api_secret=secret_context.api_keys['csys_sec'])
        hosts_query = ' OR '.join(cert_fingerprints)
        hosts_search_results = censys_hosts.search(hosts_query)
        return set([host_search_result['ip'] for host_search_result in hosts_search_results])
    except Exception:
        return set([])


def uses_cloudflare(domain):
    answers = dns.resolver.query(domain, 'A')
    for answer in answers:
        if is_cloudflare_ip(answer):
            return True

    return False


def is_cloudflare_ip(ip):
    cloudflare_subnets = [ipaddress.ip_network(ip_range) for ip_range in cloudflare_ip_ranges]
    for cloudflare_subnet in cloudflare_subnets:
        if cloudflare_subnet.overlaps(ipaddress.ip_network(ip)):
            return True
    return False


def retrieve_original_page(domain):
    url = 'https://' + domain
    try:
        original_response = requests.get(url, timeout=3)
    except requests.exceptions.Timeout:
        return ''
    except requests.exceptions.RequestException:
        return ''
    return original_response


def filter_cloudflare_ips(ips):
    return [ip for ip in ips if not is_cloudflare_ip(ip)]


def find_origins(domain, candidates):
    original_response = retrieve_original_page(domain)
    host_header_value = original_response.url.replace('https://', '').split('/')[0]
    origins = []
    for host in candidates:
        try:
            url = 'https://' + host
            headers = {
                'Host': host_header_value
            }
            response = requests.get(url, timeout=3, headers=headers, verify=False)
        except requests.exceptions.Timeout:
            continue
        except requests.exceptions.RequestException :
            continue
        if response.status_code != 200:
            continue
        if response.text == original_response.text:
            origins.append((host, 'HTML content identical to %s' % domain))
            continue
        page_similarity = similarity(response.text, original_response.text)
        if page_similarity > 0.9:
            origins.append(
                (host, 'HTML content is %d %% structurally similar to %s' % (round(100 * page_similarity, 2), domain)))
    return origins
