import concurrent.futures #https://docs.python.org/3/library/concurrent.futures.html#module-concurrent.futures

from amara3.uxml import tree
from amara3.uxml.treeutil import *

#></link>
#/>

DOC = '''\
<descriptionSet{0}>
<description>
  <title>Catamount</title>
  <date>June, 2013</date>
  <publisher>Leveler</publisher>
  <link href="http://www.levelerpoetry.com/catamount-levelheaded/"></link>
</description>
<description>
  <title>"Love ascended between us" &amp; "Folly between us"</title>
  <date>December, 2011</date>
  <publisher>String Poet</publisher>
  <link href="http://www.stringpoet.com/2011/12/translation-uche-ogbuji/"></link>
</description>
<description>
  <title>"Above Left Hand Canyon" &amp; "How Close?"</title>
  <date>March, 2013</date>
  <publisher>IthacaLit</publisher>
  <link href="http://ithacalit.com/uche-ogbuji1.html"></link>
</description>
<description>
  <title>Two Kitchens</title>
  <date>May, 2013</date>
  <publisher>Gris-Gris</publisher>
  <link href="http://www.nicholls.edu/gris-gris/issue-2/two-kitchens/"></link>
</description>
<description>
  <title>Autumn Equinox Creature Song</title>
  <date>May, 2013</date>
  <publisher>Qarrtsiluni</publisher>
  <link href="http://qarrtsiluni.com/2013/05/28/autumn-equinox-creature-song/"></link>
</description>
</descriptionSet>
'''


MICRODOC = DOC.format('')
NSDOC = DOC.format(' xmlns="http://purl.org/dc/elements/1.1/"')

def md_summary(elem):
    link = list(select_name(elem, 'link'))
    link = link[0].xml_attributes['href'] if link else ''
    title = list(select_name(elem, 'title'))
    title = title[0].xml_value if title else ''
    date = list(select_name(elem, 'date'))
    date = date[0].xml_value if date else ''
    pub = list(select_name(elem, 'publisher'))
    pub = pub[0].xml_value if pub else ''
    return '[{0}|{1}, {2} ({3})]'.format(link, title, date, pub)


def main():
    tb = tree.treebuilder()
    root = tb.parse(MICRODOC)
    print('Processes\n')
    with concurrent.futures.ProcessPoolExecutor() as executor:
        #for markdown in executor.map(summarize, select_pattern(root, ('description',))):
        for markdown in executor.map(md_summary, select_name(root, 'description')):
            print(markdown)
    print()

    print('Threads\n')
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        #for markdown in executor.map(summarize, select_pattern(root, ('description',))):
        for markdown in executor.map(md_summary, select_name(root, 'description')):
            print(markdown)


if __name__ == '__main__':
    main()
