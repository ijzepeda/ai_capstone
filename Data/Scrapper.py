
import ast
import os
import requests
from bs4 import BeautifulSoup

from fFix_FN import ffix_fn
from println import println, _format_output

LINE_WIDTH = 163

PROG_DESC = '''
'''
PROG_VER = 'recipe_scraper 0.0.1'


def get_page(page):
    try:
        page_data = requests.get(page)
        page_data.raise_for_status()
    except requests.exceptions.HTTPError as html_error:
        if html_error.response.status_code == 404:
            println(' >>>>>>>>>> 404: Page Not Found <<<<<<<<<<')
            return '404'
        else:
            println(html_error)
            return '999'
    return page_data.text


def my_clean_string(usoup):
    ''' This will clean up the string received, removing multiple spacing
    and double line ends'''
    wstring = repr(usoup)
    while '  ' in wstring:
        wstring = wstring.replace('  ', ' ')

    while r'\n \n' in wstring:
        wstring = wstring.replace(r'\n \n', r'\n')

    while r'\n\n' in wstring:
        wstring = wstring.replace(r'\n\n', r'\n')

    while r'\n ' in wstring:
        wstring = wstring.replace(r'\n ', r'\n')

    wstring = wstring.replace(b"\\u2019", "_")
    wstring = wstring.replace(b"\\u2026", '...')
    wstring = wstring.replace(b"\\ufffd", '')
    wstring = wstring.replace(b"\\xb0", '')
    wstring = wstring.replace(b"\\xc2", '')
    wstring = wstring.replace(b"\\u017e", 'z')
    wstring = wstring.replace(b"\\xe9", 'e')
    wstring = wstring.replace(b"\\xed", 'i')
    wstring = wstring.replace(b"\\xe4", 'a')
    wstring = wstring.replace(b"\\\\xae", '')
#    wstring = wstring.replace(b"\\xed", 'i')
#    wstring = wstring.replace(b"\\xed", 'i')
#    wstring = wstring.replace(b"\\xed", 'i')
#    wstring = wstring.replace(b"\\xed", 'i')
#    print repr(wstring)
    wstring = str(ast.literal_eval(wstring))
    return wstring.replace("_", "'").strip()


def create_doc(varlist):
    ''' This creates the text that will be written to the file
    the varlist is a list, comprising of:
        0 = title
        1 = author_name
        2 = total_time
        3 = recipe_notes
        4 = ingredients
        5 = directions
        6 = url of the recipe
        7 = category'''
    head = ''
    head += '<!DOCTYPE html>\n<html>\n<head lang="en">\n<meta charset="UTF-8">\n'
    head += '<title>{0} by {1}</title>\n'.format(varlist[0], varlist[1])
    head += '<style type="text/css">\n/*<![CDATA[*/\n'
    head += 'p {text-align: justify; font-family: "Times New Roman", sans-serif;}\n'
    head += '.story { width: 99%; padding: 4pt; background-color: black; color: #F0F8FF; }\n'
    head += 'BODY { color: #F0F8FF; background-color: black; font-family: "Times New Roman", '
    head += 'sans-serif; font-size:25pt; }\n'
    head += 'h1, h2, h3, h4, h5 { color: orange; font-family: Ringbearer, sans-serif; font-weight:'
    head += '100; text-align: center; }\n'
    head += 'h1 {font-size:2em;}\nh2 {font-size:1.4em;}\nh3 {font-size:1.25em;}\nh4 {font-size:'
    head += '1.10em;}\nh5 {font-size:.7em;margin:0px;}\n'
    head += 'blockquote {margin-left:1em;margin-right:1em;}\n'
    head += '.center, .c {text-align: center;}\n.italic, .i {font-style:italic;}\n'
    head += '.bold, .b {font-weight:bold;}\n.underline, .u {text-decoration:underline;}\n'
    head += '.notice, .end-note { font-size:60%; background-color: grey; border:1px dotted silver; '
    head += 'margin:0px;}\n.notice p { font-family: "Times New Roman"; color:#D2D2D2;}\n'
    head += '.notice td { font-family: "Times New Roman", sans-serif; color: #D2D2D2;}\n'
    head += '.notice th { font-family: "Times New Roman", sans-serif; color: #D2D2D2; font-weight: '
    head += 'bold;}\nA:link { color: yellow}\nA:visited { color: blue}\n'
    head += 'A:hover { color: blue; text-decoration: underline; background-color: teal;}\n'
    head += 'a:visited:hover { color: #FFF; background-color: teal;}\n'
    head += 'a:active { color: yellow; background-color: teal;}\n'
    head += 'a:visited:active { color: yellow; background-color: teal; }\n'
    head += '.copy {font-size:.85em; color: #5A5A5A; margin: 0px; }\n'
    head += '.myOtherTable, .TOC { border-collapse: collapse; width: 100%; }\n'
    head += '.myOtherTable td, .myOtherTable th { padding:5px;border:0; }\n'
    head += '.myOtherTable td { font-size: .85em; }\n/*]]>*/\n'
    head += '</style>\n</head>\n<body>\n<div class="story">\n'
    head += '<h1><a href="{0}">{1}</a></h1>\n'.format(varlist[6], varlist[0])
    head += '<h2>by<br>{0}</h2>\n<hr class="copy"/>\n'.format(varlist[1])
    head += '{0}\n<hr class="copy"/>\n'.format(varlist[7])
    ## this is the total time
    head += '{0}\n<hr class="copy"/>\n'.format(varlist[2])
    ## this is the recipe notes
    if varlist[3] != None:
        head += '{0}\n<hr class="copy"/>\n'.format(varlist[3])
    head += '<table class="myOtherTable">\n'
    head += '<colgroup><col style="width:50%"/><col style="width:50%"/></colgroup>\n'
    head += '<tr>\n<td valign="top">\n'
    ## this is the ingredients
    head += '{0}\n'.format(varlist[4])
    head += '</td>\n<td valign="top">\n'
    ## this is the directions
    head += '{0}\n'.format(varlist[5])
    head += '</td>\n</tr>\n</table>\n'
    head += '<hr class="copy"/><hr class="copy"/><hr class="copy"/><hr class="copy"/>\n'
    head += '</div>\n</body>\n</html>'
    return head


def format_total_time(soup):
    ''' I'm going to reformat the time secton so it looks better '''
    total_time1 = soup.find('div', {'class':'total-time'})
    if 'strong' in str(total_time1):
        total_time_n = total_time1.find('strong').get_text()
        total_time_m = total_time1.find('strong').nextSibling
    else:
        total_time_n = ''
        total_time_m = ''
    prep_time_t = soup.find('div', {'class':'prep-time'}).find('small').get_text()
    cook_time_t = soup.find('div', {'class':'cook-time'}).find('small').get_text()
    ttime = '<div id="recipe-time">\n'
    ttime += '<table class="myOtherTable">\n<tr>\n<th><strong>Total Time</strong></th>\n'
    ttime += '<th><strong>Prep Time</strong></th>\n'
    ttime += '<th><strong>Cook Time</strong></th>\n</tr>\n'
    ttime += '<tr>\n<td id="total-time" class="c">{0}</td>\n'.format(
        total_time_n + ' ' + total_time_m)
    ttime += '<td id="prep-time" class="c">{0}</td>\n'.format(prep_time_t)
    ttime += '<td id="cook-time" class="c">{0}</td>\n</tr>\n</table>\n</div>'.format(cook_time_t)
    return ttime.encode('utf-8', 'ignore')


def format_ingredients(soup):
    ''' removing tags that I do not want '''
    for tag in soup.findAll('div', {
            'class':'relevant-slideshow'}) + soup.findAll('div', {
                'class':'fd-ad'}) + soup.findAll('div', {
                    'class':'deals'}) + soup.findAll('div', {
                        'class':'top-cat-recipe'}) + soup.findAll('div', {
                            'class':'extras'}):
        tag.extract()
    for tag in soup.findAll('a'):
        if 'units' in str(tag):
            tag.extract()
        elif 'nutrition' in str(tag):
            tag.parent.extract()

    del soup['data-module']
    del soup['class']
    soup['id'] = 'ingredients'
    serving = soup.find('a', {'class':'servings'})
    if serving:
        del serving['data-popup-id']
        del serving['data-target']
        del serving['data-toggle']
    return my_clean_string(unicode(soup).encode('utf-8', 'ignore'))


def format_directions(soup):
    for tag in soup.findAll('div', {'class':'recipe-tools'}):
        tag.parent.extract()

    del soup['data-module']
    del soup['class']
    soup['id'] = 'directions'

    ostring = my_clean_string(unicode(soup).encode('utf-8', 'ignore'))
    ostring = ostring.replace('<li>', '<p>').replace('</li>', '</p>')
    ostring = ostring.replace('<ol>', '').replace('</ol>', '')
    return my_clean_string(ostring)


def format_recipe_notes(soup):
    if soup:
        del soup['data-module']
        soup['class'] = 'recipe-notes'
        return my_clean_string(unicode(soup).encode('utf-8', 'ignore'))
    else:
        return


def format_category(soup):
    if soup:
        soup['class'] = 'category'
        cat = unicode(soup).replace('<span class="separator"></span>', ' / ')
        return my_clean_string(cat.encode('utf-8', 'ignore'))
    else:
        return


def write_file(docum, filename, infile):
    fullpath = os.path.join(r'C:\Stan\Recipies', filename)
    if os.path.isfile(fullpath):
        if not infile:
            println('')
            prompt = '### The file "{0}" is already created. Do you wish to overwrite it?:'.format(
                filename)
            answer = raw_input(prompt)
            if answer == 'y' or answer == 'Y':
                println('')
                println(' Writing file: {0}'.format(fullpath))
                with open(fullpath, 'wt') as outfile:
                    outfile.write(docum)
            else:
                println(" Didn't save the file")
        else:
            println(" File already created... skipping")
    else:
        println('')
        println(' Writing file: {0}'.format(fullpath))
        with open(fullpath, 'wt') as outfile:
            outfile.write(docum)
    return

def format_author(soup):
    author_name = repr(soup.get_text())
    author_name = my_clean_string(author_name).strip().replace("u'", '')[:-2]
    return author_name


def save_recipe(recipe, infile=False):
    println(' Getting recipe... {0}'.format(recipe))
    response = get_page(recipe)
    if response == '404' or response == '999':
        return

    println(' Generating soup...')
    soup = BeautifulSoup(response, 'html5lib')

    println(' Generating Document...')
    category = format_category(soup.find('div', {'class':'breadcrumbs'}))
    title = my_clean_string(unicode(soup.find('h1').get_text()))
    author_name = format_author(soup.find('ul', {'class':'fd-byline'}).findAll('span')[1])
    println('')
    println(_format_output('Title:', title))
    println(_format_output('Chef:', author_name))
    println('')
    total_time = format_total_time(soup.find('div', {'class':'recipe-time'}))
    recipe_notes = format_recipe_notes(soup.find('div', {'class':'recipe-notes'}))
    ingredients = format_ingredients(soup.find('div', {'class':'ingredients'}))
    directions = format_directions(soup.find('div', {'class':'directions'}))
    docum = create_doc([title, author_name, total_time, recipe_notes,
                        ingredients, directions, recipe, category])

    filename = ffix_fn('{} {}{}{} [food_com]'.format(title, '{', author_name, '}')) + '.html'
    write_file(docum, filename, infile)
    println('=' * LINE_WIDTH)

    return


def save_input_recipes(infile):
    if os.path.exists(infile):
        with open(infile) as filefile:
            lines = filefile.readlines()
        if lines:
            lines = sorted(list(set(lines)))
            for i, line in enumerate(lines):
                line = line.strip()
                if 'http://www.food.com/recipe/' in line:
                    println(' Getting recipe {} of {}...'.format(i+1, len(lines)))
                    save_recipe(line, True)
                else:
                    println('=' * LINE_WIDTH)
                    println(' That is not a recipe page... skipping {}'.format(line))
                    println('=' * LINE_WIDTH)
        else:
            println('')
            println(' There are no recipes in the file to process...')
            println('')
    return


import argparse

PROG_DESC = "Description of your program"
PROG_VER = "1.0"  # Replace with your program version

def main():
    version = ""
    parser = argparse.ArgumentParser(description=PROG_DESC)

    parser.add_argument('-i', '--input', nargs=1, type=str, default=False,
                        help='a recipe URL from food.com')
    parser.add_argument('-f', '--file', action='store', default=False,
                        help='A file that contains a list of urls to download')
    args = parser.parse_args()

    print(' Starting Process - {0}'.format(PROG_VER))
    print('#' * 50)  # Replace LINE_WIDTH with the desired width
    if args.input:
        if 'http://www.food.com/recipe/' in args.input[0]:
            save_recipe(args.input[0])
    else:
        if args.file:
            save_input_recipes(args.file)
        else:
            print('You need to enter a URL from food.net')
            parser.print_help()

    print('#' * 50)  # Replace LINE_WIDTH with the desired width
    print(' Completed Process - {0}'.format(PROG_VER))
    print('#' * 56)  # Adjust the number based on the width

    return

def save_recipe(url, infile=False):
    println(' Getting recipe... {0}'.format(url))
    response = get_page(url)
    if response == '404' or response == '999':
        return

    println(' Generating soup...')
    soup = BeautifulSoup(response, 'html5lib')

    println(' Generating Document...')
    category = format_category(soup.find('div', {'class':'breadcrumbs'}))
    title = my_clean_string(unicode(soup.find('h1').get_text()))
    author_name = format_author(soup.find('ul', {'class':'fd-byline'}).findAll('span')[1])
    println('')
    println(_format_output('Title:', title))
    println(_format_output('Chef:', author_name))
    println('')
    total_time = format_total_time(soup.find('div', {'class':'recipe-time'}))
    recipe_notes = format_recipe_notes(soup.find('div', {'class':'recipe-notes'}))
    ingredients = format_ingredients(soup.find('div', {'class':'ingredients'}))
    directions = format_directions(soup.find('div', {'class':'directions'}))
    docum = create_doc([title, author_name, total_time, recipe_notes,
                        ingredients, directions, url, category])  # Pass the URL to create_doc

    filename = ffix_fn('{} {}{}{} [food_com]'.format(title, '{', author_name, '}')) + '.html'
    write_file(docum, filename, infile)

    url_filename = 'recipe_urls.txt'
    with open(url_filename, 'a') as url_file:
        url_file.write(url + '\n')

    println('=' * LINE_WIDTH)
    println('Recipe saved successfully!')
    println('Title: {}'.format(title))
    println('Author: {}'.format(author_name))
    println('URL: {}'.format(url))
    println('=' * LINE_WIDTH)

    return


import csv

def save_recipe(url, infile=False):
    ''' This is where the recipe will be saved to the disk '''
    println(' Getting recipe... {0}'.format(url))
    response = get_page(url)
    if response == '404' or response == '999':
        return

    println(' Generating soup...')
    soup = BeautifulSoup(response, 'html5lib')

    println(' Generating Document...')
    category = format_category(soup.find('div', {'class': 'breadcrumbs'}))
    title = my_clean_string(unicode(soup.find('h1').get_text()))
    author_name = format_author(soup.find('ul', {'class': 'fd-byline'}).findAll('span')[1])

    total_time = format_total_time(soup.find('div', {'class': 'recipe-time'}))
    recipe_notes = format_recipe_notes(soup.find('div', {'class': 'recipe-notes'}))
    ingredients = format_ingredients(soup.find('div', {'class': 'ingredients'}))
    directions = format_directions(soup.find('div', {'class': 'directions'}))

    url_filename = 'recipe_urls.txt'
    with open(url_filename, 'a') as url_file:
        url_file.write(url + '\n')
 
    csv_filename = 'recipe_details.csv'
    with open(csv_filename, 'a', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Title', 'Author', 'URL', 'Total Time', 'Recipe Notes', 'Ingredients', 'Directions'])
        csv_writer.writerow([title, author_name, url, total_time, recipe_notes, ingredients, directions])

    println('=' * LINE_WIDTH)
    println('Recipe saved successfully!')
    println('Title: {}'.format(title))
    println('Author: {}'.format(author_name))
    println('URL: {}'.format(url))
    println('=' * LINE_WIDTH)

    return


def save_input_recipes(file_path):
    pass

if __name__ == '__main__':
    main()
