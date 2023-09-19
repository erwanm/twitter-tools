import os
import sys, getopt
from collections import defaultdict

provided_col_no = None


PROG_NAME = "count-common.py"


def usage(out):
    print("Usage: ls <input files> | "+PROG_NAME+" [options] <output>",file=out)
    print("",file=out)
#    print("  <input data dir> contains subdirectories, one per document.",file=out)
    print("",file=out)
    print("  Options:")
    print("    -h: print this help message.",file=out)
    print("    -c <user_id>: the input files don't have a header. The col no to use for username is given.",file=out)
#    print("    -n <n words /doc> (default=0 for full doc)",file=out)

    print("",file=out)



def read_input_files(filenames):
    data = {}
    for file_no, filename in enumerate(filenames):
        with open(filename, newline="\n") as infile:
            header = False
            data_this_user = {} #defaultdict(list)
            if provided_col_no is not None:
                user_col = provided_col_no
            else:
                user_col = None
            for line in infile:
                fields = line.rstrip().replace("\r", " ").split('\t')
                if len(fields) > 1:
                    if header or provided_col_no is not None:
                        try:
                            data_this_user[fields[user_col]] = fields
                        except IndexError:
                            print(user_col)
                    else:
                        if "user_id" in fields:
                            user_col = fields.index("username")
                        header = True
                        if user_col is None:
                            raise Exception(f"Col name 'user_id' not found in supposed header [{','.join(fields)}] in file '{filename}'")
                else:
                    print('Weird line??', fields,file=sys.stderr)
            for user_id, user_data in data_this_user.items():
                #print(len(user_data))
                if data.get(user_id) is None:
                    data[user_id] = [1]
                    data[user_id].extend(user_data)
                else:
                    data[user_id][0] += 1
    return data




def main():
 #   global nwords
    global provided_col_no
    try:
        opts, args = getopt.getopt(sys.argv[1:],"h")
    except getopt.GetoptError:
        usage(sys.stderr)
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            usage(sys.stdout)
            sys.exit()
        elif opt == "-c":
            provided_col_no = int(arg)

    if len(args) != 1:
        usage(sys.stderr)
        sys.exit(2)

#    corpus_prefix = args[0]
    output_file = args[0]


    filenames = []
    for line in sys.stdin:
        filename = line.rstrip()
        if os.path.exists(filename):
            filenames.append(filename)
        else:
            raise Exception(f"File not found: {filename}")

    data = read_input_files(filenames)

    with open(output_file, 'w') as output:
        for user_id,data in data.items():
            n = data[0]
            prop = n / len(filenames)
            output.write(f"{str(n)}\t{str(prop)}\t"+"\t".join(data[1:])+"\n")

    

if __name__ == "__main__":
    main()
