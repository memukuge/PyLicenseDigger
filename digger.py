#!/usr/bin/env python
# coding: utf-8

import requests
import re
from pprint import pprint
import sys
import argparse

verbose = False;
warnNC = False; # warn non commercial use
warnHU = False; # warn homu use only
warnEU = False; # warn educational use onlyIf
warnOT = False; # warn other license

licenseDict = {}
packageDict = {}
classifyDict = {}

def resetDict():
    licenseDict = {}
    packageDict = {}
    classifyDict = {}

def verbosePrint(text):
    if verbose:
        pprint(text)

def digLicense(package,extra=""):
    verbosePrint("digging " + package)
    url = f'https://pypi.org/pypi/{package}/json'
    result = requests.get(url)
    if result.status_code != requests.codes.ok:
        print("ERROR: Package not found.")
        return
    json = result.json()
    license =json['info']['license']
    verbosePrint(license)
    if license in licenseDict:
        licenseDict[license] = licenseDict[license] + 1
    else:
        licenseDict[license] = 1


    for classifier in json['info']['classifiers']:
        licenseclassify = re.search('License :: (.+)',classifier)
        if licenseclassify is None:
            pass
        else:
            licenseclass = licenseclassify.group(1)
            #pprint(licenseclass)
            if licenseclass in classifyDict:
                classifyDict[licenseclass] = classifyDict[licenseclass] + 1
            else:
                classifyDict[licenseclass] = 1
            packageDict[package]=licenseclass

    verbosePrint(json['info']['requires_dist'])
    if json['info']['requires_dist'] is None:
        pass
    else:
        for require in json['info']['requires_dist']:
            #if verbose == False:

            subpackage = re.search('^[\w|\-|\.]+', require)
            subpackname = subpackage.group()
            subextra = re.search('extra \=\= \'(.+)\'',require)

            if subextra is None:
                subextrareq = None
            else:
                subextrareq = subextra.group(1)
                verbosePrint(subpackname + " is required only in extra " + subextrareq)

            if subpackname in packageDict:
                pass
                verbosePrint(subpackname + " is already checked")
            elif subextrareq is None:
                digLicense(subpackname)
            else:
                if subextrareq == extra:
                    digLicense(subpackname)
                else:
                    verbosePrint(subpackname + " is not required")



if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    #if sys.stdin.isatty():
    parser.add_argument("target", type=str)
    parser.add_argument("-e","--Extra",type=str)
    parser.add_argument("-r",action='store_true')
    parser.add_argument("-v","--Verbose" ,action='store_true')

    parser.add_argument("-wnc","--WarnNonCommercial" ,action='store_true')
    parser.add_argument("-whu","--WarnHomeUse" ,action='store_true')
    parser.add_argument("-weu","--WarnEducationalUse" ,action='store_true')
    parser.add_argument("-wo","--WarnOther" ,action='store_true')
    parser.add_argument("-wa","--WarnAll" ,action='store_true')

    args = parser.parse_args()


    if args.Verbose is True:
        verbose = true

    if args.WarnAll or args.WarnNonCommercial:
        warnNC = true
    if args.WarnAll or args.WarnHomeUse:
        warnHU = true
    if args.WarnAll or args.WarnEducationalUse:
        warnEU = true
    if args.WarnAll or args.WarnOther:
        warnOT = true

    print("====Searching Licenses in Required Packages====")
    if args.r is True:
        f = open(args.target, 'r')
        line = f.readline()
        while line:
            #print(line)
            package = re.search('^[\w|\-|\.]+', line)
            if package is None:
                #pprint("emptyline")
                pass
            else:
                packagename = package.group()
                digLicense(packagename)
            line = f.readline()
        f.close()

    else:

        packagename = args.target
        digLicense(packagename,args.Extra)


    print("====Required Packages license Statistics====")
    #pprint(licenseDict)
    pprint(classifyDict)
