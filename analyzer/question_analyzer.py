import csv, math, sys, yaml

app_constants = yaml.safe_load(open("app_constants.yml", "r"))


def analyze_question(
    scores,
    question,
    first_score_row,
    correct_answer_row,
    response_minimum,
    score_column,
    exam_metrics,
    manual_overides,
):
    question_column = scores[0].index(question)
    correct_answer = scores[correct_answer_row][question_column]
    if manual_overides and question in manual_overides.keys():
        correct_answer = manual_overides[question]
    response_count = count_responses(scores, question_column, first_score_row)
    if response_count < response_minimum:
        return
    question_metrics = calculate_question_metrics(
        scores,
        question_column,
        correct_answer,
        first_score_row,
        response_count,
        score_column,
        exam_metrics,
    )
    question_discrimination = calculate_question_discrimination(
        question_metrics["proportion_correct"],
        question_metrics["proportion_incorrect"],
        question_metrics["mean_score_of_correct_responses"],
        question_metrics["mean_score_of_incorrect_responses"],
        exam_metrics["exam_standard_deviation"],
    )
    number_bottom_quartile_who_saw_question = (
        question_metrics["number_bottom_quartile_incorrect_response"]
        + question_metrics["number_bottom_quartile_correct_response"]
    )
    number_top_quartile_who_saw_question = (
        question_metrics["number_top_quartile_incorrect_response"]
        + question_metrics["number_top_quartile_correct_response"]
    )
    question_difficulty = calculate_question_difficulty(
        number_bottom_quartile_who_saw_question,
        number_top_quartile_who_saw_question,
        question_metrics["number_bottom_quartile_correct_response"],
        question_metrics["number_top_quartile_correct_response"],
    )
    question_discrimination2 = calculate_question_discrimination2(
        exam_metrics["number_in_quartile_1"],
        exam_metrics["number_in_quartile_4"],
        question_metrics["number_bottom_quartile_correct_response"],
        question_metrics["number_top_quartile_correct_response"],
    )
    question_concept_understanding = calculate_question_concept_understanding(
        question_metrics["single_wrong_response_more_common_than_correct_response"],
        question_metrics["below_50_percent_correct"],
        question_metrics["quartile_4_below_75_percent_correct"],
        question_metrics["quartile_4_below_50_percent_correct"],
        question_metrics["quartile_4_below_25_percent_correct"],
    )
    return {
        "question": question,
        "discrimination1": question_discrimination,
        "difficulty": question_difficulty,
        "discrimination2": question_discrimination2,
        "concept_understanding": question_concept_understanding,
    }


def analyze_questions(
    scores,
    first_question_column,
    first_score_row,
    correct_answer_row,
    response_minimum,
    score_column,
    exam_metrics,
    manual_overides,
):
    question_analyses = []
    for question in scores[0][first_question_column:]:
        question_analysis = analyze_question(
            scores,
            question,
            first_score_row,
            correct_answer_row,
            response_minimum,
            score_column,
            exam_metrics,
            manual_overides,
        )
        if question_analysis:
            question_analyses.append(question_analysis)
    return question_analyses


def calculate_exam_max(scores, score_column, first_score_row):
    exam_max = 0
    for score_row in scores[first_score_row:]:
        score = score_row[score_column]
        if float(score) > exam_max:
            exam_max = float(score)
    return exam_max


def calculate_exam_mean(scores, score_column, first_score_row):
    exam_scores = []
    for score_row in scores[first_score_row:]:
        score = score_row[score_column]
        exam_scores.append(float(score))
    return sum(exam_scores) / len(exam_scores)


# Quartile 1 is the bottom, quartile 4 is the top
def calculate_exam_metrics(scores, score_column, first_score_row):
    exam_mean = calculate_exam_mean(scores, score_column, first_score_row)
    exam_standard_deviation = calculate_exam_standard_deviation(
        scores, score_column, exam_mean, first_score_row
    )
    exam_max = calculate_exam_max(scores, score_column, first_score_row)
    exam_min = calculate_exam_min(scores, score_column, first_score_row)
    exam_quartile_1 = calculate_exam_quartile(1, scores, score_column, first_score_row)
    exam_quartile_2 = calculate_exam_quartile(2, scores, score_column, first_score_row)
    exam_quartile_3 = calculate_exam_quartile(3, scores, score_column, first_score_row)
    number_in_quartile_1 = calculate_number_in_quartile(
        1,
        scores,
        score_column,
        first_score_row,
        exam_quartile_1,
        exam_quartile_2,
        exam_quartile_3,
    )
    number_in_quartile_2 = calculate_number_in_quartile(
        2,
        scores,
        score_column,
        first_score_row,
        exam_quartile_1,
        exam_quartile_2,
        exam_quartile_3,
    )
    number_in_quartile_3 = calculate_number_in_quartile(
        3,
        scores,
        score_column,
        first_score_row,
        exam_quartile_1,
        exam_quartile_2,
        exam_quartile_3,
    )
    number_in_quartile_4 = calculate_number_in_quartile(
        4,
        scores,
        score_column,
        first_score_row,
        exam_quartile_1,
        exam_quartile_2,
        exam_quartile_3,
    )
    return {
        "exam_mean": exam_mean,
        "exam_standard_deviation": exam_standard_deviation,
        "exam_max": exam_max,
        "exam_min": exam_min,
        "exam_quartile_1": exam_quartile_1,
        "exam_quartile_2": exam_quartile_2,
        "exam_quartile_3": exam_quartile_3,
        "number_in_quartile_1": number_in_quartile_1,
        "number_in_quartile_2": number_in_quartile_2,
        "number_in_quartile_3": number_in_quartile_3,
        "number_in_quartile_4": number_in_quartile_4,
    }


def calculate_exam_min(scores, score_column, first_score_row):
    exam_min = ""
    for score_row in scores[first_score_row:]:
        score = score_row[score_column]
        if exam_min == "" or float(score) < exam_min:
            exam_min = float(score)
    return exam_min


def calculate_exam_quartile(quartile, scores, score_column, first_score_row):
    exam_scores = []
    for score_row in scores[first_score_row:]:
        score = score_row[score_column]
        exam_scores.append(float(score))
    exam_scores.sort()
    if quartile == 1:
        if (len(exam_scores) / 4).is_integer():
            return (
                exam_scores[int(len(exam_scores) / 4)]
                + exam_scores[int(len(exam_scores) / 4) - 1]
            ) / 2
        else:
            return exam_scores[math.ceil(len(exam_scores) / 4)]
    elif quartile == 2:
        if (len(exam_scores) / 2).is_integer():
            return (
                exam_scores[int(len(exam_scores) / 2)]
                + exam_scores[int(len(exam_scores) / 2) - 1]
            ) / 2
        else:
            return exam_scores[math.ceil(len(exam_scores) / 2)]
    elif quartile == 3:
        if (len(exam_scores) / 4 * 3).is_integer():
            return (
                exam_scores[int(len(exam_scores) / 4 * 3)]
                + exam_scores[int(len(exam_scores) / 4 * 3) - 1]
            ) / 2
        else:
            return exam_scores[math.ceil(len(exam_scores) / 4 * 3)]


def calculate_exam_standard_deviation(scores, score_column, exam_mean, first_score_row):
    sum_of_squares = 0
    for score_row in scores[first_score_row:]:
        score = score_row[score_column]
        sum_of_squares += (float(score) - exam_mean) ** 2
    return (sum_of_squares / len(scores[first_score_row:])) ** 0.5


# Mean score of those that answered correctly (M1)
def calculate_mean_score_of_correct_responses(
    scores, question_column, correct_answer, first_score_row, score_column
):
    correct_responses = []
    for score_row in scores[first_score_row:]:
        if len(score_row) > question_column:
            response = score_row[question_column]
            if response == correct_answer:
                correct_responses.append(float(score_row[score_column]))
    return (
        sum(correct_responses) / len(correct_responses)
        if len(correct_responses) > 0
        else 0
    )


# Mean score of those that answered incorrectly (M0)
def calculate_mean_score_of_incorrect_responses(
    scores, question_column, correct_answer, first_score_row, score_column
):
    incorrect_responses = []
    for score_row in scores[first_score_row:]:
        if len(score_row) > question_column:
            response = score_row[question_column]
            if response != correct_answer and response != "":
                incorrect_responses.append(float(score_row[score_column]))
    return (
        sum(incorrect_responses) / len(incorrect_responses)
        if len(incorrect_responses) > 0
        else 0
    )


def calculate_number_in_quartile(
    quartile,
    scores,
    score_column,
    first_score_row,
    exam_quartile_1,
    exam_quartile_2,
    exam_quartile_3,
):
    if quartile == 1:
        return len(
            [
                score_row
                for score_row in scores[first_score_row:]
                if float(score_row[score_column]) <= exam_quartile_1
            ]
        )
    elif quartile == 2:
        return len(
            [
                score_row
                for score_row in scores[first_score_row:]
                if float(score_row[score_column]) > exam_quartile_1
                and float(score_row[score_column]) <= exam_quartile_2
            ]
        )
    elif quartile == 3:
        return len(
            [
                score_row
                for score_row in scores[first_score_row:]
                if float(score_row[score_column]) > exam_quartile_2
                and float(score_row[score_column]) <= exam_quartile_3
            ]
        )
    elif quartile == 4:
        return len(
            [
                score_row
                for score_row in scores[first_score_row:]
                if float(score_row[score_column]) > exam_quartile_3
            ]
        )


# https://www.researchgate.net/publication/323705126
def calculate_question_difficulty(
    number_in_quartile_1,
    number_in_quartile_4,
    number_bottom_quartile_correct_response,
    number_top_quartile_correct_response,
):
    number_both = number_in_quartile_1 + number_in_quartile_4
    if number_both == 0:
        return 0
    return (
        (number_bottom_quartile_correct_response + number_top_quartile_correct_response)
        / number_both
        * 100
    )


def calculate_question_discrimination(
    proportion_correct,
    proportion_incorrect,
    mean_score_of_correct_responses,
    mean_score_of_incorrect_responses,
    exam_standard_deviation,
):
    if proportion_correct == 0 or proportion_incorrect == 0:
        return 0
    return (
        (mean_score_of_correct_responses - mean_score_of_incorrect_responses)
        / exam_standard_deviation
    ) / (proportion_correct * proportion_incorrect) ** 0.5


# https://www.researchgate.net/publication/323705126
def calculate_question_discrimination2(
    number_in_quartile_1,
    number_in_quartile_4,
    number_bottom_quartile_correct_response,
    number_top_quartile_correct_response,
):
    number_both = number_in_quartile_1 + number_in_quartile_4
    if number_both == 0:
        return 0
    return (
        2
        * (
            number_top_quartile_correct_response
            - number_bottom_quartile_correct_response
        )
        / number_both
        * 100
    )


def calculate_question_concept_understanding(
    single_wrong_response_more_common_than_correct_response,
    below_50_percent_correct,
    quartile_4_below_75_percent_correct,
    quartile_4_below_50_percent_correct,
    quartile_4_below_25_percent_correct,
):
    score = 5
    if single_wrong_response_more_common_than_correct_response:
        score -= 1
    if below_50_percent_correct:
        score -= 1
    if quartile_4_below_75_percent_correct:
        score -= 1
    if quartile_4_below_50_percent_correct:
        score -= 1
    if quartile_4_below_25_percent_correct:
        score -= 1
    return score


def calculate_question_metrics(
    scores,
    question_column,
    correct_answer,
    first_score_row,
    response_count,
    score_column,
    exam_metrics,
):
    proportion_correct = calculate_proportion_correct(
        scores, question_column, correct_answer, first_score_row, response_count
    )
    proportion_incorrect = calculate_proportion_incorrect(
        scores, question_column, correct_answer, first_score_row, response_count
    )
    mean_score_of_correct_responses = calculate_mean_score_of_correct_responses(
        scores, question_column, correct_answer, first_score_row, score_column
    )
    mean_score_of_incorrect_responses = calculate_mean_score_of_incorrect_responses(
        scores, question_column, correct_answer, first_score_row, score_column
    )
    number_bottom_quartile_correct_response = count_bottom_quartile_correct_responses(
        scores,
        question_column,
        correct_answer,
        first_score_row,
        exam_metrics["exam_quartile_1"],
        score_column,
    )
    number_bottom_quartile_incorrect_response = (
        count_bottom_quartile_incorrect_responses(
            scores,
            question_column,
            correct_answer,
            first_score_row,
            exam_metrics["exam_quartile_1"],
            score_column,
        )
    )
    number_top_quartile_correct_response = count_top_quartile_correct_responses(
        scores,
        question_column,
        correct_answer,
        first_score_row,
        exam_metrics["exam_quartile_3"],
        score_column,
    )
    number_top_quartile_incorrect_response = count_top_quartile_incorrect_responses(
        scores,
        question_column,
        correct_answer,
        first_score_row,
        exam_metrics["exam_quartile_3"],
        score_column,
    )
    most_common_response = calculate_question_most_common_response(
        scores, question_column, first_score_row
    )
    single_wrong_response_more_common_than_correct_response = (
        True
        if most_common_response != correct_answer
        and most_common_response != ""
        and scores[question_column].count(most_common_response)
        > scores[question_column].count(correct_answer)
        else False
    )
    below_50_percent_correct = True if proportion_correct < 0.5 else False
    quartile_4_below_75_percent_correct = (
        True
        if number_top_quartile_correct_response
        < 0.75
        * (
            number_top_quartile_correct_response
            + number_top_quartile_incorrect_response
        )
        else False
    )
    quartile_4_below_50_percent_correct = (
        True
        if number_top_quartile_correct_response
        < 0.50
        * (
            number_top_quartile_correct_response
            + number_top_quartile_incorrect_response
        )
        else False
    )
    quartile_4_below_25_percent_correct = (
        True
        if number_top_quartile_correct_response
        < 0.25
        * (
            number_top_quartile_correct_response
            + number_top_quartile_incorrect_response
        )
        else False
    )
    return {
        "proportion_correct": proportion_correct,
        "proportion_incorrect": proportion_incorrect,
        "mean_score_of_correct_responses": mean_score_of_correct_responses,
        "mean_score_of_incorrect_responses": mean_score_of_incorrect_responses,
        "number_bottom_quartile_correct_response": number_bottom_quartile_correct_response,
        "number_bottom_quartile_incorrect_response": number_bottom_quartile_incorrect_response,
        "number_top_quartile_correct_response": number_top_quartile_correct_response,
        "number_top_quartile_incorrect_response": number_top_quartile_incorrect_response,
        "most_common_response": most_common_response,
        "single_wrong_response_more_common_than_correct_response": single_wrong_response_more_common_than_correct_response,
        "below_50_percent_correct": below_50_percent_correct,
        "quartile_4_below_75_percent_correct": quartile_4_below_75_percent_correct,
        "quartile_4_below_50_percent_correct": quartile_4_below_50_percent_correct,
        "quartile_4_below_25_percent_correct": quartile_4_below_25_percent_correct,
    }


def calculate_question_most_common_response(scores, question_column, first_score_row):
    response_counts = {}
    for score_row in scores[first_score_row:]:
        if len(score_row) > question_column:
            response = score_row[question_column]
            if response in response_counts:
                response_counts[response] += 1
            else:
                response_counts[response] = 1
    return max(response_counts, key=response_counts.get)


def calculate_proportion_correct(
    scores, question_column, correct_answer, first_score_row, response_count
):
    correct_count = 0
    for score_row in scores[first_score_row:]:
        if len(score_row) > question_column:
            response = score_row[question_column]
            if response == correct_answer:
                correct_count += 1
    return correct_count / response_count


def calculate_proportion_incorrect(
    scores, question_column, correct_answer, first_score_row, response_count
):
    incorrect_count = 0
    for score_row in scores[first_score_row:]:
        if len(score_row) > question_column:
            response = score_row[question_column]
            if response != correct_answer and response != "":
                incorrect_count += 1
    return incorrect_count / response_count


def count_bottom_quartile_correct_responses(
    scores,
    question_column,
    correct_answer,
    first_score_row,
    exam_quartile_1,
    score_column,
):
    count = 0
    for score_row in scores[first_score_row:]:
        if len(score_row) > question_column:
            response = score_row[question_column]
            if (
                response == correct_answer
                and float(score_row[score_column]) <= exam_quartile_1
            ):
                count += 1
    return count


def count_bottom_quartile_incorrect_responses(
    scores,
    question_column,
    correct_answer,
    first_score_row,
    exam_quartile_1,
    score_column,
):
    count = 0
    for score_row in scores[first_score_row:]:
        if len(score_row) > question_column:
            response = score_row[question_column]
            if (
                response != correct_answer
                and response != ""
                and float(score_row[score_column]) <= exam_quartile_1
            ):
                count += 1
    return count


def count_top_quartile_correct_responses(
    scores,
    question_column,
    correct_answer,
    first_score_row,
    exam_quartile_3,
    score_column,
):
    count = 0
    for score_row in scores[first_score_row:]:
        if len(score_row) > question_column:
            response = score_row[question_column]
            if (
                response == correct_answer
                and float(score_row[score_column]) > exam_quartile_3
            ):
                count += 1
    return count


def count_top_quartile_incorrect_responses(
    scores,
    question_column,
    correct_answer,
    first_score_row,
    exam_quartile_3,
    score_column,
):
    count = 0
    for score_row in scores[first_score_row:]:
        if len(score_row) > question_column:
            response = score_row[question_column]
            if (
                response != correct_answer
                and response != ""
                and float(score_row[score_column]) > exam_quartile_3
            ):
                count += 1
    return count


def count_responses(scores, question_column, first_score_row):
    count = 0
    for score_row in scores[first_score_row:]:
        if len(score_row) > question_column:
            response = score_row[question_column]
            if response != "":
                count += 1
    return count


def grade_measure(analysis_result, levels):
    for level in reversed(levels.keys()):
        if analysis_result >= levels[level]:
            return level


def grade_questions(
    question_analyses,
    discrimination1_levels,
    discrimination2_levels,
    difficulty_levels,
    concept_understanding_levels,
):
    for question_analysis in question_analyses:
        question_analysis["discrimination1_level"] = grade_measure(
            question_analysis["discrimination1"], discrimination1_levels
        )
        question_analysis["discrimination2_level"] = grade_measure(
            question_analysis["discrimination2"], discrimination2_levels
        )
        question_analysis["difficulty_level"] = grade_measure(
            question_analysis["difficulty"], difficulty_levels
        )
        question_analysis["concept_understanding_level"] = grade_measure(
            question_analysis["concept_understanding"], concept_understanding_levels
        )
    return question_analyses


def load_analyzer_config(analyzer_config_file):
    with open(analyzer_config_file, "r", encoding="utf8") as f:
        return yaml.safe_load(f)


def load_scores(scores_file):
    with open(scores_file, "r", encoding="utf8") as f:
        return list(csv.reader(f))


def main():
    if len(sys.argv) != 4:
        print(
            "Usage: python question_analyzer.py analyzer_config.yml scores.csv output.txt"
        )
        sys.exit(1)

    analyzer_config_file = sys.argv[1]
    scores_file = sys.argv[2]
    output_file_name = sys.argv[3]

    analyzer_settings = load_analyzer_config(analyzer_config_file)
    scores = load_scores(scores_file)

    # Load question settings
    first_question_column = analyzer_settings["first_question_column"]
    first_score_row = analyzer_settings["first_score_row"]
    correct_answer_row = analyzer_settings["correct_answer_row"]
    response_minimum = analyzer_settings["response_minimum"]
    score_column = analyzer_settings["score_column"]
    manual_overides = analyzer_settings["manual_overides"]

    # Load app settings
    discrimination1_levels = app_constants["discrimination1_levels"]
    discrimination2_levels = app_constants["discrimination2_levels"]
    difficulty_levels = app_constants["difficulty_levels"]
    concept_understanding_levels = app_constants["concept_understanding_levels"]

    exam_metrics = calculate_exam_metrics(scores, score_column, first_score_row)
    question_analyses = analyze_questions(
        scores,
        first_question_column,
        first_score_row,
        correct_answer_row,
        response_minimum,
        score_column,
        exam_metrics,
        manual_overides,
    )
    graded_question_analyses = grade_questions(
        question_analyses,
        discrimination1_levels,
        discrimination2_levels,
        difficulty_levels,
        concept_understanding_levels,
    )
    write_output(graded_question_analyses, output_file_name)


def write_output(graded_question_analyses, output_file_name):
    output_text = ""
    low_discrimination_levels = [
        "weak_reverse_discrimination",
        "moderate_reverse_discrimination",
        "strong_reverse_discrimination",
    ]
    low_difficulty_levels = ["easy", "minorly_difficult", "strongly_difficult"]
    low_concept_understanding_levels = ["no_understanding", "some_understanding"]
    low_discrimination_scores = [-1, -2, -3]
    low_difficulty_scores = [-2, -1, -1]
    low_concept_understanding_scores = [-2, -1]
    top_bad_question_cutoff = -4
    top_bad_questions = []
    for question_analysis in graded_question_analyses:
        if (
            question_analysis["discrimination1_level"] in low_discrimination_levels
            or question_analysis["difficulty_level"] in low_difficulty_levels
            or question_analysis["concept_understanding_level"]
            in low_concept_understanding_levels
        ):
            question_score = 0
            if question_analysis["discrimination1_level"] in low_discrimination_levels:
                question_score += low_discrimination_scores[
                    low_discrimination_levels.index(
                        question_analysis["discrimination1_level"]
                    )
                ]
            if question_analysis["difficulty_level"] in low_difficulty_levels:
                question_score += low_difficulty_scores[
                    low_difficulty_levels.index(question_analysis["difficulty_level"])
                ]
            if (
                question_analysis["concept_understanding_level"]
                in low_concept_understanding_levels
            ):
                question_score += low_concept_understanding_scores[
                    low_concept_understanding_levels.index(
                        question_analysis["concept_understanding_level"]
                    )
                ]
            if question_score <= top_bad_question_cutoff:
                top_bad_questions.append(
                    (question_analysis["question"], question_score)
                )
            output_text += question_analysis["question"] + "\n"
            if question_analysis["discrimination1_level"] in low_discrimination_levels:
                output_text += (
                    "Discrimination 1: "
                    + str(question_analysis["discrimination1"])
                    + " ("
                    + question_analysis["discrimination1_level"]
                    + ")\n"
                )
            if question_analysis["difficulty_level"] in low_difficulty_levels:
                output_text += (
                    "Difficulty: "
                    + str(question_analysis["difficulty"])
                    + " ("
                    + question_analysis["difficulty_level"]
                    + ")\n"
                )
            if (
                question_analysis["concept_understanding_level"]
                in low_concept_understanding_levels
            ):
                output_text += (
                    "Concept Understanding: "
                    + str(question_analysis["concept_understanding"])
                    + " ("
                    + question_analysis["concept_understanding_level"]
                    + ")\n"
                )
            output_text += "\n"
    output_text += "Top Bad Questions:\n"
    for question in top_bad_questions:
        output_text += question[0] + ": " + str(question[1]) + "\n"

    with open(output_file_name, "w", newline="", encoding="utf8") as f:
        f.write(output_text)

        # writer = csv.writer(f)
        # writer.writerow(['Question', 'Discrimination1', 'Difficulty', 'Discrimination2', 'Concept Understanding', 'Discrimination Level', 'Difficulty Level', 'Discrimination2 Level', 'Concept Understanding Level'])
        # for question_analysis in graded_question_analyses:
        #  writer.writerow([question_analysis['question'], question_analysis['discrimination1'], question_analysis['difficulty'], question_analysis['discrimination2'], question_analysis['concept_understanding'], question_analysis['discrimination1_level'], question_analysis['difficulty_level'], question_analysis['discrimination2_level'], question_analysis['concept_understanding_level']])


if __name__ == "__main__":
    main()
