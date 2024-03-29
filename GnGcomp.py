# Cross comparing GFWList and *ray:GeoSite
# Before running you'll need to install the package "tldextract"

# Import section
print("Importing libraries...")
import csv
import os
import re
import tldextract
print("Import completed.")

# Global variables section
print("Initializing global variables...")
gfwlist_buffer             = []
gfwlist_odin_index         = []
gfwlist_repeated_index     = []
geosite_include_buffer     = [[], []]
geosite_full_domain_buffer = [[], []]
geosite_domain_buffer      = [[], []]
geosite_regexp_buffer      = [[], []]
geosite_tld_buffer         = [[], []]
gfwlist_compared_resz      = [[], []]
result_buffer              = [[], []]
print("Global variables Initialized.")

# Functions section
print("Initializing functions...")

def Read_GFWList(filepath: str):
    cacher = []
    cachew = []
    with open(filepath, "rt", 65536, "utf8", None, None, True, None) as f_gfw:
        cacher = f_gfw.readlines()
        f_gfw.close()
    for line in cacher:
        line = line.strip().split("#")[0]
        if "." in line:
            cachew.append(line.split(" ")[0].lower())
    gfwlist_buffer.extend(cachew)
    print("Read", len(cacher), "lines from GFWList. Got", len(cachew), "domains.")

def Read_GeoSite(directorypath: str):
    cachew_tld             = []
    cachew_tld_dir         = []
    cachew_regexp          = []
    cachew_regexp_dir      = []
    cachew_domain          = []
    cachew_domain_dir      = []
    cachew_full_domain     = []
    cachew_full_domain_dir = []
    cachew_include         = []
    cachew_include_dir     = []
    cacher_size_counter = 0
    file_count          = 0
    do_not_use_file        = tuple((" ", "private"))
    do_not_use_file_prefix = tuple((" ","tld"))
    do_not_use_file_suffix = tuple((" "))
    delay_file             = tuple((" "))
    delay_file_perfix      = tuple((" ", "category"))
    delay_file_suffix      = tuple((" "))
    filelist = os.listdir(directorypath)
    for filename in filelist.copy():
        if (filename in do_not_use_file) or \
            filename.startswith(do_not_use_file_prefix) or \
            filename.endswith(do_not_use_file_suffix):
            filelist.remove(filename)
        if (filename in delay_file) or \
            filename.startswith(delay_file_perfix) or \
            filename.endswith(delay_file_suffix):
            filelist.append(filelist.pop(filelist.index(filename)))
    file_count = len(filelist)
    for i, filename in enumerate(filelist):
        cacher   = []
        filepath = os.path.join(directorypath, filename)
        with open(filepath, "rt", 4096, "utf8", None, None, True, None) as f_geosite:
            cacher = f_geosite.readlines()
            f_geosite.close()
        cacher_size_counter += len(cacher)
        for line in cacher:
            line = line.strip().split("#")[0].strip()
            if len(line) > 0:
                if line.startswith("include:"):
                    line = line[len("include:"):]
                    cachew_include.append(line.split(" ")[0].lower())
                    if "@" in line:
                        cachew_include_dir.append(filename + "@" + line.split("@")[1].split(" ")[0])
                    else:
                        cachew_include_dir.append(filename)
                elif line.startswith("regexp:"):
                    line = line[len("regexp:"):]
                    cachew_regexp.append(line.split(" ")[0].lower())
                    if "@" in line:
                        cachew_regexp_dir.append(filename + "@" + line.split("@")[1].split(" ")[0])
                    else:
                        cachew_regexp_dir.append(filename)
                elif line.startswith("full:"):
                    line = line[len("full:"):]
                    cachew_full_domain.append(line.split(" ")[0].lower())
                    if "@" in line:
                        cachew_full_domain_dir.append(filename + "@" + line.split("@")[1].split(" ")[0])
                    else:
                        cachew_full_domain_dir.append(filename)
                else:
                    if line.startswith("domain:"):
                        line = line[len("domain:"):]
                    xtrobj = tldextract.extract(line.split(" ")[0].lower())
                    if xtrobj.registered_domain != "":
                        cachew_domain.append(xtrobj.fqdn)
                        if "@" in line:
                            cachew_domain_dir.append(filename + "@" + line.split("@")[1].split(" ")[0])
                        else:
                            cachew_domain_dir.append(filename)
                    elif (xtrobj.registered_domain == "") and (xtrobj.suffix != ""):
                        cachew_tld.append(xtrobj.suffix)
                        if "@" in line:
                            cachew_tld_dir.append(filename + "@" + line.split("@")[1].split(" ")[0])
                        else:
                            cachew_tld_dir.append(filename)
        if (i + 1) % 16 == 0:
            print(i + 1, "/", file_count, " files processed.", sep = "", end = "\r")
        if (i + 1) == file_count:
            print(i + 1, "/", file_count, " files processed.", sep = "")
    geosite_include_buffer[0].extend(cachew_include)
    geosite_include_buffer[1].extend(cachew_include_dir)
    geosite_full_domain_buffer[0].extend(cachew_full_domain)
    geosite_full_domain_buffer[1].extend(cachew_full_domain_dir)
    geosite_regexp_buffer[0].extend(cachew_regexp)
    geosite_regexp_buffer[1].extend(cachew_regexp_dir)
    geosite_domain_buffer[0].extend(cachew_domain)
    geosite_domain_buffer[1].extend(cachew_domain_dir)
    geosite_tld_buffer[0].extend(cachew_tld)
    geosite_tld_buffer[1].extend(cachew_tld_dir)
    print("Read", cacher_size_counter, "lines from GeoSite. Got", len(cachew_full_domain), "full domains. Got", \
          len(cachew_domain), "domains. Got", len(cachew_tld), "TLDs. Got", len(cachew_regexp), "regexps.")

def GFWList_Self_Sanitize():
    cacher_gfwlist = gfwlist_buffer.copy()
    cachew_odin     = []
    cachew_rpet     = []
    cachew_resz_idx = []
    cachew_resz_tag = []
    print("Building data stack...")
    to_check_index  = []
    comp_shadow     = [[], [], []]
    listed_name     = set()
    for domain in cacher_gfwlist:
        comp_shadow[0].append(tldextract.extract(domain).fqdn)
        comp_shadow[1].append(tldextract.extract(domain).registered_domain)
        comp_shadow[2].append(tldextract.extract(domain).suffix)
    print("Build data stack complete.")
    for i, tdomain in enumerate(comp_shadow[2]):
        if (len(comp_shadow[1][i]) == 0) and (len(tdomain) != 0):
            listed_name.add(tdomain)
            cachew_odin.append(i)
        else:
            to_check_index.append(i)
    for i in to_check_index.copy():
        if comp_shadow[2][i] in listed_name:
            cachew_rpet.append(i)
            cachew_resz_idx.append(i)
            cachew_resz_tag.append("[REPEATED]")
            to_check_index.remove(i)
        elif comp_shadow[0][i] == comp_shadow[1][i]:
            listed_name.add(comp_shadow[1][i])
            cachew_odin.append(i)
            to_check_index.remove(i)
    for i in to_check_index.copy():
        if comp_shadow[1][i] in listed_name:
            cachew_rpet.append(i)
            cachew_resz_idx.append(i)
            cachew_resz_tag.append("[REPEATED]")
            to_check_index.remove(i)
        else:
            listed_name.add(comp_shadow[2][i])
            cachew_odin.append(i)
            to_check_index.remove(i)
    if (len(to_check_index) == 0) and ((len(cachew_odin) + len(cachew_rpet)) == len(cacher_gfwlist)):
        cachew_odin.sort()
        gfwlist_odin_index.extend(cachew_odin)
        gfwlist_repeated_index.extend(cachew_rpet)
        gfwlist_compared_resz[0].extend(cachew_resz_idx)
        gfwlist_compared_resz[1].extend(cachew_resz_tag)
        print("Public names count of GFWList: ", len(listed_name))
        print(len(cachew_odin), "effective in GFWList")
    else:
        input("Error detected, press ENTER to exit.")
        exit()

def Compare_GFWList_To_GeoSite():
    cacher_gfwlist         = gfwlist_buffer.copy()
    cacher_odin_idx        = gfwlist_odin_index.copy()
    cacher_full_domain     = geosite_full_domain_buffer[0].copy()
    cacher_full_domain_tag = geosite_full_domain_buffer[1].copy()
    cacher_domain          = geosite_domain_buffer[0].copy()
    cacher_domain_tag      = geosite_domain_buffer[1].copy()
    cacher_regexp          = geosite_regexp_buffer[0].copy()
    cacher_regexp_tag      = geosite_regexp_buffer[1].copy()
    cacher_tld             = geosite_tld_buffer[0].copy()
    cacher_tld_tag         = geosite_tld_buffer[1].copy()
    cachew_resz_idx = []
    cachew_resz_tag = []
    total_count = len(cacher_odin_idx)
    print("Building data cache for comparation...")
    target_shadow  = [[], [], []]
    compare_shadow = [[], []]
    for domain in cacher_gfwlist:
        target_shadow[0].append(tldextract.extract(domain).fqdn)
        target_shadow[1].append(tldextract.extract(domain).registered_domain)
        target_shadow[2].append(tldextract.extract(domain).suffix)
    for domain in cacher_domain:
        compare_shadow[0].append(tldextract.extract(domain).fqdn)
        compare_shadow[1].append(tldextract.extract(domain).registered_domain)
    print("Data cache built.")
    for countr, i in enumerate(cacher_odin_idx):
        marked = False
        if target_shadow[1][i] != "":
            for j, full_domain in enumerate(cacher_full_domain):
                if marked:
                    break
                elif target_shadow[0][i] == full_domain:
                    cachew_resz_idx.append(i)
                    cachew_resz_tag.append(cacher_full_domain_tag[j])
                    marked = True
            for j, regexp in enumerate(cacher_regexp):
                if marked:
                    break
                elif re.search(regexp, target_shadow[0][i]) != None:
                    cachew_resz_idx.append(i)
                    cachew_resz_tag.append(cacher_regexp_tag[j])
                    marked = True
            for j, domain in enumerate(cacher_domain):
                if marked:
                    break
                elif target_shadow[0][i] == compare_shadow[0][j]:
                    cachew_resz_idx.append(i)
                    cachew_resz_tag.append(cacher_domain_tag[j])
                    marked = True
            if len(target_shadow[0][i]) != len(target_shadow[1][i]):
                for j, domain in enumerate(cacher_domain):
                    if marked:
                        break
                    elif target_shadow[1][i] == compare_shadow[0][j]:
                        cachew_resz_idx.append(i)
                        cachew_resz_tag.append(cacher_domain_tag[j])
                        marked = True
        for j, tld in enumerate(cacher_tld):
            if marked:
                break
            elif target_shadow[2][i] == tld:
                cachew_resz_idx.append(i)
                cachew_resz_tag.append(cacher_tld_tag[j])
                marked = True
        if (countr + 1) % 64 == 0:
            print(countr + 1, "/", total_count, " completed.", sep = "", end = "\r")
        if (countr + 1) == total_count:
            print(countr + 1, "/", total_count, " completed.", sep = "")
    gfwlist_compared_resz[0].extend(cachew_resz_idx)
    gfwlist_compared_resz[1].extend(cachew_resz_tag)

def Make_Result_List():
    cacher_gfwlist  = gfwlist_buffer.copy()
    cacher_resz_idx = gfwlist_compared_resz[0].copy()
    cacher_resz_tag = gfwlist_compared_resz[1].copy()
    cachew_resz_domain = []
    cachew_resz_tag    = []
    index_set = set()
    print("Preparing result...")
    for index in cacher_resz_idx:
        index_set.add(index)
    for i in range(len(cacher_gfwlist)):
        cachew_resz_domain.append(cacher_gfwlist[i])
        if i in index_set:
            cachew_resz_tag.append(cacher_resz_tag[cacher_resz_idx.index(i)])
        else:
            cachew_resz_tag.append("")
    result_buffer[0].extend(cachew_resz_domain)
    result_buffer[1].extend(cachew_resz_tag)
    print("Result prepared.")

def Output_Correction(source: list):
    if len(source[0]) == len(source[1]):
        buffer = []
        width = len(source[0])
        for i in range(width):
            cell = [source[0][i], source[1][i]]
            buffer.append(cell)
        return buffer
    else:
        return []

def Export_Result(dir_path: str):
    cacher_result  = result_buffer.copy()
    cacher_include = geosite_include_buffer.copy()
    cacher_gfwlist = gfwlist_buffer.copy()
    report_path    = os.path.join(dir_path, "report.csv")
    structure_path = os.path.join(dir_path, "include.csv")
    strip_path     = os.path.join(dir_path, "stripped_gfwlist")
    os.path.curdir
    Make_Result_List()
    print("Starting convert and save results to", dir_path, "...")
    with open(report_path, "wt+", 16384, "utf8", None, '\n', True, None) as outreport:
        handler = csv.writer(outreport)
        dataset = Output_Correction(cacher_result)
        for cell in dataset:
            handler.writerow(cell)
        outreport.flush()
        outreport.close()
    with open(structure_path, "wt+", 16384, "utf8", None, '\n', True, None) as outstructure:
        handler = csv.writer(outstructure)
        dataset = Output_Correction(cacher_include)
        for cell in dataset:
            handler.writerow(cell)
        outstructure.flush()
        outstructure.close()
    with open(strip_path, "wt+", 131072, "utf8", None, '\n', True, None) as outstrip:
        dataset = []
        for i, domain in enumerate(cacher_gfwlist):
            if cacher_result[1][i] != "[REPEATED]":
                dataset.append(domain + "\r\n")
        outstrip.writelines(dataset)
        outstrip.flush()
        outstrip.close()
    print("Data saved.")

print("Functions initialized.")

print(" ")

# Flow section

gfwlist_path = ""
geosite_path = ""
export_path = ""

while True:
    gfwlist_path = input("Input the path of GFWList (File): ")
    if os.path.isfile(os.path.normpath(gfwlist_path)):
        break
while True:
    geosite_path = input("Input the path of GeoSite (Directory): ")
    if os.path.isdir(os.path.normpath(geosite_path)):
        break
while True:
    export_path = input("Input the directory you desired to store outputs: ")
    export_path = os.path.normpath(export_path)
    if os.path.isdir(export_path):
        break
    else:
        if not os.path.exists(export_path):
            os.makedirs(export_path)
            break
        elif os.path.isfile(export_path):
            print("This is a file path. Use default path instead.")
            export_path = os.path.dirname(__file__)
            break
        else:
            print("Something happened.")

print(" ")

print("Reading data...")
Read_GFWList(gfwlist_path)
Read_GeoSite(geosite_path)
print("Read complete.")

print("Sanitizing GFWList data...")
GFWList_Self_Sanitize()
print("Sanitize GFWList complete.")

print("Comparing GFWList data to Geosite...")
Compare_GFWList_To_GeoSite()
print("Compare ended.")

print("Prepare exporting result...")
Export_Result(export_path)
input("Press ENTER key to exit.")
print("Exit.")
