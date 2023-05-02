import csv, sys, yaml


def analyze(config, scores_file):
  output = ""
  with open(scores_file, 'r', encoding="utf8") as f:                                                                # open the csv file with the scores       
    scores = list(csv.reader(f))                                                                                    # read the csv file into a list of lists
    for student in range(config['first_score_row']-1, len(scores)):                                                 # loop through each student
      student_number_correct = 0                                                                                    # initialize the number of questions correct for this student
      student_number_correct_by_section = {}                                                                        # initialize the number of questions correct for this student by section
      student_number_correct_by_sub_section = {}                                                                    # initialize the number of questions correct for this student by sub section
      sections_starts = config['section_starts']                                                                    # get the list of section start questions
      section_numbers = config['section_numbers']                                                                   # get the list of section numbers
      section_names = config['section_names']                                                                       # get the list of section names
      sub_sections_starts = config['sub_section_starts']                                                            # get the list of sub section start questions
      sub_section_numbers = config['sub_section_numbers']                                                           # get the list of sub section numbers
      sub_section_names = config['sub_section_names']                                                               # get the list of sub section names
      section_number_of_questions = config['section_number_of_questions']                                           # get the list of section number of questions
      sub_section_number_of_questions = config['sub_section_number_of_questions']                                   # get the list of sub section number of questions
      first_question_column = config['first_question_column']-1                                                     # get the first question column, make it zero based
      for question in range(first_question_column, len(scores[student])-1):                                         # loop through each question                     
        if (scores[student][question] == scores[config['correct_answer_row']-1][question] or 
            ('Q'+str(question-first_question_column+1) in config['manual_overides'] and
              scores[student][question] == config['manual_overides']['Q'+str(question-first_question_column+1)])):  # if the student's answer matches the correct answer or the manual override
          student_number_correct += 1                                                                               # increment the number of questions correct for this student
          for section in range(len(sections_starts)-1, -1, -1):                                                     # loop backwards through each section
            if question+1-first_question_column >= sections_starts[section]:                                        # if the question is in this section
              if section_numbers[section] not in student_number_correct_by_section:                                 # if this section is not in the dictionary
                student_number_correct_by_section[section_numbers[section]] = 0                                     # initialize the number of questions correct for this section
              student_number_correct_by_section[section_numbers[section]] += 1                                      # increment the number of questions correct for this section
              break                                                                                                 # break out of the loop
          for sub_section in range(len(sub_sections_starts)-1, -1, -1):                                             # loop backwards through each sub section
            if question+1-first_question_column >= sub_sections_starts[sub_section]:                                # if the question is in this sub section
              if sub_section_numbers[sub_section] not in student_number_correct_by_sub_section:                     # if this sub section is not in the dictionary
                student_number_correct_by_sub_section[sub_section_numbers[sub_section]] = 0                         # initialize the number of questions correct for this sub section
              student_number_correct_by_sub_section[sub_section_numbers[sub_section]] += 1                          # increment the number of questions correct for this sub section
              break                                                                                                 # break out of the loop
        else:                                                                                                      # if the student's answer does not match the correct answer
          for section in range(len(sections_starts)-1, -1, -1):                                                     # loop backwards through each section
            if question+1-first_question_column >= sections_starts[section]:                                        # if the question is in this section
              if section_numbers[section] not in student_number_correct_by_section:                                 # if this section is not in the dictionary
                student_number_correct_by_section[section_numbers[section]] = 0                                     # initialize the number of questions correct for this section
              break                                                                                                 # break out of the loop
          for sub_section in range(len(sub_sections_starts)-1, -1, -1):                                             # loop backwards through each sub section
            if question+1-first_question_column >= sub_sections_starts[sub_section]:                                # if the question is in this sub section
              if sub_section_numbers[sub_section] not in student_number_correct_by_sub_section:                     # if this sub section is not in the dictionary
                student_number_correct_by_sub_section[sub_section_numbers[sub_section]] = 0                         # initialize the number of questions correct for this sub section
              break                                                                                                 # break out of the loop

      student_name_column = config['student_name_column']-1
      student_attempt_column = config['student_attempt_column']-1
      number_of_questions = config['number_of_questions']
      output += "Student {} Attempt {}:  {} correct out of {}: {}%".format(scores[student][student_name_column], scores[student][student_attempt_column], student_number_correct, number_of_questions, round(student_number_correct/number_of_questions*100, 2))
      output += "\n"
      #print()
      for section in student_number_correct_by_section:
        output += "Domain {} {}:  {} correct out of {}: {}%".format(section, section_names[section-1], student_number_correct_by_section[section], section_number_of_questions[section-1], round(student_number_correct_by_section[section]/section_number_of_questions[section-1]*100, 2))
        output += "\n"
        #print()
      for sub_section in student_number_correct_by_sub_section:
        sub_section_index = list(student_number_correct_by_sub_section.keys()).index(sub_section)
        output += "Sub Domain {} {}:  {} correct out of {}: {}%".format(sub_section, sub_section_names[sub_section_index], student_number_correct_by_sub_section[sub_section], sub_section_number_of_questions[sub_section_index], round(student_number_correct_by_sub_section[sub_section]/sub_section_number_of_questions[sub_section_index]*100, 2))
        output += "\n"
        #print()
      output += "------------------------------"
      #print("------------------------------")
      output += "\n"
  return output


def load_config(config_file):
  with open(config_file, 'r', encoding="utf8") as f:
    config = yaml.safe_load(f)
  return config


def main():
  if len(sys.argv) != 4:
    print("Usage: python grader.py config.yml scores.csv output.txt")
    sys.exit(1)
  
  config_file = sys.argv[1]
  scores_file = sys.argv[2]
  output_file = sys.argv[3]
  config = load_config(config_file)

  output = analyze(config, scores_file)
  with open(output_file, 'w', encoding="utf8") as f:
    f.write(output)


main()