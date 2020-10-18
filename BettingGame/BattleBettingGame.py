import csv
from RobotFightClass import *

constants = RobotFightConstants()
print(random.choice(constants.mech_list))
print(random.choice(constants.mech_list2))


# with open('sample_statistics_data_20201010.csv', newline='') as file:
#     csv_reader = csv.reader(file, delimiter=',')
#     for row in csv_reader:
#         # print(', '.join(row))
#         print(row)



