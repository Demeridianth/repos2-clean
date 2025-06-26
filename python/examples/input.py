def get_input(prompt, converter=str):
    while True:
        try:
            return converter(input(prompt))
        except ValueError:
            print('enter valid parameter')


def get_user_input(prompt, converter=str):
    return converter(input(prompt))


def get_choice(prompt, choices):
    while True:
        user_input = input(f'{prompt}' )
        if user_input in choices:
            return user_input
        else:
            print('enter valid choice')




#1

# questions = ["What is your name?", "What is your favorite color?", "What is your quest?"]
# n = 0
# while True:
#     print("Type q to quit")
#     answer = input(questions[n])
#     if answer == "q":
#         break
#     n = (n + 1) % 3
    
#     # n += 1
#     # if n > 2:
#     #    n = 0

# print(n)




#2

questions = ['What is your name?', 'What is your favorite color?', 'What is your quest?']
n = 0
while True:
    print('Type q to quit')
    answer = input(questions[n])
    if answer == 'q':
        break
    n += 1
    if n > 2:
        n = 0
