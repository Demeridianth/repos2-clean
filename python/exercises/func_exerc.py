from typing import Callable
from datetime import datetime


# Функция должна принимать любой dict и возвращать dict,
    # в котором ключи и значения поменялись местами. 

# def foo(d):
#     my_dict = {}
#     for key, value in d.items():
#         my_dict[value] = key
#     return my_dict    

# c = {'c': 3, 'd': 4, 'z': 5}    
# d = {'a': 1, 'b': 2}
# assert foo(c))



  # Функция должна принимать список списков и объединять их в один

# def foo(l):
#     a = str(l)
#     b = a.replace('[', '').replace(']', '').split(', ')
 
#     c = []
#     for i in b:
#         if i != '':
#             c.append(int(i))
#     return c
    
# l = [['1', '2'], [], ['6', '7', '8']]

# assert foo(l))


# def foo(l):
#     my_list = []
#     for i in l:
#         for a in i:
#             my_list.append(a)
#     return my_list

# l = [[1, 4, 6], [], ['2', '6']]
# assert foo(l))









# Функция принимает два списка одной длины (это важно)
    # Возвращает словарь, в котором ключи - значения первого списка, значения - из второго


#1

# def foo(n1, n2):
#     lst = {}
#     index_to_key = {}

#     for index, key in enumerate(n1):
#         index_to_key[index] = key

#     for index, value in enumerate(n2):
#         key = index_to_key[index]
#         lst[key] = value 

#     return lst



#2

# def foo(keys, values):
#     lst = {}
#     for i in range(len(keys)):
#         key = keys[i]
#         value = values[i]
#         lst[key] = value
        
#     return lst


#3 shortest

# def combine(list1, list2):
#     lst = {}

#     for i in range(len(list1)):
#             lst[list1[i]] = list2[i]
#     return lst

# n1 = [1, 2, 3]
# n2 = ['a', 'b', 'c']

# assert foo(n1, n2))




# Написать функцию, которая принимает два списка и возвращает список с числами находящимися в обоих списках.
#1

# def foo(numbers1, numbers2):
#     lst = []
#     for i in numbers1:
#         if i in numbers2:
#             lst.append(i)
#     return lst

# numbers1 = [1, 2, 3]
# numbers2 = [2, 5, 'c']

# assert foo(numbers1, numbers2))

# 2

# def foo(numbers1, numbers2):
#     lst = []
#     for i in numbers1:
#         for a in numbers2:
#             if i == a:
#                 lst.append(i)
#     return lst

# numbers1 = [1, 2, 3]
# numbers2 = [2, 5, 'c']

# assert foo(numbers1, numbers2))






# 1. Написать функцию, которая принимает списkи и проверяет, все
# ли элементы второго списка содержатся в первом
# def contains(a, b):
    # Например:
    # a = [1, 2, 3, 4]
    # b = [1, 2]
    # с = [1, 3, 8]
    # contains(a, b) возвращает True
    # contains(a, c) возвращает False

# def contains(a, b):
#     for i in b:
#         if i not in a:
#             return False
#     return True

           
# a = []
# b = []
# c = [1, 2, 8]

# assert contains(a, b))







# 2. Написать функции для шифрования и дешифрования сообщения
# def encrypt_message(message, secret_key):
#     message - сообщение строчными буквами, которое нужно 
#     зашифровать
    
#     secret_key - строка из 26 уникальных непробельных 
#     символов, которыми нужно заменять соответствующие 
#     (по порядковому номеру) буквы английского алфавита.
    
#     Другими словами, первым символом из secret_key мы будем 
#     заменять букву "a", второй - букву b и так далее
#     Например для message "i am a dog" и 
#     и secret_key "rmneabghxjcdfiopktulqwzysv"
#     получится "h xf x nob"

# def decrypt_message(encrypted_message, secret_key):
#     обратная операция

# def encrypt_message(message, secret_key):
#     alph = 'abcdefghijklmnopqrstuvwxyz'
    
#     encrypt = {}
#     lst = []
 
#     for i in range(len(alph)):
#         key = alph[i]
#         value = secret_key[i]
#         encrypt[key] = value
   
#     for i in message:
#         if i not in alph:
#             lst.append(i) 
#         else:
#             lst.append(encrypt[i])
        
#     return ''.join(lst)


# def decrypt_message(encrypted_message, secret_key):
#     alph = 'abcdefghijklmnopqrstuvwxyz'
#     decrypt = {}
    # lst = []

    # for i in range(len(secret_key)):
    #     key = secret_key[i]
    #     value = alph[i]
    #     decrypt[key] = value

#     for i in encrypted_message:
#         if i not in secret_key:
#             lst.append(i)
#         else:
#             lst.append(decrypt[i])
#     return ''.join(lst)

# secret_key = "rmneabghxjcdfiopktulqwzysv"
# message = '1, 2, 3, 4'
# a = encrypt_message(message, secret_key)
# assert a)
# b = decrypt_message(a, secret_key)
# assert b)
















    

    # ****************************************
















# Получает на вход две строки ОДИНАКОВОЙ длины n, text1 и text2 и возвращает
#     строку длины 2n, построенную по принципу:
#     - первый символ первой строки, первый символ второй строки
#     - второй символ первой строки, второй символ второй строки
#     - ...
#     - n-ный символ первый строки, n-ный элемент второй строки
# # def first_first(str1, str2):

#     numbers = []
#     for i in range(len(str1)):
#         numbers.append(str1[i])
#         numbers.append(str2[i])
#     return ''.join(numbers)

# assert by_numbers('1', '2'))






# Получает на вход две строки ОДИНАКОВОЙ длины n, text1 и text2 и возвращает
#     строку длины 2n, построенную по принципу:
#     - первый символ первой строки, n символ второй строки
#     - второй символ первой строки, n-1 символ второй строки
#     - ...
#     - n-ный символ первый строки, первый элемент второй строки


#1

# def first_last(str1, str2):
#     numbers = []
#     str2_b = str2[::-1]
#     for i in range(len(str1)):
#         numbers.append(str1[i])
#         numbers.append(str2_b[i])
#     return ''.join(numbers)

#2

# def first_last(str1, str2):
#     lst = []

#     for i in range(len(str1)):
#         lst.append(str1[i])
#         lst.append(str2[ - 1 - i])
#     return ''.join(lst)

# assert by_numbers('12', '34'))
# assert by_numbers('12', '34'))
# assert by_numbers('12', '34'))
# assert by_numbers('12', '34'))
# assert by_numbers('12', '34'))
# assert by_numbers('12', '34'))





# Получает на вход список целых чисел и возвращает True, если все они четные
#     и False в противном случае. Если передан пустой список, генерирует ValueError

#1:

# for i in numbers:
    #     if i % 2 == 0:
    #         continue
    #     else:
    #         return False
    # return True

#2:

# def all_even(numbers):
#     # if numbers == []:
#     if not numbers:
#         raise ValueError

#     for i in numbers:
#         if i % 2 != 0:
#             return False
        
#     return True


# assert all_even([2, 4]))



#  PALINDROME

# 1

# def is_palindrome(text):
#     text_length = len(text)
#     text_last_index = text_length - 1

#     for i in range(text_length):
#         left_char = text[i]
#         right_char = text[text_last_index - i]
#         if left_char != right_char:
#             return False

#     return True


# 2

# def is_palindrome(text):
#     text_length = len(text)
#     text_last_index = text_length - 1


#     for i in range(text_length):
#         left_index = i
#         right_index = text_last_index - i

#         if left_index >= right_index:
#             break

#         left_char = text[left_index]
#         right_char = text[right_index]
        
#         if left_char != right_char:
#             return False

#     return True


# assert is_palindrome(''))
# assert is_palindrome('a'))
# assert is_palindrome('aa'))
# assert is_palindrome('ab'))
# assert is_palindrome('aba'))
# assert is_palindrome('abb'))
# assert is_palindrome('abab'))
# assert is_palindrome('abba'))


   
# 3 (shortest)

# def if_palindrome(text1):

#     for i in range(len(text1)):
#    
#         if i >= len(text1[- 1 - i]):
#             break 

#         if text1[i] != text1[- 1 - i]:
#             return False
#     return True




# 4 (SLICE)

# def if_palindrome(text):
#     text_back = text[::-1]
#     for i in range(len(text)):
#         if text[i] != text_back[i]:
#             return False
#     return True


# text = 'abz1zba'
# assert if_palindrome(text))








# Проверить, что строка text2 является анаграммой строки text1. Другими
#     словами, проверить что text2 можно получить, переставив порядок букв в text1.

#     >>> check_is_anagram('', '')
#     True

#     >>> check_is_anagram('a', 'a')
#     True

#     >>> check_is_anagram(ab', 'ab')
#     True

#     >>> check_is_anagram('ab', 'ba')
#     True

#     >>> check_is_anagram('a', 'b')
#     False

#     >>> check_is_anagram('abbc', 'abcc')
#     False

#sorted()????????

# def if_anagram(text1, text2):
    # if len(text1) != len(text2):
    #     return False
    
    # for i in text2:
    #     if i not in text1:
    #         return False 
    
    # t1 = {}
    # t2 = {}
    # for i in text1:
    #     if i in t1:
    #         t1[i] += 1
    #     else:
    #         t1[i] = 1
    
    # for i in text2:
    #     if i in t2:
    #         t2[i] += 1
    #     else: 
    #         t2[i] = 1

    # if t1 != t2:
    #     return False
    # return True


# def if_anagram(text1, text2):
#     t1 = {}
#     t2 = {}

#     for i in text1:
#         if i not in t1:
#             t1[i] = 0

#         t1[i] += 1 

    
#     for i in text2:
#         if i in t2:
#             t2[i] += 1
#         else: 
#             t2[i] = 1

#     if t1 != t2:
#         return False
#     return True


# assert if_anagram('baab', 'bbaa'))


# def pairs_to_n(numbers: list[int], n: int) -> list[tuple[int, int]]:
    # """
    # Найти в списке целых чисел numbers все пары чисел, которые в сумме дают
    # значение n. Вернуть список, каждым элементом которого является кортеж из
    # двух элементов, содержащих пары чисел в numbers, которые в сумме дают n.
    # [1, 2]

# def pairs_to_n(numbers, n):
#     lst = []
#     for i in range(len(numbers)):
#         for z in range(i + 1, len(numbers)):
            
#             if numbers[i] + numbers[z] == n:
#                 lst.append((numbers[i], numbers[z]))
#     return lst

# assert pairs_to_n([50, 50, 20, 20], 100) == [(50, 50)]  

# assert pairs_to_n([50, 80, 3, 50, 20, 20], 100) == [(50, 50)] 
# assert pairs_to_n([50, 3, 50, 20, 20], 100) == [(50, 50)] 
# assert pairs_to_n([50, 3, 50, 20, 20], 100) == [(50, 50)] 





# def task_2(numbers: list[int]) -> tuple[int, list[int]]:
    
    # Найти в списке целых числ numbers самое часто встречающееся число и вернуть
    # кортеж. в котором:
    # - первым элементом является это число
    # - вторым элементом является список индексов этих чисел в списке (в каких позициях
    #   списка numbers это число встречалось).

# 1 works but not good

# def most_common_number(numbers):

#     n1 = {}
    # lst_number = 0
    # lst_index = []

    # for i in numbers:
    #     if i not in n1:
    #         n1[i] = 0
    #     n1[i] += 1
    
    # for i in n1:
    #     for z in n1:
    #         if n1[i] > n1[z]:
    #             if n1[i] > lst_number:
    #                 lst_number = i
    
    # for index, number in enumerate(numbers):
    #     if number == lst_number:
    #         lst_index.append(index)

    # for i in range(len(numbers)):
    #     if numbers[i] == lst_number:
    #         lst_index.append(i)

    # lst = (lst_number, lst_index)
              
    # return lst



#2 

    # number_count = {}
    # most_frequent_number = None
    # most_frequent_number_count = None
    # lst_index = []


    # for n in numbers:
    #     if n not in number_count:
    #         number_count[n] = 0
    #     number_count[n] += 1

    # for number, count in number_count.items():
    #     if most_frequent_number == None:
    #         most_frequent_number = number
    #         most_frequent_number_count = count
    #     elif count > most_frequent_number_count:
    #         most_frequent_number = number
    #         most_frequent_number_count = count

    # for i in range(len(numbers)):
    #     if numbers[i] == most_frequent_number:
    #         lst_index.append(i)

    # lst = (most_frequent_number, lst_index)

    # return lst



#3

    # number_counts = {}
    # most_frequent_number = None
    # most_frequent_number_count = 0
    # lst_index = []

    # for n in numbers:
    #     if n not in number_counts:
    #         number_counts[n] = 0
    #     number_counts[n] += 1
    
    #     if number_counts[n] > most_frequent_number_count:
    #         most_frequent_number = n
    #         most_frequent_number_count = number_counts[n]

    # for i in range(len(numbers)):
    #     if numbers[i] == most_frequent_number:
    #         lst_index.append(i)
    
    # lst = (most_frequent_number, lst_index)

    # return lst


#4 (shortest)

    # def first_s(numbers):
    # most_common_number = 0
    # most_common_number_count = 0
    # most_common = {}
    # index_lst = []

    # for n in numbers:
    #     if n not in most_common:
    #         most_common[n] = 0
    #     most_common[n] += 1

    #     if most_common[n] > most_common_number_count:
    #         most_common_number = n
    #         most_common_number_count = most_common[n]
    #

    # for n in range(len(numbers)):
    #     if numbers[n] == most_common_number:
    #         index_lst.append(n)

    # lst = (most_common_number, index_lst)

    # return lst




# assert most_common_number([1, 2, 3, 3, 3]))
# assert most_common_number([1, 2, 2, 2, 3, 4]))
# assert most_common_number([1, 1, 1, 1, 1, 4, 5]))
# assert most_common_number([]))
# assert most_common_number([1, 2, 3, 4, 5]))
# assert most_common_number([1, 2, 2, 3, 3, 4, 5]))













##################################################













    
    
   



# def devide_in_two(numbers, predicate):
#     to_true = []
#     to_false = []

#     for i in numbers:
#         if predicate(i):
#             to_true.append(i)
#         else:
#             to_false.append(i)

#     return (to_true, to_false)


# def is_odd(number):
#     return number % 2 == 0

# assert devide_in_two([1, 2, 3, 4], is_odd) == ([1, 3], [2, 4])






# function in function

# def print_greeting(name, create_greeting_text):
#     greeting_text = create_greeting_text(name)
#     assert greeting_text)
    
# def say_hi(name):
#     return f' Hi {name}'

# print_greeting('Bob', say_hi)









# def is_odd(number):
#     return number % 2 == 1

# def is_even(number):
#     return number % 2 == 0


# def is_from_five(number):
#     return number % 5 == 0


# def is_more_then_ten(number):
#     return number > 10


# def print_by_one(numbers, number_filter):
#     for i in numbers:
#         if number_filter(i):
#             assert i)

# print_by_one([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], is_odd)
# print_by_one([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], is_even)
# print_by_one([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], is_from_five)
# print_by_one([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], is_more_then_ten)



# def mutate_numbers(numbers: list[int], modifier_func: Callable[int, int]) -> list[int]:
    
    # :param numbers: Список чисел
    # :param modifier_func: Функция-преобразователь, которая получает число и 
    #     возвращает каким-то образом измененную его версию. Мы не знаем, каким. 
    #     Например это может быть функция, которая для любого числа **n** 
    #     возвращает **n + 1**.
    # :returns: Возврвщает список, в котором каждый элемент - это элемент с таким 
    #     же индексом из numbers, но пропущеный через функцию modifer_func. Например, 
    #     элемент с индексом 5 == modifier_func(numbers[5]).


# def increment(number):
#     return number + 1

# def square(number):
#     return number * number


# def mutate_numbers(numbers, modifier_func):
#     lst = []

#     for n in numbers:
        
#         lst.append(modifier_func(n))
    
#     return lst


# assert mutate_numbers([], increment) == []
# assert mutate_numbers([-1], increment) == [0]
# assert mutate_numbers([1, 2], increment) == [2, 3]


# assert mutate_numbers([], square) == []
# assert mutate_numbers([1], square) == [1]
# assert mutate_numbers([1, 2], square) == [1, 4] 







# def reduce_numbers(numbers: list[int], reduce_func: Callable[int, int, int]) -> int:
   
    # :param numbers: Список чисел, содержащий хотя бы один элемент.

    # :param reduce_func: Функция-преобразователь, которая получает два числа и  
    #     возвращает для них какой-то результат. Мы не знаем, какой. Например это 
    #     может быть функция, которая их складывает или же функция, которая их перемножает.

    # :returns: Возвращает одно число, полученное путем последовательного применения
    #     функции reducer_funс. Для каждого числа **n** из списка **numbers** в эту функцию
    #     передается результат вызова этой функции для предыдущего числа и само число.

#     Пояснение к задаче:
# - Для списка  `numbers = [1]` будет просто возвращен его единственный элемент. 
# - Для любого списка длиннее одного элемента `numbers = [1, 2, 3, 4]
#            + Возьмем первые его два элемента и применим к ним функцию 
#                reducer_func. `lst = reducer_func(numbers[0], numbers[1])`
#            + Если третьего элемента нет, вернем этот `lst`.
#            + Если третий элемент есть, то `lst = reducer_func(lst, numbers[2])
#            + и так далее
    

# def add(a, b):
#     return a + b

# def multiply(a, b):
#     return a * b

# def reduce_numbers(numbers, reduce_func):
#     lst = numbers[0]   

#     for i in range(1, len(numbers)):
#         lst = reduce_func(lst, numbers[i])

#     return lst

# assert reduce_numbers([1, 2, 3, 4], add))



# assert reduce_numbers([1], add) == 1
# assert reduce_numbers([1, 2], add) == 3
# assert reduce_numbers([1, 2, 3], add) == 6

# assert reduce_numbers([1], multiply) == 1
# assert reduce_numbers([1, 2], multiply) == 2
# assert reduce_numbers([1, 2, 3], multiply) == 6








############################################################




# У вас есть список, содержащий кортежи из двух элементов. Первый элемент - имя человека, второй - его возраст. Напишите функцию group_by_age(), которая принимает на вход список и возвращает словарь, где ключами являются значения возраста, а значениями списки имен людей с этим возрастом.

# Примеры работы данной функции:

# people = [("Alice", 25), ("Bob", 30), ("Charlie", 25), ("Dave", 35)]

# lst = group_by_age(people)

# Результат: {'25': ['Alice', 'Charlie'], '30': ['Bob'], '35': ['Dave']}


# def group_by_age(list1):
#     lst = {}

#     for name, age in list1:
#         if age in lst:
#             lst[age].append(name)
#         else:
#             lst[age] = [name]

        
    


#     return lst   

# assert group_by_age([("Alice", 25), ("Bob", 30), ("Charlie", 25), ("Dave", 35)]))








# В этой задачи вы должны, учитывая строку, заменить каждую букву её позицией в алфавите.

# Если что-то в тексте не является буквой, игнорируйте это и не возвращайте.

# «a» = 1, «b» = 2 и т.д.

# Примеры

# alphabet_position("The sunset sets at twelve o' clock.")
# Должно вернуть "20 8 5 19 21 14 19 5 20 19 5 20 19 1 20 20 23 5 12 22 5 15 3 12 15 3 11" ( это строка )






# ДОБАВИТЬ В КОНЕЦ СПИСКА

# На вход функции sort_zeros() поступает список состоящий из целых чисел. Данная функция должна вернуть этот список, отсортированный таким образом, чтобы все нули были в конце списка, а порядок остальных чисел остался бы без изменений.


# def soft_zeros(lst):
#     lst = [n for n in lst if n != 0]
#     for i in range(len(lst) -  len(lst)):
#         lst.append(0)
#     return lst

# assert soft_zeros([10, 0, 3, 0, 4, 0, 0, 5, 6, 7, 8])


#sort_seros([10, 0, 3, 0, 4, 0, 0, 5, 6, 7, 8]) --> [10, 3, 4, 5, 6, 7, 8, 0, 0, 0, 0]




#SORTED


# reverse
# lst = [4, 2, 8]
# sorted_lst = sorted(lst, reverse=True)
# assert sorted_lst)



# with key
# def take_second(x):
#     return x[1]

# my_list = [(2, 2), (3, 4), (4, 1), (1, 3)]
# sort_my_list = sorted(my_list, key=take_second)
# assert sort_my_list)




#with 2 keys
# students_info = [
#     ('Alice', 50, 18),
#     ('Jimmy', 76, 19),
#     ('Mark', 76, 18),
#     ('Elena', 43, 20),
#     ('Paul', 68, 20)
# ]

# def sorter(data):
#     marks = 100 - data[1]
#     age = data[2]
#     return marks, age

# lst = sorted(students_info, key=sorter)
# assert lst)



# credit_score_balance =  [
#     ('Jerry', 80, 1000),
#     ('Mike', 55, 2000),
#     ('Pamela', 60, 2000),
#     ('Luis', 90, 15500)
# ]

# def sorter(data):
#     credit_score = 100 - data[1]
#     ballance =  data[2]
#     return credit_score, ballance

# sorted_data = sorted(credit_score_balance, key=sorter, reverse=True)
# assert sorted_data)




# def is_anagram(a, b):
#     if sorted(a) == sorted(b):
#         return True
#     else:
#         return False
 
# def is_anagram(a, b):
#     if sorted(a) != sorted(b):
#         return False
#     return True

# assert is_anagram('thing', 'night'))


# def bigger_num(number):
#     num_str = str(number)
#     big_num = int(''.join(sorted(num_str, reverse=True)))
#     assert type(big_num))
#     return big_num
    
# assert bigger_num(2071))



# Описание

# Напишите функцию, которая путём перестановок цифр в числе возвращает наибольшее возможное число.

# Примеры

# biggerNum(2017) # Должно вернуть 7210

# biggerNum(12345) # Должно вернуть 54321


# def bigger_num(number):
#     iter_number = str(number)
#     lst =int(''.join(sorted(iter_number, reverse=True)))
#     return lst

# def bigger_num(number):
#     num = str(number)
#     result = ''
#     lst = [i for i in num]
#     for n in range(len(lst)):
#         result += (max(lst))
#         lst.remove(max(lst))
#     return result


# assert bigger_num(2017))


# lst = [1, 2, 3, 4, 5]
# max_lst = min(lst)
# assert max_lst)





# def check_if_the_sintax_is_right(text: str) -> bool:
#     lst = []
#     for k in text:
#         if k == '(':
#             lst.append(k)
#         elif k == ')' and len(lst) == 0:
#             return False
#         elif k == ')':
#             lst.pop()
#     return lst == []

# assert check_if_the_sintax_is_right('(())') == True
# assert check_if_the_sintax_is_right('())))') == False
# assert check_if_the_sintax_is_right('(()') == True


            
            


# Напишите функцию searchInsert(), которая на вход принимает отсортированный по возрастанию массив чисел и некоторое число. Необходимо найти индекс элемента массива, который равен этому числу. Если такого числа в массиве нет, то нужно вернуть индекс массива, куда это число следует вставить.

# Примеры работы данной функции:

# searchInsert([1,3,5,6], 5) --> 2
# searchInsert([1,3,5,6], 2) --> 1

### without built-in functions ###

# def search_insert(lst: list, n: int) -> int:
#     for i in range(len(lst)):
#        if n not in lst:
           
        # # elif len(lst) > n:
        #     return len(lst) + 1

            
       
        
# with index() and sorted()

# def search_insert(lst: list, n: int) -> int:
#     if n not in lst:
#        lst.append(n)
#        return sorted(lst).index(n)
#     else: 
#         return lst.index(n)

# assert search_insert([1,3,5,6], 5) == 2
# assert search_insert([1,3,5,6], 2) == 1
# assert search_insert([1,3,5,6], 3) == 1
# assert search_insert([1,3,5,6], 4) == 2
# assert search_insert([1,3,5,6], 7) == 4
# assert search_insert([1,3,5,6], 0) == 0




# def fun():
#     a = input('text: ')
#     b = input('text: ')
#     c = input('text: ')
#     return (a, b, c)

# let_a, let_b, let_c = fun()
# print(let_a, let_b, let_c)






# Напишите функцию isPerfectSquare(), которая определяет, является ли число поданное в качестве аргумента, полным квадратом другого числа. В это случае функция должна возвращать True, в противном случае False. Пользоваться встроенными функциями типа sqrt(), pow(), **0.5 запрещается. 

# isPerfectSquare(16) --> True
# isPerfectSquare(20) --> False
# isPerfectSquare(121) --> True

def is_perfect_square(n):
    i = 2
    while i * i < n:
        i += 1
    return i * i == n

######

# def is_perfect_square(num):
#     if num < 1:
#         return False
#     left, right = 1, num
#     while left <= right:
#         mid = left + (right - left) // 2
#         square = mid * mid
#         if square == num:
#             return True
#         elif square < num:
#             left = mid + 1
#         else:
#             right = mid - 1
#     return False

# print(is_perfect_square(36))







# Напишите функцию getSum(), которая принимает два целых неотрицательных числа a и b, а возвращает их сумму. При этом пользоваться операторами + и - запрещается.

# Примеры работы данной функции:

# getSum(42, 5) --> 47
# getSum(3, 7) --> 10
# getSum(4, 0) --> 4







# Напишите функцию find_missing_numbers(), на вход которой подается список длинной n, состоящий из целых чисел в диапазоне от 1 до n. Данная функция должна вернуть список всех чисел, которые отсутствуют во входящем списке, но входят в диапазон от 1 до длинны n.

# Пример работы данной функции:

# findMissedNumbers([4,3,2,7,8,2,3,1]) --> [5, 6]
# findMissedNumbers([1, 1, 1]) --> [2, 3]

# 1
# def find_missing_numbers(numbers: list) -> list:
#     return [n for n in range(1, len(numbers)) + 1 if n not in numbers]

# # 2
# def find_missing_numbers(numbers):
#     return list(set(range(1, len(numbers) + 1)) - set(numbers))


# assert find_missing_numbers([4,3,2,7,8,2,3,1]) == [5, 6]
# assert find_missing_numbers([1, 1, 1]) == [2, 3]





# Описание

# Напишите функцию count_word_occurrences, которая принимает на вход строку и возвращает словарь, содержащий количество каждого уникального слова в строке. При подсчете необходимо игнорировать регистр символов и знаки препинания.

# Примеры

# count_word_occurrences("Python is fun! Python is aboba.") # {'python': 2, 'is': 2, 'fun': 1, 'aboba': 1}
from collections import Counter
from string import punctuation





# def count_word_occurrences(s: str) -> dict:
#     for i in punctuation:
#         s = s.replace(i, "")
#     s = s.lower().split()
#     return dict(Counter(s))


# text = "Python is fun! Python is aboba."
# print(count_word_occurrences(text))







# Напишите функцию, которая будет принимать список чисел и находить среднее арифметическое всех положительных чисел в списке. Если в списке нет положительных чисел, программа должна возвращать None
# func([5, -2, 10, -8, 3]) # 6.0
# func([-1, -3, -7]) # None

# def func(lst):
#     sum = 0
#     count = 0
#     for n in lst:
#         if n > 0:
#             count += 1
#             sum += n
#     if sum > 0:
#         return sum / count
#     else:
#         return None

# print(func([5, -2, 10, -8, 3])) # 6.0
# print(func([-1, -2, -3])) # None


# reply from other programmer
# def f(lst):
#  c = [x for x in lst if x > 0]
#  return sum(c) / len(c) if c else None
 
# print(f([5, -2, 10, -8, 3])) #6.0
# print(f([-1, -3, -7])) # None

# my intepretation
# def func(lst):
#     c = []
#     for x in lst:
#         if x > 0:
#             c.append(x)
#     if c:
#         return sum(c) / len(c)
#     else:
#         return None
    
# print(func([5, -2, 10, -8, 3])) #6.0
# print(f([-1, -3, -7])) # None
    
    

    
# Даны 2 числа n, m, количество городов и количество дорог соответственно. В следующих m строках даются пути из одного города в другой. Нужно определить сколькими способами можно попасть из города 1 в город N. (Дороги имеют одностороннее движение, то есть если из первого города можно попасть во второй город, то это не значит, что можно попасть из второго в первый)

# 3 3

# 1 2
# 2 3
# 1 3
# # 2





# Oписание

# Напишите функцию find_average, которая будет принимать список чисел и возвращать среднее значение всех элементов списка.

# Примечание: Убедитесь, что функция корректно обрабатывает случай пустого списка, чтобы избежать деления на ноль.

# Примеры
# find_average([5, 10, 15, 20]) # 12.5




