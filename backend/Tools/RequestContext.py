class RequestContext:
    def __init__(self):
        self._headers = []  # all context normalised to "Key: Value" strings

    def set_cookie(self, cookie):
        """e.g. set_cookie("PHPSESSID=abc123")"""
        self._headers.append(f"Cookie: {cookie}")

    def set_bearer(self, token):
        """e.g. set_bearer("eyJ...")"""
        self._headers.append(f"Authorization: Bearer {token}")

    def add_header(self, header):
        """e.g. add_header("X-API-Key: secret")"""
        self._headers.append(header)

    def apply_to_ffuf(self, ffuf):
        for h in self._headers:
            ffuf.addAttribute("header", h)

    def apply_to_xsstrike(self, xs):
        if self._headers:
            xs.addAttribute("headers", "\\n".join(self._headers))
