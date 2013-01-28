#!/usr/bin/env python
import random
import operator
import sys
import re
import yaml

f = open('vars', 'r')
vars_json = f.read()
f.close()
VARS = yaml.load(vars_json)  # reading yaml because it's a lenient json parser

f = open('introductions', 'r')
intro_lines = filter(lambda x: x.strip() != '', f.readlines())
intro_lines = map(lambda x: x.decode('utf-8'), intro_lines)
f.close()

f = open('evidence', 'r')
evidence_lines = filter(lambda x: x.strip() != '', f.readlines())
evidence_lines = map(lambda x: x.decode('utf-8'), evidence_lines)
f.close()

f = open('warnings', 'r')
warning_lines = filter(lambda x: x.strip() != '', f.readlines())
warning_lines = map(lambda x: x.decode('utf-8'), warning_lines)
f.close()

f = open('filler', 'r')
filler_lines = filter(lambda x: x.strip() != '', f.readlines())
filler_lines = map(lambda x: x.decode('utf-8'), filler_lines)
f.close()

f = open('citations', 'r')
citation_lines = filter(lambda x: x.strip() != '', f.readlines())
citation_lines = map(lambda x: x.decode('utf-8'), citation_lines)
f.close()

for x in VARS:
  VARS[x] = filter(lambda x: x.strip() != '', map(lambda x: x.strip(), VARS[x].split(',')))

PLURALIZE_CATEGORIES = set(['has/have', 'is/are', 'was/were', 'it/them', 'its/their', '\'s/\''])

# Try not to link on these categories.  Without something like this you tend to get non-sequiturs, linked
# by the object of sentences.
LINKED_CATEGORIES_DEMOTE_PRECEDENCE = ['malady', 'dangerous_noun', 'abstract_noun', 'era']
def demote_precedence_sort(a, b):
  try:
    ascore = LINKED_CATEGORIES_DEMOTE_PRECEDENCE.index(a)
  except ValueError:
    ascore = -1
  try:
    bscore = LINKED_CATEGORIES_DEMOTE_PRECEDENCE.index(b)
  except ValueError:
    bscore = -1
  return ascore - bscore

def capitalize_first(x):
  return x[0].upper() + x[1:]

class ConspiracyGenerator:

  def getwordchoice(self, m, category, previous_word_choice, previously_used, required_mappings):
    if previous_word_choice and category in PLURALIZE_CATEGORIES:
      singular, plural = category.split('/')
      return (plural if previous_word_choice[-1] == 's' else singular, required_mappings)
    elif category in required_mappings and len(required_mappings[category]) > 0:
      # chained sentence
      word_choice = required_mappings[category][0]
      if word_choice != previous_word_choice:    # don't repeat anything
        required_mappings[category].pop(0)
        #required_mappings[category].append(word_choice)
        return word_choice, required_mappings

    for i in range(0, 20):
      word_choice = random.choice(VARS[category])
      if m not in previously_used or word_choice != previously_used[category]:
        break
    return word_choice, required_mappings

  def process(self, statement, required_mappings):
    # If a mapping is specified in required_mappings, we will prefer that
    # mapping in this statement
    previously_used = {}
    chosen_words = []
    registers = {}
    regex = re.compile('({{.*?}})')
    ms = regex.findall(statement)

    previous_word_choice = None
    for m in ms:
      m = unicode(m)
      category = m.replace('{{', '').replace('}}', '')
      if category[-1].isnumeric():
        register_number = int(category[-1])
        #register_key = category[:-1]
        category = category[:-1]   # adjust category to canonical form
        registers.setdefault(category, [])
        register_values = registers[category]
        if len(register_values) < register_number:
          # New register input
          # TODO we're trusting the writer to only use increasing registers
          # TODO combine with below
          # FIXME sentence with {{country1}} and {{country2}}
          word_choice, required_mappings = self.getwordchoice(m, category, \
                                            previous_word_choice, previously_used, required_mappings)
          registers[category].append(word_choice)
        else:
          # old register input, this is just a lookup
          word_choice = register_values[register_number - 1]
      else:
        word_choice, required_mappings = self.getwordchoice(m, category, \
                                         previous_word_choice, previously_used, required_mappings)

      replace_pattern = re.compile(m)
      previous_word_choice = previously_used[category] = word_choice
      if category not in PLURALIZE_CATEGORIES:   # we don't want matches based on these special keywords
        required_mappings.setdefault(category, [])
        required_mappings[category].append(word_choice)
      statement = replace_pattern.sub(word_choice, statement, 1)
      chosen_words.append(word_choice)
    return statement, required_mappings, chosen_words

  def add_to_chosen_words_map(self, chosen_words_map, chosen_words):
    for word in chosen_words:
      chosen_words_map.setdefault(word, 0)
      chosen_words_map[word] += 1

  def generate_citations(self, n=2):
    lines = []
    used = set()
    for i in range(0, n):
      line = random.choice(citation_lines)
      for j in range(0, 100):
        if line not in used:
          break
        line = random.choice(citation_lines)
      lines.append(line)
      used.add(line)
    return lines

  def generate_paragraph(self):
    used_filler = set()
    def unused_filler():
      for i in range(0, 20):
        filler_candidate = random.choice(filler_lines)
        if filler_candidate not in used_filler:
          break
      used_filler.add(filler_candidate)
      return filler_candidate

    lines = []
    chosen_words_map = {}
    intro_statement, previous_mappings, chosen_words = self.process(random.choice(intro_lines), {})
    first_subject = chosen_words[0]
    self.add_to_chosen_words_map(chosen_words_map, chosen_words)
    print intro_statement, previous_mappings
    lines.append(intro_statement)
    used_evidence = set()  # don't repeat evidence lines
    for num_evidence in range(0, 3):
      print '------------------------------------'
      # choose an evidence statement that contains some linkage to intro statement
      ok = False
      for i in range(0, 100):
        candidate_statement = random.choice(evidence_lines)
        possible_linked_categories = previous_mappings.keys()
        random.shuffle(possible_linked_categories)
        possible_linked_categories = sorted(possible_linked_categories, demote_precedence_sort)
        print 'considering categories:', possible_linked_categories
        for key in possible_linked_categories:
          chaining_search_str = u'{{%s}}' % (key)
          if candidate_statement.find(chaining_search_str) > -1 \
              and candidate_statement not in used_evidence:
            ok = True
        if ok: break
      if not ok:
        lines.append('**** chaining failed, could not find any key match in', previous_mappings)
      used_evidence.add(candidate_statement)
      evidence_statement, previous_mappings, chosen_words = self.process(candidate_statement, previous_mappings)
      self.add_to_chosen_words_map(chosen_words_map, chosen_words)
      print evidence_statement, previous_mappings

      lines.append(evidence_statement)
      if random.random() > .4:
        lines.append(unused_filler())

    lines.append(random.choice(warning_lines))
    lines = map(capitalize_first, lines)   # capitalize first letter
    lines = ''.join(lines)

    # determine the subject
    subject = sorted(chosen_words_map.iteritems(), key=operator.itemgetter(1), reverse=True)[0][0]
    if subject != first_subject:
      subject = '%s and %s' % (capitalize_first(first_subject), capitalize_first(subject))
    else:
      subject = capitalize_first(subject)

    return subject, lines
