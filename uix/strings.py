__all__ = ['ifind', 'i_find']

def ifind(line, word, ignoreds=''):

    local_word = []
    num = len(word)
    num_letter = 0
    for n_letter, letter in enumerate(line):
        if letter == word[num_letter]:
            num_letter += 1
            if num_letter == num:
                local_word.append(n_letter+1)
                return local_word
            elif num_letter == 1:
                local_word.append(n_letter)
        elif [x for x in ignoreds if letter == x]:
            pass
        else:
            break

def i_find(line, word, ignoreds=[]):
    local_word = []
    num = len(word)
    len_line = len(line)
    num_letter = 0
    for n_letter, letter in enumerate(line):
        if letter == word[num_letter]:
            num_letter += 1
            if num_letter == num:
                local_word.append(n_letter+1)
                if len_line > n_letter+1:
                    if line[n_letter+1] not in ignoreds[1]:
                        num_letter = 0
                        local_word.clear()
                if num_letter != 0:
                    return local_word
            elif num_letter == 1:
                local_word.append(n_letter)
                if ignoreds and n_letter != 0:
                    if line[n_letter-1] not in ignoreds[0]:
                        num_letter = 0
                        local_word.clear()
        else:
            num_letter = 0
            local_word.clear()
