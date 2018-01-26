import binascii

from secret import utils


async def on_message(message, secret_context):
    text = message.content[5:]
    if text == "":
        # print the help
        secret_context.bus.emit('secret_command', command='!help hex')
    else:
        # try to parse it as a number first
        try:
            a = int(text)
            embed = utils.simple_embed('hex', hex(a), utils.random_color())
            await secret_context.discord_client.send_message(message.channel, embed=embed)
        except Exception as e:
            # it's a string
            a = str(text)
            if a.startswith("0x"):
                try:
                    a = int(text, 16)
                    embed = utils.simple_embed('hex', hex(a), utils.random_color())
                    await secret_context.discord_client.send_message(message.channel, embed=embed)
                    return
                except Exception as e:
                    pass
            r = binascii.hexlify(a.encode('utf8'))
            embed = utils.simple_embed('hex', r.decode('utf8'), utils.random_color())
            await secret_context.discord_client.send_message(message.channel, embed=embed)
