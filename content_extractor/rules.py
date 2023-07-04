import re
from os.path import dirname
from re import Pattern


class Rule:
    def __init__(self, exclude: bool = True):
        self.exclude = exclude

    def matches(self, tag: str, attrs: dict) -> bool:
        pass


class Domain:
    def __init__(self, host: str):
        self._host: str = host
        self._rules = []

    def exclude(self, tag: str, attrs: list):
        attrs_dict = dict(attrs)
        exclude = False
        for rule in self._rules:
            if rule.matches(tag, attrs_dict):
                if not rule.exclude:
                    return False
                exclude = True
        return exclude

    def add_rule(self, rule: Rule):
        self._rules.append(rule)

class TagNameRule(Rule):
    def __init__(self, tag: str, exclude: bool = True):
        super().__init__(exclude)
        self._tag = tag

    def matches(self, tag: str, attrs: dict) -> bool:
        return self._tag == tag

class ClassNameRule(Rule):
    def __init__(self, condition: str, exclude: bool = True):
        super().__init__(exclude)
        self._condition = condition
        self._substring = False
        self._starts = False
        self._ends = False
        self._equals = False
        if condition.startswith("*") and condition.endswith("*"):
            self._condition_value = condition[1:-1]
            self._substring = True
        elif condition.startswith("*"):
            self._condition_value = condition[1:]
            self._starts = True
        elif condition.endswith("*"):
            self._condition_value = condition[:-1]
            self._ends = True
        else:
            self._condition_value = condition
            self._equals = True

    def matches(self, tag: str, attrs: dict) -> bool:
        class_names = (attrs["class"] if "class" in attrs else "").lower().split()
        condition_value = self._condition_value
        for cls in class_names:
            if self._substring:
                return condition_value in cls
            elif self._starts:
                return cls.startswith(condition_value)
            elif self._ends:
                return cls.endswith(condition_value)
            else:
                return cls == condition_value


class Rules:
    def __init__(self):
        self._domains = dict()
        self._current_domain = Domain("*")
        self._domains["*"] = self._current_domain

    def load(self, file_name: str = None):
        _file_name = file_name if file_name else dirname(__file__) + "/rules.txt"
        with open(_file_name, encoding="utf-8") as f:
            for line in f:
                self._process_line(line.strip())

    def exclude(self, host: str, tag: str, attrs: list):
        domain = self._domains.get(host)
        if not domain:
            domain = self._domains["*"]
        return domain.exclude(tag, attrs)

    def _process_line(self, line):
        if line.startswith("#"):
            return
        if line.startswith("domain:"):
            self._add_domain(line)
        if line.startswith("-") or line.startswith("+"):
            self._add_filter_rule(line)

    def _add_domain(self, domain_rule):
        host = domain_rule.split(":")[1]
        self._current_domain = self._domains.get(host)
        if not self._current_domain:
            self._current_domain = Domain(host)
            self._domains[host] = self._current_domain

    def _add_filter_rule(self, filter_rule):
        exclude = filter_rule.startswith("-")
        rule_parts = filter_rule[1:].split(":")
        rule_type = rule_parts[0]
        rule: Rule
        if rule_type == "class":
            rule = ClassNameRule(rule_parts[1], exclude)
        elif rule_type == "tag":
            rule = TagNameRule(rule_parts[1], exclude)
        else:
            raise RuntimeError(f"Не известный тип правила: {rule_type}")

        self._current_domain.add_rule(rule)
