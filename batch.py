#!/usr/local/bin/python3

import re
import subprocess, os

# stage variable
OUT_MAP = {}
OUT_MAP["IN-1"] = ["1.txt"]
LINES = []

# temp variable
FUNC_INFO = {}
FUNC_INPUT = {}
PROCESS = True

LINES.append(" IN-1 > cp > cp > wc")
LINES.append(" wc > cp > split")
LINES.append("split|1 > cp  > 1|join")
LINES.append("split|2 > cp > 2|join")
LINES.append("join > cp")

def _trim(str):
    return re.sub("^[ ]+|[ ]+$", "", str)

def _is_file(str):
    m = re.search("\[(.*)\]", str)
    if m:
        return True, m.groups()[0]
    return False, ""

def _int(i):
    if not i:
        return 1
    i = int(i)
    if i <= 0:
        i = 1
    return i

# search for function total input/output count
def _func_total_para(func):
    if func not in FUNC_INFO:
        in_para_total = 1
        out_para_total = 1
        for line in LINES:
            m = re.findall("(?:^|[ \[\]>])(?:(\d*)\|)?%s(?:-\d*)?(?:\|(\d*))?(?:$|[ \[\]>])" % func, line)
            for para in m:
                in_para_total = max(in_para_total, _int(para[0]))
                out_para_total = max(out_para_total, _int(para[1]))
        FUNC_INFO[func] = (in_para_total, out_para_total)
    return FUNC_INFO[func]

# parse 2|split-3|4
def _parse_func(func):
    func = _trim(func)
    m = re.search("^(?:(\d*)\|)?([^\|-]*)(?:-(\d*))?(?:\|(\d*))?$", func)
    if not m:
        print("func wrong format: " + func)
        exit(1)
    gp = m.groups()
    try:
        in_para = _int(gp[0])
        func = gp[1]
        fid = _int(gp[2])
        out_para = _int(gp[3])
    except:
        print("func wrong format: " + func)
        exit(1)
    if not func:
        print("func wrong format: " + func)
        exit(1)
    
    in_para_total, out_para_total = _func_total_para(func)
    
    return func, fid, in_para, in_para_total, out_para, out_para_total

# return True if all inputs are ready
def _file_input(func, file, current, total):
    global FUNC_INPUT
    if func not in FUNC_INPUT:
        FUNC_INPUT[func] = ["" for i in range(total)]
    if FUNC_INPUT[func][current - 1]:
        printf("error duplicate input for %s at %d" % (func, current))
        exit(1)
    FUNC_INPUT[func][current - 1] = file
    for f in FUNC_INPUT[func]:
        if not f:
            return False
    return True

def _pr(str):
    print(re.sub(" ", "_", str))

# replace module with real file name
def _func_replace_with_file():
    for i in range(len(LINES)):
        m = re.search("^([^>]*)(.*)", LINES[i])
        if not m:
            continue
        func_or_file = _trim(m.groups()[0])
        is_file, in_file = _is_file(func_or_file)
        if is_file:
            continue
        func, fid, _, _, out_para, _ = _parse_func(func_or_file)
        check = "%s-%d" % (func, fid)
        if check in OUT_MAP:
            file_list = OUT_MAP[check]
            LINES[i] = "[%s] %s" % (file_list[out_para - 1], _trim(m.groups()[1]))

# actual run the function
def _run_func(func, fid, in_file_list, out_para_total):
    global PROCESS, OUT_MAP
    in_file = in_file_list[0]
    out_file = in_file + "_" + func
    cmd = "_%s" % (func)

    for f in in_file_list:
        cmd = "%s %s" % (cmd, f)

    out_file_list = []
    if out_para_total > 1:
        for j in range(1, out_para_total + 1):
            out_file_list.append("%s.%d" % (out_file, j))
    else:
        out_file_list.append(out_file)
    for f in out_file_list:
        cmd = "%s %s" % (cmd, f)

    print("execute %s" % cmd)

    os.system(cmd)
    PROCESS = True
    # subprocess.run(["_" + func, in_  file, out_file], shell=True, executable='/bin/bash', env=env)
    func_id = "%s-%d" % (func, fid)
    OUT_MAP[func_id] = out_file_list

# prepare to run multi input function
def _process_multi_infile_func(ready_func_id, out_para_total):
    for i in range(len(LINES)):
        m = re.search("^([^>]*)> *([^> \[\]]*)(.*)", LINES[i])
        if not m:
            continue
        origin_func = _trim(m.groups()[1])
        func, fid, in_para, in_para_total, _, _ = _parse_func(origin_func)
        is_file, in_file = _is_file(m.groups()[0])
        out_file = in_file + "_" + func
        func_id = "%s-%d" % (func, fid)
        if func_id == ready_func_id and is_file:
            LINES[i] = "%s %s" % (origin_func, _trim(m.groups()[2]))
            print("processed multi-in line %d:  %s" % (i, LINES[i]))

# prepare to run function
def _process_func():
    global FUNC_INPUT
    FUNC_INPUT.clear()

    for i in range(len(LINES)):
        m = re.search("^([^>]*)> *([^> \[\]]*)(.*)", LINES[i])
        if not m:
            continue
        
        origin_func = _trim(m.groups()[1])
        func, fid, in_para, in_para_total, _, out_para_total = _parse_func(origin_func)
        is_file, in_file = _is_file(m.groups()[0])
        if func and is_file:
            func_id = "%s-%d" % (func, fid)
            if (in_para_total > 1):
                if (_file_input(func_id, in_file, in_para, in_para_total)):
                    # run multi-input function
                    _run_func(func, fid, FUNC_INPUT[func_id], out_para_total)
                    _process_multi_infile_func(func_id, out_para_total)
                    break
            else:
                _run_func(func, fid, [in_file], out_para_total)
                LINES[i] = "%s %s" % (origin_func, _trim(m.groups()[2]))
                print("processed line %d:  %s" % (i, LINES[i]))
                break
        else:
            print("ignore line %d:  %s" % (i, LINES[i]))
            continue

while PROCESS:
    PROCESS = False

    _func_replace_with_file()

    # print("begin dump")
    # for line in lines:
    #     print(line)
    # print("after dump")

    _process_func()
    print(OUT_MAP)
    print("")


