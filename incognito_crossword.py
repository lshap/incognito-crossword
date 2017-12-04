from fetch_crossword import get_crossword
import getpass
import json

RED = '\033[91m'
YELLOW = '\033[93m'
GREEN = '\033[32m'
WIDTH = 15

def _get_login_creds():
    email = raw_input("Enter the email associated with your account\n")
    password = getpass.getpass(prompt="Enter your password\n")
    return {'email': email, 'password': password}
    
def _is_valid_clue(clue):
    try:
        return (len(clue) == 2 and (clue[0].lower() == 'a' or clue[0].lower() == 'd')\
                and int(clue[1])) 
    except ValueError:
        return False

def _format_answer(answer):
    formatted = [a or '_' for a in answer]
    return ' '.join(formatted) + '\n'

def _get_clue_options(crossword_data):
    across_clues = [(cl['clueNum'], len(_get_answer_indices('A', cl))) \
                    for cl in crossword_data['clues']['A']]
    down_clues = [(cl['clueNum'], len(_get_answer_indices('D', cl))) \
                   for cl in crossword_data['clues']['D']]
    return 'A {} \n D {}'.format(across_clues, down_clues)

def _get_answer_indices(clue_type, clue):
    if clue_type == 'A':
        return range(clue['clueStart'], clue['clueEnd'] + 1)
    elif clue_type == 'D':
        curr = clue['clueStart']
        indices = []
        while curr <= clue['clueEnd']:
            indices.append(curr)
            curr += WIDTH
        return indices

def _get_letters(letter_arr, indices):
    letters = []
    for index in indices:
        letters.append(letter_arr[index])
    return letters

def _save_answer(answer_to_save, answers, clue_type, clue): 
    indices = _get_answer_indices(clue_type, clue)
    for index, answer_index in enumerate(indices):
        if index < len(answer_to_save):
            answers[answer_index] = answer_to_save[index]

def _get_clue(crossword_data, clue):
    try:
        clues = crossword_data['clues'][clue[0].upper()] 
        clue = next(cl for cl in clues if str(cl['clueNum']) == clue[1])
        return clue
    except StopIteration:
        return None

def _check_answer(answer, correct):
    checked_answer = []
    for attempt, correct in zip(answer, correct):
        if attempt:
            if attempt.lower() == correct.lower():
                checked_answer.append(_make_color(attempt, GREEN))
            else:
                checked_answer.append(_make_color(attempt, RED))
        else:
            checked_answer.append('_') 
    print ' '.join(checked_answer) 

def _all_correct(answers, correct_answers):
    return False

def _shares_indices(indices_1, indices_2):
    return len(set.intersection(set(indices_1), set(indices_2))) > 0

def _get_adjacent_clues(clue_type, clue, crossword_data):
    adjacent_clue_type = 'D' if clue_type == 'A' else 'A' 
    clue_indices = _get_answer_indices(clue_type, clue)
    adjacent_clues = [cl for cl in crossword_data['clues'][adjacent_clue_type] if \
                      _shares_indices(clue_indices, _get_answer_indices(adjacent_clue_type, cl))]
    print 'looking for adjacent clues of type {}'.format(adjacent_clue_type)
    if len(adjacent_clues) > 0:
        return '{} {}'.format(adjacent_clue_type, ' '.join([str(cl['clueNum']) for cl in adjacent_clues]))
    else:
        return ''

def _make_color(word, color): 
    END = '\033[0m'
    return color + word + END

def main():
    creds = _get_login_creds() 
    crossword_data = get_crossword(creds['email'], creds['password'])
    stop = False

    correct_answers = crossword_data['answers']
    answers = [None] * len(correct_answers)
    retrieved_clue = None
    desired_clue = None
    correct_clues = []

    while not stop:
        if retrieved_clue and desired_clue:
            clue_type = 'A' if desired_clue[0].lower() == 'a' else 'D' 
            adjacent_clues = _get_adjacent_clues(clue_type, retrieved_clue, crossword_data)
            print _make_color('Adjacent: {}'.format(adjacent_clues), YELLOW)

        print _get_clue_options(crossword_data)
        clue_input = raw_input("which clue\n")

        # type 'q' to quit
        if clue_input == 'q':
            break
        desired_clue = clue_input.strip().split(' ')
        retrieved_clue = _get_clue(crossword_data, desired_clue)

        if _is_valid_clue(desired_clue) and retrieved_clue: 
            clue_type = 'A' if desired_clue[0].lower() == 'a' else 'D' 
            print retrieved_clue['value']
            start = retrieved_clue['clueStart']
            end = retrieved_clue['clueEnd'] + 1

            answer_indices = _get_answer_indices(clue_type, retrieved_clue)
            answers_so_far = [answers[i] for i in answer_indices] 
            attempt = raw_input(_format_answer(answers_so_far))
            if attempt:
                cleaned_attempt = [a.strip() for a in attempt][:(end - start)]
                _save_answer(cleaned_attempt, answers, clue_type, retrieved_clue)
                check_correct = raw_input('check? (y/n)\n')
                if check_correct == 'y':
                    _check_answer(cleaned_attempt, 
                                  _get_letters(correct_answers, answer_indices))
            if _all_correct(answers, correct_answers):
                print 'Congrats, you got them all!'
                break
        else:
            print "Invalid clue option"

if __name__ == '__main__':
    main()
