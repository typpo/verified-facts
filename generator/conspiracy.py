#!/usr/bin/env python
import os
import random
import operator
import sys
import re
import yaml
import unicodedata

dirname, filename = os.path.split(os.path.abspath(__file__))
content_dir = dirname + '/content/'

f = open(content_dir + 'vars', 'r')
vars_json = f.read()
f.close()
VARS = yaml.load(vars_json)  # reading yaml because it's a lenient json parser

unicode_punctuation = {
  u'\u2018': "'",
  u'\u2019': "'",
}
def utf8normalize(text):
  global unicode_punctuation
  for src, dest in unicode_punctuation.iteritems():
    text = text.replace(src, dest)
  return text
  #return unicodedata.normalize('NFD', s).encode('ascii', 'ignore')

f = open(content_dir + 'introductions', 'r')
intro_lines = filter(lambda x: x.strip() != '', f.readlines())
intro_lines = map(lambda x: utf8normalize(x.decode('utf-8')), intro_lines)
f.close()

f = open(content_dir + 'evidence', 'r')
evidence_lines = filter(lambda x: x.strip() != '', f.readlines())
evidence_lines = map(lambda x: utf8normalize(x.decode('utf-8')), evidence_lines)
f.close()

f = open(content_dir + 'warnings', 'r')
warning_lines = filter(lambda x: x.strip() != '', f.readlines())
warning_lines = map(lambda x: utf8normalize(x.decode('utf-8')), warning_lines)
f.close()

f = open(content_dir + 'filler', 'r')
filler_lines = filter(lambda x: x.strip() != '', f.readlines())
filler_lines = map(lambda x: utf8normalize(x.decode('utf-8')), filler_lines)
f.close()

f = open(content_dir + 'citations', 'r')
citation_lines = filter(lambda x: x.strip() != '', f.readlines())
citation_lines = map(lambda x: utf8normalize(x.decode('utf-8')), citation_lines)
f.close()

f = open(content_dir + 'images', 'r')
imageurls = filter(lambda x: x.strip() != '', f.readlines())
imageurls = map(lambda x: utf8normalize(x.decode('utf-8')), imageurls)
f.close()

for x in VARS:
  VARS[x] = filter(lambda x: utf8normalize(unicode(x.strip())) != '', map(lambda x: x.strip(), VARS[x].split(',')))

PLURALIZE_CATEGORIES = set(['has/have', 'is/are', 'was/were', 'it/them', 'its/their', '\'s/\''])

# known plurals that are not part of a set
FORCE_PLURAL = set(['Illuminati', 'Opus Dei', 'Obama\'s childhood years in Kenya'])

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

  # optional verification step - check validity of all sentences and
  # output some basic stats
  def verify(self):
    intro_counts = {}
    for line in intro_lines:
      try:
        statement, required_mappings, chosen_words = self.process(line, {})
        for key,val in required_mappings.iteritems():
          intro_counts.setdefault(key, 0)
          intro_counts[key] += len(val)
      except Exception as ex:
        print 'Invalid line:', line
        print 'Exception:', ex

    evidence_counts = {}
    for line in evidence_lines:
      try:
        statement, required_mappings, chosen_words = self.process(line, {})
        for key,val in required_mappings.iteritems():
          evidence_counts.setdefault(key, 0)
          evidence_counts[key] += len(val)
      except Exception as ex:
        print 'Invalid line:', line
        print 'Exception:', ex

    # stats
    intro_counts = sorted(intro_counts.iteritems(), key=operator.itemgetter(1), reverse=True)
    evidence_counts = sorted(evidence_counts.iteritems(), key=operator.itemgetter(1), reverse=True)
    print 'Intro counts:'
    for item, count in intro_counts:
      print '  * %s - %d' % (item, count)
    print '\nEvidence counts:'
    for item, count in evidence_counts:
      print '  * %s - %d' % (item, count)

  def get_all_subjects(self):
    # Returns list of tuples of (subject, category)
    ret = []
    for x in VARS:
      for val in VARS[x]:
        ret.append((val, x))
    ret.sort()
    return ret

  def getwordchoice(self, m, category, previous_word_choice, previously_used, required_mappings):
    if previous_word_choice and category in PLURALIZE_CATEGORIES:
      singular, plural = category.split('/')
      return (plural if previous_word_choice[-1] == 's' or previous_word_choice in FORCE_PLURAL \
          else singular, required_mappings)
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
      category = utf8normalize(m.replace('{{', '').replace('}}', ''))
      if category[-1].isdigit():
        register_number = int(category[-1])
        #register_key = category[:-1]
        category = category[:-1]   # adjust category to canonical form
        registers.setdefault(category, [])
        register_values = registers[category]
        if len(register_values) < register_number:
          # New register input
          # TODO we're trusting the writer to only use increasing registers
          # TODO combine with below
          for i in range(0, 30):
            word_choice, required_mappings = self.getwordchoice(m, category, \
                                              previous_word_choice, previously_used, required_mappings)
            # registers must be unique - TODO this can be done more
            # efficiently, but doing it this way for now
            ok = True
            for reg_val in register_values:
              if word_choice == reg_val:
                ok = False
                break
            if ok:
              break
          registers[category].append(word_choice)
          #print 'put %s from cat %s in register %d' % (word_choice, category, register_number)
        else:
          # old register input, this is just a lookup
          word_choice = register_values[register_number - 1]
          #print 'got %s from cat %s in register %d' % (word_choice, category, register_number)
      else:
        word_choice, required_mappings = self.getwordchoice(m, category, \
                                         previous_word_choice, previously_used, required_mappings)

      previous_word_choice = previously_used[category] = word_choice
      if category not in PLURALIZE_CATEGORIES:   # we don't want matches based on these special keywords
        required_mappings.setdefault(category, [])
        required_mappings[category].append(word_choice)
      replace_pattern = re.compile(m)
      statement = replace_pattern.sub(word_choice, statement, 1)
      chosen_words.append(word_choice)
    return statement, required_mappings, chosen_words

  def add_to_chosen_words_map(self, chosen_words_map, chosen_words):
    for word in chosen_words:
      chosen_words_map.setdefault(word, 0)
      chosen_words_map[word] += 1

  def generate_citations(self, min=1, max=4):
    lines = []
    used = set()
    n = random.randint(min, max)
    for i in range(0, n):
      line = random.choice(citation_lines)
      for j in range(0, 100):
        if line not in used:
          break
        line = random.choice(citation_lines)
      lines.append(line)
      used.add(line)
    return lines

  def generate_paragraph(self, preset_mappings=None):
    if not preset_mappings:
      preset_mappings = {}  # prevent weird scoping bug

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
    if preset_mappings:
      # we need to choose a sentence with this category
      random.shuffle(intro_lines)
      user_key_input = preset_mappings.keys()[0]   # user wants a conspiracy about this category
      required_subject = preset_mappings[user_key_input][0]
      for line in intro_lines:
        chaining_search_str = u'{{%s}}' % (user_key_input)
        if line.find(chaining_search_str) > -1:
          intro_statement, previous_mappings, chosen_words = self.process(line, preset_mappings)
          break
    else:
      intro_statement, previous_mappings, chosen_words = \
          self.process(random.choice(intro_lines), {})
      required_subject = None
    first_subject = chosen_words[0]
    self.add_to_chosen_words_map(chosen_words_map, chosen_words)
    #print intro_statement, previous_mappings
    lines.append(intro_statement)
    used_evidence = set()  # don't repeat evidence lines
    for num_evidence in range(0, 3):
      #print '------------------------------------'
      # choose an evidence statement that contains some linkage to intro statement
      ok = False
      for i in range(0, 200):
        candidate_statement = random.choice(evidence_lines)
        possible_linked_categories = previous_mappings.keys()
        random.shuffle(possible_linked_categories)
        possible_linked_categories = sorted(possible_linked_categories, demote_precedence_sort)
        #print 'considering categories:', possible_linked_categories
        for key in possible_linked_categories:
          chaining_search_str = u'{{%s}}' % (key)
          if candidate_statement.find(chaining_search_str) > -1 \
              and candidate_statement not in used_evidence:
            ok = True
        if ok: break
      if not ok:
        lines.append('**** chaining failed, could not find any key match in %s' % (previous_mappings))
        return self.generate_paragraph()
      used_evidence.add(candidate_statement)
      evidence_statement, previous_mappings, chosen_words = self.process(candidate_statement, previous_mappings)
      self.add_to_chosen_words_map(chosen_words_map, chosen_words)
      #print evidence_statement, previous_mappings

      lines.append(evidence_statement)
      if random.random() > .4:
        lines.append(unused_filler())

    lines.append(random.choice(warning_lines))
    lines = map(capitalize_first, lines)   # capitalize first letter
    lines = ''.join(lines)

    # determine the subject
    subject = sorted(chosen_words_map.iteritems(), key=operator.itemgetter(1), reverse=True)[0][0]
    if required_subject and required_subject != first_subject:
      subject = '%s and %s' % (capitalize_first(first_subject), capitalize_first(required_subject))
    elif subject != first_subject:
      subject = '%s and %s' % (capitalize_first(first_subject), capitalize_first(subject))
    else:
      subject = capitalize_first(subject)

    # choose image
    imageurl = random.choice(imageurls)

    return subject, lines, imageurl
