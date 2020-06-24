import numpy as np


def bl_candidates(i, stuff_pos, box_dict):
    cand = [(0,0)]
    for j in range(i):
        for k in range(j):
            cand += [(stuff_pos[j][0] + box_dict[j][0], stuff_pos[k][1] + box_dict[k][1])]
            cand += [(stuff_pos[k][0] + box_dict[k][0], stuff_pos[j][1] + box_dict[j][1])]
    for j in range(i):
        cand += [(0, stuff_pos[j][1] + box_dict[j][1])]
        cand += [(stuff_pos[j][0] + box_dict[j][0], 0)]
    return cand


def is_feas(i, p, stuff_pos, box_dict, box_size):
    #check: stuff food in lunchbox
    if p[0] < 0 or box_size[0] < p[0] + box_dict[i][0]:
        return False
    #if p[1] + box_dict[i][1] > box_size[1]:
        #return False
    #check: stuff food without dulication
    for j in range(i):
        if max(p[0], stuff_pos[j][0]) < min(p[0] + box_dict[i][0], stuff_pos[j][0] + box_dict[j][0]):
            if max(p[1], stuff_pos[j][1]) < min(p[1] + box_dict[i][1], stuff_pos[j][1] + box_dict[j][1]):
                return False
    return True


def BL_method(box_dict, box_size):
    stuff_pos = []
    for i in range(len(box_dict)):
        blfp = []
        cand = bl_candidates(i, stuff_pos, box_dict)
        for p in cand:
            if is_feas(i, p, stuff_pos, box_dict, box_size):
                blfp += [p]
        min_p = min(blfp, key = lambda v:(v[1], v[0]))
        stuff_pos += [min_p]
    #print(stuff_pos)
    return stuff_pos


"""
input : cand_list [food-index, food-index ...]
        box_dict key: food-index, value: [width, height] 
        box-size [width, height]
output : stuff-pos_list [[left_x,bottom_y], [left_x, bottom_y] ...]
"""
def BL_main(cand_list, box_dict, box_size):
    new_box_list = []
    for index in cand_list:
        new_box_list.append(box_dict[index])
    stuff_pos = BL_method(new_box_list, box_size)
    #convert the order to name_list index order
    new_stuff_pos = []
    for i in range(len(cand_list)):
        index = np.where(cand_list == i)[0][0]
        new_stuff_pos.append(stuff_pos[index])
    #print(new_stuff_pos)
    return new_stuff_pos


def test():
    box_size = [20, 100]
    cand_list = np.array([1,3,0,2,4])
    box_dict = {0:[9,4], 1:[4,10], 2:[4,9], 3:[7,9], 4:[5,10]}
    stuff_pos = BL_main(cand_list, box_dict, box_size)

#test()