import re
from collections import deque
OPERATORS = ("+", "-", "*", "/")


def test_valid(string_op):
    instr = string_op.strip()
    if instr[0] == "/":
        if instr[1:] not in ["help", "exit"]:
            print("Unknown command")
            return False
    elif "=" in instr:
        return True
    else:
        pat_var_num = " *[a-zA-Z0-9]+ *"
        pat_op = "([\\+-]+|[\\*/])"
        pat_left_br = " *(\\()* *"
        pat_right_br = " *(\\))* *"
        pat_prec_sign = " *[\\+-]* *"
        pat = "^(((" + pat_prec_sign + ")|("+pat_left_br + "))*" + "(" + \
              pat_var_num + "(" + pat_op + pat_var_num + ")*)*" + pat_right_br + ")*$"
        if not re.search(pat, instr) or (len(re.findall("\\(", instr)) != len(re.findall("\\)", instr))):
            print("Invalid expression")
            return False
    return True


def resolve_signs(string_op):
    prev_str = ""
    str_rep = string_op
    while str_rep != prev_str:
        prev_str = str_rep
        str_rep = re.sub("\\s+", " ", str_rep)
        str_rep = re.sub("--", "+", str_rep)  # replace pairs of "-" for "+"
        str_rep = re.sub("\\++", "+", str_rep)  # replace extra '+' signs for just one
        str_rep = re.sub("^\\+", "", str_rep)  # replace useless + at the beginning
        str_rep = re.sub("(\\+-)|(-\\+)", "-", str_rep)  # replace '+-' or '-+' for just '-'
        str_rep = re.sub("(?<=[\\+-])\\s(?=[0-9])", "", str_rep)  # delete space between sign and number
    return str_rep


def replace_vars(string_op, dict_):
    vars_ = re.findall("([a-zA-Z]+)", string_op)
    for var in vars_:
        if var in dict_:
            string_op = re.sub(var, dict_[var], string_op)
        else:
            print("Unknown variable")
            return None
    return string_op


def mem_assignment(string_op, dict_):
    # pattern for assignment is:
    # left = right
    left_right = string_op.split("=")
    if len(left_right) <= 2:
        left_right = [i.strip() for i in left_right]
        if re.match("^[a-zA-z]+$", left_right[0]):
            # left part is ok. Is the right part ok? is it another variable or a value?
            if re.match("[a-zA-Z]+$", left_right[1]):
                # it is a variable valid name
                if left_right[1] in dict_.keys():
                    dict_[left_right[0]] = dict_[left_right[1]]
                else:
                    print("Invalid assignment")
            elif re.match("[\\+-]* *[0-9]+$", left_right[1]):
                # is it a signed number
                dict_[left_right[0]] = resolve_signs(left_right[1])
            else:
                print("Invalid assignment")
        else:
            print("Invalid identifier")
    else:
        print("Invalid assignment")
    return dict_


def precedence(op):
    """returns a valid number to compare precedence of operations"""
    if op in ["+", "-"]:
        return 1
    elif op in ["*", "/"]:
        return 2


def infix_to_posfix(str_op):
    str_op = resolve_signs(str_op)
    str_op = str_op.replace(" ", "")
    s = deque()
    result = []
    lst = re.findall("[\\+/\\*-]|[0-9]+|\\(|\\)", str_op)
    for tk in lst:
        if re.match("[0-9]+$", tk):
            result.append(tk)
        elif re.match("[\\+/\\*-]$", tk):
            if (len(s) == 0) or (s[0] == "("):
                s.appendleft(tk)
            elif re.match("[\\+\\*/-]$", s[0]):
                if precedence(tk) > precedence(s[0]):
                    s.appendleft(tk)
                else:
                    while (len(s) > 0) and (s[0] != "(") and (precedence(s[0]) >= precedence(tk)):
                        result.append(s.popleft())
                    s.appendleft(tk)
        elif tk == "(":
            s.appendleft(tk)
        elif tk == ")":
            while (len(s) > 0) and (s[0] != "("):
                result.append(s.popleft())
            s.popleft()
    if len(s) > 0:
        while (len(s) > 0) and (s[0] in OPERATORS):
            result.append(s.popleft())
        if len(s) > 0:
            print("Invalid expression")
            return None
    return ' '.join(result)


def resolve_op(a, b, op):
    a = int(a)
    b = int(b)
    if op == "+":
        return a+b
    elif op == "-":
        return a-b
    elif op == "*":
        return a*b
    elif op == "/":
        return a/b


def calculate_posfix(posfix_str):
    s = deque()
    posfix = posfix_str.split(" ")
    for tk in posfix:
        if tk.isdigit():
            s.appendleft(tk)
        elif tk in OPERATORS:
            b = s.popleft()
            a = s.popleft()
            s.appendleft(resolve_op(a, b, tk))
    if len(s) > 0:
        return s[0]
    else:
        return None


calc_mem = {}
cmd = input().strip()
while cmd != "/exit":
    if cmd != "":
        if test_valid(cmd):
            if cmd == "/help":
                print("The program calculates the sum and subtraction of numbers")
            else:
                if "=" in cmd:
                    # assignment
                    calc_mem = mem_assignment(cmd, calc_mem)
                else:
                    cmd = replace_vars(cmd, calc_mem)
                    if cmd:
                        posfix_ops = infix_to_posfix(cmd)
                        res = calculate_posfix(posfix_ops)
                        print(res)
    cmd = input()
print("Bye!")
