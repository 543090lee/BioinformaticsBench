import openai
import numpy as np
import operator
import argparse
import json
import math
import os
import sys

# from prompt import prompt

from post_filter import parse_answer, remove_not, cal_not,parse_not
openai.api_key = os.getenv("OPENAI_API_KEY")

#SEUNGMO LEE

def zero(sys, problem, stage=1, exp=""):
    if sys !="":
        
        messages=[{"role": "system", "content": sys}]
    else:
        messages=[]
    test_question= "Q: " + problem + "\n" + "A: The answer is"
    messages+=[
            {"role": "user", "content": test_question}
          ]
    return messages
   

def equiv(model_output, answer):
    model_output=model_output.replace(',', '')
    try:
        ans=float(answer.strip())
        if ans >=1:
            first=math.isclose(float(model_output.strip()), ans, abs_tol=0.1)
        else:
            first=math.isclose(float(model_output.strip()), ans, rel_tol=0.1)
    except:
        first=False
    try: 
        model=model_output.strip().split()[0]
        if ans >=1:
            second=math.isclose(float(model_output.strip()), ans, abs_tol=0.1)
        else:
            second=math.isclose(float(model_output.strip()), ans, rel_tol=0.1)
    except:
        second=False
    if first or second:
        return True
    return False

def equiv_word(model_output, answer):
    output_c = model_output.upper()
    answer_c = answer.upper()

    if output_c == answer_c:
        return True
    else:
        return False

def run(file, engine, start_n, sys):
    outputs = []
    answers = []
    types = []
    list_equiv = []
    model_outputs=[]
    ls_dict=[]

    correct = 0
    total = 0
    count=0
    sys_name=""
    with open("../data/{}.json".format(file), encoding='utf-8') as json_file:
        problems=json.load(json_file)
        for problem_data in problems:
                count+=1
                if count<=start_n:
                    continue
                prob_book = problem_data["type"]
                if problem_data["numeric"] == "y":
                    isnumeric = True
                else:
                    isnumeric = False

        model_output_ori = "The Needleman-Wunsch Algorithm does use dynamic programming to find the optimal alignment between two sequences. Therefore, the answer, according to your formatting request, is \( \boxed{0} \)."
        model_output = parse_answer(model_output_ori)
        answer = "0"
        
        print("Model's output:")
        print(model_output)
        print("Correct answer:")
        print(answer)
        print("--------------------------------------------")
        try:
            if isnumeric:
                res_equiv = equiv(model_output, answer)
            else:
                res_equiv = equiv_word(model_output, answer)

        except:
            res_equiv = False
        if res_equiv:
            correct += 1
        total += 1

        list_equiv.append(res_equiv)
        ls_dict.append({'correct': res_equiv, 'gpt solution': model_output_ori, "correct answer": answer+"@@"+problem_data["unit"],
                        "gpt answer": model_output, "source book": prob_book})
        if total % 1==0:
            with open("./output_zero{}/{}_dict_{}_{}_{}.json".format(sys_name, engine, sys_name, start_n,file), 'w') as fout:
                json.dump(ls_dict, fout)
            with open("./output_zero{}/{}_{}_{}_{}.txt".format(sys_name, engine,sys_name, start_n,file), "w+") as f:
                for k, (output, answer, correctness, model_output) in enumerate(zip(outputs, answers, list_equiv, model_outputs)):
                    f.write("\n{} Correct: {} | OUTPUT: {} | ANSWER: {} | gpt: {}\n".format(k, correctness, output, answer, model_output))

                f.write("#####################\n")
                print("#####################")
                f.write("#####################\n")
                print("Total Accuracy = {}/{} = {:.3f}".format(correct, total, correct/total))
                f.write("Total Accuracy = {}/{} = {:.3f}\n".format(correct, total, correct/total))

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--engine', type=str, default='gpt-4')
    parser.add_argument('--sys', action='store_true')
    parser.add_argument('--start_num', type=int, default=0)   
    parser.add_argument('--list_source', nargs='+', default=["alignment"])
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    for source in args.list_source:
        run(source,args.engine, args.start_num, args.sys)
