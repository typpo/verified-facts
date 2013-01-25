#!/usr/bin/env python
import random
import sys
import re

VARS = {
'malady': 'cancer, bipolar disorder, chronic pain, depression, mad cow disease, diabetes, autism, ulcers, allergies, Celiac\'s disease, Alzheimer\'s, Parkinson\'s, heart disease, restless leg syndrome, schizophrenia, ADHD, high blood pressure, chronic fatigue syndrome, Black Lung disease, myopia, age spots, melanoma, breast cancer, balding, hyperpigmentation of the skin, albinism, cataracts, dwarfism, acne, joint pain, premature aging, OCD, amnesia, leukemia, nymphomania, pinworms, cholera, sickle cell anemia, Lyme disease, Rocky Mountain spotted fever, AIDS,',

'dangerous_noun': 'oil, guns, Ebola, fluorine, alternative medicine, chemtrails, fluoride, GMOs, pesticides, nuclear power, nuclear isotopes, nuclear weapons, aspartame, DDT, trace heavy metals, mercury, lead, radioactive isotopes, arsenic, vaccines, E. coli, salmonella, petrochemicals, cocaine, crack, meth, speed, pot, marijuana, angel dust, morphine, LSD, MDMA, freon, tetrafluorocarbon, selective serotonin reuptake inhibitors, ',

'era': 'the Clinton years, the Bush wars, the Bush administration, the Reagan administration, the Carter administration, the Nixon administration, the Great Depression, the Great Recession, the American Revolution, the Vietnam War, WWI, WWII, the Civil War, ancient Rome, the Cold War, the Industrial Revolution, Obama\'s childhood years in Kenya,',

'abstract_noun': 'sex, money, hedonism, the media, unemployment, Islam, Judaism, the stock market, old age, "diversity", communism, socialism, election polls, the bible, poverty, welfare, gay marriage, "equality", the economy, feminism, global warming, religious belief, eugenics,',

'government_org': 'the FBI, the CIA, NASA, the Feds, the Federal Reserve, DARPA, the USGS, the EPA, the FDA, NATO, FEMA, the KGB, the NSA, the Pentagon, the Secret Service,',

'company': 'Google, Apple, Exxon, Halliburton, BP, Texaco, the Lehman Brothers, Facebook, Spotify, Microsoft, Tencent, Monsanto, Nestle, Kroger, Unilever, Adobe, IBM',

'country': 'the USA, the UK, Russia, Iran, Iraq, Afghanistan, Germany, Egypt, Kenya, Yemen, Somalia, China, Switzerland, France, North Korea, South Korea, Japan, Saudi Arabia, the United Arab Emirates, Kurdistan',

'organization': 'the Republicans, the Democrats, Communists, Socialists, the KKK, Libertarians, Occupy Wall Street, Wall Street, the Taliban, The Black Panthers, The Tea Party, Big Oil, Big Pharma, the Knights Templar, Freemasons, Illuminati, Opus Dei, Skull and Bones, the Shadow Government, the Mafia, the Mob, Osama bin Laden\'s descendants, Al Qaeda, the Jews, Catholics, the Atheist establishment, Reptilians, the Mainstream Media, Islamic Fundamentalists, Christian Fundamentalists, minorities, Wikileaks, Fox News, Scientology, Anonymous, Monsanto, Obama Birthers, illegal aliens,',

'event': 'the moon landing, the Holocaust, the JFK assassination, WW2, WW1, the Vietnam War, the MLK assassination, the Manhattan Project, the summer 2012 popularity of Occupy Wall Street, the Bolshevik revolution, the 2008 financial crash, the US Election of 2000, Fukushima, the Deepwater Horizon spill, the war in Iraq, the Black Plague, the American Revolution, Watergate, the Gulf oil spill, 9/11, the birth of Obama, the Anthrax scare, ',

'place': 'Area 51, the White House, the Moon, the Alaskan Wilderness, Israel, North Korea, Russia, Roswell, Chernobyl, Fukushima, Three Mile Island, the San Andreas Fault, East Germany, Northern Ireland, ocean trenches, the Salt Caverns, Yucca Mountain, Iraq, Iran, Afghanistan, AMES research center, Auschwitz, Thomas Jefferson\'s home, the Vatican, Obama\'s birthplace, the former site of 7 World Trade Center',

'famous_person': 'Hugo Chavez, Barack Obama, Arnold Schwarzenegger, Vladimir Putin, George W Bush, Bill Clinton, A Beastie Boy, Kim Jong Un, George Clooney, Lady Gaga, Madonna, Dick Cheney, Karl Rove, Glenn Beck, Saddam Hussein, Mahmoud Ahmadinejad, Julian Assange, Al Gore, The Reverend Al Sharpton, The Reverend Jesse Jackson, Michelle Obama, Billy Graham, Bill O\'Reilly, Oprah, Tom Cruise, Larry Page, Psy,',
}

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

for x in VARS:
  VARS[x] = filter(lambda x: x.strip() != '', map(lambda x: x.strip(), VARS[x].split(',')))

PLURALIZE_CATEGORIES = set(['has/have', 'is/are', 'was/were', 'it/them', 'its/their'])
OTHER_SPECIAL_CATEGORIES = set(['it/them'])

# Try not to link on these categories.  Without something like this you tend to get non-sequiturs, linked
# by the object of sentences.
LINKED_CATEGORIES_DEMOTE_PRECEDENCE = ['malady', 'dangerous_noun', 'abstract_noun']
def demote_precedence_sort(a, b):
  try:
    ascore = LINKED_CATEGORIES_DEMOTE_PRECEDENCE.index(a)
  except ValueError:
    ascore = -1
  try:
    bscore = LINKED_CATEGORIES_DEMOTE_PRECEDENCE.index(b)
  except ValueError:
    bscore = -1
  return bscore - ascore

def process(statement, required_mappings={}):
  # If a mapping is specified in required_mappings, we will prefer that
  # mapping in this statement
  previously_used = {}
  registers = {}
  regex = re.compile('({{.*?}})')
  ms = regex.findall(statement)

  def getwordchoice(category, previous_word_choice):
    if previous_word_choice and category in PLURALIZE_CATEGORIES:
      singular, plural = category.split('/')
      return plural if previous_word_choice[-1] == 's' else singular
    elif category in required_mappings and len(required_mappings[category]) > 0:
      # chained sentence
      word_choice = required_mappings[category][0]
      if word_choice != previous_word_choice:    # don't repeat anything
        # move to back
        required_mappings[category].pop(0)
        required_mappings[category].append(word_choice)
        return word_choice

    for i in range(0, 20):
      word_choice = random.choice(VARS[category])
      if m not in previously_used or word_choice != previously_used[category]:
        break
    return word_choice

  previous_word_choice = None
  for m in ms:
    m = unicode(m)
    category = m.replace('{{', '').replace('}}', '')
    if category[-1].isnumeric():
      register_number = int(category[-1])
      register_key = category[:-1]
      registers.setdefault(register_key, [])
      register_values = registers[register_key]
      if len(register_values) < register_number:
        # New register input
        # TODO we're trusting the user to only use increasing registers
        # TODO make sure we don't repeat any register
        # TODO not supporting same_* when using numbers
        word_choice = getwordchoice(register_key, previous_word_choice)
        registers[register_key].append(word_choice)
      else:
        # old register input, this is just a lookup
        word_choice = register_values[register_number - 1]
    else:
      word_choice = getwordchoice(category, previous_word_choice)

    replace_pattern = re.compile(m)
    previous_word_choice = previously_used[category] = word_choice
    if category not in PLURALIZE_CATEGORIES and \
       category not in OTHER_SPECIAL_CATEGORIES:   # we don't want matches based on these special keywords
      required_mappings.setdefault(category, [])
      required_mappings[category].append(word_choice)
    statement = replace_pattern.sub(word_choice, statement, 1)
  return statement, required_mappings

def generate_paragraph():
  used_filler = set()
  def unused_filler():
    for i in range(0, 20):
      filler_candidate = random.choice(filler_lines)
      if filler_candidate not in used_filler:
        break
    used_filler.add(filler_candidate)
    return filler_candidate

  lines = []
  intro_statement, previous_mappings = process(random.choice(intro_lines))
  print intro_statement, previous_mappings
  lines.append(intro_statement)
  used_evidence = set()  # don't repeat evidence lines
  for num_evidence in range(0, 3):
    # choose an evidence statement that contains some linkage to intro statement
    ok = False
    for i in range(0, 100):
      candidate_statement = random.choice(evidence_lines)
      # TODO figure out disconnects
      # TODO prefer some categories in previous_mappings over others.
      # eg. country should match more than abstract_noun
      possible_linked_categories = previous_mappings.keys()
      random.shuffle(possible_linked_categories)
      possible_linked_categories = sorted(possible_linked_categories, demote_precedence_sort)
      for key in possible_linked_categories:
        chaining_search_str = u'{{%s}}' % (key)
        if candidate_statement.find(chaining_search_str) > -1 \
            and candidate_statement not in used_evidence:
          ok = True
      if ok: break
    if not ok:
      lines.append('**** chaining failed, could not find any key match in', previous_mappings)
    used_evidence.add(candidate_statement)
    evidence_statement, previous_mappings = process(candidate_statement, previous_mappings)
    print evidence_statement, previous_mappings

    lines.append(evidence_statement)
    if random.random() > .4:
      lines.append(unused_filler())
    """
    if random.random() > .75:
      lines.append(unused_filler())
    if random.random() > .95:
      lines.append(unused_filler())
    """
  lines.append(random.choice(warning_lines))
  lines = map(lambda x: x[0].upper() + x[1:], lines)   # capitalize first letter
  return ''.join(lines)
