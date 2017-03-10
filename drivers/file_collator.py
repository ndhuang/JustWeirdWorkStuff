import argparse
import glob
import os
import re
import subprocess
import numpy as np

def smart_collate(basename, outname, header_lines = 1):
    if not os.path.exists(outname):
        return collate(basename, outname, header_lines = header_lines)
    last = subprocess.check_output(['tail', '-n1', outname])
    last_time = float(last.split()[0])
    
    files = sorted(glob.glob(basename + '*'))
    extension = files[0][files[0].rfind('.') + 1:]
    if extension != 'txt':
        raise NotImplementedError()
    good_files = []
    for f in files:
        if not f.endswith(extension):
            continue
        good_files.append(f)
    for file in good_files[::-1]:
        f = open(file, 'r')
        line_num = -1
        for i, line in enumerate(f):
            try:
                time = float(line.split()[0])
            except ValueError:
                continue
            if time == last_time:
                line_num = i
                break
        if line_num >= 0:
            file_num = get_filenum(basename, file)
            break

    outfile = open(outname, 'a')
    outfile.seek(0, os.SEEK_END)
    for file in good_files:
        if file_num > get_filenum(basename, file):
            continue
        f = open(file)
        lines = f.readlines()
        f.close()
        if file_num == get_filenum(basename, file):
            outfile.writelines(lines[line_num:])
        else:
            outfile.writelines(lines[header_lines:])
    outfile.close()
    
def get_filenum(basename, filename):
    pattern = basename + '(\d+)'
    match = re.match(pattern, filename)
    if match is not None:
        return int(match.groups()[0])
    else:
        raise ValueError("Bad filename " + filename)


def collate(basename, outname, header_lines = 1):
    # if os.path.exists(outname):
    #     raise RuntimeError("File exists: " + outname)
    outfile = open(outname, 'w')
    files = sorted(glob.glob(basename + '*'))
    extension = files[0][files[0].rfind('.') + 1:]
    if extension != 'txt':
        raise NotImplementedError()
    first = True
    for file in files:
        if not file.endswith(extension):
            print "Extension mismatch: {}, {}".format(file, extension)
            continue
        f = open(file, 'r')
        lines = f.readlines()
        f.close()
        if first:
            outfile.writelines(lines)
            first = False
        else:
            outfile.writelines(lines[headerlines:])
    outfile.close()        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('basename', type = str, 
                        help =  'The basename of files to collate')
    parser.add_argument('--no-keep', dest = 'keep', action = 'store_false',
                        help = 'Delete the fragment files')
    parser.add_argument('-o', '--outfile', type = str, default = None,
                        help = 'The output file, if different from default')
    args = parser.parse_args()
    smart_collate(args.basename, args.outfile)
