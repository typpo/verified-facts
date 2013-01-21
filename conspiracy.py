
import random
import sys
import re

VARS = {

'{{good_noun}}': 'the bible, money, donations,',

'{{malady}}': 'cancer, back pain, bipolar disorder, depression, decreased intelligence, foot fungus, mad cow disease, diabetes, autism, ulcers, allergies, Celiac\'s disease, Alzheimer\'s, Parkinson\'s, heart disease, restless leg syndrome, schizophrenia, ADHD, high blood pressure, chronic fatigue syndrome, Black Lung disease, myopia, age spots, melanoma, breast cancer, varicose veins, balding, anatidaephobia, paranoia, hyperpigmentation of the skin, albinism, cataracts, cavities, dwarfism, ',

'{{dangerous_noun}}': 'oil, guns, Ebola Virus, flourine, alternative medicine, chemtrails, flourine, GMOs, pesticides, nuclear power, nuclear weapons, smallpox, cancer, sucralose, DDT, trace heavy metals, lead, radioactive isotopes, arsenic,vaccines',

'{{era}}': 'biblical times, the American Revolution, the Vietnam War, WWI, WWII, the Civil War era,',

'{{abstract_noun}}': 'sex, money, the government, the media, unemployment, Islam, Judaism, the stock market, old age, diversity, communism, socialism, AIDS, manchurian candidates, election polls, the bible, peace, welfare, free food, freedom from oppression, tax rebates, the Republican playbook, the Democratic playbook, the Libertarian playbook, the gay agenda, gay marriage, "equality", the economy, feminism, ',

'{{government_org}}': 'the FBI, the CIA, the USA, the UK, the Taliban, NASA, Russia, the FDA, NATO, FEMA, the KGB,',

'{{company}}': 'Google, Apple, Exxon, Halliburton, BP, Texaco, Lehman Brothers, Facebook',

'{{country}}': 'the USA, the UK, Russia, Iran, Iraq, Afghanistan',

'{{organization}}': 'Republicans, Democrats, Communists, Socialists, KKK, Libertarians, Occupy Wall Street, Black Panthers, the Tea Party, Big Oil, Big Pharma, Big Data, the Knights Templar, Freemasons, Illuminati, Opus Dei, Skull and Bones, Shadow Government, the Mafia, the Mob, Jews, Catholics, a group of Atheists, Reptilians, the media, Islamic Fundamentalists, Christian Fundamentalists, minorities, Wikileaks, the Founding Fathers, Fox News, Scientology, Anonymous, Monsanto,',

'{{event}}': 'the moon landing, the Holocaust, the JFK assassination, WW2, WW1, the Vietnam War, the MLK assassination, the Manhattan Project, Occupy Wall Street, the Bolshevik revolution, the 2008 financial crash, the US Election of 2000, Fukushima, the Deepwater Horizon spill, the war in Iraq, the Black Plague, the American Revolution,',

'{{place}}': 'Area 51, the White House, the Moon, the Alaskan Wilderness, Israel, North Korea, Russia, Roswell, Chernobyl, Fukishima, Three Mile Island, San Andreas Fault, East Germany, Northern Ireland, ocean trenches, the Salt Caverns, Yucca Mountain, Iraq, Iran, Afghanistan, the International Space Station, Mars, AMES research center, Auschwitz, Thomas Jefferson\'s home, the Vatican',

'{{famous_person}}': 'Hugo Chavez, Barack Obama, Vladimir Putin, Osama Bin Laden, George W Bush, Bill Clinton, Madonna, JFK, J Edgar Hoover, Pink, The Beastie Boys, Kim Jong Un, Hitler, Abraham Lincoln, George Clooney, Lady Gaga, Marilyn Monroe, Dick Cheney, Karl Rove, Glenn Beck, Saddam Hussein, Mahmoud Ahmadinejad, Fidel Castro, Kim Jong Il, Kim Il Sung, Julian Assange, Al Gore, the Reverend Al Sharpton, the Reverend Jesse Jackson, Michelle Obama, Billy Graham, Bill O\'Reilly, Oprah, Tom Cruise, Jack Chick, Larry Page, Tom Cook,',

}

f = open('introductions', 'r')
intro = '\n'.join(f.readlines())
f.close()

for x in VARS:
  VARS[x] = map(lambda x: x.strip(), VARS[x].split(','))

def process(statement):
  previously_used = {}
  registers = {}
  regex = re.compile('({{.*?}})')
  ms = regex.findall(statement)
  for m in ms:
    m = unicode(m)
    if m[-1].isnumeric():
      register_number = int(m[-1])
      register_key = m[:-1]
      registers.setdefault(register_key, [])
      register_values = registers[register_key]
      if len(register_values) < register_number:
        # New register input
        # TODO we're trusting the user to only use increasing registers
        # TODO make sure we don't repeat any register
        # TODO not supporting same_* when using numbers
        for i in range(0, 20):
          word_choice = random.choice(VARS[m])
          if m not in previously_used or word_choice != previously_used[m]:
            break
        registers[register_key].append(word_choice)
      else:
        # old register input, this is just a lookup
        word_choice = register_values[register_number - 1]
    else:
      for i in range(0, 20):
        word_choice = random.choice(VARS[m])
        if m not in previously_used or word_choice != previously_used[m]:
          break

    replace_pattern = re.compile(m)
    previously_used[m] = word_choice
    statement = replace_pattern.sub(word_choice, statement, 1)
  return statement

print process(intro)
