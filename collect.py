#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
import sys
import re
from collections import defaultdict

input_file = sys.argv[1]

PAGE_SEPARATOR = "__________________________________________________________________"

page_number_re = re

call_split_re = re.compile(r"(..:..:..) Samtal till (\d*)")

DEBUG = False

class ParseException(Exception):
    pass

class Cost(object):
    def __init__(self, cost=0.0, counter=0):
        self.cost = cost
        self.counter = counter

    def __add__(self, other):
        copy = self.copy()
        if type(other) == type(copy):
            copy.cost += other.cost
        elif type(other) == float:
            copy.cost += other

        copy.counter += 1
        return copy

    def __str__(self):
        return "%6.2f %3d" % (self.cost, self.counter)

    def __repr__(self):
        return str(self)

    def copy(self):
        return Cost(self.cost, self.counter)


class Call(object):
    header = "%(date)6s %(time)8s %(number)10s %(length)7s %(cost)6s" % {
            'date': "Date",
            'time': "Time",
            'number': "Number",
            'length': "Length",
            'cost': "Cost"}

    def __init__(self, date, time, number, length, cost):
        self.date = date
        self.time = time
        self.number = number
        self.length = length
        self.cost = float(cost.replace(',','.'))

    def __str__(self):
        return "%(date)6s %(time)8s %(number)10s %(length)7s %(cost)6.2f" % {
            'date': self.date,
            'time': self.time,
            'number': self.number,
            'length': self.length,
            'cost': self.cost}
    

class Invoice(object):
    def safe_parse(fun):
        def parse_wrapper(self, *args):
            self._pre_parse_pos = self.file_txt.tell()
            if DEBUG: print "# Filepos", self._pre_parse_pos

            try:
                return fun(self,*args)
            except ParseException:
                self.file_txt.seek(self._pre_parse_pos)
                raise

        return parse_wrapper

    def __init__(self, file_name):
        self.file_name = file_name
        self.file_txt = open(file_name,'r')

        self.calls = []


    def __del__(self):
        self.file_txt.close()

    def _flush_page(self):
        self._flush_to_line(PAGE_SEPARATOR)

    def _flush_to_line(self, line_str):
        while self._next_line() != line_str:
            pass

    def _next_line(self):
        line = self.file_txt.readline()
        if DEBUG: print(line.rstrip())
        return line.strip()

    def _parse(self):
        self._flush_page()
        self._flush_page()

        self._flush_to_line("Till Telias mobilabonnemang")
        while True:
            try:
                self._parse_call_telia_cell()
            except ParseException:
                break
        for _ in range(1,4):
            self._flush_to_line("Kr exkl moms")
            while True:
                try:
                    self._parse_call_telia_cell()
                except ParseException:
                    break
                    break
        if "Till övriga svenska mobilabonnemang" == self._next_line():
            while True:
                try:
                    self._parse_call_telia_cell()
                except ParseException:
                    break
        if "Till fasta telenätet" == self._next_line():
            while True:
                try:
                    self._parse_call_telia_cell()
                except ParseException:
                    break

    def cost_number(self):
        stat = defaultdict(Cost)

        for call in self.calls:
            stat[call.number] += call.cost

        cost_sum = 0.0
        call_counter = 0

        print "#%9s\t%6s\t%3s" % ("Nummer", "SEK", "n")
        for number, cost in sorted(stat.items(), key=lambda c:c[1].cost, reverse=True):
            cost_sum += cost.cost
            call_counter += cost.counter
            print "%10s\t%6.2f\t%3d" % (number, cost.cost * 1.25, cost.counter)
        print "#%9s\t%6.2f\t%3d" % ("", cost_sum * 1.25, call_counter)

    @safe_parse
    def _parse_call_telia_cell(self):
        date = self._next_line()

        m = call_split_re.match(self._next_line())
        if m:
            time = m.group(1)
            number = m.group(2)
        else:
            if DEBUG: print "# ------------ Not a telia call"
            raise ParseException

        length = self._next_line()
        cost = self._next_line()

        call = Call(date,time,number,length,cost)
        if DEBUG: print call
        self.calls.append(call)


if '__main__' == __name__:
    invoice = Invoice(input_file)
    invoice._parse()
    invoice.cost_number()
