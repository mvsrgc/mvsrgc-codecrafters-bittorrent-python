import json
import sys

from typing import Any
from dataclasses import dataclass

# import bencodepy - available if you need it!
# import requests - available if you need it!

# Examples:
#
# - decode_bencode(b"5:hello") -> b"hello"
# - decode_bencode(b"10:hello12345") -> b"hello12345"


# Decoder originally from BencodePy by Eric Weast
# Copyright (C) 2014, 2015 by Eric Weast
# Modified by mvsrgc on 10-2023
@dataclass
class Decoder:
    data: bytes
    idx: int

    def _parse(self):
        char = self.data[self.idx : self.idx + 1]
        if char == b"i":
            self.idx += 1
            return int(self._read_to(b"e"))
        elif char in [b"0", b"1", b"2", b"3", b"4", b"5", b"6", b"7", b"8", b"9"]:
            str_len = int(self._read_to(b":"))
            return self._read(str_len)
        elif char == b"l":
            return self._parse_list()
        elif char == b"d":
            return self._parse_dict()

        return b""

    def _read(self, i: int) -> bytes:
        bytes = self.data[self.idx : self.idx + i]
        self.idx += i

        if len(bytes) != i:
            raise IndexError("Incorrect byte length returned.")

        return bytes

    def _read_to(self, terminator: bytes):
        try:
            i = self.data.index(terminator, self.idx)
            bytes = self.data[self.idx : i]
            self.idx = i + 1
            return bytes
        except ValueError:
            raise ValueError("Unable to find terminator.")

    def _parse_list(self) -> list[bytes]:
        self.idx += 1
        l = []
        while self.data[self.idx : self.idx + 1] != b"e":
            l.append(self._parse())
        self.idx += 1
        return l

    def _parse_dict(self):
        self.idx += 1
        d = {}
        while self.data[self.idx : self.idx + 1] != b"e":
            key = self._parse().decode()
            val = self._parse()
            d[key] = val
        return d

    def decode(self):
        return self._parse()


def decode_bencode(bencoded_value):
    decoder = Decoder(bencoded_value, 0)

    return decoder.decode()


def parse_list(bencoded_value, idx):
    pass


def main():
    command = sys.argv[1]

    if command == "decode":
        bencoded_value = sys.argv[2].encode()

        # json.dumps() can't handle bytes, but bencoded "strings" need to be
        # bytestrings since they might contain non utf-8 characters.
        #
        # Let's convert them to strings for printing to the console.
        def bytes_to_str(data):
            if isinstance(data, bytes):
                return data.decode()

            raise TypeError(f"Type not serializable: {type(data)}")

        print(json.dumps(decode_bencode(bencoded_value), default=bytes_to_str))
    else:
        raise NotImplementedError(f"Unknown command {command}")


if __name__ == "__main__":
    main()
