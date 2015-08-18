# Canvas/Visual Studio 12 Auto Grader
This python script unzips, builds, and tests Visual studio projects and add grades to a Canvas grade book file. Each step of the process is broken down in the `main()`. You can turn them on and off as need and to not repeat steps. All file paths are relative to root directory.

## Requirements
* [Python on your DOS path](https://docs.python.org/2/using/windows.html#excursus-setting-environment-variables)
* Visual Studio 12

## Setup
### Files
* Place Canvas grade book export in root
* Download assignments and place individual zips in `/assignments` . Note if students did not upload zips and just single files, place files in `/unzipped`.
* Place template project in `/template `

### Params
All settings are set in `main()`
* Set arg for `loadGradeBook()` to the name of the gradebook file
* Set Params
  * `modeSingle` - if you are grading a single file
  * `csFiles` - Name of files graded (enter one if its just an array)
  * `templatePath` - Directory to copy CS files to
  * `slnPath` - Location of sln file relative to root
  * `dllPath` - Location of test dll. This will appear after you build the template in `./template/projectName/bin/Debug/`
* Set the last param of `enterScore` to the column number of the assignment in the gradebook

### Fall back file (optional)
If the turned in files had an optional file, you can use this as a fallback default file. Only one back up file is supported. To set one up, follow these steps:
* Place file in
* In `params` set `defaultFile` to true
* In `params` set `defaultFileName` to the file name

## Running auto grader
Running the script can take a couple tries to finish. Some assignments may not stop running. Those assignments must be removed from `/unzipped`, graded manually and the autograder restarted. Besure to turn of unecessary methods between reruns, such as `unzip()`. To run the script: 
* cd to the grader folder
* run the script
* Manually grade a subset to verify the grades are valid.

### Transfering Grades
The final grades will be exported to `newgrades.csv` and each students build outputs will be in `/results`. To import the grades back into canvas:
* Mute the assignment on Canvas
* Open `newgrades.csv`, copy the contents
* Open the gradebook export and paste the contents but retain the first two rows.
* Unmute the grades when ready.
