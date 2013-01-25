#!/usr/bin/env python
import random
import sys
import re
import inflect

language = inflect.engine()

VARS = {

'malady': 'cancer, back pain, bipolar disorder, depression, decreased intelligence, foot fungus, mad cow disease, diabetes, autism, ulcers, allergies, Celiac\'s disease, Alzheimer\'s, Parkinson\'s, heart disease, restless leg syndrome, schizophrenia, ADHD, high blood pressure, chronic fatigue syndrome, Black Lung disease, myopia, age spots, melanoma, breast cancer, varicose veins, balding, anatidaephobia, paranoia, hyperpigmentation of the skin, albinism, cataracts, cavities, dwarfism, acne, joint pain, premature aging, fibrodysplasia ossificans progressiva, OCD, prosopagnosia, amnesia, leukemia, nymphomania, pinworms, cholera, sickle cell anemia, Lyme disease, Rocky Mountain spotted fever, ',

'dangerous_noun': 'oil, guns, Ebola Virus, fluorine, alternative medicine, chemtrails, fluoride, GMOs, pesticides, nuclear power, nuclear isotopes, nuclear weapons, aspartame, DDT, trace heavy metals, mercury, lead, radioactive isotopes, arsenic, vaccines, E. coli, salmonella, petrochemicals, cocaine, crack, meth, speed, pot, marijuana, angel dust, morphine, LSD, MDMA, freon, tetrafluorocarbon, selective serotonin reuptake inhibitors, ',

'era': 'the Clinton years, the Bush wars, the Bush administration, the Reagan administration, the Carter administration, the Nixon administration, the Great Depression, the Great Recession, the American Revolution, the Vietnam War, WWI, WWII, the Civil War, ancient Rome, the Cold War, the Industrial Revolution, Obama\'s childhood years in Kenya,',

'abstract_noun': 'sex, money, the media, unemployment, Islam, Judaism, the stock market, old age, diversity, communism, socialism, AIDS, manchurian candidates, election polls, the bible, poverty, peace, welfare, freedom from oppression, tax rebates, the gay agenda, gay marriage, "equality", the economy, feminism, global warming, religious belief, eugenics,',

'government_org': 'the FBI, the CIA, the Taliban, NASA, the Feds, the Federal Reserve, DARPA, the USGS, the EPA, the FDA, NATO, FEMA, the KGB,',

'company': 'Google, Apple, Exxon, Halliburton, BP, Texaco, the Lehman Brothers, Facebook, Spotify, Microsoft, Tencent, Monsanto, Nestle, Kroger, Unilever, Adobe, IBM',

'country': 'the USA, the UK, Russia, Iran, Iraq, Afghanistan, Germany, Egypt, Kenya, Yemen, Somalia, China, Switzerland, France, North Korea, South Korea, Japan, Saudi Arabia, Qatar, Kurdistan',

'organization': 'Republicans, Democrats, Communists, Socialists, the KKK, Libertarians, Occupy Wall Street, Wall Street, Black Panthers, the Tea Party, Big Oil, Big Pharma, the Knights Templar, Freemasons, Illuminati, Opus Dei, Skull and Bones, Shadow Government, the Mafia, the Mob, Jews, Catholics, a group of Atheists, Reptilians, the media, Islamic Fundamentalists, Christian Fundamentalists, minorities, Wikileaks, the Founding Fathers, Fox News, Scientology, Anonymous, Monsanto, Obama Birthers, illegal aliens,',

'event': 'the moon landing, the Holocaust, the JFK assassination, WW2, WW1, the Vietnam War, the MLK assassination, the Manhattan Project, Occupy Wall Street, the Bolshevik revolution, the 2008 financial crash, the US Election of 2000, Fukushima, the Deepwater Horizon spill, the war in Iraq, the Black Plague, the American Revolution, Watergate, Gulf oil spill, 9/11, the birth of Obama, the Anthrax scare, ',

'place': 'Area 51, the White House, the Moon, the Alaskan Wilderness, Israel, North Korea, Russia, Roswell, Chernobyl, Fukushima, Three Mile Island, the San Andreas Fault, East Germany, Northern Ireland, ocean trenches, the Salt Caverns, Yucca Mountain, Iraq, Iran, Afghanistan, the International Space Station, Mars, AMES research center, Auschwitz, Thomas Jefferson\'s home, the Vatican, Obama\'s birthplace, the former site of 7 World Trade Center',

'famous_person': 'Hugo Chavez, Barack Obama, Arnold Schwarzenegger, Vladimir Putin, Osama Bin Laden, George W Bush, Bill Clinton, Madonna, JFK, J Edgar Hoover, Pink, A Beastie Boy, Kim Jong Un, Hitler, Abraham Lincoln, George Clooney, Lady Gaga, Marilyn Monroe, Dick Cheney, Karl Rove, Glenn Beck, Saddam Hussein, Mahmoud Ahmadinejad, Fidel Castro, Kim Jong Il, Kim Il Sung, Julian Assange, Al Gore, the Reverend Al Sharpton, the Reverend Jesse Jackson, Michelle Obama, Billy Graham, Bill O\'Reilly, Oprah, Tom Cruise, Jack Chick, Larry Page, Psy, ',

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

PLURALIZE_CATEGORIES = set(['has/have', 'is/are', 'was/were', 'it/them'])
OTHER_SPECIAL_CATEGORIES = set(['it/them'])

def process(statement, required_mappings={}):
  # If a mapping is specified in required_mappings, we will prefer that
  # mapping in this statement
  previously_used = {}
  registers = {}
  mappings = {}   # the mappings used to generate this statement
  regex = re.compile('({{.*?}})')
  ms = regex.findall(statement)

  def getwordchoice(category, previous_word_choice):
    if previous_word_choice and category in PLURALIZE_CATEGORIES:
      singular, plural = category.split('/')
      return plural if previous_word_choice[-1] == 's' else singular
    elif category in required_mappings and len(required_mappings[category]) > 0:
      # chained sentence
      word_choice = required_mappings[category][0]
      required_mappings[category].pop(0)
    else:
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
    mappings.setdefault(category, [])
    mappings[category].append(word_choice)
    statement = replace_pattern.sub(word_choice, statement, 1)
  return statement, mappings

def random_intro():
  return process(random.choice(intro_lines))[0]

def random_evidence():
  return process(random.choice(evidence_lines))[0]

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
  lines.append(intro_statement)
  used_evidence = set()  # don't repeat evidence lines
  for num_evidence in range(0, 3):
    # choose an evidence statement that contains some linkage to intro statement
    ok = False
    for i in range(0, 100):
      candidate_statement = random.choice(evidence_lines)
      for key in previous_mappings:
        chaining_search_str = u'{{%s}}' % (key)
        if candidate_statement.find(chaining_search_str) > -1 \
            and candidate_statement not in used_evidence:
          ok = True
      if ok: break
    if not ok:
      lines.append('**** chaining failed, could not find any key match in', previous_mappings)
    used_evidence.add(candidate_statement)
    evidence_statement, previous_mappings = process(candidate_statement, previous_mappings)

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
  return ''.join(lines)

#print process('{{company}} clearly {{has/have}} a secret deal with Youtube-- all videos highlighting its abuses in {{country}} are taken down without explanation.')
