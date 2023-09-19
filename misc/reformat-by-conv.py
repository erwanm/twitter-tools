import os
import sys, getopt
import random
from collections import defaultdict

PROG_NAME = "reformat-by-conv.py"

conv_prob = 1 

def usage(out):
    print("Usage: ls <files> | "+PROG_NAME+" [options] <output dir>",file=out)
    print("",file=out)
    print("  Reads input tweet files as tsv with headers containing tweets, creates",file=out)
    print("  one tsv file without header by conversation: <output dir>/<conv id>.",file=out)
    print("  (used to convert from the original tsv format with many users/conversations",file=out)
    print("  to the format by conversation required for the distributed preprocessing)",file=out)
    print("  ",file=out)
    print("  Options:")
    print("    -h: print this help message.",file=out)
    print(f"    -c <prob>: prob to select a conversation. default: {conv_prob}",file=out)
    print("",file=out)



def read_input_files(filenames, output_dir):
    for file_no, filename in enumerate(filenames):
        with open(filename, newline="\n") as infile:
            print(f"\r{file_no}/{len(filenames)}", flush=True, end ='')
            header = False
            conv_col = None
            map_files = {}
            for line0 in infile:
                line = line0.rstrip()
                fields = line.replace("\r", " ").split('\t')
                conv_id = None
                if len(fields) > 1:
                    if header:
                        try:
                            conv_id = fields[conv_col]
                        except IndexError:
                            print(conv_col)
                        f = map_files.get(conv_id)
                        if f is None:
                            if random.random() < conv_prob:
                                outname = os.path.join(output_dir, conv_id)
                                f = open(outname, "w") 
                                map_files[conv_id] = f
                        if f is not None:
                            f.write(line0)
                    else:
                        if "conversation_id" in fields:
                            conv_col = fields.index("conversation_id")
                        header = True
                        if conv_col is None:
                            raise Exception(f"Col name 'text' and/or 'conversation_id' and/or 'user_id' not found in supposed header [{','.join(fields)}] in file '{filename}'")
                else:
                    print('Weird line??', fields,file=sys.stderr)
            for myid,myfile in map_files.items():
                myfile.close()


                


def main():
    global conv_prob
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hc:")
    except getopt.GetoptError:
        usage(sys.stderr)
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            usage(sys.stdout)
            sys.exit()
        elif opt == "-c":
            conv_prob = float(arg)
    if len(args) != 1:
        usage(sys.stderr)
        sys.exit(2)

    output_dir = args[0]
      
    filenames = []
    for line in sys.stdin:
        filename = line.rstrip()
        if os.path.exists(filename):
            filenames.append(filename)
        else:
            raise Exception(f"File not found: {filename}")
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    print("Processing...", flush=True)
    read_input_files(filenames, output_dir)

if __name__ == "__main__":
    main()
