# -*- coding: utf-8 -*-
import random
import os

# Function to generate a number for guess attempts
def udf_number_generator(A,Aux,B,numbers_discarded):
    valid = False
    Aux = A
    while (valid == False):
        Qnumber_guess = random.randrange(Aux,B)
        # Numbers discarded case
        if (Qnumber_guess in numbers_discarded):
            valid == False
        # Excluding A case
        elif (Qnumber_guess == A):
            valid == False
        else:
            valid = True
    return Qnumber_guess

# Function to guess the number
def udf_number_guess():
    judge_options=["TOO_SMALL","TOO_BIG","CORRECT","WRONG_ANSWER"]
    cases = 0
    attempts = 0
    numbers_discarded = []
    error_program = False
    # Get test cases
    try:
        T = int(input())
    except Exception as e:
        os._exit(0)
    while (cases!=T):
        # Get limits
        try:
            limits=input().split(" ")
            A=int(limits[0])
            B=int(limits[1])
        except Exception as e:
            os._exit(0)

        # Get number of attempts for Ti case
        try:
            attempts_guess=int(input())
        except Exception as e:
            os._exit(0)

        while (attempts < attempts_guess):
            Qnumber_guess = udf_number_generator(A,A,B,numbers_discarded)
            print(Qnumber_guess)
            try:
                judge_answers=input()
            except Exception as e:
                os._exit(0)

            if(judge_answers == judge_options[0]):
                #print ("TOO_SMALL")
                numbers_discarded.append(Qnumber_guess)
                udf_number_generator(Qnumber_guess,A,B,numbers_discarded)
                attempts+=1

            elif(judge_answers == judge_options[1]):
                #print ("TOO_BIG")
                numbers_discarded.append(Qnumber_guess)
                udf_number_generator(A,A,Qnumber_guess,numbers_discarded)
                attempts+=1

            elif(judge_answers == judge_options[2]):
                #print ("CORRECT")
                break

            elif(judge_answers == judge_options[3]):            
                #print ("WRONG_ANSWER")
                break
            # Validating wrong input
            else:
                #print ("error 1")
                error_program = True
                break
        Qnumber_guess = attempts = 0
        numbers_discarded = []
        cases+=1
        # Unexpected exit
        if(error_program):
            #print ("error 2")
            break

def main():
    udf_number_guess()

if __name__ == '__main__':
    main()
