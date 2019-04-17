# -*- coding: utf-8 -*-
import random
import os

# Function to generate a number for guess attempts
def udf_number_generator(A,Aux,B,numbers_discarded):
    Aux = A
    valid = False
    Qnumber_guess = 0
    while (valid == False):
        Qnumber_guess = random.randrange(Aux,B+1)
        # Numbers discarded case
        if (Qnumber_guess in numbers_discarded):
            continue
        # Excluding A case
        elif (Qnumber_guess == A):
            continue
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

        Aux = A
        # Get number of attempts for Ti case
        try:
            attempts_guess=int(input())
        except Exception as e:
            os._exit(0)

        Qnumber_guess = udf_number_generator(A,A,B,numbers_discarded)
        while (attempts < attempts_guess):
            print(Qnumber_guess)
            try:
                judge_answers=input()
            except Exception as e:
                os._exit(0)

            if(judge_answers == judge_options[0]):
                #print ("TOO_SMALL")
                attempts+=1
                if (attempts != attempts_guess):
                    numbers_discarded.append(Qnumber_guess)
                    A = Qnumber_guess
                    Qnumber_guess = udf_number_generator(A,Aux,B,numbers_discarded)

            elif(judge_answers == judge_options[1]):
                #print ("TOO_BIG")
                attempts+=1
                if (attempts != attempts_guess):
                    numbers_discarded.append(Qnumber_guess)
                    B = Qnumber_guess
                    Qnumber_guess = udf_number_generator(A,Aux,B,numbers_discarded)

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
