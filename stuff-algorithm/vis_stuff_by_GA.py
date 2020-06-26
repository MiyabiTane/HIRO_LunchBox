import random
from copy import deepcopy
import cv2
import numpy as np

from BL_algorithm import BL_main

#box_list = [[4,2,2], [4,4,4], [4,4,4], [3,3,3], [2,2,3.5], [4,4,4], [4,2,2], [4,4,4], [2,2,3.5], [3,3,3]]
#box_size = [12,11]
#test1 ------
name_list = ["rolled_egg", "fried_chiken", "brocolli", "tomato", "octopus_wiener", "fried_chiken", "rolled_egg", "brocolli", "octopus_wiener", "tomato"]
box_list = [[80,40,40], [70,70,80], [70,70,80], [60,60,60], [40,40,70], [80,80,80], [80,40,40], [80,80,80], [40,40,70], [55,55,60]]
#test2-----
#name_list = ["rolled_egg", "fried_chiken", "brocolli", "tomato", "octopus_wiener", "fried_chiken", "rolled_egg", "brocolli", "octopus_wiener", "tomato", "rolled_egg", "fried_chiken", "tomato", "octopus_wiener", "brocolli"]
#box_list = [[50,50,50]] * len(name_list)
#-----
box_size = [180,220]
like_list = [["octopus_wiener", "octopus_wiener"], ["rolled_egg", "rolled_egg"], ["tomato", "tomato"]]
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
            copy = deepcopy(init_list)
            random.shuffle(copy)
            self.cand_list.append(copy)
        self.cand_list = np.array(self.cand_list)
        #print(self.cand_list)
        self.like_list = like_list
        self.dislike_list = dislike_list
        #for visalize
        self.name_list = name_list


    def evaluate(self):
    #output : list [int, int, int ...] sum(int) = 1
    #         represents each indivisual's probability of being next parent
        def calc_point(list, stuff_pos, plus_flag):
            point = 0
            for food1, food2 in list:
                for index_1 in self.name_to_index_dict[food1]:
                    for index_2 in self.name_to_index_dict[food2]:
                        if stuff_pos[index_1][0] + self.box_dict[index_1][0] == stuff_pos[index_2][0]:
                            #if stuff_pos[index_1][1] <= stuff_pos[index_2][1] < stuff_pos[index_2][1] + self.box_dict[index_2][1]:
                            if 0 <= stuff_pos[index_2][1] - stuff_pos[index_1][1] + self.box_dict[index_2][1]/2 <= self.box_dict[index_1][1]:
                                # | food1 | food2 |
                                point += 1 if plus_flag else -1
                        elif stuff_pos[index_1][1] + self.box_dict[index_1][1] == stuff_pos[index_2][1]:
                            #if stuff_pos[index_1][0] <= stuff_pos[index_2][0] < stuff_pos[index_2][0] + self.box_dict[index_2][0]:
                            if 0 <= stuff_pos[index_2][0] - stuff_pos[index_1][0] + self.box_dict[index_2][0]/2 <= self.box_dict[index_1][0]:
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
            #if cannot stuff, point -= 1
            for i in range(len(stuff_pos)):
                if stuff_pos[i][0] + self.box_dict[i][0] > self.box_size[0] or stuff_pos[i][1] + self.box_dict[i][1] > self.box_size[1]:
                    point -= 1
            points.append(point)
        #for_choose_parameter
        max_point = max(points)
        points = map(lambda x: x-(min(points)), points)
        if float(sum(points)) == 0:
            points = [1.0/len(points)] * len(points)
        else:
            points = map(lambda x: float(x)/float(sum(points)), points)
        #print(points)
        return points, max_point


    def partial_crossover(self, parent_1, parent_2):
        #input  : list of parents
        #output : list of children 
        num = len(parent_1)
        cross_point = random.randrange(1, num-1)
        child_1 = parent_1
        child_2 = parent_2
        for i in range(num - cross_point):
            target_index = cross_point + i
            value_1 = parent_1[target_index]
            value_2 = parent_2[target_index]
            index_1 = np.where(parent_1 == value_2)
            index_2 = np.where(parent_2 == value_1)
            child_1[target_index] = value_2
            child_2[target_index] = value_1
            child_1[index_1] = value_1
            child_2[index_2] = value_2
        return child_1, child_2


    def generate_next_generation(self):
    #update self.cand_list    
        points, max_point = self.evaluate()
        copy = deepcopy(self.cand_list)
        for i in range(self.indivisuals//2):
            index_1, index_2 = np.random.choice(len(points), 2, replace = True, p = points)
            #print(index_1, index_2)
            parent_1 = self.cand_list[index_1]
            parent_2 = self.cand_list[index_2]
            child_1, child_2 = self.partial_crossover(parent_1, parent_2)
            copy[2*i] = child_1
            copy[2*i + 1] = child_2
        self.cand_list = deepcopy(copy)
        #print(self.cand_list)


    def mutation(self, num_mutation = 3, mute_per = 0.7):
    # num_mutaiton can mutate at the percentage of mute_per 
        mutation_genes = np.random.choice(len(self.cand_list), num_mutation, replace = False)
        for index in mutation_genes:
            copy = deepcopy(self.cand_list[index])
            flag = np.random.choice(2, 1, p = [1 - mute_per, mute_per])
            if flag == 1:
                #print("mutate ", index)
                values = np.random.choice(copy, 2, replace = False)
                copy[np.where(self.cand_list[index] == values[0])] = values[1]
                copy[np.where(self.cand_list[index] == values[1])] = values[0]
            self.cand_list[index] = deepcopy(copy)
    

    def GA_main(self):
        for j in range(self.generation):
            #print(i)
            #print(self.cand_list)
            self.generate_next_generation()
            self.mutation()
            if j % 100 == 0:
                #select the one whose point is highest
                print(self.cand_list)
                points, max_point = self.evaluate()
                print("max point is", max_point)
                print(self.cand_list[(np.argmax(points))])
                best_stuff = BL_main(self.cand_list[(np.argmax(points))], self.box_dict, self.box_size)
                print(best_stuff)
                #if food overflow, keep the index in cannot_stuff
                cannot_stuff = []
                for i in range(len(best_stuff)):
                    if best_stuff[i][0] + self.box_dict[i][0] > self.box_size[0] or best_stuff[i][1] + self.box_dict[i][1] > self.box_size[1]:
                        cannot_stuff += [i]
                    else:
                        best_stuff[i] = (best_stuff[i][0] + self.box_dict[i][0]/2, best_stuff[i][1] + self.box_dict[i][1]/2)
                self.visualize(best_stuff, cannot_stuff, "test3/" + str(j) + ".png")
        print(best_stuff)
        return best_stuff, cannot_stuff


    def visualize(self, best_stuff, cannot_stuff, name):
        down = 300
        img = np.full((300,300, 3), 200, dtype=np.uint8)
        cv2.rectangle(img, (0, 0), (self.box_size[0], self.box_size[1]), (0, 0, 0))
        color_dict = {"tomato": (0,0,255), "rolled_egg": (0,255,255), "octopus_wiener": (255,0,255), "fried_chiken": (0,0,128), "brocolli": (0,128,0)}
        for i in range(len(best_stuff)):
            if i in cannot_stuff:
                point_1 = (300 - self.box_dict[i][0], down)
                point_2 = (300, down - self.box_dict[i][1])
                down -= self.box_dict[i][1]
            else:
                point_1 = (best_stuff[i][0] - self.box_dict[i][0]//2, best_stuff[i][1] - self.box_dict[i][1]//2)
                point_2 = (best_stuff[i][0] + self.box_dict[i][0]//2, best_stuff[i][1] + self.box_dict[i][1]//2)
            color = color_dict[self.name_list[i]]
            cv2.rectangle(img, point_1, point_2, color, thickness=-1)
            cv2.rectangle(img, point_1, point_2, (255,255,0))
        cv2.imwrite(name, img)


def test():
    stuff = StuffFood(name_list, box_list, box_size, like_list, dislike_list, 12, 1001)
    best_stuff, cannot_stuff = stuff.GA_main()       


test()