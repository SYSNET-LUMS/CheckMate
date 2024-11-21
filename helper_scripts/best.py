with open("logs/fft-iclib_47_RF_2.csv",'r') as file:
    oc = 0
    with open("logs/original_checkpoints_fft-iclib-47e-6_RF_2.txt",'r') as file_2:
        oc = int(file_2.readline())
    file_2.close()
    print(oc)
    

    line = file.readline()
    best = 9999
    i = 0
    best_1 = -1
    while line:
        # print(line)
        line = file.readline()

        this_line = line.split(",")

        # print(this_line)
        i += 1
        try:
            om = float(this_line[-2]) + float(this_line[-1])/oc
            if om < best:
                best = om
                best_1 = i
        except:
            pass
        # print(om)
    
    print("best: ", best)
    print("best: ", best_1)

