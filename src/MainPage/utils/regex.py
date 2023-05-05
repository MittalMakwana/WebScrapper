import re
import logging

logging.basicConfig(level=logging.INFO)


class CardRegex:
    _name = r'(?P<name>.*)'
    _size = r'(?P<size>.*)'
    _quality = r'(?P<quality>\d+p)'
    _type = r'(?P<type>\w*)'
    _day = r'(?P<day>\d+)'
    _month = r'(?P<month>.+)\s?'
    _yr = r'(?P<yr>\d\d\d\d)?'
    _ordinal = r'(st|nd|rd|th)?\s'
    _ep = r'(?P<ep>(?:S\d*(EP?\d*T?O?\d*)?)?)'
    _part = r'(Part \d)?\s?'
    _view_type = r'(?P<view_type>3D|V2)\s'
    _str = rf"{_name}\s(\((?P<dt>(?:{_day}{_ordinal}{_month})?{_yr})\)\s+)\s?{_ep}\s?{_part}({_view_type})?{_quality}\s?{_type}(.*)\[{_size}\]$"
    CARD_REGEX = re.compile(_str)

    def __init__(self):
        self.regex = self.CARD_REGEX

    def match(self, text):
        if isinstance(text, str):
            try:
                _dict = self.regex.match(text).groupdict()
                logging.debug(f"Regex matched for: '{text}'")
                return _dict
            except AttributeError:
                logging.error(f"Regex not matched for: '{text}'")
                return {}
        else:
            raise TypeError(f"Expected str, got {type(text)}")

    def __repr__(self) -> str:
        return self._str


if __name__ == "__main__":
    from sampletext import text
    for t in text.split('\n'):
        CardRegex().match(t)
    print(repr(CardRegex()))
