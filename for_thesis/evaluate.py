import cv2
import numpy as np
import copy

ANS_POS = [(91.59645935685536, 15.410331363106977), (93.01074491154962, 81.11674556760481), (59.64833247189204, 9.818634530787627), (22.92159767847562, 19.0505028854418), (77.61417078447568, 45.98121071976683), (19.65842280754873, 60.73054699668711), (55.54046096442451, 78.02979116000563)]
# ANS_SIZE = [[30.820662726213953, 36.28597954004505, 1.8886327743530273], [39.94997370857021, 42.493337195596126, 28.9614200592041], [19.637269061575253, 27.610274229881597, 31.95011615753174], [45.84319535695124, 38.1010057708836, 28.733491897583008], [63.54195085504887, 30.32109598710575, 26.517391204833984], [39.31684561509746, 45.259082451607014, 24.733901023864746], [32.447230698654096, 33.77606489337185, 32.36323595046997]]
ANS_SIZE = [[30.820662726213953, 36.28597954004505], [39.94997370857021, 42.493337195596126], [19.637269061575253, 27.610274229881597], [38.1010057708836, 45.84319535695124], [30.32109598710575, 63.54195085504887], [45.259082451607014, 39.31684561509746], [33.77606489337185, 32.447230698654096]]

def red_to_white():
    img = cv2.imread("img/diff_box_2.png")
    img_array = img.astype(np.float)
    # print(img_array)
    img_array[np.where((img_array==[0,0,255]).all(axis=2))] = [255,255,255]
    out = img_array.astype(np.uint8)
    cv2.imwrite("img/output.jpg", out)


class GetClickedPos:

    def __init__(self):
        self.keep_pos = []

    def get_position(self, img_name):

        def onMouse(event, x, y, flags, params):
            if event == cv2.EVENT_LBUTTONDOWN:
                print("clicked pos (x, y) = ", x, y)
                self.keep_pos.append([x, y])

        img = cv2.imread(img_name, cv2.IMREAD_COLOR)
        cv2.namedWindow('window', cv2.WINDOW_NORMAL)
        cv2.imshow('window', img)
        cv2.setMouseCallback('window', onMouse)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        print(self.keep_pos)


def get_result_info(flag = False): 
    result_rect = []
    result_rot = []
    if flag:
        print("左上から時計回りにお弁当箱の四隅をクリックして下さい")
        print("クリックが終わったらキーボードを押して下さい")
        get_cpos = GetClickedPos()
        get_cpos.get_position("img/output_0.png")
        left_top, right_top, right_bottom, left_bottom = get_cpos.keep_pos
        # 射影変換する
        # https://qiita.com/mix_dvd/items/5674f26af467098842f0
        pts1 = np.float32([left_top, right_top, right_bottom, left_bottom])
        pts2 = np.float32([[0, 0], [100, 0], [100, 110], [0, 110]])

        img = cv2.imread("img/output_after10.png")
        M = cv2.getPerspectiveTransform(pts1, pts2)
        new_img = cv2.warpPerspective(img, M, (100, 110))
        new_img = cv2.rotate(new_img, cv2.ROTATE_90_CLOCKWISE)
        cv2.imwrite("img/result.png", new_img)
    for i in range(len(ANS_POS)):
        img = cv2.imread("img/result.png")
        black_img = np.zeros((100, 110, 3))
        cur_img = cv2.drawMarker(img, (int(ANS_POS[i][0]), int(ANS_POS[i][1])), (0, 0, 255), markerType=cv2.MARKER_STAR, markerSize=10)
        cv2.imwrite("img/cur.png", cur_img)
        print("*がついた食材を縁取って下さい。終わったらキーボードを押して下さい")
        get_cpos = GetClickedPos()
        get_cpos.get_position("img/cur.png")
        for i in range (len(get_cpos.keep_pos)):
            p1 = (int(get_cpos.keep_pos[i][0]), int(get_cpos.keep_pos[i][1]))
            if i == len(get_cpos.keep_pos) - 1:
                p2 = (int(get_cpos.keep_pos[0][0]), int(get_cpos.keep_pos[0][1]))
            else:
                p2 = (int(get_cpos.keep_pos[i + 1][0]), int(get_cpos.keep_pos[i + 1][1]))
            cv2.line(black_img, p1, p2, (255, 255, 255), thickness=1, lineType=cv2.LINE_4)
        th, im_th = cv2.threshold(black_img.astype(np.uint8), 220, 255, cv2.THRESH_BINARY_INV)
        im_floodfill = im_th.copy()
        h, w = im_th.shape[:2]
        mask = np.zeros((h+2, w+2), np.uint8)
        cv2.floodFill(im_floodfill, mask, (0,0), 255)
        im_out = np.zeros((100, 110, 3))
        im_out[np.where((im_floodfill==[255, 255, 255]).all(axis=2))] = [255, 255, 255]
        # cv2.imwrite("img/fill.png", im_out)
        # 食材の形を矩形近似
        img_gray = cv2.cvtColor(im_out.astype(np.uint8), cv2.COLOR_BGR2GRAY)
        contours, _hierarchy = cv2.findContours(img_gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        rect = cv2.minAreaRect(contours[0])
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        # print(box)
        x_sorted = box.copy().tolist()
        x_sorted.sort(key=lambda x:x[0])
        left_lst = x_sorted[:2]
        right_lst = x_sorted[2:]
        left_lst.sort(key=lambda x:x[1])
        right_lst.sort(key=lambda x:x[1])
        lt, lb, rt, rb = left_lst[0], left_lst[1], right_lst[0], right_lst[1]
        result_rect.append((lt, lb, rt, rb))
        # 回転の大きさ（度）
        if rb[1] == rt[1]:
            result_rot.append(0)
        else:
            si_ta = np.arctan((rb[0] - rt[0]) / (rb[1] - rt[1]))
            result_rot.append(np.rad2deg(si_ta))
    # print(result_pos, result_size, result_rot)
    return result_rect, result_rot


def evaluate(visualize=True):
    result_rect, result_rot = get_result_info(flag=False)
    img = cv2.imread("img/result.png")
    for i in range(len(ANS_POS)):
        lt, lb, rt, rb = result_rect[i]
        if visualize:
            cv2.line(img, (lt[0], lt[1]), (rt[0], rt[1]), (0, 0, 255), thickness=2, lineType=cv2.LINE_4)
            cv2.line(img, (lt[0], lt[1]), (lb[0], lb[1]), (0, 0, 255), thickness=2, lineType=cv2.LINE_4)
            cv2.line(img, (rt[0], rt[1]), (rb[0], rb[1]), (0, 0, 255), thickness=2, lineType=cv2.LINE_4)
            cv2.line(img, (lb[0], lb[1]), (rb[0], rb[1]), (0, 0, 255), thickness=2, lineType=cv2.LINE_4)
        width =  np.sqrt((rb[0] - lb[0])**2 + (rb[1] - lb[1])**2)
        length = np.sqrt((lb[0] - lt[0])**2 + (lb[1] - lt[1])**2)
        # 食材の位置
        result_pos = ((lt[0] + lb[0] + rt[0] + rb[0]) / 4, (lt[1] + lb[1] + rt[1] + rb[1]) / 4)
        # 食材の大きさ
        result_size = (length, width)
        ans_px, ans_py = ANS_POS[i][0], ANS_POS[i][1]
        res_px, res_py = result_pos[0], result_pos[1]
        print(" ------- ")
        print("rect: ", result_rect[i])
        print("位置： ", ANS_POS[i], result_pos, " 差分： ", np.linalg.norm([ans_px - res_px, ans_py - res_py]))
        ans_len, ans_wid = ANS_SIZE[i][0], ANS_SIZE[i][1]
        res_len, res_wid = result_size[0], result_size[1]
        print("大きさ: ", ANS_SIZE[i][:2], result_size, "差分: ", np.linalg.norm([ans_len - res_len, ans_wid - res_wid]))
        print("回転: ", result_rot[i])
    cv2.imwrite("img/output_ev.jpg", img)


def check_lbox_size():
    img = cv2.imread("img/output_0.png")
    cur_img = cv2.line(img, (0, 300), (639, 300), (255, 0, 0))
    cv2.imwrite("img/cur2.png", cur_img)
    print("左から３点クリック")
    get_cpos = GetClickedPos()
    get_cpos.get_position("img/cur2.png")
    p1, p2, p3 = get_cpos.keep_pos
    ans = (p3[0] - p2[0]) * 170/ (p3[0] - p1[0])
    print("おかずを詰める部分の横幅" + str(ans) + "mm")

# red_to_white()
# evaluate()
check_lbox_size()

# https://learnopencv.com/filling-holes-in-an-image-using-opencv-python-c/
