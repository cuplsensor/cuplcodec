import base64


class B64Decoder:
    URLSAFE_PADDING_BYTE = '.'
    RFC3548_PADDING_BYTE = '='

    @classmethod
    def b64decode(cls, b64string):
        # Replace padding byte with RFC3548
        b64string = b64string.replace(cls.URLSAFE_PADDING_BYTE, cls.RFC3548_PADDING_BYTE)
        return base64.urlsafe_b64decode(b64string)