
import random
import sys
import re

VARS = {

'{{real_noun}}': 'oil, guns, Ebola Virus, flourine, alternative medicine, chemtrails, flourine, GMOs, DNA, manchurian candidates, election polls, nuclear power, nuclear weapons, smallpox',

'{{concept}}': 'sex, the bible, money, the government, the media, unemployment, Islam, Judaism, the stock market, time, death, old age, cancer, diversity, communism, socialism, AIDS',

'{{government_noun}}': 'the FBI, the CIA, the USA, the UK, the Taliban, NASA, Russia, the FDA, NATO, FEMA, the KGB',

'{{company}}': 'Google, Apple, Exxon, Haliburton, BP, Texaco, Lehman Brothers, Facebook',

'{{country}}': 'the USA, the UK, Russia, Iran, Iraq, Afghanistan',

'{{organization}}': 'Republicans, Democrats, Communists, Socialists, KKK, Libertarians, Occupy Wall Street, Black Panthers, The Tea Party, Big Oil, Big Pharma, Big Data, The Knights Templar, Freemasons, Illuminati, Opus Dei, Skull and Bones, Shadow Government, the Mafia, the Mob, Jews, Catholics, Atheists, Reptilians, the media, Islamic Fundamentalists, Christian Fundamentalists, minorities,',

'{{event}}': 'the moon landing, the Holocaust, the JFK assassination, WW2, WW1, the Vietnam War, the MLK assassination, the Manhattan Project, Occupy Wall Street, the Bolshevik revolution, the 2008 financial crash, the US Election of 2000, Fukushima, the Deepwater Horizon spill, the war in Iraq, the Black Plague,',

'{{place}}': 'Area 51, the White House, the Moon, the Alaskan Wilderness, Israel, North Korea, Russia, Roswell, Chernobyl, Fukishima, Three Mile Island, San Andreas Fault, East Germany, Northern Ireland, ocean trenches, the Salt Caverns, Yucca Mountain, Iraq, Iran, Afghanistan, the International Space Station, Mars, AMES research center, Auschwitz',

'{{famous_person}}': 'Hugo Chavez, Barack Obama, Vladimir Putin, Osama Bin Laden, George W Bush, Bill Clinton, Madonna, JFK, J Edgar Hoover, Pink, The Beastie Boys, Kim Jong Un, Hitler, Abraham Lincoln, George Clooney, Lady Gaga, Marilyn Monroe, Dick Cheney, Karl Rove, Glenn Beck, Saddam Hussein, Mahmoud Ahmadinejad, Fidel Castro, Kim Jong Il, Kim Il Sung.',

'{{searched_noun}}': sys.argv[1] if len(sys.argv) > 1 else 'searched_noun',

}


f = open('sentences_test', 'r')
statement = '\n'.join(f.readlines())
f.close()

for x in VARS:
  VARS[x] = map(lambda x: x.strip(), VARS[x].split(','))


previously_used = {}
regex = re.compile('({{.*?}})')
ms = regex.findall(statement)
for m in ms:
  if m.startswith('{{same_'):
    prev_used_key = m.replace('same_', '')
    word_choice = previously_used[prev_used_key]
  else:
    for i in range(0, 20):
      word_choice = random.choice(VARS[m])
      if m not in previously_used or word_choice != previously_used[m]:
        break

  replace_pattern = re.compile(m)
  previously_used[m] = word_choice
  statement = replace_pattern.sub(word_choice, statement, 1)


print statement
