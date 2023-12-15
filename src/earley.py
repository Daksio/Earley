class Rule:
    def __init__(self, rule_id, left, right):
        self.rule_id = rule_id
        self.left = left
        self.right = right


class State:
    def __init__(self, left, right, dot_pos, root, state_id):
        self.state_id = state_id
        self.left = left
        self.right = right
        self.dot_pos = dot_pos
        self.root = root
        self.dot_val = self.right[self.dot_pos] if self.dot_pos < len(self.right) else ""
        self.is_last = 1 if self.dot_pos == len(self.right) else 0

    def move_dot(self):
        return State(self.left, self.right, min(self.dot_pos + 1, len(self.right)), self.root, self.state_id)

    def next_sym(self):
        return self.right[self.dot_pos + 1] if self.dot_pos + 1 < len(self.right) else None

    def __hash__(self):
        return hash(self.left + "->" + self.right[: self.dot_pos] + "." + self.right[self.dot_pos :] + "," + str(self.root))

    def __eq__(self, other):
        return (
            self.left == other.left
            and self.right == other.right
            and self.dot_pos == other.dot_pos
            and self.root == other.root
            and self.dot_val == other.dot_val
            and self.is_last == other.is_last
            and self.state_id == other.state_id
        )


class Vertex:
    def __init__(self, states):
        self.states = states

    def __hash__(self):
        return hash(str(self.states))

    def __eq__(self, other):
        return self.states == other.states


class Earley:
    def fit(self, start, terms, non_terms, rules_list):
        self.check_input_accuracy(start, terms, non_terms, rules_list)
        self.terms = terms
        self.non_terms = non_terms
        self.start = start
        self.non_terms.append("&")
        self.rules = dict()
        self.Buildrules(start, list(rules_list))
        self.vertices = dict()

    def check_input_accuracy(self, start, terms, non_terms, rules_list):
        if start not in non_terms:
            raise RuntimeError("Начало должно быть нетерминальным символом.")
        if len(set(non_terms) & set(terms)) != 0:
            raise RuntimeError("Наборы терминальных и нетерминальных символов не должны пересекаться.")
        for rule in rules_list:
            rule_ = list(rule.split("->"))
            if len(rule_) != 2:
                raise RuntimeError("Правила должны состоять из двух частей, разделенных символом '->'")
            if len(rule_[0]) != 1:
                raise RuntimeError("LHS правила должен быть одним символом")
            if rule_[0] not in non_terms:
                raise RuntimeError("Правила должны начинаться с нетерминального символа")
            for char in rule_[1]:
                if char not in non_terms and char not in terms:
                    raise RuntimeError(f"Символ '{char}' отсутствует в списке символов.")

    def Buildrules(self, start, rules_list):
        for i in self.non_terms:
            self.rules[i] = set()
        for i in range(len(rules_list)):
            rule = Rule(i + 1, *rules_list[i].split("->"))
            self.rules[rule.left].add(rule)
        self.rules["&"].add(Rule(0, "&", start))

    def Predict(self, vertex_number):
        stack = []
        stack.extend(list(self.vertices[vertex_number]))
        done = set()
        while stack:
            item = stack.pop(0)
            if item in done:
                continue
            if item.dot_val in self.terms or item.dot_val == "":
                done.add(item)
                continue
            for rule in self.rules[item.dot_val]:
                if rule.left == item.dot_val:
                    state = State(rule.left, rule.right, 0, vertex_number, rule.rule_id)
                    if state not in stack:
                        stack.append(state)
            done.add(item)
        if self.vertices[vertex_number] == done:
            return False
        else:
            self.vertices[vertex_number] = done
            return True

    def Complete(self, vertex_number):
        stack = []
        check = False
        stack.extend(list(self.vertices[vertex_number]))
        new_states = set()
        while stack:
            item = stack.pop(0)
            if item.is_last:
                for expect in self.vertices[item.root]:
                    if expect.dot_val == item.left:
                        new_item = expect.move_dot()
                        if (new_item not in self.vertices[vertex_number] and new_item not in new_states):
                            new_states.add(new_item)
                            check = True
        self.vertices[vertex_number].update(new_states)
        return check

    def Scan(self, vertex_number, symbol):
        self.vertices[vertex_number + 1] = set()
        for item in self.vertices[vertex_number]:
            if item.dot_val == symbol:
                self.vertices[vertex_number + 1].add(item.move_dot())

    def applyPredict(self, word):
        self.vertices[0] = set()
        for rule in self.rules[self.start]:
            state = State(rule.left, rule.right, 0, 0, rule.rule_id)
            self.vertices[0].add(state)
        while self.Predict(0) or self.Complete(0):
            continue
        for i in range(1, len(word) + 1):
            self.Scan(i - 1, word[i - 1])
            while self.Predict(i) or self.Complete(i):
                continue
        for item in self.vertices[len(word)]:
            if item.is_last and item.root == 0 and item.left == self.start:
                return True
        return False


if __name__ == "__main__":
    N, Alphabet, P = [int(i) for i in input().split()]
    non_terms = list(input())
    terms = list(input())
    Rules = set()
    for _ in range(P):
        Rules.add(input())
    begin = input()
    Parser = Earley()
    Parser.fit(begin, terms, non_terms, Rules)
    check = int(input())
    for _ in range(check):
        word = input()
        print("Yes" if Parser.applyPredict(word) else "No")