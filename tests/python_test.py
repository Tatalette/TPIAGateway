# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 23:17:36 2024

@author: PC
"""
import random as rand

def put_letter(char:str,word:str)->list:
    if word and char:
        position = []
        for i in range(len(word)):
            if char == word[i]:
                position.append(i)
    else:
        position = "Error in char or word "
    return position

def outPutStr(word:str,l_list:list[int])->str:
    if word:
        hash_word = ""
        for i in range(len(word)):
            if i in l_list:
                hash_word += str(word[i])+" "
            else:
                hash_word += "_ "
    else:
        hash_word = "Error : no word "
    return hash_word

def runGame():
    list_word = []
    difficulty = input("Tapez : easy, normal ou hard pour choisir le niveau de difficulté")
    with open("./pli07.txt","r") as f:
        for line in f:
            word_l = len(line)-1
            if difficulty == "easy":
                if 4 <= word_l <= 6:
                    list_word.append(line)
            elif difficulty == "normal":
                if 7 <= word_l <= 8:
                    list_word.append(line)
            else:
                if 9<= word_l:
                    list_word.append(line)
    #Select random word in list
    word_rand = list_word[rand.randint(0,len(list_word)-1)]
    #create list with index in it
    find_word = []
    print("Jeu du pendu, nombre de lettres à trouver : ",outPutStr(word_rand, []))
    start = True
    pendu = ["","|______","|/ \ ","| T ","| O ","|---] "]
    error = 0
    print(word_rand)
    while start:
        letter = input("Veuillez saisir une lettre : ")
        if letter.upper() in word_rand.upper() and word_rand.index(letter.upper()) not in find_word:
            for i in range(len(word_rand)):
                if letter.upper() == word_rand[i].upper():
                    find_word.append(i)
                    print(find_word)
        else:
            error += 1
        print("Etat du mot : ",outPutStr(word_rand, find_word))
        print("Etat du pendu : ")
        for i in range(error,0,-1):
            print(pendu[i])
        if len(find_word)==len(word_rand):
            print("VICTOIRE")
            start = False
        elif error == 5:
            for i in range(error):
                print("PERDU")
                print(pendu[i])
                start = False
    
                 
def main():
    """
    Point d'entrée du programme.
    """
    print("TEST PUT LETTER ")
    print("Test avec o dans bonjour : ", put_letter("o","bonjour"))
    print("Test avec j dans ours : ", put_letter("j","ours"))
    print("-----------------------------")
    print("TEST OUTPUTSTR")
    print("Test avec bonjour, [0,1,5] : ", outPutStr("bonjour",[0,1,5]))
    print("Test avec chouette, [2,3,21] : ", outPutStr("chouette",[2,3,21]))
    print("-----------------------------")
    runGame()

if __name__ == "__main__":
    print("Le script est exécuté directement.")
    main()
else:
    print("Le script est importé comme un module.")
    