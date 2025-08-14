from pyexcel.cookbook import merge_all_to_a_book
# import pyexcel.ext.xlsx # no longer required if you use pyexcel >= 0.2.2 
import glob


merge_all_to_a_book(glob.glob("/ssd11/other/meiyy02/code_files/jpn-cn-200/jpn_Jpan-cn_200.csv"), "/ssd11/other/meiyy02/code_files/jpn-cn-200/jpn_Jpan-cn_200.xlsx")