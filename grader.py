import csv, sys, yaml


def analyze(config, scores_file):
  with open(scores_file, 'r', encoding="utf8") as f:
    scores = list(csv.reader(f))
    for student in range(config['first_score_row']-1, len(scores)):
      student_number_correct = 0
      student_number_correct_by_section = {}
      student_number_correct_by_sub_section = {}
      sections_starts = config['section_starts']
      section_numbers = config['section_numbers']
      section_names = config['section_names']
      sub_sections_starts = config['sub_section_starts']
      sub_section_numbers = config['sub_section_numbers']
      sub_section_names = config['sub_section_names']
      section_number_of_questions = config['section_number_of_questions']
      sub_section_number_of_questions = config['sub_section_number_of_questions']
      first_question_column = config['first_question_column']-1
      for question in range(first_question_column, len(scores[student])-1):
        if scores[student][question] == scores[config['correct_answer_row']-1][question]:
          student_number_correct += 1
          for section in range(len(sections_starts)-1, -1, -1):
            if question+1-first_question_column >= sections_starts[section]:
              if section_numbers[section] not in student_number_correct_by_section:
                student_number_correct_by_section[section_numbers[section]] = 0
              student_number_correct_by_section[section_numbers[section]] += 1
              break
          for sub_section in range(len(sub_sections_starts)-1, -1, -1):
            if question+1-first_question_column >= sub_sections_starts[sub_section]:
              if sub_section_numbers[sub_section] not in student_number_correct_by_sub_section:
                student_number_correct_by_sub_section[sub_section_numbers[sub_section]] = 0
              student_number_correct_by_sub_section[sub_section_numbers[sub_section]] += 1
              break
      student_name_column = config['student_name_column']-1
      student_attempt_column = config['student_attempt_column']-1
      number_of_questions = config['number_of_questions']
      print("Student {} Attempt {}:  {} correct out of {}: {}%".format(scores[student][student_name_column], scores[student][student_attempt_column], student_number_correct, number_of_questions, round(student_number_correct/number_of_questions*100, 2)))
      for section in student_number_correct_by_section:
        print("Domain {} {}:  {} correct out of {}: {}%".format(section, section_names[section-1], student_number_correct_by_section[section], section_number_of_questions[section-1], round(student_number_correct_by_section[section]/section_number_of_questions[section-1]*100, 2)))
      for sub_section in student_number_correct_by_sub_section:
        sub_section_index = list(student_number_correct_by_sub_section.keys()).index(sub_section)
        print("Sub Domain {} {}:  {} correct out of {}: {}%".format(sub_section, sub_section_names[sub_section_index], student_number_correct_by_sub_section[sub_section], sub_section_number_of_questions[sub_section_index], round(student_number_correct_by_sub_section[sub_section]/sub_section_number_of_questions[sub_section_index]*100, 2)))
      print("------------------------------")


def load_config(config_file):
  with open(config_file, 'r') as f:
    config = yaml.safe_load(f)
  return config


def main():
  if len(sys.argv) != 3:
    print("Usage: python grader.py config.yml scores.csv")
    sys.exit(1)
  
  config_file = sys.argv[1]
  scores_file = sys.argv[2]
  config = load_config(config_file)

  analyze(config, scores_file)


main()