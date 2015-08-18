import csv
import json
import zipfile 
import os
import subprocess
from shutil import copy
import re
import math

def loadGradeBook(gradebookFile):
  gradebook = []
  i = 0
  with open(gradebookFile, 'rb') as csvfile:
    students = csv.reader(csvfile, delimiter=',')
    for row in students:
      if i > 1:
        gradebook.append(row)
      i+=1

  return gradebook


def unzip(assignmentsPath):
  assDir = path = os.path.abspath(assignmentsPath)
  for dirName, subdirList, fileList in os.walk(assignmentsPath):
    print('Found directory: %s' % dirName)
    for fname in fileList:
        filepath = os.path.join(dirName, fname)
        if filepath.endswith('.zip'):
          print('\tUnzipping: %s' % fname)
          zip = zipfile.ZipFile(filepath.decode('utf-8').strip())
          path = os.path.abspath("./unzipped/").decode('utf-8').strip()
          zip.extractall(u"\\\\?\\" + path + "\\"+ fname.replace(".zip","").encode('utf-8').strip())

def get_immediate_subdirectories(d):
    return filter(os.path.isdir, [os.path.join(d,f) for f in os.listdir(d)])

def grade(params):
  grades = {}
  if params['modeSingle']:
    for root, dirs, files in os.walk("./unzipped"):
      for fname in files:
        print "\n\n========================\nGrading: " + fname + "\n========================"
        copy(os.path.join(root, fname), params['templatePath'])
        os.remove(params['templatePath'] + params['csFiles'][0])
        os.rename(params['templatePath'] + fname, params['templatePath'] + params['csFiles'][0])

        print "\n\nBuilding...\n"
        results = buildAndTest(params['slnPath'], params['dllPath'], fname)
        grades[fname] = results
        print "Results: \n" 
        print results
  else:
    for proj in get_immediate_subdirectories("./unzipped"):
      if not "__MACOSX" in proj:
        print "\n\n========================\nGrading: " + proj + "\n========================"
        missing = False
        listFound = False
        for codeFile in params['csFiles']:
          found = False
          for root, dirs, files in os.walk(proj):
            for fname in files:
              if fname.lower().endswith(codeFile.lower()) and not "._" in fname:
                print("Copying: " + fname)
                copy(os.path.join(root, fname), params['templatePath'])
                os.rename(params['templatePath'] + fname, params['templatePath'] + codeFile)
                found = True

              if params['defaultFile'] and fname == params['defaultFileName']:
                print "Copying custom listDict"
                copy(os.path.join(root, fname), params['templatePath'])
                listFound = True

          if not found:
            missing = True

        if params['defaultFile'] and  not listFound:
          print "Using template listDict"
          copy(params['defaultFileName'], params['templatePath'])

        if not missing:
          print "\n\nBuilding...\n"
          results = buildAndTest(params['slnPath'], params['dllPath'], proj[11:])
          grades[proj[11:]] = results
          print "Results: \n" 
          print results
        else:
          print "MISSING FILES"
          exportTests("MISSING FILES",proj[11:])
          grades[proj[11:]] = {'passed': 0, 'failed': 89}
  return grades

def buildAndTest(slnPath, dllPath,name):
  buildPath = '"C:/Program Files (x86)/MSBuild/12.0/Bin/MSBuild.exe" ' + slnPath
  build = subprocess.Popen(buildPath, shell=True, stdout=subprocess.PIPE).stdout.read()
  if not "Build FAILED." in build:
    print "\ntesting...\n"
    testPath = '"C:/Program Files (x86)/Microsoft Visual Studio 12.0/Common7/IDE/MSTest.exe" /testcontainer:'+ dllPath + ' /detail:errormessage'
    output =  subprocess.Popen(testPath, stdout=subprocess.PIPE, shell=True).stdout.read()
    exportTests(output,name)
    results = cleanResults(output)
  else:
    print "NO BUILD"
    exportTests(build,name)
    results = {'passed': 0, 'failed': 99}
  return results

def cleanResults(results):
  results = results.split('Summary')[1]
  passed = re.search(r'Passed.+\d+', results)
  failed = re.search(r'Failed.+\d+', results)
  if passed:
    passed = passed.group(0)
    passed =  int(re.search(r'\d+',passed).group(0))
  else:
    passed = 0

  if failed:
    failed = failed.group(0)
    failed =  int(re.search(r'\d+',failed).group(0))
  else:
    failed = 0

  return {'passed': passed, 'failed': failed}

def exportTests(out,name):
  outfile = open('./results/'+name+'.txt', 'w')
  outfile.write(out)
  outfile.close()

def exportGrades(grades, name):
  with open(name, 'w') as outfile:
    json.dump(grades, outfile)

def cleanGrades(fname):
  gradeDict = {}
  with open(fname) as data_file:    
    grades = json.load(data_file)
    print grades

  for key in grades.keys():
    idNum = re.search(r'_\w+_', key).group(0).split("_")[1]
    gradeDict[idNum] = grades[key]
  
  return gradeDict

def enterScore(gradebook, grades, col):
  newgrades = []
  for row in gradebook:
    idNum = row[1]
    print "\nID: " + row[1]
    if idNum in grades:
      newGrade = math.ceil(100*float(grades[idNum]['passed'])/(grades[idNum]['failed'] + grades[idNum]['passed']))
      print "Current grade: " + row[col] 
      if not row[col] or int(row[col]) <= 0:
        row[col] = newGrade
        print "Grade: ", newGrade
        newgrades.append(row[0])
      else:
        print "Already Graded"
    else:
      print "no submission"
      row[col] = 0
  exportGrades(newgrades, "changed.txt")
  return gradebook

def exportCanvas(grades):
  with open('newgrades.csv', 'wb') as csvfile:
    gradewriter = csv.writer(csvfile, delimiter=',')
    for student in grades:
      gradewriter.writerow(student)

def main():
  gradebook = loadGradeBook("08_Jun_20-02_Grades-2015SP_EECS_214-0_SEC20_AND_395-0_SEC20.csv")
  unzip("./assignments") 

  params = {
    'modeSingle': False,                                        # Student uploaded single CS file
    'csFiles': ["BinaryHeap.cs","UndirectedGraph.cs"],          # Directory to copy CS files from, relative to unzipped project directory
    'templatePath': "./template/PathPlanner/",                  # Directory to copy CS files to, relative to root directory
    'slnPath': "\"./template/PathPlanner.sln\"",                # Location of sln file relative to root
    'dllPath': "./template/Tests/bin/Debug/Tests.dll"           # Location of test dll relative to root
    'defaultFile': False,                                       # Optional default file if custom file is not uploaded
    'defaultFileName' : "",                                     # Name of default file. Plase in root
  }

  grades = grade(params)
  exportGrades(grades,"grades.txt")
  grades = cleanGrades("grades.txt")
  newGrades = enterScore(gradebook,grades, 10)
  exportCanvas(newGrades)


main()