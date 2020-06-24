"""
input : cand_list [food-index, food-index ...]
        box_dict key: food-index, value: [width, height] 
        box-size [width, height]
output : stuff-pos_list [[left_x,bottom_y], [left_x, bottom_y] ...]
"""
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
    if p[1] + box_dict[i][1] > box_size[1]:
        return False
    #check: stuff food without dulication
    for j in range(i):
        if max(p[0], stuff_pos[j][0]) < min(p[0] + box_dict[i][0], stuff_pos[j][0] + box_dict[j][0]):
            if max(p[1], stuff_pos[j][1]) < min(p[1] + box_dict[i][1], stuff_pos[j][1] + box_dict[j][1]):
                return False
    return True


def BL_method(cand_list, box_dict, box_size):
    stuff_pos = []
    for i in cand_list:
        blfp = []
        cand = bl_candidates(i, stuff_pos, box_dict)
        for p in cand:
            if is_feas(i, p, stuff_pos, box_dict, box_size):
                blfp += [p]
        min_p = min(blfp, key = lambda v:(v[1], v[0]))
        stuff_pos += [min_p]
    return stuff_pos

def test():
    box_size = [20, 100]
    cand_list = [0,1,2,3,4]
    box_dict = {0:[9,4], 1:[4,10], 2:[4,9], 3:[7,9], 4:[5,10]}
    stuff_pos = BL_method(cand_list, box_dict, box_size)
    print(stuff_pos)

#test()