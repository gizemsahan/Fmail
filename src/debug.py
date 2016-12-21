#!/usr/bin/python3
# -*- coding: utf-8 -*-

class Debugger(object):
    def __init__(self, is_active=True):
        self.is_active = is_active

    def print(self, message):
        if self.is_active:
            print(message)

    def print_error(self, title, function, possible_reason):
        if self.is_active:
            print("[!]"                + title)
            print("Function        : " + function)
            print("Possible reason : " + possible_reason)