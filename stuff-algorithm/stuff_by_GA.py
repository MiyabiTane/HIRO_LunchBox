import numpy as np
import random
import copy as dcopy
from BL_algorithm import BL_main

name_list = ["rolled_egg", "fried_chiken", "brocolli", "tomato", "octopus_wiener", "fried_chiken", "rolled_egg", "brocolli", "octopus_wiener", "tomato"]
box_list = [[4,2,2], [4,4,4], [4,4,4], [3,3,3], [2,2,3.5], [4,4,4], [4,2,2], [4,4,4], [2,2,3.5], [3,3,3]]
box_size = [12,1]
like_list = [["rolled_egg", "rolled_egg"], ["brocolli", "fried_chiken"], ["tomato", "tomato"]]
dislike_list = [["octopus_wiener", "fried_chiken"]]
"""
x: width, y: height
"""

class StuffFood():

    def __init__(self, name_list, box_list, box_size, like_list, dislike_list, indivisuals, generation):
        self.indivisuals = indivisuals
        self.generation = generation
        self.box_size = box_size
        self.name_to_index_dict = {}
        for i, food in enumerate(name_list):
            if food in self.name_to_index_dict:
                self.name_to_index_dict[food] += [i]
            else:
                self.name_to_index_dict[food] = [i]
        self.box_dict = {}
        for i in range(len(name_list)):
            self.box_dict[i] = box_list[i][:2]
        #print(self.box_dict)
        self.cand_list = []
        init_list = [i for i in range(len(name_list))]
        for i in range(indivisuals):
            copy = dcopy.deepcopy(init_list)
            random.shuffle(copy)
            self.cand_list.append(copy)
        self.cand_list = np.array(self.cand_list)
        #print(self.cand_list)
        self.like_list = like_list
        self.dislike_list = dislike_list


    def evaluate(self):

        def calc_point(list, stuff_pos, plus_flag):
            point = 0
            for food1, food2 in list:
                for index_1 in self.name_to_index_dict[food1]:
                    for index_2 in self.name_to_index_dict[food2]:
                        if stuff_pos[index_1][0] + self.box_dict[index_1][0] == stuff_pos[index_2][0]:
                            # | food1 | food2 |
                            point += 1 if plus_flag else -1
                        elif stuff_pos[index_1][1] + self.box_dict[index_1][1] == stuff_pos[index_2][1]:
                            # food1
                            # -----
                            # food2
                            point += 1 if plus_flag else -1
            return point

        points = []
        for lst in self.cand_list:
            point = 0
            stuff_pos = BL_main(lst, self.box_dict, self.box_size)
            #if satisfy the like condition, point +=1
            point += calc_point(self.like_list, stuff_pos, plus_flag = True)
            #if satisfy the dislike condition, point -=1
            point += calc_point(self.dislike_list, stuff_pos, plus_flag = False)
            points.append(point)
        points = map(lambda x: x-(min(points)), points)
        points = map(lambda x: float(x)/float(sum(points)), points)
        print(points)

    #To Do--------------------------




stuff = StuffFood(name_list, box_list, box_size, like_list, dislike_list, 10, 100)
stuff.evaluate()
        




