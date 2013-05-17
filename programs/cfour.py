import math
import sys

def check_input(args,nodeInfo):
  def error(message):
    print(message)
    sys.exit(1)
  
  # Parse Input File and perform checks
  def convert_mem_units(memory, iUnits):
    # Conversion factors from denoted units to MB
    memConv = {"INTEGERWORDS": 7.62939*math.pow(10,-6), "KB": 1/1024.0, "MB": 1.0, "GB": 1024, "TB": math.pow(1024.0,2)}
    return memory * memConv[iUnits] 
  def clean_job_line(line):
    if "*CFOUR(" in line: line = line.split("*CFOUR(")[1]
    if ")" in line: line = line.split(")")[0]
    line = line.lstrip(" ").rstrip("\n").rstrip(" ")
    return line.upper()
  def parse_job_line(line, keywords):
    items = line.split(",")
    for item in items: keywords.update({item.split("=")[0]: item.split("=")[1]})
  def find_job_item(keywords, item_names, throw_error):
    for name in item_names:
      if name in keywords: return keywords[name]
    if throw_error:
      error(" or ".join(item_names)+" not found in keyword list")
    else:
      return False
 
  keywords = {}
  inputData = open(args['input'],"r").readlines()  
  for i in range(0, len(inputData)):
    if "*CFOUR" in inputData[i]:
      for j in range(i, len(inputData)):
        if len(inputData[j].split()) < 1: break
        else: parse_job_line(clean_job_line(inputData[j]), keywords)

  if args['parseInput']:
    # Checking for Appropriate Job Memory
    jobMemory = find_job_item(keywords, ["MEM","MEMORY"], False)
    if jobMemory:
      jobMemory = int(jobMemory)
      jobMemUnit = find_job_item(keywords, ["MEM_UNIT"], False)
      if jobMemUnit: # Convert Memory to MB
        jobMemory = convert_mem_units(jobMemory, jobMemUnit.upper())
      else:
        jobMemory = convert_mem_units(jobMemory, "INTEGERWORDS")
    nodeMemLimit = nodeInfo[args['queue']]['nodeMem'] * 0.95 / args['nslots']
    if jobMemory > nodeMemLimit: # Check if memory is more than 90% of Node
      error("Please reduce the memory of your job from "+str(jobMemory)+" MB to "+str(int(nodeMemLimit))+" MB or less for "+str(args['nslots'])+" processors")

def footer():
  # Explicity list the files we want to save because there will be other crap in there
  toSave = [ 'FCMINT', 'FCMFINAL', 'ZMATnew', 'JMOL.plot', 'JOBARC', 'FJOBARC', 'DIPDER', 'HESSIAN', 'MOLDEN' ]
  cmd = "tar --transform \"s,^,Job_Data_${JOB_ID}/,\" -vczf ${SGE_O_WORKDIR}/Job_Data_${JOB_ID}.tgz %s" % (' '.join(toSave))

  return cmd
 