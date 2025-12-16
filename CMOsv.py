#!/usr/bin/env python3
"""
Парсер учебного конфигурационного языка (вариант 18) в XML
"""

import sys
import re
import argparse
from typing import Dict, List, Any, Union


class ConfigParser:
    def __init__(self):
        self.constants: Dict[str, Any] = {}

    #
    #  ЧИСЛА
    #
    def parse_number(self, token: str) -> Union[int, float, str]:
        try:
            return int(token)
        except ValueError:
            try:
                return float(token)
            except ValueError:
                return token

    #
    #  МАССИВЫ: ТОЛЬКО ФОРМАТ '(
    #
    def parse_array(self, tokens: List[str]) -> tuple[List[Any], int]:
        result = []
        i = 0

        while i < len(tokens):
            token = tokens[i]

            # Конец массива
            if token == ')':
                break

            # Вложенный массив — обязательно "'("
            elif token == "'(":
                nested, consumed = self.parse_array(tokens[i + 1:])
                result.append(nested)
                i += consumed + 1

            # Вложенный словарь
            elif token == '([':
                nested, consumed = self.parse_dict(tokens[i:])
                result.append(nested)
                i += consumed - 1

            # Число
            elif re.match(r'^[+-]?([1-9][0-9]*|0)$', token):
                result.append(self.parse_number(token))

            # Константа
            elif token in self.constants:
                result.append(self.constants[token])

            # Строка (по ТЗ их нет, но токен может попасть)
            else:
                result.append(token)

            i += 1

        return result, i + 1

    #
    #  СЛОВАРЬ ([ KEY : VALUE ])
    #
    def parse_dict(self, tokens: List[str]) -> tuple[Dict[str, Any], int]:
        result = {}
        i = 1  # пропускаем '(['

        while i < len(tokens):
            token = tokens[i]

            # Конец словаря
            if token == '])':
                break

            # Игнорируем скобки — они могут остаться после массивов
            if token in ('(', ')'):
                i += 1
                continue

            # Убираем хвосты ]
            clean_token = token.rstrip(']') if token.endswith(']') else token

            # Проверка имени по ТЗ
            if not re.match(r'^[_A-Z][_a-zA-Z0-9]*$', clean_token):
                i += 1
                continue

            key = clean_token
            i += 1

            # Должен быть ':'
            if i >= len(tokens) or tokens[i] != ':':
                raise ValueError(f"Expected ':' after key {key}")
            i += 1

            # Значение должно идти
            if i >= len(tokens):
                raise ValueError(f"Expected value after ':' for key {key}")

            value_token = tokens[i]
            clean_value = value_token.rstrip(']') if value_token.endswith(']') else value_token

            #
            # Значение — массив
            #
            if clean_value == "'(":
                i += 1
                value, consumed = self.parse_array(tokens[i:])
                result[key] = value
                i += consumed

            #
            # Значение — словарь
            #
            elif clean_value == '([':
                value, consumed = self.parse_dict(tokens[i:])
                result[key] = value
                i += consumed - 1

            #
            # Выражение
            #
            elif clean_value == '|':
                expr_tokens = []
                i += 1
                while i < len(tokens) and tokens[i] != '|':
                    expr_tokens.append(tokens[i])
                    i += 1
                if i >= len(tokens):
                    raise ValueError("Unclosed expression")
                result[key] = self.evaluate_postfix(expr_tokens)
                i += 1

            #
            # Константа
            #
            elif clean_value in self.constants:
                result[key] = self.constants[clean_value]
                i += 1

            #
            # Число
            #
            elif re.match(r'^[+-]?([1-9][0-9]*|0)$', clean_value):
                result[key] = self.parse_number(clean_value)
                i += 1

            #
            # Строка
            #
            else:
                result[key] = clean_value
                i += 1

            if i < len(tokens) and tokens[i] == ',':
                i += 1

        return result, i + 1

    #
    #  ВЫЧИСЛЕНИЕ ПОСТФИКСА
    #
    def evaluate_postfix(self, tokens: List[str]) -> Any:
        stack = []
        i = 0

        while i < len(tokens):
            token = tokens[i]

            # Служебные скобки — игнорируем
            if token in ('(', ')'):
                i += 1
                continue

            # mod()
            if token == 'mod()':
                b = stack.pop()
                a = stack.pop()
                stack.append(a % b)
                i += 1
                continue

            # concat()
            if token == 'concat()':
                b = stack.pop()
                a = stack.pop()
                stack.append(str(a) + str(b))
                i += 1
                continue

            # +
            if token == '+':
                b = stack.pop()
                a = stack.pop()
                stack.append(a + b)
                i += 1
                continue

            # -
            if token == '-':
                b = stack.pop()
                a = stack.pop()
                stack.append(a - b)
                i += 1
                continue

            # Константа
            if token in self.constants:
                stack.append(self.constants[token])
                i += 1
                continue

            # Число
            if re.match(r'^[+-]?([1-9][0-9]*|0)$', token):
                stack.append(self.parse_number(token))
                i += 1
                continue

            # Идентификатор / строка
            stack.append(token)
            i += 1

        return stack[0] if stack else None

    #
    #  ОСНОВНОЙ ПАРСЕР
    #
    def parse(self, text: str) -> Dict[str, Any]:
        # Удаляем комментарии
        lines = text.split("\n")
        cleaned = []
        in_ml = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith("\\"):
                continue

            if line.startswith("=begin"):
                in_ml = True
                continue

            if line.startswith("=cut"):
                in_ml = False
                continue

            if in_ml:
                continue

            cleaned.append(line)

        code = " ".join(cleaned)

        #
        # Токенизация
        #
        tokens = []
        i = 0
        while i < len(code):

            if code[i].isspace():
                i += 1
                continue

            # Мультисимвольные токены
            if code[i:i+2] == "'(":
                tokens.append("'(")
                i += 2
                continue

            if code[i:i+2] == "(['":
                tokens.append("(['")
                i += 2
                continue

            if code[i:i+2] == "(['":
                pass

            if code[i:i+2] == "(['":
                pass

            if code[i:i+2] == "([":
                tokens.append("([")
                i += 2
                continue

            if code[i:i+2] == "])":
                tokens.append("])")
                i += 2
                continue

            # Односимвольные токены
            if code[i] in "()|,:;=":
                tokens.append(code[i])
                i += 1
                continue

            # Идентификатор/число
            j = i
            while j < len(code) and not code[j].isspace() and code[j] not in "()|,:;=":
                j += 1
            tokens.append(code[i:j])
            i = j

        #
        # Обработка констант
        #
        i = 0
        new_tokens = []
        while i < len(tokens):

            if tokens[i] == "set" and i + 3 < len(tokens) and tokens[i+2] == '=':
                name = tokens[i+1]
                value_token = tokens[i+3]

                # set X = | ... |
                if value_token == "|":
                    expr = []
                    j = i+4
                    while j < len(tokens) and tokens[j] != "|":
                        expr.append(tokens[j])
                        j += 1
                    if j >= len(tokens):
                        raise ValueError("Unclosed expression")
                    self.constants[name] = self.evaluate_postfix(expr)
                    i = j + 1

                # set X = NUMBER
                elif re.match(r'^[+-]?([1-9][0-9]*|0)$', value_token):
                    self.constants[name] = self.parse_number(value_token)
                    i += 4

                # set X = TOKEN
                else:
                    self.constants[name] = value_token
                    i += 4

                if i < len(tokens) and tokens[i] == ';':
                    i += 1

                continue

            new_tokens.append(tokens[i])
            i += 1

        tokens = new_tokens

        #
        # Основной словарь
        #
        result = {}
        i = 0
        while i < len(tokens):
            if tokens[i] == "([":
                d, consumed = self.parse_dict(tokens[i:])
                result.update(d)
                i += consumed
            else:
                i += 1

        return result

    #
    #  XML
    #
    def to_xml(self, data: Dict[str, Any], indent: int = 0) -> str:
        xml = []
        sp = "  " * indent

        for key, value in data.items():

            if isinstance(value, dict):
                xml.append(f"{sp}<{key}>")
                xml.append(self.to_xml(value, indent + 1))
                xml.append(f"{sp}</{key}>")

            elif isinstance(value, list):
                xml.append(f"{sp}<{key}>")
                for item in value:
                    if isinstance(item, dict):
                        xml.append(self.to_xml({"item": item}, indent + 1))
                    else:
                        xml.append(f"{sp}  <item>{item}</item>")
                xml.append(f"{sp}</{key}>")

            else:
                xml.append(f"{sp}<{key}>{value}</{key}>")

        return "\n".join(xml)


#
#  MAIN
#
def main():
    parser = argparse.ArgumentParser(description="Конфигурационный парсер (вариант 18)")
    parser.add_argument("-o", "--output", required=True)
    args = parser.parse_args()

    text = sys.stdin.read()
    parser_obj = ConfigParser()

    try:
        data = parser_obj.parse(text)
        xml = f'<?xml version="1.0" encoding="UTF-8"?>\n<config>\n{parser_obj.to_xml(data, 1)}\n</config>'

        with open(args.output, "w", encoding="utf-8") as f:
            f.write(xml)

        print(f"Успешно сконвертировано в {args.output}")

    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
