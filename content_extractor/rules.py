from enum import Enum
from os.path import dirname

_DEFAULT_RULES_FILE_NAME = dirname(__file__) + "/default_rules.txt"


class Rule:
    def __init__(self, exclude: bool = True):
        self.exclude = exclude

    def matches(self, tag: str, attrs: dict) -> bool:
        pass


class RuleResolution(Enum):
    Unknown = 0,
    Exclude = 1,
    Include = 2


class Domain:
    def __init__(self, hosts: str):
        self._hosts: str = hosts
        self._filter_rules = []
        self._header_rules = []
        self._paragraph_rules = []
        self._debug = False

    def resolve(self, tag: str, attrs: list) -> RuleResolution:
        return self._resolve(tag, attrs, self._filter_rules)

    def resolve_header(self, tag, attrs: list) -> RuleResolution:
        return self._resolve(tag, attrs, self._header_rules)

    def resolve_paragraph(self, tag, attrs: list) -> RuleResolution:
        return self._resolve(tag, attrs, self._paragraph_rules)

    def add_filter_rule(self, rule: Rule):
        self._filter_rules.append(rule)

    def add_header_rule(self, rule: Rule):
        self._header_rules.append(rule)

    def add_paragraph_rule(self, rule: Rule):
        self._paragraph_rules.append(rule)

    def _resolve(self, tag: str, attrs: list, rules: list) -> RuleResolution:
        attrs_dict = dict(attrs)
        resolution = RuleResolution.Unknown
        for rule in rules:
            if rule.matches(tag, attrs_dict):
                if not rule.exclude:
                    if self._debug:
                        print(f"D: include <{tag}, {attrs}> by rule {rule}")
                    return RuleResolution.Include
                resolution = RuleResolution.Exclude
                if self._debug:
                    print(f"D: exclude <{tag}, {attrs}> by rule {rule}")
        return resolution


class TagNamesRule(Rule):
    def __init__(self, tags: str, exclude: bool = True):
        super().__init__(exclude)
        self._tags = set(map(str.strip, tags.split(",")))

    def matches(self, tag: str, attrs: dict) -> bool:
        return tag in self._tags

    def __repr__(self) -> str:
        return f"{'-' if self.exclude else '+'}TagNamesRule[tags={self._tags}]"


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
            if self._substring and condition_value in cls:
                return True
            elif self._starts and cls.startswith(condition_value):
                return True
            elif self._ends and cls.endswith(condition_value):
                return True
            elif cls == condition_value:
                return True

        return False

    def __repr__(self) -> str:
        return f"{'-' if self.exclude else '+'}ClassNameRule[{self._condition}]"


class AttributeRule(Rule):
    def __init__(self, rule_spec: str, exclude: bool = True):
        super().__init__(exclude)
        self._rule_spec = rule_spec
        parts = rule_spec.split(":")
        self._attr = parts[0]
        condition = parts[1]
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
        if self._attr not in attrs:
            return False
        attr_value = attrs[self._attr].lower()
        condition_value = self._condition_value
        if self._substring and condition_value in attr_value:
            return True
        elif self._starts and attr_value.startswith(condition_value):
            return True
        elif self._ends and attr_value.endswith(condition_value):
            return True
        elif attr_value == condition_value:
            return True
        else:
            return False

    def __repr__(self) -> str:
        return f"{'-' if self.exclude else '+'}AttributeRule[{self._rule_spec}]"


class Rules:
    def __init__(self):
        self._domains = dict()
        self._current_domain = Domain("*")
        self._domains["*"] = self._current_domain

    def load(self, file_name: str = None):
        _file_name = file_name if file_name else _DEFAULT_RULES_FILE_NAME
        with open(_file_name, encoding="utf-8") as f:
            for line in f:
                self._process_line(line.strip())

    def exclude(self, host: str, tag: str, attrs: list):
        domain = self._domains.get(host)
        resolution = domain.resolve(tag, attrs) if domain else RuleResolution.Unknown
        if resolution == RuleResolution.Unknown:
            default_rules = self._domains["*"]
            resolution = default_rules.resolve(tag, attrs)
        return resolution == RuleResolution.Exclude

    def is_header(self, host: str, tag: str, attrs: list):
        domain = self._domains.get(host)
        resolution = domain.resolve_header(tag, attrs) if domain else RuleResolution.Unknown
        if resolution == RuleResolution.Unknown:
            default_rules = self._domains["*"]
            resolution = default_rules.resolve_header(tag, attrs)
        return resolution == RuleResolution.Include

    def is_paragraph(self, host: str, tag: str, attrs: list):
        domain = self._domains.get(host)
        resolution = domain.resolve_paragraph(tag, attrs) if domain else RuleResolution.Unknown
        if resolution == RuleResolution.Unknown:
            default_rules = self._domains["*"]
            resolution = default_rules.resolve_paragraph(tag, attrs)
        return resolution == RuleResolution.Include

    def _process_line(self, line):
        if line.startswith("#"):
            return
        if line.startswith("domain:"):
            self._add_domain(line)
        elif line.startswith("-") or line.startswith("+"):
            self._add_filter_rule(line)
        elif line.startswith("header:"):
            self._add_header_rule(line)
        elif line.startswith("paragraph:"):
            self._add_paragraph_rule(line)

    def _add_domain(self, domain_rule):
        host_names = domain_rule.split(":")[1]
        hosts = list(map(str.strip, host_names.split(",")))
        self._current_domain = self._domains.get(hosts[0])
        if not self._current_domain:
            self._current_domain = Domain(host_names)
            for host in hosts:
                self._domains[host] = self._current_domain

    def _create_filter_rule(self, filter_rule) -> Rule:
        exclude = filter_rule.startswith("-")
        rule_parts = filter_rule[1:].split(":", maxsplit=1)
        rule_type = rule_parts[0]
        rule_spec = rule_parts[1]
        rule: Rule
        if rule_type == "class":
            rule = ClassNameRule(rule_spec, exclude)
        elif rule_type == "tag":
            rule = TagNamesRule(rule_spec, exclude)
        elif rule_type == "attr":
            rule = AttributeRule(rule_spec, exclude)
        else:
            raise RuntimeError(f"Неизвестный тип правила: {rule_type}")

        return rule

    def _add_filter_rule(self, filter_rule):
        rule = self._create_filter_rule(filter_rule)
        self._current_domain.add_filter_rule(rule)

    def _add_header_rule(self, filter_rule: str):
        rule_parts = filter_rule.split(":", maxsplit=1)
        rule_spec = "+" + rule_parts[1]
        rule = self._create_filter_rule(rule_spec)
        self._current_domain.add_header_rule(rule)

    def _add_paragraph_rule(self, filter_rule: str):
        rule_parts = filter_rule.split(":", maxsplit=1)
        rule_spec = "+" + rule_parts[1]
        rule = self._create_filter_rule(rule_spec)
        self._current_domain.add_paragraph_rule(rule)
