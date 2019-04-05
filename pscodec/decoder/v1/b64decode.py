import base64

URLSAFE_PADDING_BYTE = '.'
RFC3548_PADDING_BYTE = '='


def b64decode(b64string):
    # Replace padding byte with RFC3548
    b64string = b64string.replace(URLSAFE_PADDING_BYTE, RFC3548_PADDING_BYTE)
    return base64.urlsafe_b64decode(b64string)