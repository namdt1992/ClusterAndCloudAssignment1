import datetime
import ijson

a = datetime.datetime.now()
sourceFile = open('D:/data/demo.txt', 'w', encoding='utf-8')
count = 0
with open("twitter-data-small.json", 'rb') as input_file:
    # load json iteratively
    parser = ijson.items(input_file, 'item')
    for parse in parser:
        count = count +1
        sourceFile.writelines(str(parse))
        #sourceFile.writelines()
sourceFile.writelines(str(count))
b = datetime.datetime.now()
c = b-a
sourceFile.write("time is {}".format(c))
sourceFile.close()